# NOD2 — inflammatory bowel disease

**Phase 0/1 deterministic review draft. Human scientific review pending; no LLM synthesis has run.**

Selected disease: `MONDO_0005265`. Packet: `packet_42151cbc97e89bc94e9812a821396b40ab21ec89f176cff98bb5e90c5f1277de`.

Snapshot captured: 2026-09-19T01:19:57.753426+00:00. Data release: 26.06.

## Retrieval coverage

| Section | Status | Records | Interpretation |
|---|---|---:|---|
| evidence | truncated | 300 | unavailable |
| clinical | truncated | 0 | unavailable |
| safety | complete_empty | 0 | unknown |
| tractability | complete | 28 | not_assessed |
| function | complete | 3 | not_assessed |

Stopped at configured snapshot bound: 3 pages; 300 of 4003 rows

Clinical coverage is limited to drug-bearing evidence rows. Target annotations are not disease-specific.
An empty safety result means no curated records returned under this query; it does not establish safety.

## Inspectable source observations

- A captured gwas_credible_sets record is annotated to inflammatory bowel disease (MONDO_0005265); relation to selected IBD: direct.
  - [rec_024edd59be3d740248626f8e810da8cecc6935cd1eb073291e21aaa612a72f8d](https://platform.opentargets.org/evidence/ENSG00000167207/MONDO_0005265); cassette `nod2_evidence_0.json`, JSON pointer `/data/disease/evidences/rows/97`.
- A captured uniprot_variants record is annotated to inflammatory bowel disease 1 (MONDO_0009960); relation to selected IBD: descendant_of_selected.
  - [rec_02174e483c9e9ec490e77180f886ff53e863214712536ff1e7c63b682ecdfbad](https://platform.opentargets.org/evidence/ENSG00000167207/MONDO_0009960); cassette `nod2_evidence_0.json`, JSON pointer `/data/disease/evidences/rows/12`.

## Interpretation still to do

Biological mechanism, genetic causality, direction of intervention, conflict assessment, tissue context, and translational usefulness have not been assessed. Review the raw records before adding these claims.

Record counts are not independent replications. Association scores are not therapeutic success probabilities. A valid reference does not prove that a sentence is scientifically supported.
