# What the current result establishes

The code preserves defined structural invariants and catches the four tested
faults. It does not prove the correctness of upstream data, cure hallucinations,
or infer whether arbitrary prose is supported by cited records.

Both disease-evidence captures stop after 300 rows. They are not random samples,
complete evidence inventories, or suitable for ranking targets. Empty clinical
subsets cannot establish absence of trials or drugs. A target safety query is
complete only relative to the requested API annotation; it is not a systematic
safety review. Source scores and evidence counts are not probabilities or
independent replications.

The Phase 1 clinical adapter uses drug-bearing disease evidence. It retains exact
source indications, stage labels, and target-matched mechanisms. It does not
retrieve all target drugs or independently verify regulatory status against a
regulator. `APPROVAL` means the captured source reports APPROVAL for that indication;
`PHASE_4` is not converted to APPROVAL. Ontology ancestry does not broaden approval.

The NOD2 reference case was AI-prepared from inspected raw JSON and reviewed by
Chris Lawrence, RN. Source-review metadata was reconciled on September 22, 2026;
the exact original review date remains null, and prior metadata is retained. A live
NOD2 baseline was reviewed as **needs revision**. The subsequent live-nod2-06
run also contained three confirmed error-bearing claims; a separate corrected
derivative was signed off on 2026-09-22. Frozen
expectations are regression checks, not a held-out benchmark. Revisions informed
by that output must be reported as development on the same case, not held-out
evaluation. TNF remains a second-target smoke test, not an unbiased benchmark.

The revision enforces single-source-disease claims and stricter direct citations.
Scalar prose support, citation coverage of every named item, publication years,
and source qualifiers remain prompt-guided and human-reviewed. Even an unrelated
tractability citation on a safety sentence can still pass if labeled
`retrieved_fact`; an explicit test preserves this limitation. The host renders
retrieval summaries from section metadata, but it cannot guarantee that a model
will obey instructions to omit duplicate retrieval claims.

Before interpreting genetics, learn the difference between variant association,
gene assignment, gene-burden evidence, molecular effect, and pharmacological
intervention. A statistical genetics reviewer should review those interpretations.
A drug-discovery reviewer should assess target plausibility, modalities, tissue
context, and translational limitations. Neither clinical experience nor this
schema alone supplies that expertise. Specialist review is recommended for these
interpretations, not claimed completed or expanded into a v1 review panel.

The repository checkout is the supported runtime: fixtures and skill files live
beside the source. Wheel-only deployment, authentication, remote transport, and
multi-user operation are not implemented. MCP uses the tested supported v1 SDK
line; future migration to v2 requires rerunning the contract tests.
