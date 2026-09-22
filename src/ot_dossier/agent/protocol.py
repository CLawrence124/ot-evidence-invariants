"""Shared adapter contract, independent of how the CLI module is launched."""
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

ASSEMBLE = "assemble_target_disease_evidence"
VALIDATE = "validate_dossier_references"


class ModelReply(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: dict
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    provider_metadata: dict = Field(default_factory=dict)


class ModelAdapter(Protocol):
    model_id: str
    mode: str

    async def respond(self, context: dict) -> ModelReply: ...
