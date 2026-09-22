"""Regression cases derived from the signed-off NOD2 review, using frozen sources."""
import pytest

from ot_dossier.agent.loop import render
from ot_dossier.cli import review_dossier
from ot_dossier.domain.dossier_validator import validate_dossier_references
from ot_dossier.domain.evidence_assembler import assemble_target_disease_evidence
from ot_dossier.domain.models import Dossier, EvidencePacket


@pytest.fixture
def packet():
    return assemble_target_disease_evidence("NOD2")


def with_refs(packet, refs, assertion="direct_evidence"):
    data = review_dossier(packet).model_dump(mode="json")
    data["claims"] = [data["claims"][0]]
    data["claims"][0].update(record_refs=refs, assertion=assertion)
    return Dossier.model_validate(data)


@pytest.mark.parametrize("assertion", ["direct_evidence", "retrieved_fact"])
def test_one_direct_record_cannot_launder_descendant_scope(packet, assertion):
    # Mirrors claim-04: an IBD gene-burden observation plus Crohn observations.
    rows = [r for r in packet.records if r.source == "gene_burden"]
    direct = next(r for r in rows if r.disease_relation == "direct")
    descendant = next(r for r in rows if r.disease_relation == "descendant_of_selected")
    result = validate_dossier_references(packet, with_refs(packet, [direct.record_ref, descendant.record_ref], assertion))
    codes = {f.code for f in result.findings}
    assert not result.valid
    assert "MIXED_DISEASE_SCOPE" in codes
    if assertion == "direct_evidence":
        assert "INDIRECT_SCOPE" in codes


def test_direct_assertion_cannot_include_target_context(packet):
    direct = next(r for r in packet.records if r.disease_relation == "direct")
    context = next(r for r in packet.records if r.kind == "function")
    result = validate_dossier_references(packet, with_refs(packet, [direct.record_ref, context.record_ref]))
    assert not result.valid
    assert "INDIRECT_SCOPE" in {f.code for f in result.findings}


@pytest.mark.parametrize("relation,assertion", [("direct", "direct_evidence"), ("descendant_of_selected", "retrieved_fact")])
def test_same_disease_multiple_records_remain_valid(packet, relation, assertion):
    first = next(r for r in packet.records if r.kind == "evidence" and r.disease_relation == relation)
    refs = [r.record_ref for r in packet.records if r.kind == "evidence" and r.source_disease.id == first.source_disease.id][:2]
    assert len(refs) == 2
    assert validate_dossier_references(packet, with_refs(packet, refs, assertion)).valid


def test_renderer_separates_evidence_totals_from_unknown_clinical_total(packet):
    text = render(packet, review_dossier(packet), "test", "live")
    assert "evidence: truncated; 300 records returned; total 4003" in text
    assert "clinical: truncated; 0 records returned; total unknown" in text
    assert "safety: complete_empty; 0 records returned; total 0" in text
    assert "packet.json#/sections/clinical" in text
    assert "packet.json#/sections/safety" in text
    # Exercise unknown versus a known total: renderer must read metadata, not hard-code it.
    data = packet.model_dump(mode="json")
    data["sections"]["clinical"]["retrieval"]["total"] = 17
    changed = EvidencePacket.model_validate(data)
    assert "clinical: truncated; 0 records returned; total 17" in render(changed, review_dossier(changed), "test")


def test_validator_still_does_not_prove_prose_entailment(packet):
    # Scope fixes must not be advertised as solving the unrelated safety-citation finding.
    tractability = next(r for r in packet.records if r.kind == "tractability")
    data = with_refs(packet, [tractability.record_ref], "retrieved_fact").model_dump(mode="json")
    data["claims"][0]["text"] = "The safety query returned no records."
    result = validate_dossier_references(packet, Dossier.model_validate(data))
    assert result.valid  # Exists + structured contracts; human review must flag support.


def test_corrupted_reference_gets_exact_hints_but_is_not_replaced(packet):
    record = next(r for r in packet.records if r.source == "uniprot_literature")
    malformed = record.record_ref[:48] + "6e7b86c5763a7119af92f684d95"
    dossier = with_refs(packet, [malformed], "retrieved_fact")
    result = validate_dossier_references(packet, dossier)
    assert not result.valid
    finding = next(f for f in result.findings if f.code == "DANGLING_REFERENCE")
    assert record.record_ref in finding.message
    assert "uniprot_literature" in finding.message
    assert "no automatic substitution" in finding.message
    assert dossier.claims[0].record_refs == (malformed,)
