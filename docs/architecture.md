# Implementation walkthrough

Start at `domain/models.py`. Pydantic checks the shape of a packet and relationships
between its fields: a direct record must name the selected disease; a descendant
must be listed in the frozen ontology; a clinical record retains one source
indication, drug, mechanisms, stage, report ID, and provenance. Unknown mechanisms
or stage remain typed unknown values.

Then read `domain/evidence_assembler.py`. `load_snapshot` verifies file hashes;
`assemble` is a pure cassette-to-packet transformation, with no model or network.
It verifies entity identity, pagination cursor chains, source-target matches,
counts, errors, and disease membership. Partial field failures cannot turn into
complete empty collections. It deduplicates content-addressed records and marks
duplicate upstream evidence IDs as a partial-retrieval problem.

`record_ref` hashes canonical normalized record content, including entity identity
and source attributes. Provenance separately records the response hash, cassette,
JSON pointer, and Open Targets page. `packet_id` hashes the full normalized packet
except its own ID, including snapshot metadata. Timestamps come from capture,
never the replay clock. Hashes provide integrity/reproducibility, not authentication.

The five sections summarize evidence, clinical context, safety, function, and
tractability. Completion always has a query scope. Clinical section completeness
can never exceed the parent evidence retrieval. Safety is a target annotation,
not a disease-specific safety evaluation. Unqueried tissue context is documented
as not assessed in the draft, not invented from other annotations.

`domain/dossier_validator.py` accepts structured claims. A model must label its
assertion kind; the validator does not infer that label from English. It checks
reference membership, selected entities, direct scope, exact-indication APPROVAL,
and explicit safety assertions. Presenting incorrect prose with a benign assertion
label can pass, as an explicit regression test demonstrates. Human scientific review
must evaluate claim entailment. Validator v0.2 rejects multiple source diseases
within a claim and requires every citation in a `direct_evidence` assertion to
be direct disease evidence. Target-level or descendant observations must be
separate claims. This narrow contract does not compare prose values with records.

`mcp/server.py` exposes precisely those two operations and keeps a server-local
packet registry. Clients supply handles, not replacement evidence packets. The
registry holds at most the two fixed snapshot cases. Pydantic return types generate
MCP output schemas. Tool errors cover malformed calls, unsupported identifiers,
and unknown handles; scientific contract violations return ValidationResult.

`cli.py` renders a few deterministic source observations and full packet JSON.
It does not synthesize a mechanism or target recommendation. The implemented agent
uses the same tools and schemas; no business rule should migrate into the server
or depend exclusively on a prompt.
