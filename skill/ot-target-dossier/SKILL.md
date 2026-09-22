---
name: ot-target-dossier
description: Review NOD2 or TNF evidence for inflammatory bowel disease using the project's two MCP tools, preserving scope, provenance, and missingness in a structured dossier.
---

# Open Targets target dossier

Use this skill with `assemble_target_disease_evidence` and
`validate_dossier_references` from the local Open Targets Evidence Invariants server.
Read [scientific rules](references/scientific-rules.md) before interpreting records.

Assemble the explicitly selected NOD2 or TNF case for IBD. Retain the returned
packet ID, source disease on every record, retrieval limits, and section states.
Write claims with record_refs from that packet and an accurate structured assertion
kind. Keep source facts separate from hypotheses and unassessed interpretations.
Do not label a claim `retrieved_fact` to evade a direct-scope or approval check.
Use one source disease per claim. A `direct_evidence` claim may cite only direct
disease evidence, not descendant or target-context records. Separate those
observations, even when they come from the same study.

Before submission, check every named entity, numerical value/range, direction,
and qualifier against the exact attached records as described in the scientific
rules. Omit details that cannot be supported within this frozen packet. Leave
retrieval counts and empty-section summaries to the host's metadata renderer;
do not attach an unrelated record to make such a summary look cited.

Validate the structured dossier against its packet handle, correct errors, and
surface unresolved findings. If the server reports an unknown handle, assemble
the case in the current process again. If tools are unavailable, say so; do not
invent tool results. Successful validation establishes reference membership and
specific structured contracts, not scientific support for every sentence.

Respect the host's tool-call and repair budgets. Emit Markdown and JSON only after
host validation. Keep human review status visible; each newly generated dossier
requires its own review, regardless of reviews of earlier runs. Do not add target ranking, candidate
discovery, or outside evidence to this deliberately narrow workflow.
