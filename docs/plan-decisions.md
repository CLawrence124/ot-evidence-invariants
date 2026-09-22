# Basis and scope decisions

This document records initial implementation decisions. The agent was subsequently implemented and evaluated; see [current results](evaluation-summary.md). References below to deferred work describe the initial phase, not current completion status.

Read before implementation: the attached `Pasted text.txt`, preserved verbatim as
`source-plan.txt`, and the subsequent conversation accepting the scaled-down plan.
The attachment is design input, not a verified statement of current API behavior.

The current request overrides the attachment's optional-TNF scope: IBD, NOD2, and
TNF are required. One reference case and four synthetic fault tests are required.
No official-MCP comparator or large benchmark is included.

We map **Phase 0** to Session 1 (reference evidence and manual review) and **Phase 1**
to Session 2 (typed packet and deterministic assembler). Source retrieval and a
review worksheet are prepared; a builder must independently review and sign the
reference case. We did not pretend four hours of human review happened, nor label
AI-prepared facts as human-verified. Scaffolding and software can proceed while
that scientific acceptance criterion remains open.

The two simple MCP wrappers, validator, reusable skill, and four fault tests were
small enough to implement against the Phase 1 domain contracts. A real MCP client
test checks that boundary. The model-driven loop is explicitly deferred; a canned
or deterministic response is not called an agent.

Changes driven by source inspection:

- IBD resolves to MONDO_0005265 in the frozen release. The documented EFO_0003767
  example returns null. Crohn disease is MONDO_0005011, an observed descendant.
- The live schema has clinicalStage rather than the historical phase-based shape.
  Query drug-bearing evidence rows and preserve the exact stage/indication unit.
  Comprehensive target clinical-context retrieval is not implemented in Phase 1.
- Capture three pages of 100 rows per target. Expose truncation rather than expanding
  to tens of thousands of rows. This selection must not support absence claims.
- Use JSON for the small reference files to avoid a YAML runtime dependency.
- Use the official MCP Python SDK's built-in FastMCP, pinned to tested `mcp==1.30.0`.
  This is the maintained v1 compatibility line, not the newest SDK major. Current
  SDK main documents v2; switching SDK major adds no value to the scoped milestone.
  The separate `fastmcp` package is not installed. Its version is not confused with
  either `mcp` or `fastmcp-remote`.
- Missingness uses a typed state and reason; raw JSON nulls are preserved as source
  data. A present value uses a separate `present` state.
- An invalid structured direct-scope assertion is an ERROR, stronger than the
  attachment's suggested warning. Prose entailment remains outside the validator.
- No supported claim says that prompting can never enforce a rule; the narrower
  engineering thesis is in the README.
