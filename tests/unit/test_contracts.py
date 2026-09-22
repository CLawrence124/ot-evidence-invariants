from copy import deepcopy
import json

import pytest
from pydantic import ValidationError

from ot_dossier.api.graphql_client import canonical
from ot_dossier.cli import review_dossier
from ot_dossier.domain.evidence_assembler import DEFAULT_SNAPSHOT, assemble, assemble_target_disease_evidence, load_snapshot
from ot_dossier.domain.dossier_validator import validate_dossier_references
from ot_dossier.domain.models import Claim, Datum, Dossier, EvidencePacket, Retrieval


@pytest.mark.parametrize("target", ["NOD2", "TNF"])
def test_replay_is_byte_identical_and_scoped(target):
    first = assemble_target_disease_evidence(target)
    second = assemble_target_disease_evidence(target)
    assert canonical(first.model_dump(mode="json")) == canonical(second.model_dump(mode="json"))
    assert first.sections["evidence"].retrieval.status == "truncated"
    assert first.sections["evidence"].retrieval.returned == 300
    for r in first.records:
        if r.disease_relation == "direct":
            assert r.source_disease.id == first.disease_scope.selected.id
        if r.disease_relation == "descendant_of_selected":
            assert r.source_disease.id in first.disease_scope.descendant_ids
    assert validate_dossier_references(first, review_dossier(first)).valid


@pytest.mark.parametrize("kwargs", [
    dict(status="truncated", returned=1, total=2),
    dict(status="complete_empty", returned=0, total=0, errors=("upstream error",)),
    dict(status="complete", returned=1, total=2),
    dict(status="complete_empty", returned=1, total=1),
])
def test_invalid_retrieval_states_rejected(kwargs):
    with pytest.raises(ValidationError):
        Retrieval(**kwargs)


def test_missingness_requires_a_reason():
    with pytest.raises(ValidationError):
        Datum(state="unknown")
    with pytest.raises(ValidationError):
        Datum(state="present")


def test_invalid_entities_are_not_empty_results():
    for target, disease in [("BAD", "IBD"), ("NOD2", "EFO_0003767")]:
        with pytest.raises(ValueError):
            assemble_target_disease_evidence(target, disease)
    manifest, cassettes = load_snapshot(DEFAULT_SNAPSHOT)
    cassettes["entities.json"]["response"]["data"]["disease"] = None
    with pytest.raises(ValueError, match="Entity lookup failed"):
        assemble("NOD2", manifest, cassettes)


def test_partial_graphql_errors_cannot_become_empty():
    manifest, cassettes = load_snapshot(DEFAULT_SNAPSHOT)
    cassettes["nod2_context.json"]["response"]["errors"] = [{"message": "safety failed"}]
    packet = assemble("NOD2", manifest, cassettes)
    assert packet.sections["safety"].retrieval.status == "failed"
    assert packet.sections["safety"].interpretation.state == "unavailable"


def test_null_context_distinct_from_empty():
    manifest, cassettes = load_snapshot(DEFAULT_SNAPSHOT)
    cassettes["nod2_context.json"]["response"]["data"]["target"] = None
    packet = assemble("NOD2", manifest, cassettes)
    assert packet.sections["safety"].retrieval.status == "failed"


def test_pagination_chain_mismatch_rejected():
    manifest, cassettes = load_snapshot(DEFAULT_SNAPSHOT)
    cassettes["nod2_evidence_1.json"]["request"]["variables"]["cursor"] = "wrong"
    with pytest.raises(ValueError, match="cursor chain"):
        assemble("NOD2", manifest, cassettes)


def test_upstream_target_mismatch_rejected():
    manifest, cassettes = load_snapshot(DEFAULT_SNAPSHOT)
    cassettes["nod2_evidence_0.json"]["response"]["data"]["disease"]["evidences"]["rows"][0]["target"]["id"] = "WRONG"
    with pytest.raises(ValueError, match="target mismatch"):
        assemble("NOD2", manifest, cassettes)


def test_tampered_cassette_rejected(tmp_path):
    manifest, _ = load_snapshot(DEFAULT_SNAPSHOT)
    (tmp_path / "manifest.json").write_text(json.dumps({"files": {"entities.json": manifest["files"]["entities.json"]}}))
    (tmp_path / "entities.json").write_text("{}")
    with pytest.raises(ValueError, match="checksum"):
        load_snapshot(tmp_path)


def test_record_ids_survive_dictionary_order():
    manifest, cassettes = load_snapshot(DEFAULT_SNAPSHOT)
    first = assemble("NOD2", manifest, cassettes)
    reordered = json.loads(json.dumps(cassettes, sort_keys=True))
    assert first == assemble("NOD2", manifest, reordered)


def claim_dossier(packet, record_ref, assertion):
    return Dossier(packet_id=packet.packet_id, target_id=packet.target.id, disease_id=packet.disease_scope.selected.id,
        claims=(Claim(id="fault", text="Synthetic deliberately invalid assertion", target_id=packet.target.id,
                      disease_id=packet.disease_scope.selected.id, record_refs=(record_ref,), assertion=assertion),),
        section_states={k:s.interpretation for k,s in packet.sections.items()})


def codes(packet, dossier):
    result = validate_dossier_references(packet, dossier)
    assert not result.valid
    return {f.code for f in result.findings}


def test_fault_descendant_only_cannot_be_direct():
    manifest, cassettes = load_snapshot(DEFAULT_SNAPSHOT)
    row = next(r for r in cassettes["nod2_evidence_0.json"]["response"]["data"]["disease"]["evidences"]["rows"] if r["disease"]["id"] != "MONDO_0005265")
    cassettes["nod2_evidence_0.json"]["response"]["data"]["disease"]["evidences"] = {"count":1,"cursor":None,"rows":[row]}
    for name in ["nod2_evidence_1.json", "nod2_evidence_2.json"]:
        del cassettes[name]
    packet = assemble("NOD2", manifest, cassettes)
    record = next(r for r in packet.records if r.kind == "evidence")
    assert record.disease_relation == "descendant_of_selected"
    assert "INDIRECT_SCOPE" in codes(packet, claim_dossier(packet, record.record_ref, "direct_evidence"))
    bad = packet.model_dump(mode="json")
    next(r for r in bad["records"] if r["kind"] == "evidence")["disease_relation"] = "direct"
    with pytest.raises(ValidationError, match="frozen ontology"):
        EvidencePacket.model_validate(bad)


def test_fault_wrong_indication_approval():
    # Explicit synthetic clinical unit, not an assertion about any actual drug.
    packet = assemble_target_disease_evidence("TNF")
    data = packet.model_dump(mode="json")
    clinical = next(r for r in data["records"] if r["kind"] == "clinical")
    clinical["source_disease"] = {"id":"SYNTHETIC_UNRELATED", "name":"Synthetic unrelated indication"}
    clinical["disease_relation"] = "unrelated"
    clinical["attributes"]["clinical_stage"] = {"state":"present", "value":"APPROVAL", "reason":""}
    data["packet_id"] = "synthetic-wrong-indication"
    packet = EvidencePacket.model_validate(data)
    assert "INDICATION_MISMATCH" in codes(packet, claim_dossier(packet, clinical["record_ref"], "approval_for_selected"))


def test_fault_removed_safety_does_not_establish_safety():
    manifest, cassettes = load_snapshot(DEFAULT_SNAPSHOT)
    cassettes["tnf_context.json"]["response"]["data"]["target"]["safetyLiabilities"] = []
    packet = assemble("TNF", manifest, cassettes)
    assert packet.sections["safety"].retrieval.status == "complete_empty"
    assert packet.sections["safety"].interpretation.state == "unknown"
    assert "UNSUPPORTED_SAFETY_INFERENCE" in codes(packet, claim_dossier(packet, packet.records[0].record_ref, "safe_target"))


def test_fault_dangling_citation():
    packet = assemble_target_disease_evidence("NOD2")
    assert "DANGLING_REFERENCE" in codes(packet, claim_dossier(packet, "rec_nonexistent", "retrieved_fact"))


def test_cross_target_reference_is_rejected():
    packet = assemble_target_disease_evidence("NOD2")
    other = assemble_target_disease_evidence("TNF")
    assert "DANGLING_REFERENCE" in codes(packet, claim_dossier(packet, other.records[0].record_ref, "retrieved_fact"))


def test_reference_validity_is_not_entailment():
    packet = assemble_target_disease_evidence("NOD2")
    # Deliberately false text can pass: do not claim that this validator understands prose.
    data = claim_dossier(packet, packet.records[0].record_ref, "retrieved_fact").model_dump(mode="json")
    data["claims"][0]["text"] = "This target cures every disease."
    assert validate_dossier_references(packet, Dossier.model_validate(data)).valid
