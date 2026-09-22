# Step 3: run a live Claude dossier

Current milestone (2026-09-22): live-nod2-06 completed, its review is recorded, and a separate corrected derivative is signed off. TNF has fresh simulated integration coverage. See [evaluation summary](evaluation-summary.md). Earlier attempt descriptions below are historical, not instructions to repeat a paid run.

For the next run after the signed-off NOD2 review, use
[revision 01 and the live-nod2-06 command](revision-01.md). The earlier runs below
remain useful setup and failure-history examples; do not overwrite their folders.

The live adapter is implemented and tested offline. A successful live run is a
separate check: it requires your own Anthropic API key, model access, and billing.
Offline HTTP mocks are not evidence that your account can access the model or that
a real model will produce scientifically supported claims.

## What changes from Step 2

The same host, two MCP tools, frozen records, typed dossier, final validator,
repair limits, and output files are used. Instead of a scripted response, Claude
chooses native tool calls and writes the dossier. The adapter matches each native
`tool_use` ID to its `tool_result`. There is no third MCP tool or remotely hosted
MCP server. Claude receives public evidence through our local client.

After successful assembly, the live adapter disables further native tool calls.
Claude submits its draft directly and the host invokes validation; errors return
to Claude for repair within the existing budgets. This avoids paying for a model
turn solely to repeat a previously validated draft as final JSON.

Default model: `claude-sonnet-4-6`, a documented Sonnet identifier. The adapter
checks it with the Models API before generation and records returned model IDs.
This is a deliberately fixed starting model, not a claim that it is the newest.
SDK: `anthropic==1.7.0`, installed and tested with Python 3.12.6. The SDK's v1 line
uses httpx2; its dependencies are pinned alongside the existing httpx dependency.

## 1. Prepare your terminal

In VS Code, open the project folder and its terminal, then:

```bash
source .venv/bin/activate
python -m pip install -r requirements.lock
```

The SDK is already installed in the environment used during implementation, but
the install command makes the setup reproducible on another checkout/environment.
It does not call the model or charge your Anthropic account.

## 2. Run one NOD2 smoke test with a private key prompt

```bash
PYTHONPATH=src python -m ot_dossier.agent.loop --mode live --target NOD2 --prompt-key --out generated/live-nod2-01
```

At `Anthropic API key (hidden, not saved):`, paste your key **in that terminal**
and press Return. Nothing appears while you paste; this is expected. Do not paste
the key into chat, a Python source file, or a command that will enter shell history.
The key is held in the running process, not written to output files or passed to
the MCP server. You can reuse the prompt for each live run.

If `ANTHROPIC_API_KEY` is already set in that terminal's environment, omit
`--prompt-key`. The program does not automatically read `.env` files. Existing
`.env` files remain ignored by Git. No subscription or API credential is inferred
from the desktop apps you have signed into.

Use a new output directory for every attempt. Existing directories are never
overwritten, including failed attempts. You do not need to start `ot-dossier-mcp`
manually. `PYTHONPATH=src` avoids the editable-install path-file issue encountered
on this Mac.

This command makes paid generation requests. Evidence, scientific rules, tool
schemas, candidate claims, and feedback are sent to the official Anthropic API.
No frozen raw files are modified. Start with NOD2 before trying TNF.

## 3. Understand the limits and progress

The terminal reports that live mode has started. MCP request messages may follow.
The trace is flushed as work progresses; model generation can be quiet while the
API is working. Allow time for a response rather than starting duplicate runs.

| Limit | Default |
|---|---:|
| Generation requests | 4 |
| Estimated input allowance per request, including reserve | 80,000 tokens |
| Cumulative input allowance | 200,000 tokens |
| Maximum output per request | 4,096 tokens |
| Cumulative output allowance | 12,000 tokens |
| MCP tool requests, including host validation | 8 |
| Repair opportunities | 2 |
| Host model-turn timeout (including preflight) | 180 seconds |
| MCP operation timeout | 30 seconds |

Before each generation request, the adapter asks Anthropic to count the complete
request, including tools, system instructions, and conversation history. It reserves
5% plus 256 tokens above the estimate and refuses requests over budget. Estimates
can differ from actual usage; this is not an exact dollar spending cap. Review
[current API pricing](https://platform.claude.com/docs/en/about-claude/pricing)
for the chosen model. Automatic SDK retries are disabled to avoid hidden repeat
requests. A timeout can still incur provider usage even if no usage response arrives.

The evidence sent to the model is a **lossless compact view**, not a smaller sample:
common provenance, record context (including disease scope), and missing-state
descriptions are stored once in lookup tables. Attribute names are stored as shared
column lists, with each record's values in the same order; section membership uses
record indices. The model instructions explain how to read these zero-based tables.
Every original record, attribute value,
missingness state, and disease label is retained. The current view uses short
packet-local citation handles and unwrapped present upstream IDs. The original
full citation IDs are exactly reconstructible; final outputs retain them. Tests reconstruct
the exact original packet. The full normal EvidencePacket is still saved as
`packet.json`. If the request is too large, the run stops; it never silently drops
records or changes the evidence to fit the budget.

## 4. Check the result before reading the narrative

Open `generated/live-nod2-01/result.json`.

- `status: completed`: the exact final candidate passed host validation. Read
  `dossier.md`, which is labeled **LIVE MODEL DRAFT**, and `validation.json`.
- `status: failed`: inspect the reason and trace. No final dossier is published.
  Earlier paid requests may still have consumed tokens.

`usage` and `provider_usage` report returned token counts, including cache fields
when present. `provider_usage.requests_sent` tracks generation attempts; model
lookup and token-count requests are separate. Usage for a request that timed out
before returning is unknown, not zero.

The trace adds `provider_model_checked`, `provider_preflight`, `provider_request`,
and `provider_response` events to the existing MCP/validation events. It records
the actual request content and model output for review, without authentication
headers or the API key. `run_config.json` records the SDK/model, limits, projection
version, and instruction hashes. Do not mistake a provider message ID for a source
evidence citation.

## 5. Review the real dossier

Successful structural validation is not scientific validation. Use the human-reviewed
F1–F5/P1–P5 checklist to score the **generated dossier** separately. Check whether
facts and caveats were preserved, and trace citations for claims about genetics,
mechanism, clinical indications, safety, and tractability. Missing expected facts
are findings; do not rewrite reference answers to match the model. Record unsupported
inferences and cannot-judge items. A `retrieved_fact` label cannot make false prose
true; the deterministic validator still does not judge arbitrary entailment.

After reviewing NOD2, reuse the same command with `--target TNF` and a new directory
such as `generated/live-tnf-01`. TNF's packet is larger and may hit an input limit;
the failure reason will say so. Investigate coverage/token design before changing
limits, rather than silently reducing the evidence.

## Common failures

The first live NOD2 attempt (`generated/live-nod2-01`) confirmed authentication and
model access, but stopped before its second generation request: the old `lossless-v1`
view required an estimated 92,353 input tokens (97,227 with reserve), above 80,000.
One generation request had completed, using 2,628 input and 91 output tokens.
This is not a successful dossier run.

The revised `lossless-v2` view reduces NOD2's canonical packet JSON from 253,508 to
174,880 characters, preserving all data. Character counts are not token counts;
the provider preflight must still confirm it fits. Spending limits are unchanged.
After updating the code, retry in a fresh directory:

```bash
PYTHONPATH=src python -m ot_dossier.agent.loop --mode live --target NOD2 --prompt-key --out generated/live-nod2-02
```

No dependency reinstall is needed for this source-only update. Check the new
directory's `result.json`; keep the first attempt as a record of the observed failure.

| Message | Next action |
|---|---|
| `ANTHROPIC_API_KEY is missing` | Use `--prompt-key` in your interactive terminal. |
| HTTP 401 | Check the key in your Anthropic account; enter it again privately. |
| HTTP 403/404 | Check account/model access; the configured model ID is in run_config. |
| HTTP 429 | Check provider rate limits and available credits; avoid rapid retries. |
| `INPUT_TOKEN_BUDGET_EXHAUSTED` | Read preflight counts; this turn's generation was not sent. |
| `PROVIDER_REQUEST_BUDGET_EXHAUSTED` | The run reached its four-request cap. Inspect why it needed more turns. |
| `REPAIR_BUDGET_EXHAUSTED` | Inspect invalid candidates and findings; no accepted dossier exists. |
| Connection/timeout error | Check connectivity and provider usage before starting another paid attempt. |

Source contracts checked during implementation:
[official Python SDK](https://github.com/anthropics/anthropic-sdk-python),
[tool-call handling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls),
[token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting),
[Sonnet 4.6](https://platform.claude.com/docs/en/models/sonnet-4-6/overview).
