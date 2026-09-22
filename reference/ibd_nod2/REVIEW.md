# NOD2–IBD reference review

**Status: source review completed by Chris Lawrence, RN, using AI-assisted preparation and recorded human notes.**

Metadata was reconciled on September 22, 2026 from the recorded source-review confirmations. The exact original review date was not reliably established; `reviewed_at` is null rather than guessed. Prior metadata is retained in `review_metadata_reconciliation`. Expected values, per-item verdicts, and notes were not changed. This is a source-field review, not independent verification of the cited publications. Dossier review and sign-off are separate artifacts under `evaluations/`.

The walkthrough below documents the original review procedure; it is retained for reuse and does not require the completed review to be repeated.

## Your first review session

1. Open `fixtures/cassettes/26.06/entities.json`. Inside `response.data`, check IBD,
   NOD2, TNF, and the null legacy identifier. Inspect the descendant list. These
   are the exact entities the software will use.
2. Read each of the five facts in `reference_facts.json`. Each `check` gives a
   cassette and JSON pointer into its **response** object. Follow those pointers
   directly, not through the generated packet. A `length` check counts a list;
   a `contains` check tests membership. Read nearby fields for context.
3. For the gene-burden row, inspect `disease`, `datasourceId`, `literature`,
   `directionOnTarget`, `directionOnTrait`, and `oddsRatio`. Record what these
   fields establish and what they do not. The cited publication has not been
   independently reviewed as part of this milestone.
4. Review the five prohibited inferences. Explain the reason each is unsupported.
   Note uncertainties that require a genetics or drug-discovery reviewer.
5. Inspect `examples/nod2_ibd.md` and its packet JSON. Confirm source scope and
   missingness survived normalization. The draft intentionally does not attempt
   a mechanism-of-action recommendation.

Record `human_verdict` (`pass`, `fail`, or `cannot_judge`) and notes for all ten
items. Fill `reviewer` and `reviewed_at`; set review_status to `verified` only after
all corrections are resolved. Leave ambiguous scientific conclusions unverified.
If expected facts need correction, record why and retain the old snapshot.

## What a packet is, in practical terms

Think of it as a structured abstraction form. Each row retains its source disease,
target, source attributes, and the location of the original record. The code
checks whether the form is internally consistent. An agent will later write a
narrative from it; you evaluate whether the narrative is supported.

The current automated reference checks establish that the five expected source
observations still match the frozen records. They do not score fact coverage or
scientific quality of an agent dossier. Those ratings remain pending.

## Guided walkthrough in VS Code

Allow about 45–60 minutes for a first pass. The objective is to verify that the
reference describes the captured source accurately. This is not independent
verification of the underlying publications or a clinical recommendation.

Keep `reference_facts.json` open beside the raw cassette you are reviewing.
In VS Code, right-click an editor tab and choose Split Right to compare files.
Edit only the reference review fields, not the frozen cassettes. Their checksums
protect the captured source; changing a fixture would invalidate the snapshot.

### F1: Verify the entities

Open `fixtures/cassettes/26.06/entities.json`. A cassette contains `request`
(what was asked) and `response` (what came back). Read `response.data`, not a
matching identifier inside the request's query string. Confirm the returned
`nod2`, `disease`, and `legacy` values against F1. The null legacy lookup means
that lookup returned no entity in this capture; it is not a statement that IBD
does not exist. Record a verdict and your own explanation.

### F2: Follow disease scope

In the same response, find `disease.descendants` and locate MONDO_0005011.
Then open `nod2_evidence_0.json` and search for the full record ID
`92d9b75f6f91fc43f6e23459b250f33cc7454428`. Inspect its `disease` object.
The two checks together establish the recorded relationship: this row names
Crohn disease, while the selected query disease is IBD. The packet should retain
that distinction rather than relabel the row's disease as IBD.

### F3: Count the retrieved pages

From the project terminal, with `.venv` active, paste this entire block:

```bash
python - <<'PY'
import json
from pathlib import Path

folder = Path("fixtures/cassettes/26.06")
retrieved = 0
for path in sorted(folder.glob("nod2_evidence_*.json")):
    cassette = json.loads(path.read_text())
    page = cassette["response"]["data"]["disease"]["evidences"]
    rows = len(page["rows"])
    retrieved += rows
    print(path.name, "rows:", rows, "reported total:", page["count"])
print("Total retrieved:", retrieved)
PY
```

This is a read-only inspection of the raw files. `json.loads` reads JSON into
Python objects; `len` counts list entries. It does not call the assembler or API.
Compare the output with F3: three pages of 100 versus a reported total of 4,003.
The difference explains the packet's `truncated` status. The 300 rows are not
necessarily a representative sample or independent observations.

### F4: Inspect the gene-burden record

Return to the exact record from F2. Check its ID, datasourceId, disease,
directionOnTarget, directionOnTrait, oddsRatio, and literature against F4.
The reference pointer `rows/32` means the 33rd item because array indices begin
at zero; it is not line 32 of the file. Record whether the stated fields match.
Do not turn agreement with a source field into a claim that its underlying study
or causal interpretation has been independently verified. Note any interpretation
questions separately. Reading the primary paper is additional work.

### F5: Inspect missing safety information

Open `nod2_context.json`. Under `response.data.target`, find `safetyLiabilities`.
Check for an empty list `[]` and whether `response` contains GraphQL `errors`.
An empty result without errors differs from a failed query. Neither establishes
that a target is safe. Compare this with the generated packet's `safety` section:
`retrieval.status` should be `complete_empty`; `interpretation.state` should be
`unknown`.

### Record verdicts without changing expected answers

For each F item, edit only `human_verdict` and `reviewer_notes` initially:

- `pass`: the statement accurately describes the source within its stated limits.
- `fail`: the statement contradicts or overstates the inspected source.
- `cannot_judge`: you cannot resolve the question yet; explain what is needed.

For each P item, **pass means you agree the inference should be prohibited**, not
that its quoted statement is true. Explain why it exceeds the evidence. Use
`cannot_judge` when the proposed prohibition or its scientific basis needs review.
These P judgments assess the reference rubric; they do not yet score an agent's
output. Write your own notes rather than copying the prepared rationale.

Preserve JSON syntax: double-quoted strings, commas between fields, no trailing
comma after the last field. Save, then check syntax and the five source checks:

```bash
python -m json.tool reference/ibd_nod2/reference_facts.json > /dev/null
python -m pytest tests/unit/test_reference_case.py -v
```

The first command is silent on success; the second should report five passing
tests for the frozen source observations. Neither command judges your review
notes or verifies an agent dossier. Fill reviewer/date after your actual review;
leave overall status pending if unresolved items remain. If an expected answer
needs correction, document the discrepancy before editing it.

### Compare the draft with the packet

Open `generated/nod2_ibd.md` and `generated/nod2_ibd.packet.json` from your CLI run.
Each Markdown citation names a `record_ref`; find that reference in the packet's
`records` list. Its provenance supplies the cassette and JSON pointer back to
the source. Trace at least one claim all the way back:

```text
Draft sentence → packet record_ref → source cassette + pointer → raw record
```

Ask two separate questions: does the record exist, and does it support the
sentence? The validator helps with the first and specific structured contracts.
Your source review addresses the second. When finished, bring forward any failed
or uncertain items before integrating the model-driven agent.
