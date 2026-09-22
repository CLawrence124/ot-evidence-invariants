# Application material

## Resume bullet

Built an AI-assisted Open Targets evidence-review prototype with a custom Python MCP server, typed evidence packets, frozen API replay, and deterministic checks for disease scope, indication-specific approval, missing safety data, and citation validity; evaluated a live NOD2–IBD dossier through documented human review and tested TNF integration.

## Project description

I built a narrow target-dossier agent around public Open Targets data to explore which scientific constraints should be enforced in software and which still require human judgment. A custom MCP server exposes evidence assembly and reference validation over a deterministic domain layer. The agent produces Markdown and JSON dossiers with source-record provenance and explicit retrieval limits. A live NOD2 evaluation passed structural validation but still contained citation and numeric errors; I documented those findings and reviewed a separate corrected dossier. TNF exercises the same infrastructure through a scripted integration run. The project draws on my clinical abstraction and quality-assurance background, and was developed with AI coding assistance.

## Interview points

- Why a custom MCP server? To expose narrow reproducible evidence contracts; not to duplicate the whole platform or claim superiority over the official server.
- What did MCP contribute? A typed interface separating the model-facing tools from deterministic data processing. The host controls execution and final validation.
- What did review catch? Existing citations that failed to support source labels, a named variant, or a numeric endpoint. Citation membership is not scientific entailment.
- What changed? Tighter scope rules, host-rendered retrieval summaries, schema-constrained short citation handles, and bounded model requests with traceable failures.
- What is incomplete? Live TNF evaluation, publication-level/specialist validation, deployment, and held-out testing. The current result is an individual-builder portfolio prototype.
- What would come next? Structured claim fields for numeric ranges and named entities, then tests on newly selected cases. Do not claim these are already implemented.

## Share with the application

Use the repository README as the entry point, with the evaluation summary and short demo. Repository: [CLawrence124/ot-evidence-invariants](https://github.com/CLawrence124/ot-evidence-invariants). No new provider run is needed. Do not claim production readiness, validated target selection, or autonomous discovery.
