"""Public contracts; scientific claims must not rely on free-text parsing."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

Missing = Literal["unknown", "not_assessed", "unavailable", "not_applicable"]
Status = Literal["complete", "complete_empty", "truncated", "partial", "failed"]
Relation = Literal["direct", "descendant_of_selected", "unrelated", "target_context"]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Datum(Model):
    state: Literal["present", "unknown", "not_assessed", "unavailable", "not_applicable"]
    value: JsonValue = None
    reason: str = ""

    @model_validator(mode="after")
    def consistent(self):
        if self.state == "present" and self.value is None:
            raise ValueError("A present value cannot be null")
        if self.state != "present" and (self.value is not None or not self.reason):
            raise ValueError("Missing values need a state and reason, and cannot carry a value")
        return self


class Entity(Model):
    id: str
    name: str


class DiseaseScope(Model):
    selected: Entity
    descendant_ids: tuple[str, ...]
    include_descendants: Literal[True] = True


class Retrieval(Model):
    status: Status
    returned: int = Field(ge=0)
    total: int | None = Field(default=None, ge=0)
    reason: str = ""
    errors: tuple[str, ...] = ()

    @model_validator(mode="after")
    def consistent(self):
        if self.total is not None and self.returned > self.total:
            raise ValueError("Returned count exceeds upstream total")
        if self.status in ("truncated", "partial", "failed") and not self.reason:
            raise ValueError("Incomplete retrieval needs a reason")
        if self.status in ("complete", "complete_empty"):
            if self.errors or self.total != self.returned:
                raise ValueError("Complete retrieval requires a matching count and no errors")
            if (self.returned == 0) != (self.status == "complete_empty"):
                raise ValueError("Empty results require complete_empty")
        if self.status == "failed" and self.returned:
            raise ValueError("A failed retrieval cannot contain records; use partial")
        return self


class Provenance(Model):
    cassette: str
    response_sha256: str
    json_pointer: str
    source_url: str


class Record(Model):
    record_ref: str
    kind: Literal["evidence", "clinical", "safety", "function", "tractability"]
    target_id: str
    source_disease: Entity | None = None  # None only for target-level annotations.
    disease_relation: Relation
    source: str
    upstream_id: Datum
    attributes: dict[str, Datum]
    provenance: Provenance

    @model_validator(mode="after")
    def clinical_unit(self):
        if self.kind in ("evidence", "clinical") and self.source_disease is None:
            raise ValueError("Disease evidence must retain its source disease")
        if self.kind == "clinical":
            for key in ("drug_id", "drug_name", "mechanisms", "clinical_stage", "clinical_report_id"):
                if key not in self.attributes:
                    raise ValueError(f"Clinical unit missing {key}")
            if self.attributes["drug_id"].state != "present":
                raise ValueError("Clinical record requires an identified drug")
        return self


class Section(Model):
    retrieval: Retrieval
    record_refs: tuple[str, ...]
    interpretation: Datum
    scope: str


class EvidencePacket(Model):
    schema_version: Literal["0.1"] = "0.1"
    packet_id: str
    snapshot_id: str
    endpoint: str
    retrieved_at: str
    release: dict[str, JsonValue]
    target: Entity
    disease_scope: DiseaseScope
    records: tuple[Record, ...]
    sections: dict[str, Section]

    @model_validator(mode="after")
    def enforce_scope(self):
        refs = {r.record_ref for r in self.records}
        if len(refs) != len(self.records):
            raise ValueError("Duplicate record references")
        for record in self.records:
            if record.target_id != self.target.id:
                raise ValueError("Record target does not match packet")
            if record.source_disease is None:
                expected = "target_context"
            elif record.source_disease.id == self.disease_scope.selected.id:
                expected = "direct"
            elif record.source_disease.id in self.disease_scope.descendant_ids:
                expected = "descendant_of_selected"
            else:
                expected = "unrelated"
            if record.disease_relation != expected:
                raise ValueError("Disease relation conflicts with the frozen ontology")
            if record.kind == "evidence" and expected not in ("direct", "descendant_of_selected"):
                raise ValueError("Out-of-scope disease evidence")
        required = {"evidence", "clinical", "safety", "function", "tractability"}
        if set(self.sections) != required:
            raise ValueError("Packet requires exactly the five supported sections")
        for name, section in self.sections.items():
            if set(section.record_refs) - refs:
                raise ValueError("Section has dangling references")
            actual = {r.record_ref for r in self.records if r.kind == name}
            if set(section.record_refs) != actual or len(section.record_refs) != len(actual):
                raise ValueError("Section must reference exactly its own records")
            if section.retrieval.returned != len(actual):
                raise ValueError("Section count does not match its records")
            if section.retrieval.status in ("failed", "partial", "truncated") and section.interpretation.state != "unavailable":
                raise ValueError("Incomplete sections require unavailable interpretation")
            if section.retrieval.status == "complete_empty" and section.interpretation.state != "unknown":
                raise ValueError("No returned records establish no positive or negative conclusion")
        return self


class Claim(Model):
    id: str
    text: str = Field(min_length=1)
    target_id: str
    disease_id: str
    record_refs: tuple[str, ...] = Field(min_length=1)
    assertion: Literal["retrieved_fact", "direct_evidence", "approval_for_selected", "safe_target"] = "retrieved_fact"


class Dossier(Model):
    packet_id: str
    target_id: str
    disease_id: str
    claims: tuple[Claim, ...]
    section_states: dict[str, Datum]


class Finding(Model):
    code: str
    severity: Literal["ERROR", "WARNING"]
    claim_id: str = ""
    message: str


class ValidationResult(Model):
    valid: bool
    findings: tuple[Finding, ...]
    scope: str = "Checks structured assertions and reference membership, not scientific entailment or arbitrary prose."
