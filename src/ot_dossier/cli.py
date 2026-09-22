"""Offline review drafts, deliberately not presented as model-generated dossiers."""
import argparse
from pathlib import Path

from ot_dossier.api.graphql_client import canonical
from ot_dossier.domain.evidence_assembler import assemble_target_disease_evidence
from ot_dossier.domain.dossier_validator import validate_dossier_references
from ot_dossier.domain.models import Claim, Dossier


def review_dossier(packet):
    claims = []
    # A bounded sample for manual inspection, not a scientific synthesis or ranking.
    for relation in ("direct", "descendant_of_selected"):
        record = next((r for r in packet.records if r.kind == "evidence" and r.disease_relation == relation), None)
        if record:
            claims.append(Claim(id=f"scope-{relation}",
                text=f"A captured {record.source} record is annotated to {record.source_disease.name} ({record.source_disease.id}); relation to selected IBD: {relation}.",
                target_id=packet.target.id, disease_id=packet.disease_scope.selected.id,
                record_refs=(record.record_ref,), assertion="direct_evidence" if relation == "direct" else "retrieved_fact"))
    clinical = next((r for r in packet.records if r.kind == "clinical" and r.attributes["clinical_stage"].value == "APPROVAL"), None)
    if clinical:
        claims.append(Claim(id="clinical-example", text=f"One captured record reports {clinical.attributes['drug_name'].value}, stage APPROVAL, for {clinical.source_disease.name} ({clinical.source_disease.id}). This is the source indication, not approval for every IBD subtype.",
            target_id=packet.target.id, disease_id=packet.disease_scope.selected.id,
            record_refs=(clinical.record_ref,)))
    return Dossier(packet_id=packet.packet_id, target_id=packet.target.id, disease_id=packet.disease_scope.selected.id,
                   claims=tuple(claims), section_states={k: s.interpretation for k, s in packet.sections.items()})


def markdown(packet, dossier):
    version = packet.release["dataVersion"]
    release_label = f"{version['year']}.{version['month']}"
    lines = [f"# {packet.target.name} — inflammatory bowel disease", "",
             "**Phase 0/1 deterministic review draft. Human scientific review pending; no LLM synthesis has run.**", "",
             f"Selected disease: `{packet.disease_scope.selected.id}`. Packet: `{packet.packet_id}`.", "",
             f"Snapshot captured: {packet.retrieved_at}. Data release: {release_label}.", "",
             "## Retrieval coverage", "", "| Section | Status | Records | Interpretation |", "|---|---|---:|---|"]
    for name, section in packet.sections.items():
        lines.append(f"| {name} | {section.retrieval.status} | {section.retrieval.returned} | {section.interpretation.state} |")
    lines.extend(["", packet.sections["evidence"].retrieval.reason, "",
                  "Clinical coverage is limited to drug-bearing evidence rows. Target annotations are not disease-specific.",
                  "An empty safety result means no curated records returned under this query; it does not establish safety.", "",
                  "## Inspectable source observations", ""])
    records = {r.record_ref: r for r in packet.records}
    for claim in dossier.claims:
        lines.append(f"- {claim.text}")
        for ref in claim.record_refs:
            r = records[ref]
            lines.append(f"  - [{ref}]({r.provenance.source_url}); cassette `{r.provenance.cassette}`, JSON pointer `{r.provenance.json_pointer}`.")
    lines.extend(["", "## Interpretation still to do", "",
                  "Biological mechanism, genetic causality, direction of intervention, conflict assessment, tissue context, and translational usefulness have not been assessed. Review the raw records before adding these claims.", "",
                  "Record counts are not independent replications. Association scores are not therapeutic success probabilities. A valid reference does not prove that a sentence is scientifically supported.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, choices=["NOD2", "TNF"])
    parser.add_argument("--disease", default="IBD")
    parser.add_argument("--out", type=Path, default=Path("generated"))
    args = parser.parse_args()
    packet = assemble_target_disease_evidence(args.target, args.disease)
    dossier = review_dossier(packet)
    result = validate_dossier_references(packet, dossier)
    if not result.valid:
        raise ValueError(result.model_dump_json())
    args.out.mkdir(parents=True, exist_ok=True)
    stem = args.target.lower() + "_ibd"
    for name, model in (("packet", packet), ("dossier", dossier), ("validation", result)):
        (args.out / f"{stem}.{name}.json").write_text(canonical(model.model_dump(mode="json")) + "\n")
    (args.out / f"{stem}.md").write_text(markdown(packet, dossier))
    print(f"Wrote deterministic review draft and JSON to {args.out.resolve()}")


if __name__ == "__main__":
    main()
