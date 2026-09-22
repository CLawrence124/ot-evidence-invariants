import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from ot_dossier.agent.loop import ASSEMBLE, VALIDATE, Limits, ModelReply, RunStopped, run_agent
from ot_dossier.agent.simulated import SimulatedModel


def trace(out):
    return [json.loads(line) for line in (out / "trace.jsonl").read_text().splitlines()]


@pytest.mark.parametrize("target", ["NOD2", "TNF"])
def test_success_uses_real_mcp_and_host_validation(tmp_path, target):
    out = tmp_path / "run"
    result = asyncio.run(run_agent(SimulatedModel(), target, out))
    assert result["status"] == "completed"
    assert result["tool_calls"] == 2
    assert result["usage"] == {"input_tokens": 0, "output_tokens": 0}
    events = trace(out)
    requests = [e for e in events if e["event"] == "tool_request"]
    assert [(e["name"], e["origin"]) for e in requests] == [(ASSEMBLE, "model"), (VALIDATE, "host_final")]
    assert {"packet.json", "dossier.json", "dossier.md", "validation.json", "trace.jsonl", "run_config.json", "result.json"} == {p.name for p in out.iterdir()}
    packet = json.loads((out / "packet.json").read_text())
    dossier = json.loads((out / "dossier.json").read_text())
    assert dossier["packet_id"] == packet["packet_id"]
    assert "SIMULATED MODEL" in (out / "dossier.md").read_text()
    assert events[-1]["event"] == "completed"


@pytest.mark.parametrize("scenario,code,calls", [("repair", "INVALID_DOSSIER", 3), ("malformed", "MALFORMED_DOSSIER", 2)])
def test_one_repair_succeeds_without_saving_bad_candidate(tmp_path, scenario, code, calls):
    out = tmp_path / "run"
    result = asyncio.run(run_agent(SimulatedModel(scenario), "NOD2", out))
    assert result["repairs"] == 1
    assert result["tool_calls"] == calls
    assert any(e.get("code") == code for e in trace(out))
    assert "rec_nonexistent" not in (out / "dossier.json").read_text()


@pytest.mark.parametrize("scenario,reason,calls,repairs", [
    ("invalid", "REPAIR_BUDGET_EXHAUSTED", 4, 2),
    ("budget", "TOOL_BUDGET_EXHAUSTED", 8, 0),
])
def test_budget_stops_without_final_dossier(tmp_path, scenario, reason, calls, repairs):
    out = tmp_path / "run"
    with pytest.raises(RunStopped, match=reason):
        asyncio.run(run_agent(SimulatedModel(scenario), "NOD2", out))
    result = json.loads((out / "result.json").read_text())
    assert result["status"] == "failed"
    assert result["tool_calls"] == calls
    assert result["repairs"] == repairs
    assert not (out / "dossier.json").exists()
    assert not (out / "dossier.md").exists()
    assert trace(out)[-1]["event"] == "failed"


class ChangeOneReply(SimulatedModel):
    def __init__(self, change):
        super().__init__()
        self.change = change
        self.changed = False

    async def respond(self, context):
        reply = await super().respond(context)
        if reply.action["kind"] == "final" and not self.changed:
            self.changed = True
            self.change(reply.action)
        return reply


@pytest.mark.parametrize("change,code", [
    (lambda a: a["dossier"].update(packet_id="invented"), "UNKNOWN_PACKET"),
    (lambda a: a["dossier"].update(claims=[]), "INVALID_DOSSIER"),
    (lambda a: a["dossier"]["section_states"].pop("safety"), "INVALID_DOSSIER"),
    (lambda a: a["dossier"].update(target_id="WRONG"), "INVALID_DOSSIER"),
    (lambda a: a.update(kind="invalid_kind"), "MALFORMED_ACTION"),
])
def test_invalid_final_is_repaired(tmp_path, change, code):
    out = tmp_path / "run"
    result = asyncio.run(run_agent(ChangeOneReply(change), "NOD2", out))
    assert result["repairs"] == 1
    assert any(e.get("code") == code for e in trace(out))


class FirstToolWrong(SimulatedModel):
    def __init__(self, action):
        super().__init__()
        self.first = action

    async def respond(self, context):
        if self.first is not None:
            action, self.first = self.first, None
            return ModelReply(action=action)
        return await super().respond(context)


def test_mixed_disease_final_is_rejected_then_repaired_over_mcp(tmp_path):
    def mix_scopes(action):
        claims = action["dossier"]["claims"]
        claims[0]["record_refs"].extend(claims[1]["record_refs"])

    out = tmp_path / "run"
    result = asyncio.run(run_agent(ChangeOneReply(mix_scopes), "NOD2", out))
    assert result["repairs"] == 1
    validations = [e for e in trace(out) if e["event"] == "final_validation"]
    assert not validations[0]["validation"]["valid"]
    assert {f["code"] for f in validations[0]["validation"]["findings"]} >= {"INDIRECT_SCOPE", "MIXED_DISEASE_SCOPE"}
    assert validations[-1]["validation"]["valid"]
    saved = json.loads((out / "dossier.json").read_text())
    assert all(len(c["record_refs"]) == 1 for c in saved["claims"])


@pytest.mark.parametrize("action", [
    {"kind":"tool", "name":"invented_tool", "arguments":{}},
    {"kind":"tool", "name":ASSEMBLE, "arguments":{"target":"TNF"}},
    {"kind":"tool", "name":ASSEMBLE, "arguments":{"target":12}},
    {"kind":"tool", "name":VALIDATE, "arguments":{"packet_id":"missing", "dossier":{"packet_id":"missing", "target_id":"x", "disease_id":"x", "claims":[], "section_states":{}}}},
])
def test_tool_errors_are_bounded_and_recoverable(tmp_path, action):
    out = tmp_path / "run"
    result = asyncio.run(run_agent(FirstToolWrong(action), "NOD2", out))
    assert result["tool_calls"] == 3
    assert result["repairs"] == 1
    assert any(e.get("code") == "TOOL_ERROR" for e in trace(out))


def test_final_validation_cannot_exceed_budget(tmp_path):
    out = tmp_path / "run"
    with pytest.raises(RunStopped, match="TOOL_BUDGET_EXHAUSTED"):
        asyncio.run(run_agent(SimulatedModel(), "NOD2", out, Limits(max_tool_calls=1)))
    assert not (out / "dossier.json").exists()


def test_turn_budget_stops_before_another_model_call(tmp_path):
    with pytest.raises(RunStopped, match="MODEL_TURN_BUDGET_EXHAUSTED"):
        asyncio.run(run_agent(SimulatedModel(), "NOD2", tmp_path / "run", Limits(max_turns=1)))


def test_zero_repairs_stops_on_first_invalid_candidate(tmp_path):
    out = tmp_path / "run"
    with pytest.raises(RunStopped, match="REPAIR_BUDGET_EXHAUSTED"):
        asyncio.run(run_agent(SimulatedModel("repair"), "NOD2", out, Limits(max_repairs=0)))
    assert not (out / "dossier.json").exists()


class BrokenModel(SimulatedModel):
    async def respond(self, context):
        raise RuntimeError("simulated provider failure")


def test_model_failure_has_trace_and_no_dossier(tmp_path):
    out = tmp_path / "run"
    with pytest.raises(RunStopped, match="simulated provider failure"):
        asyncio.run(run_agent(BrokenModel(), "NOD2", out))
    assert trace(out)[-1]["event"] == "failed"
    assert not (out / "dossier.md").exists()


def test_timeout_is_logged(tmp_path, monkeypatch):
    # Keep real initialization; force timeout only at the model response boundary.
    import ot_dossier.agent.loop as loop
    original = asyncio.wait_for

    async def expire_model(awaitable, timeout):
        if getattr(awaitable, "cr_code", None) == SimulatedModel.respond.__code__:
            awaitable.close()
            raise TimeoutError("simulated model timeout")
        return await original(awaitable, timeout)

    monkeypatch.setattr(loop.asyncio, "wait_for", expire_model)
    out = tmp_path / "run"
    with pytest.raises(RunStopped, match="simulated model timeout"):
        asyncio.run(run_agent(SimulatedModel(), "NOD2", out))
    assert not (out / "dossier.md").exists()
    assert trace(out)[-1]["event"] == "failed"


def test_existing_run_is_never_overwritten(tmp_path):
    out = tmp_path / "run"
    out.mkdir()
    (out / "keep.txt").write_text("previous work")
    with pytest.raises(FileExistsError):
        asyncio.run(run_agent(SimulatedModel(), "NOD2", out))
    assert (out / "keep.txt").read_text() == "previous work"


class ValidatesThenChanges(SimulatedModel):
    def __init__(self):
        super().__init__()
        self.finals = 0

    async def respond(self, context):
        reply = await super().respond(context)
        if reply.action["kind"] == "final":
            self.finals += 1
            if self.finals == 1:
                dossier = reply.action["dossier"]
                return ModelReply(action={"kind":"tool", "name":VALIDATE,
                    "arguments":{"packet_id":dossier["packet_id"], "dossier":dossier}})
            if self.finals == 2:
                reply.action["dossier"]["claims"][0]["record_refs"] = ["rec_changed_after_validation"]
        return reply


def test_previous_valid_tool_result_cannot_approve_changed_final(tmp_path):
    out = tmp_path / "run"
    result = asyncio.run(run_agent(ValidatesThenChanges(), "NOD2", out))
    assert result["repairs"] == 1
    requests = [e for e in trace(out) if e["event"] == "tool_request"]
    assert [e["origin"] for e in requests if e["name"] == VALIDATE] == ["model", "host_final", "host_final"]
    assert "rec_changed_after_validation" not in (out / "dossier.json").read_text()


def test_documented_module_cli(tmp_path):
    root = Path(__file__).resolve().parents[2]
    out = tmp_path / "cli-run"
    completed = subprocess.run([sys.executable, "-m", "ot_dossier.agent.loop", "--target", "NOD2", "--out", str(out)],
        cwd=root, env={**os.environ, "PYTHONPATH": str(root / "src")}, capture_output=True, text=True, timeout=45)
    assert completed.returncode == 0, completed.stderr
    assert "SIMULATED run completed" in completed.stdout
    assert json.loads((out / "result.json").read_text())["status"] == "completed"
