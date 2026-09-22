# Revision 01: changes following the NOD2 review

Current milestone (2026-09-22): live-nod2-06 completed, its review is recorded, and a separate corrected derivative is signed off. TNF has fresh simulated integration coverage. See [evaluation summary](evaluation-summary.md). Earlier attempt descriptions below are historical, not instructions to repeat a paid run.

Baseline: `generated/live-nod2-02`. Its AI-assisted human review was signed off
on 2026-09-22 with disposition **needs revision**. The baseline and its signed
review are preserved. The frozen data, record IDs, two MCP tools, model,
packet/dossier schemas, and spending limits remain unchanged.

## What changed and what that proves

| Review finding | Revision | How it is checked |
|---|---|---|
| Claim-04 mixes direct IBD with descendant Crohn evidence | Reject claims containing multiple source diseases. Require every citation in a `direct_evidence` claim to be direct disease evidence. | Domain regression tests plus rejection/repair through the real MCP loop. |
| Claims 08/10 cite unrelated records for retrieval facts | Host summaries now explicitly show returned and total counts, distinguish unknown clinical total from evidence-query total, and point to packet section metadata. Instruct the model to leave these summaries to the host. | Renderer tests verify distinct metadata values. Live review recorded in evaluations/live-nod2-06. |
| Claim-02 transfers directions between variants | Skill requires record-by-record matching of identity, score, target direction, and trait direction. | Prompt-guided; human checks against the next output required. |
| Claims 01/03 add unsupported dates or inadequately cite ranges | Omit dates absent from source fields; cite range endpoints and use consistent rounding. | Prompt-guided; human checks required. |
| Claim-06 drops “By similarity” | Preserve qualifiers on the particular source sentence summarized. | Prompt-guided; human checks required. |
| Claim-09 names an uncited disease | Require an attached citation for every named entity; split diseases across claims and prefer fewer fully supported examples. | Single-disease citation sets enforced; coverage of the actual prose remains human-reviewed. |

Initial revision validator version: `0.2-single-disease-claims` (later extended to `0.2.1-citation-repair-hints`). Renderer version:
`0.2-explicit-section-totals`. Both appear in new run configuration, alongside
prompt/skill hashes and the unchanged model/projection information. The original
successful validation reflects the earlier validator; rechecking an old candidate
under the new rules does not alter its historical result.

No broad prose entailment checker was added. A model can still write unsupported
text using valid citations or label it `retrieved_fact`. Passing these software
checks must not be reported as proof of scientific correctness.

Verification: **84 tests passed**, including repair of a mixed-scope candidate
over real MCP; the skill's structural validation passed. A read-only check of
the original dossier under the new validator is saved in
`evaluations/revision-01/baseline-revalidation.json`. Attempt 03 exercised the
revised instructions but did not complete; the subsequent validation-flow fix
was subsequently exercised by live-nod2-04 through live-nod2-06; see the current evaluation summary.

## Budget-flow fix after live-nod2-03

The first revised live attempt failed on the cumulative input budget. The model
assembled evidence, submitted a draft to validation, then submitted a corrected
draft to validation. The corrected draft passed, but another model turn was needed
to emit final JSON. That turn required 78,427 reserved input tokens on top of
145,856 already used, exceeding the unchanged 200,000 total allowance. No fourth
generation request was sent. The trace contains the candidate, but the failed run
did not publish a final dossier or receive scientific review.

The adapter now disables native tool calls after successful assembly using the
installed SDK's `tool_choice: {type: none}` contract. Claude submits final JSON
directly; the host calls the same validation MCP tool and returns failures as
repair feedback. No passing tool-call candidate is silently promoted to a final
submission. This removes a redundant finalization turn and counts repairs through
the host's existing repair budget. All request and token caps remain unchanged;
an expensive or repeatedly invalid run can still stop at a budget boundary.

The instructions also clarify that every claim's `disease_id` is the selected IBD
ID, even when its cited source disease is a descendant. The SDK/MCP regression
test covers a draft with both entity and mixed-scope errors, followed by successful
repair in three generation requests total (assembly, draft, repair).

## Output-format and citation-repair fix after live-nod2-04

Attempt 04 used host-owned validation as intended. Its first draft failed on a
nonexistent citation that blended two real record IDs. Its repair response began
with explanatory prose, so strict JSON parsing rejected it. The next repair's
reserved input plus 146,825 tokens already used exceeded the 200,000 cumulative
allowance. Both responses ended normally; neither was truncated by max_tokens.
No fourth generation request or final dossier was produced.

The adapter now requests Anthropic structured JSON output after assembly, using a
closed, packet-specific schema with the selected entity IDs and exact section
interpretations. The installed SDK's schema transformer removes unsupported
constraints; the host still applies the full domain schema and validator. The
output schema is included in preflight token counting, and the duplicate prose
schema is omitted after assembly. Refusal, incomplete output, or unexpected
malformed responses remain fail-closed. Provider documentation:
[structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).

Validator `0.2.1-citation-repair-hints` now includes up to three spelling-similar,
existing record IDs with source/kind/disease and source pointers when a citation
does not exist. These are candidates for inspection, not evidence of support.
The model must choose a supported citation or remove the claim; no automatic
replacement occurs. The original draft still fails validation in the regression
check, and the newly supplied hints include the relevant source record.

This fix is tested offline; no paid request was made during implementation.
It does not establish improved scientific accuracy or guarantee completion within
the unchanged budgets. The original successful baseline and failed attempts remain
preserved. A second repair after two full-context generations can still exceed
the cumulative limit.

## Citation handles after live-nod2-05

Attempt 05 returned valid JSON, but the first draft mixed source diseases in one
claim. Its repair then changed the final character of a citation hash to a
nonexistent ID. The next request exceeded both input limits: 80,756 reserved
tokens versus the 80,000 per-request cap and 148,786 already used versus the
200,000 cumulative allowance. No fourth generation request was sent.

The adapter now sends a `lossless-v3` packet view using short packet-local handles
(`R0000`, `R0001`, etc.) in `record_ref`. The final-output schema enumerates the
allowed handles and groups them by source disease, so a schema-compliant claim
cannot invent a handle or combine different source diseases. These choices do
not prove the selected record supports the prose. Direct assertion labels still
undergo domain validation after decoding.

The adapter resolves each selected handle by exact lookup against the original
assembled packet. It never guesses based on similarity. A different packet ID
or unknown handle fails closed. Provider responses keep the short handles in the
trace; `citation_handles_resolved` records the exact mapping used. Saved dossiers,
the host/MCP validation calls, and final packets retain the original full IDs.
No MCP tool or scientific schema was added or removed.

The view also unwraps present string upstream IDs, preserving missing-state
objects. Original record hashes can be reconstructed from the complete record
content using the assembler's hash rule; round-trip tests recover the entire
original packet, including IDs, for both targets. No record is sampled out.
This reduces repetitive input as well as avoiding long-ID copying in output.
Actual new token counts still require provider preflight; limits are unchanged.
The NOD2 packet view shrank from 174,880 to 142,027 JSON characters. The new
output schema also takes input space, and is included in the provider's preflight;
character savings alone are not a guarantee of token-budget fit.

## Historical run command (optional reproduction)

From the project folder, with your existing virtual environment:

```bash
source .venv/bin/activate
PYTHONPATH=src python -m ot_dossier.agent.loop --mode live --target NOD2 --prompt-key --out generated/live-nod2-06
```

Paste the API key only at the hidden terminal prompt. No dependency reinstall or
separate MCP server launch is needed. This starts a new paid run under the same
four-generation-request and token limits. If the directory exists, choose the next
unused name; never replace a baseline or failed run.

The host launches the server, checks each final candidate, and writes the result.
Start by checking `result.json`. A failed run may contain useful repair feedback
in `trace.jsonl`; a completed run still needs a new review.

## Evaluation procedure used for the revision

Use the existing signed reference observations. Review the new dossier against
the old findings, matching by content rather than claim number (numbers can change).
Record each old issue as resolved, persists, omitted, or cannot judge. An omitted
claim is not evidence that synthesis of that fact improved; assess coverage too.
Check all new claims for new errors, not just the old problem sentences. Keep
record membership, factual support, expected-fact coverage, and inference limits
as separate outcomes.

The completed review is under `evaluations/live-nod2-06/`. The baseline sign-off
was not copied to the new output; the edited derivative has its own sign-off.
TNF has a separate scripted integration run; live TNF review is deferred. Improvements on this reviewed NOD2 case are
development results, not held-out generalization or superiority to another MCP.
