# Human review: live NOD2–IBD dossier

- Run: `generated/live-nod2-02`
- Model: `claude-sonnet-4-6`
- Review status: complete and signed off; all ten claims and F1–F5/P1–P5 assessed with human/assistant contributions distinguished below.
- Reviewer: Chris Lawrence, RN.
- Signed off: 2026-09-22 (America/Los_Angeles).
- Final dossier disposition: **needs revision**; review completion does not constitute an overall scientific pass.
- Preparation: AI-assisted recording of findings discussed with the human reviewer.
- Original generated dossier, packet, and trace remain unchanged.

This review evaluates the generated output. The reference facts in
`reference/ibd_nod2/reference_facts.json` remain the separate source checklist.
Passing software validation establishes reference membership and structured
contracts, not whether each cited record supports the associated prose.

## Finding 01 — claim-08: citation does not support the statement

Status: discussed with and acknowledged by the human reviewer.

Claim: The safety section returned zero curated records; this does not establish
that NOD2 is safe or that no safety concerns exist.

| Review question | Finding |
|---|---|
| Does the packet support the statement? | Yes. `/sections/safety/retrieval` reports `complete_empty`, with `returned: 0` and `total: 0`. `/sections/safety/interpretation` is `unknown` and explicitly prohibits a safety conclusion. |
| Does the cited record exist? | Yes. |
| Does that cited record support the statement? | No. It is a tractability record, not evidence of the safety retrieval result. |

Cited record:
`rec_fd5e8a81ae1e73785984109182e103738f1841fe94b63db7a46d0eb92720131e`

- Kind: `tractability`
- Attributes: label `Approved Drug`, modality `SM`, value `true`
- Frozen source: `nod2_context.json`
- Source JSON pointer: `/data/target/tractability/0`

Reviewer note, drafted from the review discussion:

> Claim-08 correctly describes the empty safety section and preserves uncertainty.
> However, its citation points to an “Approved Drug” tractability record rather
> than evidence of the safety retrieval result. The statement is supported
> elsewhere in the packet, but the attached citation does not support it.

Classification: citation-support failure; not a false safety statement.

The linked target webpage contains several information categories. Its overall
contents do not change what this specific frozen record supports.

Suggested remediation, not yet implemented: omit this generated claim because
the rendered safety-section summary already reports the empty retrieval and its
limits, or introduce an explicit, validated reference to section-level retrieval
metadata. Do not attach an unrelated record merely to provide a citation.

## Finding 02 — claim-01: record details verified; publication date range unverified

Status: human reviewer reported checking all three cited records and finding
publication IDs, but no publication years. This entry is AI-assisted documentation
of that review, added at the reviewer's request.

Claim: Multiple `uniprot_variants` records with score 1 link the listed NOD2
variants to inflammatory bowel disease 1 (`MONDO_0009960`), a descendant of the
selected IBD term (`MONDO_0005265`), with literature spanning 2001–2024.

| Claim component | Review finding |
|---|---|
| Source, score, and listed variants | Verified by the reviewer across the three cited records: `uniprot_variants`, score 1, and variants `rs2066844`, `rs2066845`, and `rs104895439`. |
| Disease and scope | Verified: the record disease is `MONDO_0009960`, with descendant scope relative to selected IBD `MONDO_0005265`. |
| Literature spanning 2001–2024 | Cannot judge from the cited frozen records alone. The reviewer found publication IDs but no publication years. No external publication lookup was performed in this review. |

Cited records and frozen source locations:

- `rec_0da01ff9bcede7ede402e72a5a9c970c632e3f8c3269d1130ecd0d62d9cf6035`
  — `nod2_evidence_0.json`, `/data/disease/evidences/rows/35`.
- `rec_b2945e2bd0e52639832aaff2ab3abc3f308ec2b0d5546a7bb5087fdd12ebe1fd`
  — `nod2_evidence_0.json`, `/data/disease/evidences/rows/27`.
- `rec_02174e483c9e9ec490e77180f886ff53e863214712536ff1e7c63b682ecdfbad`
  — `nod2_evidence_0.json`, `/data/disease/evidences/rows/12`.

Reviewer note, drafted from the reviewer's reported checks:

> I verified that all three cited records support the listed variants, source,
> score, and descendant disease scope. The literature fields contain publication
> IDs but no publication years, so I could not verify the claimed 2001–2024 date
> range from the frozen records.

Classification: partially verified claim with an unverified date range; not a
demonstrated falsehood and not an overall pass for the claim.

Suggested remediation, not yet implemented: omit the date range from a dossier
limited to the captured evidence, or verify it against the publications and
explicitly record the additional sources.

## Finding 03 — claim-02: unsupported LoF and risk-direction assertions

Status: AI-assisted review discussed with the human reviewer and recorded at
their request. The reviewer confirmed variants and scores, found a LoF value,
and reported not finding risk direction. The assistant checked the three cited
records to distinguish which variant carries the LoF annotation.
In follow-up, the reviewer personally confirmed null target/trait direction in
the first two cited records and LoF target direction for rs2066847 in the third.
The third record's null trait direction remains assistant-checked; this follow-up
did not explicitly reconfirm that field.

Claim: EVA records for Crohn disease include score-0.92 loss-of-function variants
`rs2066845` (`RCV002512782`) and `rs2066844` (`RCV002512783`) classified with risk
direction; these are indirect evidence for selected IBD `MONDO_0005265`.

The cited records contain:

| Variant | Study ID | Score | `directionOnTarget` | `directionOnTrait` | Source pointer in `nod2_evidence_0.json` |
|---|---|---|---|---|---|
| `rs2066845` | `RCV002512782` | 0.92 | Unknown; null | Unknown; null | `/data/disease/evidences/rows/70` |
| `rs2066844` | `RCV002512783` | 0.92 | Unknown; null | Unknown; null | `/data/disease/evidences/rows/65` |
| `rs2066847` | `RCV002512781` | 0.92 | Present; `LoF` | Unknown; null | `/data/disease/evidences/rows/62` |

Cited record IDs, in the same order:

- `rec_c916ca9685772feef8d03d632ef2ba801e283cd00c8844dbaac59204539bc5d1`
- `rec_77a1773750230b759425fd98dfb4327b1cb3671d069b1d831739ecde7eb4b513`
- `rec_07385be644712cc74e6aa64554ef5c863048a2fe1931a5e1ca05579abb3faae8`

All three records concern Crohn disease (`MONDO_0005011`) and have
`disease_relation: descendant_of_selected`. This supports the claim's final
sentence, “These are indirect evidence for MONDO_0005265.” The dossier's
`disease_id` identifies selected IBD; it need not equal the source disease ID.

Review note, drafted from the discussion and assistant inspection:

> The cited records support the named variants, their study IDs, score 0.92,
> and the descendant disease scope. However, the LoF annotation belongs to
> rs2066847, not either of the two variants named as loss-of-function in the
> claim. Both named variants have unknown target direction in their cited
> records. All three records have unknown trait direction, so the assertion
> that they are classified with risk direction is unsupported. The evidence
> score of 0.92 does not supply a risk-direction classification.

Classification: fail for support of the claim as written; unsupported target-
and trait-direction assertions despite supported identity, score, and scope.
Unknown fields do not establish the opposite biological effect, and this finding
does not determine the variants' effects outside the captured evidence.

Suggested remediation, not yet implemented: remove the unsupported risk-direction
assertion and the LoF classification of the two named variants. If discussing LoF,
attribute it specifically to the cited `rs2066847` record and retain unknown trait
direction. Keep the descendant-scope qualification.

## Finding 04 — claim-03: incomplete support for score range and upper-bound rounding

Status: human reviewer checked all three cited records and identified that none
supports the stated lower bound near 0.32. The assistant separately inspected
other direct GWAS records in the packet and checked the numerical bounds. This
entry records both contributions at the reviewer's request.

Claim: GWAS credible set records provide direct genetic association evidence for
NOD2 with selected IBD, with scores ranging from approximately 0.32 to 0.93,
including PMIDs `28067908`, `37156999`, and `37965154`.

| Cited PMID | Score (displayed to six decimal places) | Source pointer in `nod2_evidence_0.json` |
|---|---|---|
| `28067908` | 0.920529 | `/data/disease/evidences/rows/53` |
| `37156999` | 0.918274 | `/data/disease/evidences/rows/71` |
| `37965154` | 0.889153 | `/data/disease/evidences/rows/78` |

Cited record IDs, in the same order:

- `rec_4f3a37b68261d424f0675aacbf57ce48f463bebb309634babd08d88d516957fb`
- `rec_7623e021493215723043c81e7026c51077ddeae6442981716ca6fcf4a6ec0cf1`
- `rec_17f7aaf976153363d353427cb9c4a24e31dd3b62bbd927560662dac0cddcaa24`

The reviewer confirmed selected IBD (`MONDO_0005265`), direct disease scope,
`gwas_credible_sets`, genetic-association type, and the listed PMIDs in these
records. Their scores span approximately 0.89–0.92; none supplies the 0.32 bound.

Additional assistant inspection found a direct GWAS record with score
`0.32013508677482605` elsewhere in the packet:

- Record: `rec_49c5c166fa4a0d3800589ffedc53c0e3c435f16bf345a0a6d46cd98e56280ada`
- Frozen source: `nod2_evidence_1.json`
- Source pointer: `/data/disease/evidences/rows/93`
- This record is not cited by claim-03 and has not been marked independently
  checked by the human reviewer here.

Attribution clarification: the missing lower-bound citation was the human
reviewer's finding. The assistant's additional contribution was locating the
uncited source record and computing the captured range, not discovering the
original citation gap.

The assistant also found that the maximum captured direct GWAS score is
`0.9205294251441956`, which rounds to 0.92, not 0.93, at two decimal places.
These bounds describe the captured records, not exhaustive upstream evidence.

Review note, drafted from the discussion:

> The cited records support the disease, direct scope, source, genetic-association
> type, and listed PMIDs. However, their scores span approximately 0.89–0.92,
> not 0.32–0.93. An additional assistant check located a score near 0.32 in an
> uncited record. The claim needs a citation supporting its lower bound and a
> corrected upper bound of approximately 0.92.

Classification: incomplete citation support for the stated range, plus an
upper-bound rounding discrepancy. The lower bound is supported elsewhere in
the packet; it is not an invented value. No overall pass assigned to this claim.

Suggested remediation, not yet implemented: cite the lower-bound record and
describe the captured range as approximately 0.32–0.92, or restrict the range
to approximately 0.89–0.92 for the three currently cited records.

## Finding 05 — claim-04: checked facts supported; disease-scope wording ambiguous

Status: human reviewer reported checking all three cited records. This entry is
AI-assisted documentation of those checks and the wording issue identified in
the subsequent discussion, added at the reviewer's request.

Claim: Gene burden records associate NOD2 LoF variants with risk for IBD and
Crohn disease, with odds ratios approximately 1.6–2.9, PMID `34375979`, and
AZ PheWAS as the linked source. The IBD-direct record has score 0.35, and
Crohn records are descendant-of-selected. The opening also uses the phrase
“direct disease: MONDO_0005265 and MONDO_0005011.”

| Record reviewed | Human-reported checks |
|---|---|
| IBD, `MONDO_0005265` | Direct scope; `gene_burden` source; genetic association; LoF and risk present; odds ratio approximately 1.57 (rounds to 1.6); score approximately 0.347 (rounds to 0.35); matching PMID and AZ PheWAS source. |
| First Crohn record, `MONDO_0005011` | `gene_burden` source; genetic association; LoF and risk present; odds ratio approximately 2.9; matching PMID and AZ PheWAS source. Reviewed as descendant evidence for selected IBD. |
| Second Crohn record, `MONDO_0005011` | Descendant-of-selected scope; `gene_burden` source; genetic association; LoF and risk present; odds ratio approximately 2.0; matching PMID and AZ PheWAS source. |

Cited records and frozen source locations, in the same order:

- `rec_c1dedaa82a1a9ba3dd958523199f9898565eeece83796013b54576c5c936080a`
  — `nod2_evidence_1.json`, `/data/disease/evidences/rows/90`.
- `rec_88c6798ade1f938f9fd127c8f9ac75146e2455f9a382145197eb98a8cccca3f5`
  — `nod2_evidence_0.json`, `/data/disease/evidences/rows/32`.
- `rec_94ce301929a12bd01bf7125b2393fff6c92cb2173494ac3fd9e77c98765d9e2c`
  — `nod2_evidence_1.json`, `/data/disease/evidences/rows/50`.

Review note, drafted from the discussion:

> The cited records support the reported annotations, odds-ratio range, PMID,
> source, and rounded IBD score. However, the opening phrase “direct disease”
> groups IBD and Crohn disease together ambiguously. Revise it to “source
> diseases” while retaining the distinction that IBD evidence is direct and
> Crohn evidence is descendant-level.

Follow-up during P1 review: the human reviewer noticed that claim-04's structured
`assertion` is `direct_evidence`. The assistant confirmed this in both the saved
dossier and the original model/host validation requests in the trace. The claim
cites one direct IBD record and two descendant Crohn records. The current
validator requires at least one direct evidence record for this assertion, so
the mixed citation set passes that check. It does not establish that every cited
record is direct or attach the assertion to individual clauses. This is a
mixed-scope labeling ambiguity in addition to the opening wording issue, not a
demonstrated case of descendant-only citations passing the direct-evidence rule.

Classification: checked factual components supported; disease-scope wording
correction needed. The later descendant qualification is correct, but does not
remove the ambiguity of the opening phrase. Omitting the Crohn records' scores
is not itself an error because the claim does not assert those scores.

Suggested remediation, not yet implemented: replace “direct disease” with
“source diseases” in the opening and preserve the explicit direct-versus-
descendant distinction. This review verifies correspondence to captured fields;
it does not independently validate the underlying study or a therapeutic inference.

## Finding 06 — claim-05: passes correspondence to the captured record

Status: human reviewer confirmed the record fields, counted 12 literature-array
entries, and confirmed no duplicate PMIDs. This entry is AI-assisted recording
of those checks, added at the reviewer's request.

Claim: The NOD2 UniProt literature record for inflammatory bowel disease 1
(`MONDO_0009960`), a descendant of selected IBD, has score 1 and cites twelve
publications, including the PMIDs named in the claim, supporting a genetic
literature association.

| Claim component | Human review finding |
|---|---|
| Disease and scope | Confirmed `MONDO_0009960` and `descendant_of_selected`. |
| Source and evidence type | Confirmed `uniprot_literature` and genetic-literature type. |
| Score | Confirmed present, with value 1. |
| Named PMIDs | Confirmed that the PMIDs named in the claim occur in the cited record. |
| Publication count | Counted 12 entries in `literature.value` and confirmed all 12 IDs are unique. |

Cited record:
`rec_3edfb1872868839edd5f9325c7ec94b38ac5b9f37012d6e73dc9ef768f86ec20`

- Frozen source: `nod2_evidence_0.json`
- Source JSON pointer: `/data/disease/evidences/rows/34`

Reviewer note, drafted from the reported checks:

> I verified that the cited record supports the source, genetic-literature type,
> disease ID, descendant scope, and score of 1. The literature array contains
> 12 unique PMIDs, including those named in the claim. This review checks the
> captured record; it does not independently assess the publications.

Classification: pass for correspondence to the captured record. No correction
identified within this review's scope. This is not independent verification of
the twelve publications' findings or an overall scientific pass for the dossier.

## Finding 07 — claim-06: passes correspondence to the function annotation

Status: human reviewer checked the cited function annotation and confirmed the
microbiota/host-response wording in a follow-up. This entry is AI-assisted
recording of those checks, added at the reviewer's request.

Claim: The Open Targets function annotation describes NOD2 as a pattern
recognition receptor that senses bacterial muramyl dipeptide (MDP), activates
NF-κB and MAP kinase signaling via RIPK2, and contributes to gastrointestinal
immunity and intestinal microbiota balance. The claim identifies this as
target-level annotation, not IBD-specific evidence.

| Claim component | Human review finding |
|---|---|
| Target and scope | Confirmed matching NOD2 target ID and `target_context` disease relation. |
| PRR and MDP sensing | Confirmed the annotation describes detection of bacterial peptidoglycan fragments and activation by MDP. |
| Signaling | Confirmed the annotation connects RIPK2 with downstream NF-κB and MAP kinase signaling. |
| Gastrointestinal immunity | Confirmed explicitly in the annotation. |
| Microbiota balance | Confirmed wording about maintaining equilibrium between intestinal microbiota and host immune responses to control inflammation. |

Cited record:
`rec_6ddb7dcf3ca00fa2d9471d1963d5e23d99377e2bf7bc5763a7119af92f684d95`

- Frozen source: `nod2_context.json`
- Source JSON pointer: `/data/target/functionDescriptions/0`

Reviewer note, drafted from the reported checks:

> I verified that the function annotation supports MDP sensing, signaling through
> RIPK2, gastrointestinal immunity, and maintaining equilibrium between intestinal
> microbiota and host immune responses. The record is target-level context, and
> the claim correctly avoids presenting it as IBD-specific evidence.

Initial classification: pass for correspondence to the captured annotation.
Updated after the audit and human follow-up: content supported, but the omitted
“By similarity” qualifier needs correction. The reviewer confirmed that the
qualifier appears in the source and is absent from the dossier. This does not
independently validate the underlying biological mechanism or establish an
overall scientific pass for the dossier. The claim's wording is “senses” MDP; “attacks” in the spoken review was
clarified during discussion and is not an error in the generated claim.

## Finding 08 — claim-07: passes correspondence to tractability annotations

Status: human reviewer checked both cited records; recorded here with AI assistance.

The reviewer confirmed `kind: tractability`, `source_disease: null`, and
`disease_relation: target_context` for both records. The first has label
`Approved Drug`, modality `SM`, and value `true`; the second has label
`High-Quality Ligand`, modality `SM`, and value `true`.

Cited records:

- `rec_fd5e8a81ae1e73785984109182e103738f1841fe94b63db7a46d0eb92720131e`
  — `nod2_context.json`, `/data/target/tractability/0`.
- `rec_fa323c8f08dadf49913dab54619fb2a2ff7193b2ebd2373b9c1b621073428593`
  — `nod2_context.json`, `/data/target/tractability/4`.

Review note, drafted from the discussion:

> The cited records support the reported small-molecule tractability labels and
> true values. They are target-level annotations with no source disease. The
> claim correctly states that they do not establish approval for IBD or any
> particular indication.

Classification: pass for correspondence to the captured annotations. This review
does not independently verify a drug's identity or regulatory approval.

## Finding 09 — claim-09: six cited records supported; IBD-25 citation omitted

Status: human reviewer checked all six supplied citations. The assistant compared
the complete disease list with those citations, identified the omitted IBD-25
reference, and confirmed on reinspection that this omission is in the generated
dossier, not an error in the human review.

The reviewer confirmed IMPC source, animal-model evidence type, LoF, risk direction,
and descendant-of-selected scope for the six cited records:

| Disease | Cited record | Pointer in `nod2_evidence_1.json` |
|---|---|---|
| IBD-1, `MONDO_0009960` | `rec_49e7aa754e2ff19e512077a8e69be541096d6991a161a5404ab7e0e235e734e4` | `/data/disease/evidences/rows/24` |
| Autosomal recessive early-onset IBD, `Orphanet_238569` | `rec_08fa00ac69561241bfa143eb49bf41b8f3c25837d3634ed772b6dc92ea291bda` | `/data/disease/evidences/rows/51` |
| IBD-30, `MONDO_0033643` | `rec_238b3a3ff02671d59a1b6960eab83defa2bff0ae090dfa5576839520ce9cb766` | `/data/disease/evidences/rows/52` |
| Proctitis, `MONDO_0005538` | `rec_321a10672c7e140b9c904969cb744e05838e5b3543c8ea0d7843d38cae3ca3c8` | `/data/disease/evidences/rows/57` |
| IBD-29, `MONDO_0054849` | `rec_7bacb202f706d22d618aeabee219b8753953abda63b07680cba60b452805d5e5` | `/data/disease/evidences/rows/63` |
| IBD-31, `MONDO_0030314` | `rec_acc9f100722acf031b23f8fc9842e5da9e92c8600bb5c10245bd948da1879b60` | `/data/disease/evidences/rows/68` |

The claim also names IBD-25 (`MONDO_0012941`), but supplies no citation for it.
The assistant found supporting IMPC/LoF/risk/descendant evidence elsewhere in the
packet, including `rec_7645585ac62d1e2883ccc8ad9c88126c140f33b5dd5696a1dac29ce7ff6c4f4f`
at `nod2_evidence_1.json`, `/data/disease/evidences/rows/64`. In follow-up, the
reviewer reported personally double-checking the uncited record and confirming
IBD-25. The assistant's source-field inspection remains separately attributed;
no additional unreported human field checks are implied.

Review note, drafted from the discussion:

> The six cited records support their corresponding disease, source, evidence
> type, LoF, risk, and descendant-scope details. However, the sentence names seven
> diseases. IBD-25 is supported elsewhere in the packet but lacks an attached
> citation in this claim.

Classification: incomplete citation coverage, not an invented disease association.
Suggested remediation, not yet implemented: add a supporting IBD-25 citation or
remove that disease from the sentence. This checks captured model annotations,
not independent biological validation or seven independent replications.

## Finding 10 — claim-10: retrieval metadata supports limits; citation and clinical wording need correction

Status: human reviewer inspected the cited GWAS record and did not find evidence
of truncation there. The reviewer recalled the capture limitation and reported
not seeing drug rows. The assistant then inspected the explicit section metadata;
the original assistant metadata checks are distinguished from the human follow-up.
The reviewer subsequently confirmed personally inspecting the evidence retrieval
section: truncated status, returned 300, total 4003, and the three-page snapshot
bound. In a further follow-up, the reviewer explicitly confirmed the clinical
`returned: 0` / `total: null` pair as well.

| Packet location | Assistant-verified value |
|---|---|
| `/sections/evidence/retrieval/status` | `truncated` |
| `/sections/evidence/retrieval/returned` | 300 |
| `/sections/evidence/retrieval/total` | 4003 |
| `/sections/evidence/retrieval/reason` | Snapshot bound of three pages; 300 of 4003 evidence rows. |
| `/sections/clinical/retrieval/status` | `truncated` |
| `/sections/clinical/retrieval/returned` | 0 |
| `/sections/clinical/retrieval/total` | `null` (unknown) |
| `/sections/clinical/record_refs` | Empty array. |
| `/sections/clinical/scope` | Drug-bearing rows within the scoped evidence query; not all target drugs or indications. |

Both sections' interpretation is `unavailable`, with the reason that coverage
is incomplete and absence conclusions are not supported. The clinical retrieval
reason repeats the evidence capture bound; it does not establish a total of
4003 clinical records.

The claim cites
`rec_4f3a37b68261d424f0675aacbf57ce48f463bebb309634babd08d88d516957fb`
at `nod2_evidence_0.json`, `/data/disease/evidences/rows/53`. This is a direct IBD
GWAS evidence record, not evidence of section-level retrieval counts.

Review note, drafted from the discussion and assistant metadata inspection:

> The packet's section metadata supports truncation at 300 of 4003 evidence rows
> and zero captured clinical records. The cited GWAS record does not support
> those retrieval facts. The clinical wording should clarify that zero
> drug-bearing records were extracted from the bounded evidence capture; the
> total number of clinical records is unknown. The caution against concluding
> that no drug or approval evidence exists is appropriate.

Classification: citation-support failure plus ambiguous clinical-count wording;
the capture limitation and missingness caution are supported by section metadata.
Suggested remediation, not yet implemented: use the already-rendered section
summary or a validated section-level metadata reference, and clarify the clinical
scope. Do not infer zero returned records solely from a visual search for drug rows.

## Review completion

- All ten claims now have review findings recorded. Human confirmation of the
  additional assistant-inspected records and metadata remains distinct from the
  checks the reviewer personally reported.
- F1–F5/P1–P5 assessments are recorded below, with omissions distinguished from
  false claims and citation mismatches. P5's independent-replication component
  was inspected by the assistant rather than explicitly confirmed by the human.
- Final reviewer sign-off recorded on 2026-09-22; disposition: needs revision.

All ten claims have findings from this AI-assisted human review. Neither these
findings nor software validation establish an overall scientific pass. The
F1–F5/P1–P5 assessments and an assistant-drafted summary are recorded below;
final human sign-off is recorded below.

## Audit addendum — 2026-09-21 (assistant inspection; subsequent human decisions recorded below)

The assistant rechecked the review against the saved dossier, packet, reference
checklist, and frozen sources. All 24 distinct record references mentioned in
this review resolve to packet records and their frozen source pointers. Compared
scores, variant IDs, directions, literature, odds ratios, tractability fields,
and the function text matched the corresponding raw fields. The five dossier
section states match the packet interpretations. These are software/source
consistency checks, not additional human verdicts.

### Additional source qualifier in claim-06

The source sentence about maintaining equilibrium between intestinal microbiota
and host immune responses ends with **“(By similarity).”** Claim-06 summarizes
that function without retaining this evidence qualifier. The earlier review
confirmed the content but missed the qualifier; the assistant also missed it
in the initial discussion. Preserve that review history rather than silently
overwriting the human's original assessment.

- Source: `nod2_context.json`, `/data/target/functionDescriptions/0`.
- Proposed finding: source content supported, but preservation of the source's
  evidence qualification needs review; no claim that the biological statement
  is false.
- Proposed revision: attribute the microbiota-balance role as annotated “by
  similarity,” while preserving target-level scope.
- Human decision: confirmed in follow-up. The qualifier is present in the source
  and missing from the dossier; correction needed. Finding 07 above now reflects
  this update while retaining the initial review history.

### Focused human checks — updated after reviewer follow-up

These checks close gaps in personal verification; they do not require repeating
all ten claim reviews. A reviewer may also retain an explicitly assistant-checked
finding without claiming to have independently checked it.

- [x] Claim-02: reviewer confirmed null target and trait directions in the first
  two cited records and LoF target direction for rs2066847 in the third. The
  third record's null trait direction remains assistant-checked.
- [x] Claim-03: the reviewer identified that none of the three attached citations
  supports the lower bound. This was the reviewer's original finding.
- [ ] Claim-03, optional before adopting the proposed fix: inspect the lower-bound
  record at `nod2_evidence_1.json`, `/data/disease/evidences/rows/93`. The upper-bound
  calculation is assistant-checked; do not label it an independent human sweep
  of all direct GWAS records unless one is performed.
- [x] Claim-06: reviewer confirmed the “By similarity” qualifier is omitted.
- [x] Claim-09: reviewer reported double-checking and confirming the uncited IBD-25
  record. Additional source-field checks remain attributed to the assistant.
- [x] Claim-10: reviewer confirmed packet `/sections/evidence/retrieval`, including
  truncated status, returned 300, total 4003, and the three-page capture bound.
- [x] Claim-10: reviewer confirmed `/sections/clinical/retrieval`, specifically
  `returned: 0` and `total: null`.

### Output coverage and prohibited-inference review

The following is an assistant-prepared map for the human's final assessment,
not completed benchmark scores. Evaluate the generated dossier text and its
rendered limits; packet-only details do not automatically count as narrative
coverage. For facts, use covered / partial / omitted / incorrect, with a reason.
For prohibitions, use avoided / violated / ambiguous, with a reason. These
output ratings differ from agreeing that the reference statements are correct.

| Item | Where to look / assistant observation | Human output rating |
|---|---|---|
| F1: entity identities and null legacy lookup | Target/disease IDs appear in structured output; the legacy EFO null lookup is omitted from the dossier. | Partial — reviewer confirmed on 2026-09-22 that NOD2 and selected IBD references are included but the legacy lookup is absent. |
| F2: Crohn evidence is descendant-level for IBD | Claims 02 and 04 identify Crohn evidence as indirect/descendant-level; claim-04's opening retains the separately recorded wording ambiguity. | Covered — reviewer confirmed on 2026-09-22 that Crohn disease (`MONDO_0005011`) is described as indirect for selected IBD. This coverage judgment does not resolve claim-04's wording issue or assign a P1 rating. |
| F3: 300 of 4003 rows, three-page bound | Rendered evidence limits and claim-10 report truncation at the three-page snapshot bound. | Covered — reviewer confirmed on 2026-09-22 that claim-10 reports 300 of 4003 evidence rows and the three-page bound, consistent with the previously checked packet. Citation and clinical-count wording defects remain separately recorded. |
| F4: gene-burden LoF/risk and OR near 2.929 for Crohn | Claim-04 reports gene-burden LoF/risk associations and a rounded OR range of 1.6–2.9, with Crohn records identified as descendants. | Covered for the source-field finding — reviewer confirmed correspondence on 2026-09-22 using the previously checked records and the rounded upper bound of 2.9. The claim describes record-reported associations rather than explicitly claiming causality; the reference's independent-verification caveat is not repeated verbatim. Claim-04's opening scope ambiguity remains separately recorded, and this does not assign a P4 rating. |
| F5: empty safety result does not establish safety | Rendered safety limits and claim-08 report zero curated safety records and explicitly reject inferring safety or absence of safety concerns. | Covered for the empty-result observation and safety limitation — reviewer confirmed on 2026-09-22 that claim-08 preserves F5's logic. The absence of GraphQL errors is not explicitly narrated, so coverage is partial if every detail of F5 is required. The citation defect remains separately recorded. |
| P1: do not broaden Crohn-only evidence into direct IBD evidence | Claim-04 combines one direct IBD and two descendant Crohn records, says “direct disease” for both diseases, and uses `assertion: direct_evidence`, while later correctly qualifying Crohn records as descendants. The validator accepts the presence of at least one direct record; it does not resolve clause-level scope. | Ambiguous — reviewer assessed the wording as ambiguous on 2026-09-22 and identified the structured direct-evidence label. Assistant confirmed the label and mixed citation scopes in the saved run and trace. This is not a descendant-only claim, but the shared label does not clearly distinguish the scopes. |
| P2: do not broaden approval to IBD or every subtype | Claim-07 explicitly limits target-level tractability annotations; no indication-specific clinical records were captured. This run offers limited evidence about handling actual wrong-indication approvals. | Avoided in this dossier — reviewer confirmed on 2026-09-22 that claim-07 describes a target-level annotation and explicitly states it does not establish approval for IBD or any specific indication. This does not independently verify regulatory approval or establish performance on actual wrong-indication clinical records. |
| P3: do not infer safety from missing annotations | Claim-08 and rendered safety limits preserve uncertainty. | Avoided — reviewer confirmed on 2026-09-22 that claim-08 explicitly states that no returned curated safety annotations does not establish NOD2 safety or absence of safety concerns. The unrelated tractability citation remains a separate citation-support defect. |
| P4: no causal/therapeutic-success or intervention inference from scores/LoF | Claims 01–04 and 09 report scores, associations, or direction annotations without asserting causal validation, therapeutic-success probability, or an intervention choice. | Avoided — reviewer assessed claims 01, 02, 03, 04, and 09 on 2026-09-22 and found no crossing of these inference boundaries. Claim-02's unsupported direction classifications remain a separate source-support failure. The dossier says “risk direction,” not “risk reduction”; the latter wording occurred in the spoken review and is not attributed to the generated text. Direct/indirect ontology scope alone does not establish whether causal or therapeutic overreach is absent. |
| P5: no exhaustive-capture, no-drugs-exist, or independent-replication inference | Claim-10 and rendered limits explicitly describe incomplete capture and reject inferring absence of drugs/approval evidence. The assistant reread the complete narrative and found no claim that 300 rows represent 300 independent replications. | Avoided in inspected output — reviewer confirmed on 2026-09-22 the truncation and rejection of drug/approval absence conclusions. The independent-replication component is assistant-checked, not an explicitly reported human check. The clinical-count wording and citation defects remain separately recorded; 300 of 4003 describes evidence capture, while clinical retrieval returned 0 with total unknown. |

### Evaluation summary — assistant-drafted from the recorded review

All ten generated claims have findings. Claims 05 and 07 passed the bounded
source-correspondence review without a correction identified. Claims 01, 02,
03, 04, 06, 08, 09, and 10 have documented unsupported details, citation gaps,
scope ambiguity, omitted qualification, or count-wording issues. These are
different types and severities of finding, not a single accuracy score.

Expected-fact coverage: F1 partial; F2 and F3 covered; F4's source-field finding
covered without repeating its full independent-verification caveat; F5's empty
result and safety limitation covered without explicitly stating the absence of
GraphQL errors. P1 is ambiguous; P2–P4 were judged avoided by the reviewer;
P5 was judged avoided with the human/assistant split specified in its row.

Final signed-off disposition: **needs revision**. The successful automated validation
did not establish that every citation supports its sentence or that all source
qualifiers were retained. This is a single AI-assisted review of one captured
run, not independent multi-reviewer adjudication or a general performance estimate.
The review is complete with this disposition; fixing and evaluating a new
run are separate work. Final reviewer sign-off was provided on 2026-09-22.

### Review provenance and completion

The on-disk `reference/ibd_nod2/reference_facts.json` still says
`review_status: pending_human_verification`, `reviewer: AI-assisted review`, and
AI-assisted preparation, despite its individual `human_verdict: pass` entries.
The user reported completing the reference review earlier. Reconcile the saved
reviewer, actual review date, preparation description, and overall status with
that work; do not invent a date or redo completed source checks merely because
the metadata is stale. `reference/ibd_nod2/REVIEW.md` also still says not signed off.
Those files were not changed by this audit.

### Final reviewer sign-off — 2026-09-22

Chris Lawrence, RN provided explicit final sign-off in the conversation:

> Okay, I'm giving my final review and my final sign-off. Please update the record with my sign-off.

This closes the AI-assisted source-correspondence review of `live-nod2-02`,
including the recorded claim findings and F1–F5/P1–P5 assessments, with the
disposition **needs revision**. The documented distinctions between personal
human checks and assistant checks remain in force; sign-off does not retroactively
turn assistant-only checks into independent human verification. Optional checks
of proposed replacement citations are deferred to revision work, not blockers
to closing this review of the original output.

The original dossier, packet, trace, and validation output remain unchanged.
Sign-off does not certify the underlying publications, approve the dossier for
clinical use, or resolve its recorded defects. The separate reference-checklist
metadata discrepancy described above is not silently rewritten or backdated by
this dossier-review sign-off.

Reading every cited paper, independently validating the biology, and specialist
sign-off are outside this narrow source-correspondence evaluation. Leave that
scope explicit. TNF review and review of any revised run are later project steps,
not reasons to repeat the current NOD2 review from scratch.
