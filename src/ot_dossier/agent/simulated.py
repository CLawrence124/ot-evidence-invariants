"""Scripted model adapter exercising the real host and MCP, not scientific reasoning."""
from ot_dossier.agent.protocol import ASSEMBLE, ModelReply
from ot_dossier.cli import review_dossier
from ot_dossier.domain.models import EvidencePacket


class SimulatedModel:
    mode = "simulated"

    def __init__(self, scenario="happy"):
        if scenario not in {"happy", "repair", "malformed", "invalid", "budget"}:
            raise ValueError("Unknown simulated scenario")
        self.scenario = scenario
        self.model_id = "scripted-v1/" + scenario
        self.submissions = 0

    async def respond(self, context):
        packets = [m["data"] for m in context["history"] if m["role"] == "tool_result" and m["name"] == ASSEMBLE and not m["is_error"]]
        if not packets or self.scenario == "budget":
            return ModelReply(action={"kind": "tool", "name": ASSEMBLE, "arguments": {"target": context["target"], "disease": "IBD"}})
        packet = EvidencePacket.model_validate(packets[-1])
        # Deterministic observations only, drawn from the returned tool data.
        dossier = review_dossier(packet).model_dump(mode="json")
        self.submissions += 1
        if self.scenario == "invalid" or (self.scenario == "repair" and self.submissions == 1):
            dossier["claims"][0]["record_refs"] = ["rec_nonexistent"]
        if self.scenario == "malformed" and self.submissions == 1:
            dossier = {"claims": "deliberately malformed"}
        return ModelReply(action={"kind": "final", "dossier": dossier})
