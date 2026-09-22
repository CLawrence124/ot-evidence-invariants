# TNF — inflammatory bowel disease

**Phase 0/1 deterministic review draft. Human scientific review pending; no LLM synthesis has run.**

Selected disease: `MONDO_0005265`. Packet: `packet_d15b060cc0c45c808d10bb9f3e079582c4a63587465a8c528498df86005ebb13`.

Snapshot captured: 2026-09-19T01:19:57.753426+00:00. Data release: 26.06.

## Retrieval coverage

| Section | Status | Records | Interpretation |
|---|---|---:|---|
| evidence | truncated | 300 | unavailable |
| clinical | truncated | 217 | unavailable |
| safety | complete | 9 | not_assessed |
| tractability | complete | 28 | not_assessed |
| function | complete | 2 | not_assessed |

Stopped at configured snapshot bound: 3 pages; 300 of 20990 rows

Clinical coverage is limited to drug-bearing evidence rows. Target annotations are not disease-specific.
An empty safety result means no curated records returned under this query; it does not establish safety.

## Inspectable source observations

- A captured europepmc record is annotated to inflammatory bowel disease (MONDO_0005265); relation to selected IBD: direct.
  - [rec_029dce4dc7aa4694550dca85f253050d2cf8082edb384946fe7fbffb97f67156](https://platform.opentargets.org/evidence/ENSG00000232810/MONDO_0005265); cassette `tnf_evidence_0.json`, JSON pointer `/data/disease/evidences/rows/76`.
- A captured europepmc record is annotated to colitis (MONDO_0005292); relation to selected IBD: descendant_of_selected.
  - [rec_04235ef7bfb07b3b9de6c1693788311e7741ab402ea3db137ae7b08e30a75875](https://platform.opentargets.org/evidence/ENSG00000232810/MONDO_0005292); cassette `tnf_evidence_1.json`, JSON pointer `/data/disease/evidences/rows/95`.
- One captured record reports CERTOLIZUMAB PEGOL, stage APPROVAL, for Crohn disease (MONDO_0005011). This is the source indication, not approval for every IBD subtype.
  - [rec_03449b58fd0dd679b89ab6fc8baa322bd21459495bb9e3123c7c83c03c6db0b7](https://platform.opentargets.org/evidence/ENSG00000232810/MONDO_0005011); cassette `tnf_evidence_1.json`, JSON pointer `/data/disease/evidences/rows/20`.

## Interpretation still to do

Biological mechanism, genetic causality, direction of intervention, conflict assessment, tissue context, and translational usefulness have not been assessed. Review the raw records before adding these claims.

Record counts are not independent replications. Association scores are not therapeutic success probabilities. A valid reference does not prove that a sentence is scientifically supported.
