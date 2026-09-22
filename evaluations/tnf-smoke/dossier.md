# TNF–IBD simulated-agent dossier

**SIMULATED MODEL — scripted integration exercise, not LLM synthesis or a human-reviewed scientific dossier.**

Model: `scripted-v1/happy`. Packet: `packet_d15b060cc0c45c808d10bb9f3e079582c4a63587465a8c528498df86005ebb13`.

## Captured evidence and limits

- evidence: truncated; 300 records returned; total 20990; interpretation unavailable.
  Scope: Selected disease plus frozen descendants; bounded evidence pages.
  Retrieval detail: Stopped at configured snapshot bound: 3 pages; 300 of 20990 rows.
  Coverage is incomplete; absence conclusions are not supported.
  Metadata source: `packet.json#/sections/evidence` (host-rendered; not an individual evidence record).
- clinical: truncated; 217 records returned; total unknown; interpretation unavailable.
  Scope: Drug-bearing rows within the scoped evidence query; not all target drugs or indications.
  Underlying evidence capture limit: Stopped at configured snapshot bound: 3 pages; 300 of 20990 rows.
  Returned counts drug-bearing records extracted from the captured evidence, not all drugs or indications; the evidence-query total is not a clinical-record total.
  Coverage is incomplete; absence conclusions are not supported.
  Metadata source: `packet.json#/sections/clinical` (host-rendered; not an individual evidence record).
- safety: complete; 9 records returned; total 9; interpretation not_assessed.
  Scope: Target-level annotation; not IBD-specific or a comprehensive safety assessment.
  Records retrieved; scientific interpretation requires review.
  Metadata source: `packet.json#/sections/safety` (host-rendered; not an individual evidence record).
- tractability: complete; 28 records returned; total 28; interpretation not_assessed.
  Scope: Target-level annotation; not IBD-specific or a comprehensive safety assessment.
  Records retrieved; scientific interpretation requires review.
  Metadata source: `packet.json#/sections/tractability` (host-rendered; not an individual evidence record).
- function: complete; 2 records returned; total 2; interpretation not_assessed.
  Scope: Target-level annotation; not IBD-specific or a comprehensive safety assessment.
  Records retrieved; scientific interpretation requires review.
  Metadata source: `packet.json#/sections/function` (host-rendered; not an individual evidence record).

Record counts are not independent replications. Association scores are not therapeutic success probabilities.

## Scripted claims

- A captured europepmc record is annotated to inflammatory bowel disease (MONDO_0005265); relation to selected IBD: direct.
  - [rec_029dce4dc7aa4694550dca85f253050d2cf8082edb384946fe7fbffb97f67156](https://platform.opentargets.org/evidence/ENSG00000232810/MONDO_0005265) — `tnf_evidence_0.json`, `/data/disease/evidences/rows/76`; scope `direct`.
- A captured europepmc record is annotated to colitis (MONDO_0005292); relation to selected IBD: descendant_of_selected.
  - [rec_04235ef7bfb07b3b9de6c1693788311e7741ab402ea3db137ae7b08e30a75875](https://platform.opentargets.org/evidence/ENSG00000232810/MONDO_0005292) — `tnf_evidence_1.json`, `/data/disease/evidences/rows/95`; scope `descendant_of_selected`.
- One captured record reports CERTOLIZUMAB PEGOL, stage APPROVAL, for Crohn disease (MONDO_0005011). This is the source indication, not approval for every IBD subtype.
  - [rec_03449b58fd0dd679b89ab6fc8baa322bd21459495bb9e3123c7c83c03c6db0b7](https://platform.opentargets.org/evidence/ENSG00000232810/MONDO_0005011) — `tnf_evidence_1.json`, `/data/disease/evidences/rows/20`; scope `descendant_of_selected`.

## Review status

Host validation checks structure and reference contracts, not scientific entailment. This generated output still requires human review. No clinical recommendation or target ranking is made.
