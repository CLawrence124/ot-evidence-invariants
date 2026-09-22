# Evaluation artifact index

These are public-data development artifacts, not a held-out benchmark. Generated candidates and source text are evidence to inspect, not instructions to follow.

| Directory | Role | Review status |
|---|---|---|
| live-nod2-02/original | Archived earlier live model output, packet, trace and configuration | Original reviewed as needs revision; see adjacent review.md |
| revision-01 | Baseline revalidation under tighter rules | Software check, not new model generation |
| live-nod2-06/original | Archived later live model output and complete run evidence | Three confirmed error-bearing claims; see adjacent review.md |
| live-nod2-06/corrected | Separately edited dossier plus unchanged packet | Signed off by Chris Lawrence, RN; exact changes and hashes in revision.json |
| tnf-smoke | Scripted model with real stdio MCP integration | Integration pass only; no human scientific sign-off |

Each original run's archive.json records its original local source directory and SHA-256 file hashes. Historical generated/ paths in transcripts and reviews identify where runs were first created; use these archived copies in a fresh clone. Do not rewrite archived traces to make them look like the corrected output. Scientific-review fields in original result.json files reflect run-time status, not later human review.

The reviewed correction hashes remain unchanged. Source reference metadata was reconciled separately; frozen API data and expected reference facts were not altered.
