# Verification record

Current milestone: September 22, 2026. See [evaluation findings](evaluation-summary.md) for scientific-review outcomes and [repository audit](repository-audit.md) for pre-upload checks.

## Software verification

The full suite covers 84 tests: frozen replay and integrity, typed missingness,
entity/scope consistency, four fault injections, reference-case expectations,
real stdio MCP contracts, bounded host failures/repairs, and the live adapter with
mock provider transport. The existing environment run passed in 39.79 seconds.
A clean-environment audit is recorded separately in repository-audit.md.

The five source-reference tests compare frozen fields, not human notes or paper
conclusions. The full suite explicitly demonstrates that unsupported prose can
pass a reference-membership check. Mock provider tests exercise the real SDK and
local MCP server but do not incur provider costs or prove live scientific quality.

Frozen NOD2 and TNF packets reproduce byte-identically. Capture manifests verify
file hashes. Archived original runs carry SHA-256 manifests; the corrected dossier
has separate signed-artifact hashes. These provide integrity, not authentication.

## Live development history

| Attempt | Outcome |
|---|---|
| live-nod2-01 | Assembly completed; next request stopped at input preflight; no final dossier. |
| live-nod2-02 | Completed; 3 MCP calls, 0 repairs; human-assisted review disposition needs revision. Archived under evaluations/live-nod2-02/original. |
| live-nod2-03 | Cumulative input limit stopped another finalization turn. Led to host-owned final validation. |
| live-nod2-04 | Dangling citation followed by malformed repair; cumulative input stop. Led to structured JSON output and citation hints. |
| live-nod2-05 | Mixed scope then mutated reference; input limits stopped another repair. Led to constrained short citation handles and lossless-v3 projection. |
| live-nod2-06 | Completed in 2 generation requests, 2 MCP calls, 0 repairs. Three error-bearing claims remained despite valid references/contracts. A separate corrected derivative was reviewed and signed off. |

See [revision history](revision-01.md) for the changes and [artifact index](../evaluations/README.md) for shareable evidence. The interrupted development attempts are described historically; their local generated/ directories are not required to run the repository. Original completed runs and the corrected derivative are archived for review.

The successful run is not a controlled before/after study, cost benchmark, or
held-out evaluation. Revisions were informed by review of the same NOD2 case.
TNF's latest recorded run is scripted integration only, with no provider tokens.

## Boundaries

No independent primary-publication review, specialist biological validation,
multiple-reviewer agreement, official-MCP comparison, or deployment is claimed.
The source reference review and the corrected dossier sign-off are distinct.
The automated suite blocks socket connections in its test process; MCP subprocesses
use only the replay assembler. Dependency installation requires network access.
