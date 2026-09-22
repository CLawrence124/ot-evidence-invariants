# Corrected derivative: changes and coverage

Status: signed off by Chris Lawrence, RN on 2026-09-22; corrected dossier and disclosed coverage limits accepted. Original run and its review findings remain separate. This is not a new agent run and must not replace the original output when reporting model performance.

## Changes for final review

- C001: removed the gene_burden citation from a GWAS claim. All 13 remaining citations are GWAS credible-set records; cited score endpoints round to 0.32 and 0.92.
- C002: clarified that the captured literature records map to the selected disease term. Explicitly distinguishes exact disease scope from experimental proof. Citations unchanged; no paper-level entailment review claimed.
- C004: narrowed the claim to rs2066845 and rs2066844 with their two matching UniProt variant citations. Removed unsupported rs2066847 from this claim and removed the unrelated literature and unused variant citations. This does not imply rs2066847 is absent from the packet; C005 still reports its EVA record.
- C006: changed the cited odds-ratio range to 1.91–2.93; verified all five cited records' LoF/risk fields and Crohn descendant scope. Replaced “across multiple phenotype codes” with “cited records” and explicitly bounded the statement to source-field observations.
- C003, C005, C007, C008 and all section states are unchanged. Their prior human confirmations remain in the parent review; they are not a sign-off on this entire derivative.

## Reference-case coverage — assistant assessment

Coverage assesses the dossier's text and accompanying citations/metadata; it is not a claim that all reference wording was reproduced. The packet is byte-identical to the original run.

| Expected fact | Coverage | Evidence or remaining limit |
|---|---|---|
| F1: NOD2/IBD identity and null legacy lookup | Partial | Correct selected IDs in JSON and claims; legacy EFO_0003767 lookup is not reported in the dossier. |
| F2: Crohn is an IBD descendant, indirect for selected IBD | Covered | C005 labels descendant scope; C006 explicitly states indirect scope. |
| F3: 300 of 4,003 rows, three-page capture | Covered | Host-rendered evidence summary states 300 returned, 4,003 total, three-page bound, and truncated retrieval. |
| F4: Crohn gene-burden LoF/risk and OR 2.9291 | Core covered | C006 cites the reference row, reports LoF/risk, rounds the upper endpoint to 2.93, and disclaims independent causal interpretation. Full precision is in the cited packet record. |
| F5: empty safety response does not establish safety | Core covered; response-error detail omitted | Host summary reports complete_empty, zero records, unknown interpretation, and no safety conclusion. It does not explicitly report the absence of GraphQL errors. |

These coverage gaps are documented rather than filled with unsupported record citations. They do not constitute new scientific errors, but the dossier should not be scored as reproducing every detail of F1–F5.

## Prohibited inferences — assistant assessment

| Rule | Assessment of corrected derivative |
|---|---|
| P1: descendant evidence promoted to direct IBD evidence | Avoided: direct claims concern selected IBD; C004–C006 retain descendant scope, with explicit indirect wording in C004/C006. |
| P2: broaden indication approval | Avoided: C008 explicitly describes target-level flags, not IBD-specific approval. |
| P3: empty safety data means safe | Avoided: safety interpretation stays unknown and expressly disallows a safety conclusion. |
| P4: score proves causality/success or LoF determines intervention | Avoided: source observations, no intervention recommendation; score/success distinction in host summary. |
| P5: exhaustive capture, no drugs, independent replications | Avoided: truncated scope, clinical total unknown, no absence conclusion, and explicit non-independence warning. |

## Verification and final human sign-off

Typed Dossier parsing and deterministic reference validation passed with no findings. Focused checks passed for C001 source/range, C004 named variants/source/score/scope, and C006 directions/scope/numeric endpoints. Original run file hashes were checked unchanged. See revision.json for exact before/after claims and source hashes.

Chris Lawrence, RN reviewed the corrected dossier and changes/coverage assessment and explicitly requested final sign-off on 2026-09-22 (“Reviewed- sign off”). This accepts the corrected wording and disclosed coverage limits, including the omitted legacy lookup and GraphQL-error detail. The sign-off incorporates the documented human checks and assistant pre-checks; it does not represent independent human verification of every cited row or underlying publication. Assistant-performed assessments retain their attribution. The original run remains an uncorrected model output with the documented errors; this derivative must not be reported as unassisted model success.
