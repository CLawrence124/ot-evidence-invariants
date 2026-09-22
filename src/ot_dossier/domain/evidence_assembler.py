"""Replay-only service. API-specific normalization lives here, never in MCP."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ot_dossier.api.graphql_client import ROOT, TARGETS, DISEASE, canonical, digest
from ot_dossier.domain.models import (Datum, DiseaseScope, Entity, EvidencePacket,
                                      Provenance, Record, Retrieval, Section)

DEFAULT_SNAPSHOT = ROOT / "fixtures/cassettes/26.06"


def datum(value, reason="Upstream returned no value") -> Datum:
    return Datum(state="unknown", reason=reason) if value is None else Datum(state="present", value=value)


def load_snapshot(path: Path) -> tuple[dict, dict]:
    manifest = json.loads((path / "manifest.json").read_text())
    cassettes = {}
    for name, expected in manifest["files"].items():
        if Path(name).name != name:
            raise ValueError("Invalid cassette path")
        raw = (path / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError(f"Cassette checksum mismatch: {name}")
        cassettes[name] = json.loads(raw)
    return manifest, cassettes


def assemble_target_disease_evidence(target: str, disease: str = "IBD", snapshot: Path = DEFAULT_SNAPSHOT) -> EvidencePacket:
    symbol = next((s for s, i in TARGETS.items() if target.upper() == s or target == i), None)
    if symbol is None or disease not in ("IBD", DISEASE):
        raise ValueError("v1 accepts NOD2/TNF and IBD/MONDO_0005265 only; legacy EFO ID is not silently remapped")
    manifest, cassettes = load_snapshot(snapshot)
    return assemble(symbol, manifest, cassettes)


def assemble(symbol: str, manifest: dict, cassettes: dict) -> EvidencePacket:
    """Pure transformation. Tests may supply explicitly synthetic cassette copies."""
    target_id = TARGETS[symbol]
    entities = cassettes["entities.json"]
    edata = entities["response"].get("data") or {}
    if entities["response"].get("errors") or not edata.get("disease"):
        raise ValueError("Entity lookup failed; cannot treat a null disease as empty evidence")
    disease = edata["disease"]
    if disease["id"] != DISEASE or edata[symbol.lower()] != {"id": target_id, "approvedSymbol": symbol}:
        raise ValueError("Frozen entity identities do not match requested case")
    if edata["meta"] != manifest["release"]:
        raise ValueError("Release metadata mismatch")
    scope = DiseaseScope(selected=Entity(id=disease["id"], name=disease["name"]), descendant_ids=tuple(sorted(disease["descendants"])))
    records: dict[str, Record] = {}

    def relation(entity):
        if entity is None:
            return "target_context"
        if entity["id"] == DISEASE:
            return "direct"
        return "descendant_of_selected" if entity["id"] in scope.descendant_ids else "unrelated"

    def add(kind, row, attrs, source, cassette_name, pointer, entity=None, upstream=None):
        cassette = cassettes[cassette_name]
        content = {"kind": kind, "target_id": target_id, "source_disease": entity,
                   "disease_relation": relation(entity), "source": source,
                   "upstream_id": datum(upstream), "attributes": {k: datum(v) for k, v in attrs.items()}}
        serial = {k: v.model_dump(mode="json") if isinstance(v, Datum) else v for k, v in content.items()}
        serial["attributes"] = {k: v.model_dump(mode="json") for k, v in content["attributes"].items()}
        ref = "rec_" + digest(serial)
        records.setdefault(ref, Record(record_ref=ref, **content, provenance=Provenance(
            cassette=cassette_name, response_sha256=digest(cassette["response"]), json_pointer=pointer,
            source_url=f"https://platform.opentargets.org/evidence/{target_id}/{entity['id']}" if entity else f"https://platform.opentargets.org/target/{target_id}")))

    prefix = symbol.lower()
    names = sorted((n for n in cassettes if n.startswith(prefix + "_evidence_")), key=lambda n: int(n.rsplit("_", 1)[1].split(".")[0]))
    errors, totals, raw_rows, seen_ids = [], set(), 0, set()
    cursor = None
    last_page = {}
    for index, name in enumerate(names):
        cassette = cassettes[name]
        variables = cassette["request"]["variables"]
        if variables["targets"] != [target_id] or variables["disease"] != DISEASE or variables["cursor"] != cursor:
            raise ValueError("Cassette request identity or cursor chain mismatch")
        body = cassette["response"]
        errors.extend(e.get("message", str(e)) for e in body.get("errors", []))
        d = (body.get("data") or {}).get("disease")
        page = (d or {}).get("evidences")
        if not page:
            errors.append("Evidence field unavailable")
            break
        if d["id"] != DISEASE:
            raise ValueError("Evidence response disease mismatch")
        last_page = page
        totals.add(page["count"])
        for offset, row in enumerate(page["rows"]):
            raw_rows += 1
            if row["id"] in seen_ids:
                errors.append("Duplicate upstream evidence ID across pages")
                continue
            seen_ids.add(row["id"])
            if row["target"]["id"] != target_id:
                raise ValueError("Upstream evidence target mismatch")
            ptr = f"/data/disease/evidences/rows/{offset}"
            attrs = {k: v for k, v in row.items() if k not in ("id", "target", "disease", "drug")}
            add("evidence", row, attrs, row["datasourceId"], name, ptr, row["disease"], row["id"])
            if row.get("drug"):
                drug = row["drug"]
                mechanisms = (drug.get("mechanismsOfAction") or {}).get("rows")
                # Keep only mechanisms explicitly mapped to this target.
                mechanisms = None if mechanisms is None else [m for m in mechanisms if target_id in [t["id"] for t in m["targets"]]]
                add("clinical", row, {"drug_id": drug["id"], "drug_name": drug["name"],
                    "mechanisms": mechanisms, "clinical_stage": row.get("clinicalStage"),
                    "clinical_report_id": row.get("clinicalReportId")}, row["datasourceId"], name, ptr, row["disease"], row["id"])
        next_cursor = page.get("cursor")
        if next_cursor and next_cursor == cursor:
            errors.append("Pagination cursor did not advance")
        cursor = next_cursor
        if index < len(names) - 1 and not cursor:
            raise ValueError("Unexpected extra pages after terminal cursor")
    if len(totals) > 1:
        errors.append("Upstream total changed across pages")
    if not names:
        errors.append("No evidence pages captured")
    total = next(iter(totals)) if len(totals) == 1 else None
    count = sum(r.kind == "evidence" for r in records.values())
    if total is not None and count > total:
        raise ValueError("Evidence exceeds upstream total")
    if errors:
        status, reason = ("partial" if count else "failed"), "; ".join(errors)
    elif count == total:
        status, reason = ("complete" if count else "complete_empty"), ""
    elif cursor and last_page.get("rows"):
        status, reason = "truncated", f"Stopped at configured snapshot bound: {len(names)} pages; {count} of {total} rows"
    else:
        status, reason = "partial", "Pagination ended before upstream count was reached"

    def section(kind, retrieval, scope_text):
        refs = tuple(sorted(r.record_ref for r in records.values() if r.kind == kind))
        if retrieval.status in ("truncated", "partial", "failed"):
            state, reason = "unavailable", "Coverage is incomplete; absence conclusions are not supported"
        elif not refs:
            state, reason = "unknown", "No curated records returned under this retrieval; no negative or safety conclusion follows"
        else:
            state, reason = "not_assessed", "Records retrieved; scientific interpretation requires review"
        return Section(retrieval=retrieval, record_refs=refs, interpretation=Datum(state=state, reason=reason), scope=scope_text)

    sections = {"evidence": section("evidence", Retrieval(status=status, returned=count, total=total, reason=reason, errors=tuple(errors)), "Selected disease plus frozen descendants; bounded evidence pages")}
    clinical_count = sum(r.kind == "clinical" for r in records.values())
    # Clinical completeness is ONLY relative to the captured disease-evidence query.
    cr = Retrieval(status=status if status not in ("complete", "complete_empty") else ("complete" if clinical_count else "complete_empty"),
                   returned=clinical_count, total=clinical_count if status in ("complete", "complete_empty") else None,
                   reason=reason, errors=tuple(errors))
    sections["clinical"] = section("clinical", cr, "Drug-bearing rows within the scoped evidence query; not all target drugs or indications")
    name = prefix + "_context.json"
    cassette = cassettes.get(name)
    body = cassette["response"] if cassette else {}
    context = (body.get("data") or {}).get("target") or {}
    if context and context["id"] != target_id:
        raise ValueError("Context target mismatch")
    if cassette and cassette["request"]["variables"].get("target") != target_id:
        raise ValueError("Context request target mismatch")
    for kind, field in (("safety", "safetyLiabilities"), ("tractability", "tractability"), ("function", "functionDescriptions")):
        rows = context.get(field)
        context_errors = tuple(e.get("message", str(e)) for e in body.get("errors", []))
        for i, row in enumerate(rows or []):
            attrs = {"description": row} if isinstance(row, str) else row
            add(kind, row, attrs, row.get("datasource", "Open Targets") if isinstance(row, dict) else "Open Targets", name, f"/data/target/{field}/{i}")
        n = sum(r.kind == kind for r in records.values())
        failed = rows is None or bool(context_errors)
        retrieval = Retrieval(status=("partial" if n else "failed") if failed else ("complete" if n else "complete_empty"),
                              returned=n, total=None if failed else n, reason="Target annotation unavailable or returned errors" if failed else "", errors=context_errors)
        sections[kind] = section(kind, retrieval, "Target-level annotation; not IBD-specific or a comprehensive safety assessment")
    contents = dict(snapshot_id="snapshot_" + digest(manifest), endpoint=entities["endpoint"],
                    retrieved_at=entities["retrieved_at"], release=edata["meta"],
                    target=Entity(id=target_id, name=symbol), disease_scope=scope,
                    records=tuple(sorted(records.values(), key=lambda r: r.record_ref)), sections=sections)
    provisional = EvidencePacket(packet_id="pending", **contents)
    packet_id = "packet_" + digest(provisional.model_dump(mode="json", exclude={"packet_id"}))
    return EvidencePacket(packet_id=packet_id, **contents)
