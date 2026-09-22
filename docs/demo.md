# Five-minute local demo

Run from the repository root with its virtual environment. No API key or network capture is needed. Choose a new output directory if the suggested one already exists.

## 1. State the problem (30 seconds)

“An evidence record about Crohn disease must not silently become direct evidence for the selected IBD term. An existing citation also need not support the sentence citing it. This project separates those two problems.”

## 2. Show one preserved observation (60 seconds)

Open fixtures/cassettes/26.06/nod2_evidence_0.json. Under response.data.disease.evidences.rows, index 32 reports Crohn disease, LoF, risk, and odds ratio 2.9291000366210938. Index 32 is the 33rd array item. In the archived packet, search rec_88c6798ade1f938f9fd127c8f9ac75146e2455f9a382145197eb98a8cccca3f5 and show descendant_of_selected plus its cassette pointer.

## 3. Exercise both tools (60 seconds)

```bash
source .venv/bin/activate
PYTHONPATH=src python -m ot_dossier.agent.loop --target TNF --out generated/demo-tnf-01
```

Expected: simulated completion, two MCP tool calls, zero repairs. The scripted model requests assemble_target_disease_evidence; the host requires validate_dossier_references on the final submission. This uses a real stdio MCP connection but no language-model generation.

## 4. Show the four contract failures (60 seconds)

```bash
PYTHONPATH=src python -m pytest tests/unit/test_contracts.py -k test_fault -v
```

Four tests should pass because the deliberately invalid cases are rejected: descendant-only direct evidence, wrong-indication approval, unsupported safety, and nonexistent citation. Passing a fault test means rejecting its synthetic error, not accepting the invalid claim.

## 5. Show the limitation and review outcome (90 seconds)

Open evaluations/live-nod2-06/original/dossier.json and validation.json. The validator accepted the original output, yet C006 cites a minimum odds ratio of 1.9051 while stating 1.92. Show the attributed review and separate corrected dossier. Explain that software establishes citation existence and structured scope; claim support needs further checking. Do not describe the edited derivative as the model's original answer.

Finish with the bounded result: live NOD2, scripted TNF, signed human review of an edited derivative, frozen provenance, and known limits. A live provider call is unnecessary for this demo.
