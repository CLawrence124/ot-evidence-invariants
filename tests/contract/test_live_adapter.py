"""Real Anthropic SDK + fake HTTP + real local MCP. No paid API requests."""
import asyncio
import json

import anthropic
import httpx2
import pytest

from ot_dossier.agent.anthropic_adapter import AnthropicAdapter, expand_packet
from ot_dossier.agent.loop import RunStopped, run_agent
from ot_dossier.cli import review_dossier
from ot_dossier.domain.models import EvidencePacket


@pytest.mark.parametrize("repair", [False, True, "scope"])
def test_sdk_http_to_mcp_round_trip(tmp_path, repair):
    requests = []
    generations = 0

    def handler(request):
        nonlocal generations
        assert request.headers["x-api-key"] == "test-secret-never-write-to-trace"
        if "/models/" in request.url.path:
            return httpx2.Response(200, json={"id":"claude-sonnet-4-6", "type":"model", "display_name":"Test model", "created_at":"2026-02-17T00:00:00Z"})
        payload = json.loads(request.content)
        requests.append(payload)
        if request.url.path.endswith("count_tokens"):
            if generations:
                assert payload["output_config"]["format"]["type"] == "json_schema"
            return httpx2.Response(200, json={"input_tokens":1234})
        generations += 1
        if generations == 1:
            content = [{"type":"tool_use", "id":"call_assembly", "name":"assemble_target_disease_evidence", "input":{"target":"NOD2","disease":"IBD"}}]
            stop = "tool_use"
        elif repair is True and generations == 2:
            content = [{"type":"text", "text":"deliberately not JSON"}]
            stop = "end_turn"
        else:
            tool_result = next(b for m in payload["messages"] if m["role"] == "user" for b in m["content"] if b["type"] == "tool_result")
            assert tool_result["tool_use_id"] == "call_assembly"
            packet = EvidencePacket.model_validate(expand_packet(json.loads(tool_result["content"])["data"]))
            dossier = review_dossier(packet)
            candidate = dossier.model_dump(mode="json")
            handles = {r.record_ref: f"R{i:04d}" for i,r in enumerate(packet.records)}
            for claim in candidate["claims"]:
                claim["record_refs"] = [handles[ref] for ref in claim["record_refs"]]
            if repair == "scope" and generations == 2:
                candidate["claims"][0]["record_refs"].extend(candidate["claims"][1]["record_refs"])
                candidate["claims"][1]["disease_id"] = "MONDO_0005011"
            assert payload["tool_choice"] == {"type":"none"}
            assert payload["output_config"]["format"]["type"] == "json_schema"
            if repair != "scope" or generations != 2:
                import jsonschema
                jsonschema.validate({"kind":"final", "dossier":candidate}, payload["output_config"]["format"]["schema"])
            content = [{"type":"text", "text":json.dumps({"kind":"final","dossier":candidate})}]
            stop = "end_turn"
        return httpx2.Response(200, json={"id":f"msg_{generations}", "type":"message", "role":"assistant",
            "model":"claude-sonnet-4-6", "content":content, "stop_reason":stop, "stop_sequence":None,
            "usage":{"input_tokens":1200, "output_tokens":100}})

    async def scenario():
        async with anthropic.AsyncAnthropic(api_key="test-secret-never-write-to-trace", base_url="https://api.anthropic.com", max_retries=0,
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))) as client:
            return await run_agent(AnthropicAdapter(client), "NOD2", tmp_path / "run")
    result = asyncio.run(scenario())
    assert result["mode"] == "live"
    assert result["repairs"] == int(bool(repair))
    assert result["usage"] == {"input_tokens":1200 * generations, "output_tokens":100 * generations}
    assert result["provider_usage"]["requests_sent"] == generations
    out = tmp_path / "run"
    assert "LIVE MODEL DRAFT" in (out / "dossier.md").read_text()
    for path in out.iterdir():
        assert "test-secret-never-write-to-trace" not in path.read_text()
    events = [json.loads(line) for line in (out / "trace.jsonl").read_text().splitlines()]
    assert any(e["event"] == "provider_preflight" for e in events)
    assert any(e["event"] == "citation_handles_resolved" for e in events)
    saved = json.loads((out / "dossier.json").read_text())
    assert all(ref.startswith("rec_") for c in saved["claims"] for ref in c["record_refs"])
    assert any(e["event"] == "tool_request" and e["origin"] == "host_final" for e in events)
    assert not any(e["event"] == "tool_request" and e["name"] == "validate_dossier_references" and e["origin"] == "model" for e in events)
    if repair == "scope":
        assert generations == 3  # assembly, draft, repair; no extra finalization request
        invalid = next(e for e in events if e["event"] == "final_validation" and not e["validation"]["valid"])
        assert {f["code"] for f in invalid["validation"]["findings"]} >= {"ENTITY_MISMATCH", "MIXED_DISEASE_SCOPE"}


def test_auth_failure_logs_no_key_or_raw_error_body(tmp_path):
    calls = []

    def handler(request):
        calls.append(request.url.path)
        return httpx2.Response(401, json={"type":"error", "error":{"type":"authentication_error", "message":"RAW_PRIVATE_BODY_test-secret"}})

    async def scenario():
        async with anthropic.AsyncAnthropic(api_key="test-secret",base_url="https://api.anthropic.com", max_retries=0,
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))) as client:
            await run_agent(AnthropicAdapter(client), "NOD2", tmp_path / "run")
    with pytest.raises(RunStopped, match="HTTP 401"):
        asyncio.run(scenario())
    assert len(calls) == 1
    out = tmp_path / "run"
    assert not (out / "dossier.json").exists()
    for path in out.iterdir():
        assert "test-secret" not in path.read_text()
        assert "RAW_PRIVATE_BODY" not in path.read_text()
