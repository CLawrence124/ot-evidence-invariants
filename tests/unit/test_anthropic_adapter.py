import asyncio
from copy import deepcopy
import json
from types import SimpleNamespace

import pytest
from anthropic.types import Message

from ot_dossier.agent.anthropic_adapter import AnthropicAdapter, LiveLimits, compact_packet, expand_packet
from ot_dossier.agent.protocol import ASSEMBLE
from ot_dossier.cli import review_dossier
from ot_dossier.domain.evidence_assembler import assemble_target_disease_evidence
from ot_dossier.domain.models import Dossier


def message(content, stop="end_turn", usage=None):
    return Message.model_validate({"id":"msg_test", "type":"message", "role":"assistant",
        "model":"claude-sonnet-4-6", "content":content, "stop_reason":stop, "stop_sequence":None,
        "usage":usage or {"input_tokens":100, "output_tokens":20}})


class FakeClient:
    def __init__(self, replies=(), count=100):
        self.replies = list(replies)
        self.count = count
        self.sent = []
        self.counted = []
        self.models = SimpleNamespace(retrieve=self.retrieve)
        self.messages = SimpleNamespace(count_tokens=self.count_tokens, create=self.create)

    async def retrieve(self, model_id):
        return SimpleNamespace(id=model_id)

    async def count_tokens(self, **kwargs):
        self.counted.append(deepcopy(kwargs))
        return SimpleNamespace(input_tokens=self.count)

    async def create(self, **kwargs):
        self.sent.append(deepcopy(kwargs))
        return self.replies.pop(0)


def context():
    return {"system":"test instructions", "skill":"scope rules", "scientific_rules":"no overclaims",
            "target":"NOD2", "disease":"IBD", "history":[], "remaining_tool_calls":8, "remaining_repairs":2,
            "dossier_schema":Dossier.model_json_schema(),
            "tools":[{"name":ASSEMBLE, "description":"test assembler", "inputSchema":{"type":"object"}}]}


def aliased_action(packet):
    dossier = review_dossier(packet).model_dump(mode="json")
    refs = {r.record_ref: f"R{i:04d}" for i,r in enumerate(packet.records)}
    for claim in dossier["claims"]:
        claim["record_refs"] = [refs[r] for r in claim["record_refs"]]
    return {"kind":"final", "dossier":dossier}


@pytest.mark.parametrize("target", ["NOD2", "TNF"])
def test_projection_preserves_all_fields_and_records(target):
    packet = assemble_target_disease_evidence(target).model_dump(mode="json")
    original = deepcopy(packet)
    projected = compact_packet(packet)
    assert packet == original
    assert expand_packet(projected) == original
    assert len(projected["records"]) == len(packet["records"])
    assert len(json.dumps(projected)) < len(json.dumps(packet)) * 0.36
    assert [r["record_ref"] for r in projected["records"]] == [f"R{i:04d}" for i in range(len(original["records"]))]


def test_projection_detects_changed_scope_and_missing_values():
    packet = assemble_target_disease_evidence("NOD2").model_dump(mode="json")
    projected = compact_packet(packet)
    damaged = deepcopy(projected)
    damaged["projection"]["record_contexts"][0]["disease_relation"] = "invented_scope"
    with pytest.raises(ValueError, match="round-trip"):
        expand_packet(damaged)
    damaged = deepcopy(projected)
    row = next(r for r in damaged["records"] if r["attributes"]["present_values"])
    row["attributes"]["present_values"].pop()
    with pytest.raises(ValueError):
        expand_packet(damaged)


def test_native_tool_result_id_and_final_json_usage():
    packet = assemble_target_disease_evidence("NOD2").model_dump(mode="json")
    client = FakeClient([
        message([{"type":"tool_use", "id":"tool_123", "name":ASSEMBLE, "input":{"target":"NOD2"}}], "tool_use"),
        message([{"type":"text", "text":json.dumps(aliased_action(assemble_target_disease_evidence("NOD2")))}]),
    ])
    model = AnthropicAdapter(client)
    c = context()
    first = asyncio.run(model.respond(c))
    assert first.action["kind"] == "tool"
    c["history"] = [{"role":"model", "action":first.action}, {"role":"tool_result", "name":ASSEMBLE,"is_error":False,"data":packet}]
    second = asyncio.run(model.respond(c))
    result = client.sent[1]["messages"][-1]["content"][0]
    assert result["type"] == "tool_result"
    assert result["tool_use_id"] == "tool_123"
    assert expand_packet(json.loads(result["content"])["data"]) == packet
    assert second.action["kind"] == "final"
    assert client.sent[1]["tool_choice"] == {"type":"none"}
    assert model.usage_summary()["input_tokens"] == 200
    assert model.usage_summary()["output_tokens"] == 40
    assert client.sent[0]["tools"][0]["input_schema"] == c["tools"][0]["inputSchema"]
    assert client.sent[0]["tool_choice"]["disable_parallel_tool_use"] is True


@pytest.mark.parametrize("text", ["not json", "[]", '{"kind":"tool","name":"invented"}'])
def test_malformed_text_becomes_host_repair(text):
    model = AnthropicAdapter(FakeClient([message([{"type":"text", "text":text}])]))
    reply = asyncio.run(model.respond(context()))
    assert reply.action["kind"] == "malformed_provider_output"
    assert reply.output_tokens == 20


@pytest.mark.parametrize("stop", ["max_tokens", "refusal", "pause_turn"])
def test_incomplete_or_refusal_never_becomes_final(stop):
    model = AnthropicAdapter(FakeClient([message([{"type":"text", "text":'{"kind":"final","dossier":{}}'}], stop)]))
    reply = asyncio.run(model.respond(context()))
    assert reply.action["kind"] == "malformed_provider_output"


def test_parallel_calls_are_not_executed_and_have_error_results():
    client = FakeClient([message([{"type":"tool_use", "id":f"tool_{i}", "name":ASSEMBLE, "input":{"target":"NOD2"}} for i in range(2)], "tool_use")])
    model = AnthropicAdapter(client)
    reply = asyncio.run(model.respond(context()))
    assert reply.action["kind"] == "malformed_provider_output"
    assert [b["tool_use_id"] for b in model.messages[-1]["content"]] == ["tool_0","tool_1"]
    assert all(b["is_error"] for b in model.messages[-1]["content"])


def test_input_preflight_blocks_generation():
    client = FakeClient(count=80001)
    model = AnthropicAdapter(client)
    with pytest.raises(RuntimeError, match="INPUT_TOKEN_BUDGET"):
        asyncio.run(model.respond(context()))
    assert not client.sent


def test_cumulative_input_budget_blocks_generation():
    client = FakeClient(count=100)
    model = AnthropicAdapter(client, limits=LiveLimits(max_total_input=500))
    model.input_tokens = 200
    with pytest.raises(RuntimeError, match="INPUT_TOKEN_BUDGET"):
        asyncio.run(model.respond(context()))
    assert not client.sent


def test_output_budget_caps_request_and_then_stops():
    client = FakeClient([message([{"type":"text", "text":'{}'}])])
    model = AnthropicAdapter(client, limits=LiveLimits(max_total_output=20))
    asyncio.run(model.respond(context()))
    assert client.sent[0]["max_tokens"] == 20
    with pytest.raises(RuntimeError, match="OUTPUT_TOKEN_BUDGET"):
        asyncio.run(model.respond(context()))
    assert len(client.sent) == 1


def test_provider_request_limit():
    client = FakeClient()
    model = AnthropicAdapter(client)
    model.requests = 4
    with pytest.raises(RuntimeError, match="REQUEST_BUDGET"):
        asyncio.run(model.respond(context()))
    assert not client.counted


def test_usage_includes_cache_tokens():
    usage = {"input_tokens":100, "output_tokens":20, "cache_read_input_tokens":30, "cache_creation_input_tokens":40}
    model = AnthropicAdapter(FakeClient([message([{"type":"text","text":'{}'}],usage=usage)]))
    reply = asyncio.run(model.respond(context()))
    assert reply.input_tokens == 170
    assert model.usage_summary()["cache_read_input_tokens"] == 30


def test_final_feedback_is_a_user_message_not_an_unpaired_tool_result():
    client = FakeClient([message([{"type":"text","text":'{}'}]), message([{"type":"text","text":'{}'}])])
    model = AnthropicAdapter(client)
    c = context()
    asyncio.run(model.respond(c))
    c["history"] = [{"role":"feedback", "code":"MALFORMED_ACTION", "detail":"repair"}]
    asyncio.run(model.respond(c))
    assert client.sent[1]["messages"][-1]["content"][0]["type"] == "text"
    assert "MALFORMED_ACTION" in client.sent[1]["messages"][-1]["content"][0]["text"]


def test_host_rejected_native_action_gets_matching_error_result():
    client = FakeClient([message([{"type":"text","text":'{}'}])])
    model = AnthropicAdapter(client)
    model.messages = [{"role":"assistant", "content":[{"type":"tool_use","id":"bad_call","name":ASSEMBLE,"input":{}}]}]
    model.pending = [{"id":"bad_call", "name":ASSEMBLE}]
    c = context()
    c["history"] = [{"role":"feedback", "code":"MALFORMED_ACTION", "detail":"invalid tool arguments"}]
    asyncio.run(model.respond(c))
    first = client.sent[0]["messages"][-1]["content"][0]
    assert first["type"] == "tool_result" and first["tool_use_id"] == "bad_call"
    assert first["is_error"]


def test_provider_cannot_request_validation_after_assembly():
    client = FakeClient([message([{"type":"tool_use", "id":"unexpected", "name":"validate_dossier_references", "input":{}}], "tool_use")])
    model = AnthropicAdapter(client)
    c = context()
    c["history"] = [{"role":"tool_result", "name":ASSEMBLE, "is_error":False,
                     "data":assemble_target_disease_evidence("NOD2").model_dump(mode="json")}]
    reply = asyncio.run(model.respond(c))
    assert client.sent[0]["tool_choice"] == {"type":"none"}
    assert reply.action["kind"] == "malformed_provider_output"
    assert not model.pending
    assert model.messages[-1]["content"][0]["is_error"] is True


@pytest.mark.parametrize("target", ["NOD2", "TNF"])
def test_closed_final_schema_preserves_domain_shape(target):
    import jsonschema
    from ot_dossier.agent.anthropic_adapter import final_output_schema
    packet = assemble_target_disease_evidence(target)
    schema = final_output_schema(packet.model_dump(mode="json"))
    jsonschema.Draft202012Validator.check_schema(schema)
    action = aliased_action(packet)
    jsonschema.validate(action, schema)
    invalid = deepcopy(action)
    invalid["dossier"]["claims"][0]["disease_id"] = "MONDO_0005011"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(invalid, schema)
    invalid = deepcopy(action)
    invalid["dossier"]["section_states"]["safety"]["value"] = "safe"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(invalid, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({**action, "explanation":"extra prose"}, schema)
    def closed(node):
        if isinstance(node, dict):
            if node.get("type") == "object":
                assert node["additionalProperties"] is False
            for value in node.values(): closed(value)
        elif isinstance(node, list):
            for value in node: closed(value)
    closed(schema)


def test_alias_schema_rejects_invented_and_mixed_disease_citations():
    import jsonschema
    from ot_dossier.agent.anthropic_adapter import final_output_schema, resolve_citations
    packet = assemble_target_disease_evidence("NOD2")
    raw = packet.model_dump(mode="json")
    schema = final_output_schema(raw)
    action = aliased_action(packet)
    decoded, mapping = resolve_citations(action, raw)
    assert decoded["dossier"] == review_dossier(packet).model_dump(mode="json")
    assert mapping
    invalid = deepcopy(action)
    invalid["dossier"]["claims"][0]["record_refs"] += invalid["dossier"]["claims"][1]["record_refs"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(invalid, schema)
    for bad_ref in ("R9999", "R0", packet.records[0].record_ref):
        invalid = deepcopy(action)
        invalid["dossier"]["claims"][0]["record_refs"] = [bad_ref]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(invalid, schema)
        with pytest.raises(ValueError, match="Unknown local citation"):
            resolve_citations(invalid, raw)
    invalid = deepcopy(action)
    invalid["dossier"]["packet_id"] = "wrong-packet"
    with pytest.raises(ValueError, match="assembled packet"):
        resolve_citations(invalid, raw)
