# Small-case evaluation: what happened

Assessment date: September 22, 2026. This is a development-case evaluation, not a held-out benchmark. Review methods combine assistant field checks, human spot-checks, and human claim review; see the attributed review records.

| Artifact | Result | What it establishes |
|---|---|---|
| NOD2 live run, live-nod2-06 | Completed; 2 model requests, 2 MCP calls, 0 repairs; 63,391 input and 1,341 output tokens | The revised transport and bounded host loop completed on this case. |
| Original dossier reference validator | Valid, no findings | Structured contracts and reference membership passed; prose support is a separate question. |
| Human-assisted review of eight claims | Three confirmed error-bearing claims | C001 includes a gene-burden citation in a GWAS claim; C004 names rs2066847 without a supporting citation in that claim; C006 gives 1.92 as a lower bound when a cited value rounds to 1.91. This is not a calibrated accuracy rate. |
| Corrected derivative | Signed off by Chris Lawrence, RN | Accepted edited output with declared coverage limits; not unassisted model success. |
| TNF scripted run on current implementation | Completed; 2 MCP calls, 0 repairs, no provider tokens | Same server/schema/host path works for a second target; no live TNF or scientific-quality claim. |

## Application packaging verification

On September 22, 2026, the full offline test suite passed in the existing environment (**84 tests in 39.79 seconds**) and then in an isolated clean-install copy (**84 tests in 40.20 seconds**). See the [pre-upload audit](repository-audit.md). A fresh TNF simulation completed with two real MCP calls and zero repairs. Archived run hashes, signed corrected-artifact hashes, and the new document links were verified. No paid provider call was made during this finishing pass.

## Engineering changes informed by review

Stricter single-source-disease claims and direct-citation checks prevent mixed scope in structured assertions. Retrieval summaries are rendered from metadata. Model-visible short citation handles resolve exactly to packet references; schema constraints limit citation selection to existing handles within one source disease. Scientific values remain in a lossless packet projection. These measures do not establish that a chosen record supports the prose.

Earlier attempts stopped at local token limits. The successful run demonstrates completion after the changes; it does not establish a controlled cost comparison, universal reliability, or superiority over another MCP server. The original NOD2 baseline was also reviewed and retained as needing revision.

## Reusable evidence

- [Original live output and trace](../evaluations/live-nod2-06/original/)
- [Attributed review findings](../evaluations/live-nod2-06/review.md)
- [Corrected dossier](../evaluations/live-nod2-06/corrected/dossier.md) and [signed review with F1–F5/P1–P5 coverage](../evaluations/live-nod2-06/corrected/review.md)
- [TNF simulated result](../evaluations/tnf-smoke/result.json)
- [Four synthetic fault tests](../tests/unit/test_contracts.py)

The original and TNF runs are archived byte-for-byte outside ignored generated/ so they can accompany a repository submission. archive.json records source paths and hashes.

## Limits to state in an interview

Both targets' evidence retrieval is capped at 300 rows. There is no official-MCP comparator, held-out benchmark, independent publication review, specialist biological validation, or deployment. The corrected dossier omits the legacy identifier lookup and explicit GraphQL-error detail. Source-checklist metadata was reconciled from recorded human confirmations on September 22, 2026, retaining the old metadata and leaving the original review date null; the dated dossier sign-off is separate. TNF has integration coverage only. These limits are retained rather than concealed by a single accuracy score.
