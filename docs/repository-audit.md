# Pre-upload repository audit

Completed September 22, 2026. Disposition: ready for external review as a local portfolio prototype, within the declared scientific and deployment limits. Nothing was published during this audit.

## Fixes made

- Reorganized the README around a five-minute reviewer route, concrete results, a reproducible quick start, and limits. Moved the long beginner walkthrough to docs/local-mcp.md and removed the original machine path.
- Declared jsonschema as a runtime dependency because the agent imports it; it was previously only in the test extra (the lock file already installed it).
- Updated current-status documentation and clearly labeled historical development notes.
- Reconciled source-reference review metadata from the recorded human confirmations. Preserved prior metadata, left the uncertain original review date null, and changed no expected fact, per-item verdict, or review note.
- Archived the earlier NOD2 baseline alongside the newer live run, TNF simulation, and signed corrected derivative. Added an artifact index so ignored generated/ files are not needed to review the completed evidence.
- Expanded Git exclusions for alternate virtual environments, environment files, private-key file extensions, and macOS metadata.
- Added a read-only GitHub Actions workflow to install pinned dependencies and run offline tests. Hosted CI has not run yet; no passing CI badge is claimed.

## Reproduction checks

Created a fresh Python 3.12 environment and downloaded the exact requirements.lock dependencies. Installed an isolated copy containing only Git-upload-eligible repository files, without copying the original virtual environment or generated/ directory.

| Check | Result |
|---|---|
| Pinned dependency installation | Passed |
| Editable installation from isolated copy | Passed |
| Dependency consistency, pip check | Passed |
| Full suite from isolated copy | 84 passed in 40.20 seconds |
| Installed ot-dossier entry point, NOD2 and TNF | Both produced artifacts |
| Scripted TNF agent through real stdio MCP | Completed; 2 tool calls, 0 repairs |
| Archive and signed-artifact SHA-256 checks | Passed; signed dossier unchanged |
| JSON/JSONL parse checks | Passed |
| Relative Markdown file links | Passed |
| Upload file inspection | No binaries, symlinks, or individual files over 10 MB |
| Credential-pattern/local-machine-path scan | No matches in upload-eligible files |

The credential scan checks common API-token/private-key formats; it is not a formal security audit. Clean installation and execution were verified on macOS with Python 3.12.6. The Linux CI workflow is configured but not yet exercised on GitHub. Dependency downloads used network access; tests and scripted runs made no paid model calls.

## Reviewability and honest claims

The official Open Targets MCP is not used by this custom server. Frozen API replay, structured scientific contracts, mandatory final validation, and attributed review form the contribution. The original live output's valid references did not prevent three scientific citation/numeric issues; the corrected derivative remains explicitly separate. Review is development on the same case, not a held-out benchmark.

Live TNF scientific evaluation, independent publication/specialist review, deployment, and comparative performance are not completed. Those limits do not prevent reviewing the implemented prototype. The original source-review date is unknown and explicitly null; its reconciliation date is not presented as that date.

## Upload handoff

Use the project files selected by Git's ignore rules, or the separately prepared clean ZIP. Do not drag the entire local folder into a browser upload: it also contains local environments and generated work intentionally excluded from publication. No commits or remote repository were created by this audit. After publishing, inspect the rendered README and let GitHub Actions run; add the actual repository URL to the application materials.
