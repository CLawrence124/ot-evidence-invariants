# Scientific interpretation rules

- A record's source disease remains explicit. Descendants of IBD are indirect
  evidence for the selected parent; they do not become direct by changing prose.
- Drug, target-matched mechanism, indication, stage, and provenance stay together.
  Source-reported APPROVAL for Crohn disease or an unrelated indication does not
  establish approval for the selected IBD term or every subtype. PHASE_4 is not
  silently converted to APPROVAL.
- Unknown means queried but no value established. Not assessed means interpretation
  or a question was not evaluated. Unavailable means failed/incomplete retrieval
  prevents a conclusion. Not applicable needs an explicit justification.
- An empty safety annotation says no curated records returned under that query.
  It does not establish safety. Partial/truncated retrieval cannot support absence
  claims. Complete-empty still applies only to the specified source/query.
- Association scores are not probabilities of therapeutic success. Genetic
  association is not causal target validation. Genetic direction alone is not a
  recommendation to inhibit or activate a protein.
- Target-level tractability is not disease efficacy; baseline expression is not a
  disease mechanism. Tissue context is not assessed by the current queries.
- Records may overlap. Do not treat row count as independent replication.
- Cite only references in the packet. Read their source disease and attributes;
  reference membership does not establish entailment. Human review must assess
  support, mechanistic overreach, conflicting evidence, and missing context.

## Clause-level source checks before submission

- Keep variant identity, score, directionOnTarget, directionOnTrait, odds ratio,
  and study identifier attached to the same record. Never transfer LoF or risk
  from a nearby record to a named variant whose direction is unknown. LoF is
  target direction; risk is trait direction; neither can be inferred from score.
- Every named disease, variant, and publication ID must be supported by an attached
  citation. Prefer fewer examples if a long list cannot be fully supported.
- For a numerical range, cite both endpoints, specify the source disease and
  captured subset, and round consistently. A matching value elsewhere in the
  packet does not repair a missing citation. Do not present a subset's range as
  the range of all captured records without checking all relevant records.
- Publication IDs do not encode publication years. Omit date ranges unless the
  cited records explicitly supply those dates; do not infer them from memory.
- Preserve evidence qualifications attached to the summarized source sentence,
  including “By similarity,” “may,” and “predicted.” Attribution to an annotation
  does not justify removing its qualification. Do not upgrade these to proof in
  humans or to IBD-specific mechanisms.
- Report tractability as the source's annotation label and value, retaining the
  target-level limit. An “Approved Drug” flag is not independently verified
  regulatory approval, and does not establish an indication.
- Retrieval counts and missingness belong to section metadata, not individual
  study records. The host renders those summaries directly. A clinical total of
  null remains unknown even when the evidence query reports a numeric total.

These checks guide synthesis; the validator does not parse arbitrary prose to
prove compliance. Human review remains necessary after structural validation.
