# Bounded agent loop

Implemented in `loop.py`: real stdio MCP client, skill/rules loading, typed model
actions, mandatory final validation, two repair opportunities, eight total tool
requests, twelve model turns, and operation timeouts. A new output directory holds
trace/config/result files; accepted runs also save packet, dossier, Markdown, and
validation results. Existing runs cannot be overwritten.

`simulated.py` implements the async model interface with fixed behaviors: success,
one invalid citation then repair, malformed dossier then repair, repeated invalid
citations, and repeated tool calls. It uses returned packets, not live evidence.
This is an integration harness, not a live model or scientific evaluation.

See [simulation guide](../../../docs/simulated-agent.md) for the offline walkthrough. Step 3 is implemented
in `anthropic_adapter.py`: Anthropic SDK 1.7.0, native tool messages, lossless packet
projection, preflight token counting, and cumulative usage limits. The default
model is claude-sonnet-4-6. [live guide](../../../docs/live-agent.md) explains the first paid smoke run.
No key is required for simulated mode. Mock tests do not establish live success.

Live NOD2 has completed and received attributed review; see the [evaluation summary](../../../docs/evaluation-summary.md). TNF has scripted integration coverage only.
