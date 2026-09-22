# Step 2: run the simulated agent

This step tests the agent host with a scripted stand-in for a language model.
It uses the real local MCP server and frozen evidence. There are no Anthropic
calls, credentials, billable tokens, or newly generated scientific interpretations.
The simulator reuses the deterministic source-observation draft. It is not a
demonstration of Claude's scientific reasoning or a finished reference evaluation.

## Start in your VS Code project terminal

Activate the existing project environment, then run:

```bash
source .venv/bin/activate
PYTHONPATH=src python -m ot_dossier.agent.loop --target NOD2 --out generated/agent-nod2-01
```

`PYTHONPATH=src` tells Python where this checkout's source code lives, for this
command only. This also avoids relying on the editable-install path file that
macOS previously marked hidden. `-m` runs the `ot_dossier.agent.loop` module.
The loop launches and stops its own MCP server; don't start a second server.

Expect a completion message reporting **2 tool calls and 0 repairs**. Routine MCP
request messages may also appear in the terminal. Output goes into a new directory.
If it already exists, choose `agent-nod2-02`, etc.; existing runs are never replaced.

## What the program did

1. Loaded the skill and scientific rules, and recorded their hash with the prompt
   and output schema hashes. A hash helps identify exactly which instructions ran.
2. Launched the local MCP server and discovered its two tool contracts.
3. Asked the simulator for an action. It requested NOD2–IBD evidence.
4. Executed that request over MCP and sent the returned packet back to the simulator.
5. Received a scripted final dossier. The simulator does not need to call validation:
   the host always validates the exact final submission itself through MCP, and
   compares that result with the local deterministic validator.
6. Required at least one claim and exactly the five packet section states. Missing
   sections fail final acceptance even when the tool represents them as warnings.
7. Wrote final files only after acceptance. A completed run does not mark the output
   human-reviewed or establish scientific entailment.

## Inspect the run

| File | Purpose |
|---|---|
| `dossier.md` | Readable output, prominently labeled simulated |
| `dossier.json` | The exact accepted structured claims |
| `packet.json` | The evidence packet received through MCP |
| `validation.json` | Final deterministic validation findings |
| `trace.jsonl` | Ordered events: model actions, tool arguments/results, feedback, final status |
| `run_config.json` | Model identity, target, limits, prompt/skill/schema hashes |
| `result.json` | Completion/failure status, counters, packet ID on success, simulated usage |

JSON output is indented. JSONL intentionally has one JSON object per line: each
line is a separate event. To see a compact trace without reading full packets:

```bash
python - <<'PY'
import json
from pathlib import Path
path = Path("generated/agent-nod2-01/trace.jsonl")
for line in path.read_text().splitlines():
    event = json.loads(line)
    print(event["event"], event.get("name", ""), event.get("origin", ""), event.get("code", ""))
PY
```

Read `result.json` before treating files as a successful result. Failure runs
retain config, trace, and a failed result; they do not leave final dossier files.
Trace files include full public evidence and candidates, including deliberately
invalid candidates. Those trace entries are not accepted dossier outputs.

## Watch one correction happen

```bash
PYTHONPATH=src python -m ot_dossier.agent.loop --target NOD2 --scenario repair --out generated/agent-repair-01
```

The simulator submits a nonexistent citation on purpose. The host sends validation
feedback; the simulator submits a corrected dossier. Expect **3 tool calls and
1 repair**. Look for `DANGLING_REFERENCE` in the trace and valid references in the
final dossier. The simulator is programmed to fix this mistake; this does not
prove that a real model can repair its own errors.

`--scenario malformed` similarly submits a dossier with the wrong structure first.
It should finish with **2 tool calls and 1 repair** because malformed JSON structure
is rejected before calling the validation tool.

## Watch the stopping limits

```bash
PYTHONPATH=src python -m ot_dossier.agent.loop --target NOD2 --scenario invalid --out generated/agent-invalid-01
PYTHONPATH=src python -m ot_dossier.agent.loop --target NOD2 --scenario budget --out generated/agent-budget-01
```

Both commands intentionally exit with a nonzero status. The first keeps submitting
a bad citation: the initial attempt plus two repairs are rejected. The second
keeps requesting evidence and is stopped before a ninth tool request is executed.
Expect `REPAIR_BUDGET_EXHAUSTED` and `TOOL_BUDGET_EXHAUSTED`, respectively.

Limits: eight total tool requests (including mandatory host validation), two repair
opportunities across malformed actions/dossiers and tool/final-validation errors,
twelve model turns, and a 30-second timeout per model or MCP operation. Budget
exhaustion and timeouts fail closed; the host does not silently extend the budget.
If all tool calls have been spent, a final candidate cannot bypass validation.

## Try TNF and run tests

```bash
PYTHONPATH=src python -m ot_dossier.agent.loop --target TNF --out generated/agent-tnf-01
python -m pytest -q
```

The same loop, schema, rules, and validator are used for both targets. Tests cover
success, dangling citations, malformed dossiers/actions, wrong entities, unknown
tools/handles, missing sections, empty dossiers, repeated failures, budgets,
timeouts, model failure, and refusal to overwrite a previous run.

## What comes next

The Step 3 adapter is now implemented with native Anthropic messages, usage
accounting, and input/output budgets. Follow `docs/live-agent.md` for the first
paid smoke test. The default remains simulated unless `--mode live` is explicit.
Live model performance and human scoring are not established by the mock tests.
Your reference review stays separate from the generated output's review status.
