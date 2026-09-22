"""Native Anthropic tool messages, bounded requests, and reversible packet projection."""
from __future__ import annotations

from copy import deepcopy
import json
from math import ceil

from pydantic import BaseModel, ConfigDict, Field

from ot_dossier.agent.protocol import ASSEMBLE, ModelReply
from ot_dossier.api.graphql_client import canonical, digest
from ot_dossier.domain.models import Claim

DEFAULT_MODEL = "claude-sonnet-4-6"
TRANSPORT_PROMPT = """First call assemble_target_disease_evidence. Once evidence is
returned, native tool calls are disabled: submit your draft directly as ONLY a
JSON object {"kind":"final","dossier":...}. The host calls
validate_dossier_references on that exact draft and sends any errors back for
repair. Do not request validation yourself or wait for another turn to finalize.
Do not print tool actions as text. Return the final JSON
matching the supplied Dossier schema, without Markdown fences. Aim for 5–10 concise
source-grounded claims across the available evidence, not a target recommendation.
Prefer short claims and few fully supported examples over long lists. Each claim
must concern one source disease; all citations for direct_evidence must be direct
disease evidence. Split direct IBD and descendant observations into separate claims.
Every claim's target_id and disease_id identify the requested pair: copy the
packet target.id and disease_scope.selected.id, including in descendant claims.
Keep the source disease in the prose and citations, not in the claim disease_id.
Copy section_states exactly from each packet section's interpretation. Do not turn
empty sections into factual claims with record citations; the renderer displays
their limits and exact section metadata. Do not generate safety-empty, capture-count,
or no-clinical-rows claims: these are covered in the host-rendered section summary.
The packet projection is lossless: projection.record_contexts[context_index]
supplies each record's kind, target_id, source_disease, disease_relation, and source.
Read that context before interpreting a record's disease scope. Provenance metadata
entries supply common provenance. For attributes, zip projection.present_columns
[columns_index] with present_values (a positional array) to recover named values.
other_states_index selects projection.attribute_state_layouts (missing-state groups).
All table indices are zero-based. Sections use
record_indices into the records array instead of repeating long references. Every
record remains included. An empty present array is still an empty array, not a
negative scientific conclusion. In the model-facing packet, record_ref is a short
handle such as R0000. Copy those handles into record_refs; the adapter resolves
them exactly to the original full IDs before host validation and saving. Handles
are local to this packet, not new scientific identifiers. The output schema permits
only existing handles grouped by source disease. Do not copy or invent long hashes.
A string upstream_id is a present source ID; missing upstream IDs retain their
typed missingness object. Citation handles and upstream source IDs are distinct.
Respect budget feedback. Leave one tool call for mandatory host final validation.
"""


class LiveLimits(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    max_requests: int = Field(default=4, ge=1, le=4)
    max_input_per_request: int = Field(default=80000, ge=1, le=80000)
    max_total_input: int = Field(default=200000, ge=1, le=200000)
    max_output_per_request: int = Field(default=4096, ge=1, le=4096)
    max_total_output: int = Field(default=12000, ge=1, le=12000)


def final_output_schema(packet: dict) -> dict:
    """Closed provider schema; domain validation still checks scientific contracts.

    Specializing the five interpretation states avoids the domain model's open
    dictionaries/recursive JsonValue, unsupported by provider structured output.
    """
    from anthropic import transform_schema

    def obj(properties):
        return {"type": "object", "properties": properties,
                "required": list(properties), "additionalProperties": False}

    def literal(value):
        if value is None:
            return {"type": "null"}
        if not isinstance(value, str):
            raise ValueError("Unsupported section interpretation value in live output schema")
        return {"type": "string", "const": value}

    target = packet["target"]["id"]
    disease = packet["disease_scope"]["selected"]["id"]
    claim = transform_schema(Claim.model_json_schema())
    claim["properties"]["target_id"] = literal(target)
    claim["properties"]["disease_id"] = literal(disease)
    groups = {}
    for i, record in enumerate(packet["records"]):
        disease_id = record["source_disease"]["id"] if record["source_disease"] else None
        groups.setdefault(disease_id, []).append(f"R{i:04d}")
    claim["properties"]["record_refs"] = {"anyOf": [
        {"type": "array", "minItems": 1, "items": {"type": "string", "enum": refs}}
        for refs in groups.values()]}
    return obj({"kind": literal("final"), "dossier": obj({
        "packet_id": literal(packet["packet_id"]),
        "target_id": literal(target), "disease_id": literal(disease),
        "claims": {"type": "array", "minItems": 1, "items": claim},
        "section_states": obj({name: obj({key: literal(value)
            for key, value in section["interpretation"].items()})
            for name, section in packet["sections"].items()}),
    })})


def compact_packet(packet: dict) -> dict:
    """Losslessly factor fields and use exact local handles for content-hashed IDs."""
    result = deepcopy(packet)
    provenance_table = []
    attribute_state_layouts = []
    record_contexts = []
    present_columns = []
    for record in result["records"]:
        context = {key: record.pop(key) for key in
                   ("kind", "target_id", "source_disease", "disease_relation", "source")}
        if context not in record_contexts:
            record_contexts.append(context)
        record["context_index"] = record_contexts.index(context)
        original = record["attributes"]
        present, absent = {}, []
        for name, value in original.items():
            if value["state"] == "present" and value["reason"] == "":
                present[name] = value["value"]
            else:
                match = next((g for g in absent if g["datum"] == value), None)
                if match is None:
                    match = {"fields": [], "datum": value}
                    absent.append(match)
                match["fields"].append(name)
        if absent not in attribute_state_layouts:
            attribute_state_layouts.append(absent)
        columns = list(present)
        if columns not in present_columns:
            present_columns.append(columns)
        record["attributes"] = {"columns_index": present_columns.index(columns),
                                "present_values": list(present.values()),
                                "other_states_index": attribute_state_layouts.index(absent)}
        p = record["provenance"]
        common = {k:v for k,v in p.items() if k != "json_pointer"}
        if common not in provenance_table:
            provenance_table.append(common)
        record["provenance"] = {"metadata_index": provenance_table.index(common), "json_pointer": p["json_pointer"]}
    ref_index = {r["record_ref"]:i for i,r in enumerate(result["records"])}
    for section in result["sections"].values():
        section["record_indices"] = [ref_index[ref] for ref in section.pop("record_refs")]
    for i, record in enumerate(result["records"]):
        record["record_ref"] = f"R{i:04d}"
        upstream = record["upstream_id"]
        if upstream["state"] == "present" and upstream["reason"] == "" and isinstance(upstream["value"], str):
            record["upstream_id"] = upstream["value"]
    result["projection"] = {"version": "lossless-v3", "original_packet_sha256": digest(packet),
                            "record_count": len(packet["records"]), "provenance_table": provenance_table,
                            "record_contexts": record_contexts, "present_columns": present_columns,
                            "attribute_state_layouts": attribute_state_layouts}
    return result


def expand_packet(projected: dict) -> dict:
    """Inverse used to test that the model view preserves every source field."""
    result = deepcopy(projected)
    projection = result.pop("projection")
    if projection["version"] not in ("lossless-v1", "lossless-v2", "lossless-v3"):
        raise ValueError("Unsupported packet projection version")
    for i, record in enumerate(result["records"]):
        a = record["attributes"]
        if projection["version"] in ("lossless-v2", "lossless-v3"):
            record.update(projection["record_contexts"][record.pop("context_index")])
            present = zip(projection["present_columns"][a["columns_index"]], a["present_values"], strict=True)
        else:
            present = a["present_values"].items()
        attributes = {k:{"state":"present", "value":v, "reason":""} for k,v in present}
        for group in projection["attribute_state_layouts"][a["other_states_index"]]:
            for name in group["fields"]:
                attributes[name] = group["datum"]
        record["attributes"] = attributes
        p = record["provenance"]
        record["provenance"] = {**projection["provenance_table"][p["metadata_index"]], "json_pointer":p["json_pointer"]}
        if projection["version"] == "lossless-v3":
            if record["record_ref"] != f"R{i:04d}":
                raise ValueError("Invalid local citation handle")
            if isinstance(record["upstream_id"], str):
                record["upstream_id"] = {"state":"present", "value":record["upstream_id"], "reason":""}
            record["record_ref"] = "rec_" + digest({k:v for k,v in record.items() if k not in ("record_ref", "provenance")})
    for section in result["sections"].values():
        section["record_refs"] = [result["records"][i]["record_ref"] for i in section.pop("record_indices")]
    if digest(result) != projection["original_packet_sha256"]:
        raise ValueError("Packet projection did not round-trip")
    return result


def resolve_citations(action: dict, packet: dict) -> tuple[dict, dict]:
    """Exact packet-local lookup only; never guess or repair a citation choice."""
    result = deepcopy(action)
    if result.get("kind") != "final" or result.get("dossier", {}).get("packet_id") != packet["packet_id"]:
        raise ValueError("Final citation handles must belong to the assembled packet")
    aliases = {f"R{i:04d}": r["record_ref"] for i,r in enumerate(packet["records"])}
    used = {}
    for claim in result["dossier"]["claims"]:
        refs = claim["record_refs"]
        if any(not isinstance(ref, str) or ref not in aliases for ref in refs):
            raise ValueError("Unknown local citation handle; choose an exact R handle from the packet")
        used.update({ref: aliases[ref] for ref in refs})
        claim["record_refs"] = [aliases[ref] for ref in refs]
    return result, used


class AnthropicAdapter:
    mode = "live"

    def __init__(self, client, model_id=DEFAULT_MODEL, limits: LiveLimits | None = None):
        self.client = client
        self.model_id = model_id
        self.limits = limits or LiveLimits()
        self.messages = []
        self.seen_history = 0
        self.pending = []
        self.requests = 0
        self.input_tokens = self.output_tokens = 0
        self.cache_read_tokens = self.cache_write_tokens = 0
        self.resolved_model = None
        self.event = lambda *args, **kwargs: None

    def configuration(self):
        import anthropic
        return {"provider": "anthropic", "sdk_version": anthropic.__version__,
                "model_id": self.model_id, "limits": self.limits.model_dump(),
                "projection": "lossless-v3", "transport_prompt": TRANSPORT_PROMPT,
                "validation_flow": "host-owned-after-assembly-v1",
                "final_output_format": "packet-handles-single-disease-json-schema-v2",
                "transport_prompt_sha256": digest(TRANSPORT_PROMPT), "automatic_retries": 0}

    def usage_summary(self):
        return {"requests_sent": self.requests, "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens, "cache_read_input_tokens": self.cache_read_tokens,
                "cache_creation_input_tokens": self.cache_write_tokens, "resolved_model": self.resolved_model,
                "note": "Reported usage only; a timed-out request may still incur provider usage not returned here."}

    def _sync(self, context):
        blocks = []
        new = context["history"][self.seen_history:]
        for item in new:
            if item["role"] == "tool_result":
                if self.pending:
                    block = self.pending.pop(0)
                    if block["name"] != item["name"]:
                        raise RuntimeError("Native tool-result name mismatch")
                    data = deepcopy(item)
                    if item["name"] == ASSEMBLE and not item["is_error"]:
                        data["data"] = compact_packet(item["data"])
                    blocks.append({"type":"tool_result", "tool_use_id":block["id"],
                                   "is_error":item["is_error"], "content":canonical(data)})
                else:
                    blocks.append({"type":"text", "text":"Host validation result: " + canonical(item)})
            elif item["role"] == "feedback":
                blocks.append({"type":"text", "text":"Host feedback: " + canonical(item)})
        if self.pending:
            if not any(item["role"] == "feedback" for item in new):
                raise RuntimeError("Missing native tool result before next provider request")
            # A malformed native action can be rejected by the host before execution.
            # The provider still requires a matching tool_result for its tool_use ID.
            rejected = [{"type":"tool_result", "tool_use_id":b["id"], "is_error":True,
                         "content":"Host rejected this action before execution; see validation feedback."} for b in self.pending]
            blocks = rejected + blocks
            self.pending = []
        self.seen_history = len(context["history"])
        blocks.append({"type":"text", "text":canonical({"remaining_tool_calls":context["remaining_tool_calls"], "remaining_repairs":context["remaining_repairs"]})})
        if not self.messages:
            blocks.insert(0, {"type":"text", "text":f"Prepare a bounded dossier for {context['target']} and {context['disease']}. Assemble evidence first."})
        self.messages.append({"role":"user", "content":blocks})

    async def respond(self, context):
        import anthropic
        if self.requests >= self.limits.max_requests:
            raise RuntimeError("PROVIDER_REQUEST_BUDGET_EXHAUSTED")
        self._sync(context)
        packets = [item["data"] for item in context["history"] if item["role"] == "tool_result"
                   and item["name"] == ASSEMBLE and not item["is_error"]]
        assembled = bool(packets)
        tools = [{"name": t["name"], "description":t.get("description", ""), "input_schema":t["inputSchema"]} for t in context["tools"]]
        schema_instruction = ("Return the final envelope specified by the structured output schema."
                              if assembled else "Dossier JSON schema: " + canonical(context["dossier_schema"]))
        system = "\n\n".join([context["system"], context["skill"], context["scientific_rules"],
                                 TRANSPORT_PROMPT, schema_instruction])
        request = {"model":self.model_id, "system":system, "messages":deepcopy(self.messages),
                   "tools":tools, "tool_choice": {"type":"none"} if assembled else {"type":"auto", "disable_parallel_tool_use":True},
                   "thinking":{"type":"disabled"}}
        if assembled:
            request["output_config"] = {"format": {"type": "json_schema",
                                                   "schema": final_output_schema(packets[-1])}}
        try:
            if self.resolved_model is None:
                info = await self.client.models.retrieve(self.model_id)
                self.resolved_model = info.id
                self.event("provider_model_checked", requested=self.model_id, resolved=info.id)
            count = await self.client.messages.count_tokens(**request)
            # Count endpoint is an estimate: reserve 5% plus 256 tokens, not a dollar guarantee.
            reserved = ceil(count.input_tokens * 1.05) + 256
            remaining_output = min(self.limits.max_output_per_request, self.limits.max_total_output - self.output_tokens)
            self.event("provider_preflight", estimated_input=count.input_tokens, reserved_input=reserved,
                       output_allowance=remaining_output, input_used=self.input_tokens)
            if reserved > self.limits.max_input_per_request or self.input_tokens + reserved > self.limits.max_total_input:
                raise RuntimeError(
                    f"INPUT_TOKEN_BUDGET_EXHAUSTED: estimated={count.input_tokens}, "
                    f"with_reserve={reserved}, per_request_limit={self.limits.max_input_per_request}, "
                    f"input_used={self.input_tokens}, total_limit={self.limits.max_total_input}; "
                    "no generation request sent for this turn")
            if remaining_output <= 0:
                raise RuntimeError("OUTPUT_TOKEN_BUDGET_EXHAUSTED")
            request["max_tokens"] = remaining_output
            self.event("provider_request", number=self.requests + 1, payload=request)
            self.requests += 1
            response = await self.client.messages.create(**request)
        except anthropic.APIStatusError as exc:
            # Never log raw response bodies or exception strings containing request data.
            raise RuntimeError(f"Anthropic API error HTTP {exc.status_code}; check API key, billing, model access, or rate limits. No automatic retry.") from None
        except anthropic.APIConnectionError:
            raise RuntimeError("Anthropic connection/timeout error; usage may be unknown. No automatic retry.") from None
        data = response.model_dump(mode="json")
        self.event("provider_response", response=data)
        usage = data["usage"]
        read = usage.get("cache_read_input_tokens") or 0
        write = usage.get("cache_creation_input_tokens") or 0
        input_tokens = usage["input_tokens"] + read + write
        self.input_tokens += input_tokens
        self.output_tokens += usage["output_tokens"]
        self.cache_read_tokens += read
        self.cache_write_tokens += write
        self.messages.append({"role":"assistant", "content":data["content"]})
        blocks = [b for b in data["content"] if b["type"] == "tool_use"]
        metadata = {"message_id":data["id"], "model":data["model"], "stop_reason":data["stop_reason"],
                    "raw_usage":usage, "estimated_input_tokens":count.input_tokens}
        if data["stop_reason"] == "tool_use" and len(blocks) == 1 and not assembled:
            self.pending = blocks
            block = blocks[0]
            action = {"kind":"tool", "name":block["name"], "arguments":block["input"]}
        elif data["stop_reason"] == "end_turn" and not blocks:
            text = "".join(b["text"] for b in data["content"] if b["type"] == "text")
            try:
                action = json.loads(text)
                if not isinstance(action, dict) or action.get("kind") != "final":
                    action = {"kind":"malformed_provider_output", "reason":"Expected a final JSON object"}
            except json.JSONDecodeError:
                action = {"kind":"malformed_provider_output", "reason":"Final text was not JSON"}
            if assembled and action.get("kind") == "final":
                try:
                    action, mapping = resolve_citations(action, packets[-1])
                    self.event("citation_handles_resolved", packet_id=packets[-1]["packet_id"], mapping=mapping)
                except (ValueError, KeyError, TypeError, AttributeError) as exc:
                    action = {"kind":"malformed_provider_output", "reason":str(exc)}
        else:
            # Resolve any provider-emitted calls as rejected so the next request remains legal.
            if blocks:
                self.messages.append({"role":"user", "content":[{"type":"tool_result", "tool_use_id":b["id"], "is_error":True,
                    "content":"Not executed: tool calls are disabled after assembly; otherwise exactly one complete call is required."} for b in blocks]})
            action = {"kind":"malformed_provider_output", "reason":f"Unsupported or incomplete response: {data['stop_reason']}"}
        return ModelReply(action=action, input_tokens=input_tokens, output_tokens=usage["output_tokens"], provider_metadata=metadata)


def create_adapter(api_key: str, model_id=DEFAULT_MODEL):
    from anthropic import AsyncAnthropic
    if not api_key or not api_key.strip():
        raise ValueError("ANTHROPIC_API_KEY is missing; use --prompt-key or set it in your terminal")
    # Explicit endpoint prevents an inherited alternate endpoint from receiving the key.
    client = AsyncAnthropic(api_key=api_key.strip(), base_url="https://api.anthropic.com",
                            max_retries=0, timeout=150.0)
    return AnthropicAdapter(client, model_id)
