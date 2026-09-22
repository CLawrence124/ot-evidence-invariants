"""Deterministic validity is intentionally narrower than scientific entailment."""
from difflib import get_close_matches
import json
from ot_dossier.domain.models import Dossier, EvidencePacket, Finding, ValidationResult

VALIDATOR_VERSION = "0.2.1-citation-repair-hints"

def validate_dossier_references(packet: EvidencePacket, dossier: Dossier) -> ValidationResult:
    findings = []

    def report(code, message, claim_id="", severity="ERROR"):
        findings.append(Finding(code=code, severity=severity, claim_id=claim_id, message=message))

    if dossier.packet_id != packet.packet_id:
        report("PACKET_MISMATCH", "Dossier belongs to a different packet")
    if (dossier.target_id, dossier.disease_id) != (packet.target.id, packet.disease_scope.selected.id):
        report("ENTITY_MISMATCH", "Dossier entities differ from the selected pair")
    records = {r.record_ref: r for r in packet.records}
    ids = set()
    for claim in dossier.claims:
        if claim.id in ids:
            report("DUPLICATE_CLAIM_ID", "Claim IDs must be unique", claim.id)
        ids.add(claim.id)
        if claim.target_id != packet.target.id or claim.disease_id != packet.disease_scope.selected.id:
            report("ENTITY_MISMATCH", "Claim entities differ from selected pair", claim.id)
        missing = set(claim.record_refs) - records.keys()
        if missing:
            candidates = []
            for ref in sorted(missing)[:3]:
                matches = []
                for match in get_close_matches(ref, records, n=3, cutoff=0.5):
                    r = records[match]
                    matches.append({"record_ref": match, "kind": r.kind, "source": r.source,
                                    "source_disease": r.source_disease.model_dump() if r.source_disease else None,
                                    "cassette": r.provenance.cassette,
                                    "json_pointer": r.provenance.json_pointer})
                candidates.append({"invalid_ref": ref, "candidates": matches})
            report("DANGLING_REFERENCE", "Missing record(s): " + ", ".join(sorted(missing))
                   + ". Exact existing IDs with similar spelling (not proof of claim support; inspect the records, choose an appropriate citation or remove the claim; no automatic substitution): "
                   + json.dumps(candidates, separators=(",", ":")), claim.id)
        cited = [records[r] for r in claim.record_refs if r in records]
        disease_ids = {r.source_disease.id for r in cited if r.source_disease is not None}
        if len(disease_ids) > 1:
            report("MIXED_DISEASE_SCOPE", "Split source diseases into separate claims; each claim may cite only one source disease", claim.id)
        if claim.assertion == "direct_evidence" and (
            not cited or not all(r.kind == "evidence" and r.disease_relation == "direct" for r in cited)
        ):
            report("INDIRECT_SCOPE", "Every citation in a direct-evidence claim must be direct disease evidence; split descendant or target-context observations into separate claims", claim.id)
        if claim.assertion == "approval_for_selected":
            approved = any(r.kind == "clinical" and r.disease_relation == "direct" and r.attributes["clinical_stage"].value == "APPROVAL" for r in cited)
            if not approved:
                report("INDICATION_MISMATCH", "No cited clinical record has APPROVAL for the exact selected disease; PHASE_4 is not substituted", claim.id)
        if claim.assertion == "safe_target":
            report("UNSUPPORTED_SAFETY_INFERENCE", "This packet cannot establish that a target is safe", claim.id)
    for name, section in packet.sections.items():
        state = dossier.section_states.get(name)
        if state is None:
            report("REQUIRED_SECTION_UNKNOWN", f"{name} needs an explicit section state", severity="WARNING")
        elif state != section.interpretation:
            report("MISSINGNESS_MISMATCH", f"{name} must preserve the packet's interpretation state")
    return ValidationResult(valid=not any(f.severity == "ERROR" for f in findings), findings=tuple(findings))
