# Open Targets evidence invariants

A reproducible target-dossier prototype for **NOD2 and TNF in inflammatory bowel
disease (IBD)**. It explores which scientific constraints can be enforced in code
and which still require human judgment.

Built by Chris Lawrence, RN with AI coding assistance. Public Open Targets data
only; no employer or client materials. Local research prototype, not a clinical
recommendation system.

## Review in five minutes

1. Read the [evaluation findings](docs/evaluation-summary.md).
2. Compare the [original live NOD2 dossier](evaluations/live-nod2-06/original/dossier.md)
   with the [corrected dossier](evaluations/live-nod2-06/corrected/dossier.md)
   and [signed review](evaluations/live-nod2-06/corrected/review.md).
3. Inspect [the domain validator](src/ot_dossier/domain/dossier_validator.py),
   [thin MCP server](src/ot_dossier/mcp/server.py), and
   [four fault-injection tests](tests/unit/test_contracts.py).
4. Run the [offline demo](docs/demo.md); no API key is required.

## What this adds

Open Targets already has an [official MCP server](https://github.com/opentargets/platform-mcp)
for access to its API. This project is a **separate, task-specific server** that
replays frozen GraphQL responses. It does not call, replace, or claim superiority
over the official MCP.

- `assemble_target_disease_evidence`: creates a typed packet with disease scope,
  source-record provenance, and explicit missingness and retrieval limits.
- `validate_dossier_references`: checks packet-bound citations and selected
  structured assertions. It does not determine whether arbitrary prose is true.
- A bounded agent loop requires final validation and records tool calls, repairs,
  versions, and token use. A [reusable skill](skill/ot-target-dossier/SKILL.md)
  guides synthesis. Markdown and JSON outputs support subsequent review.

For example, a Crohn disease record remains descendant evidence for selected IBD.
Calling it direct IBD evidence in a structured assertion is rejected. Inferring
what intervention to use from a LoF/risk label still requires scientific judgment.

| Synthetic fault | Checked behavior |
|---|---|
| Descendant evidence asserted as direct | Reject with `INDIRECT_SCOPE` |
| Approval for an unrelated indication asserted for IBD | Reject with `INDICATION_MISMATCH` |
| Empty safety data interpreted as a safe target | Preserve unknown state; reject structured safety assertion |
| Nonexistent citation | Reject with `DANGLING_REFERENCE` |

## Results and limits

The reviewed live NOD2 run completed with **2 generation requests, 2 MCP calls,
0 repairs, and 63,391 input / 1,341 output tokens**. Structural validation passed,
but human-assisted review identified three error-bearing claims: a mismatched
source citation, an uncited named variant, and an incorrect numeric lower bound.
A separate edited derivative was signed off by Chris Lawrence, RN on September
22, 2026, with partial factual coverage disclosed. It is not unassisted model success.

TNF passed scripted integration through the real MCP server. **Live TNF scientific
evaluation is not completed.** Both targets use 300-row frozen evidence captures,
not exhaustive or representative evidence samples. There is no held-out benchmark,
official-MCP comparison, independent publication review, or specialist validation.
See [evaluation details](docs/evaluation-summary.md) and [limitations](docs/limitations.md).

## Quick start — Python 3.12

From this repository directory:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
python -m pip install --no-deps --no-build-isolation -e .
python -m pytest -q
PYTHONPATH=src python -m ot_dossier.agent.loop --target NOD2 --out generated/demo-nod2-01
```

Dependency installation needs network access once. Tests and this **scripted**
demo use frozen data and no model API. Expected demo result: two MCP calls and
zero repairs. Use a new output directory on each run; the agent refuses overwrite.
The loop launches its own stdio MCP server. Open `generated/demo-nod2-01/dossier.md`
and `result.json` afterward.

For deterministic source-observation drafts without the agent loop:

```bash
PYTHONPATH=src python -m ot_dossier.cli --target NOD2 --out generated
PYTHONPATH=src python -m ot_dossier.cli --target TNF --out generated
```

The ordinary CLI overwrites its named draft outputs in the specified directory;
the agent's per-run directories are immutable by convention and protected from
overwrite by the host. Installed entry points are `ot-dossier` and
`ot-dossier-mcp`. See the [beginner MCP walkthrough](docs/local-mcp.md) or
[optional paid live-run guide](docs/live-agent.md). Keep API keys out of files and Git.

The supported runtime is an editable checkout: fixtures and skill files are loaded
from the repository. Wheel-only deployment and remote hosting are not supported.

## Architecture and reproducibility

```text
Open Targets GraphQL → frozen cassettes + checksum manifest
                                  ↓
                         deterministic assembler
                                  ↓
                         typed EvidencePacket
                                  ↓
                 two stdio MCP tools ↔ bounded agent host
                                  ↓
                   required validation → JSON + Markdown
                                  ↓
                      attributed human/assistant review
```

[Architecture](docs/architecture.md) explains the code boundaries. Packet IDs and
record IDs are content-derived; provenance retains cassette names, response hashes,
and JSON pointers. Frozen replay is reproducible, but a fresh API query need not
return the same evidence. [Verification](docs/verification.md) records the checks; the [pre-upload audit](docs/repository-audit.md) includes a clean installation and 84 passing tests.

| Frozen data release 26.06 | NOD2 | TNF |
|---|---:|---:|
| Captured evidence rows | 300 | 300 |
| Upstream matching rows | 4,003 | 20,990 |
| Direct / descendant rows | 31 / 269 | 64 / 236 |
| Curated target safety records returned | 0 | 9 |

Clinical context is limited to drug-bearing rows in that evidence capture.
An empty result is not proof of safety or absence of drugs. Source-reported
`APPROVAL` stays with its exact indication; `PHASE_4` is not converted to approval.

The [source reference case](reference/ibd_nod2/reference_facts.json) contains five
reviewed source facts and five prohibited inferences; its metadata distinguishes
human source review from publication-level validation. The [artifact index](evaluations/README.md)
separates original outputs, scripted runs, review findings, and edited derivatives.

## Scope and attribution

No UI, deployment, ranking, RAG/vector database, additional biomedical source,
official-MCP comparator, or large benchmark. See [scope decisions](docs/plan-decisions.md).

Code: [Apache-2.0](LICENSE). Open Targets Platform data is marked CC0; retain
upstream attribution and consult its [licensing](https://platform-docs.opentargets.org/licence)
and [citation guidance](https://platform-docs.opentargets.org/citation).
Only queried fields are frozen; no paper full text is redistributed.
[Sources](docs/sources.md) and [NOTICE](NOTICE) document attribution. No endorsement
by Open Targets, Anthropic, or a data provider is implied.
