# Revised NOD2 dossier review — live-nod2-06

Status: original output retains confirmed C001, C004, and C006 errors. The separate corrected derivative was signed off by Chris Lawrence, RN on 2026-09-22; this does not mark the original output as passing.
Preparation: assistant inspection of saved output and packet; not independent biological validation.
Baseline: `generated/live-nod2-02`, with signed review in `evaluations/live-nod2-02/review.md`.

## Run verification

Completed with two generation requests, two MCP tool calls, zero repairs, 63,391 input tokens and 1,341 output tokens. Validation reports valid with no findings. Packet ID matches the baseline. These checks do not establish claim support.

## Baseline comparison — preliminary assistant observations

- Baseline mixed direct/descendant gene-burden claim is now split into C003 and C006.
- EVA C005 now names rs2066847 with its own LoF annotation and does not assert a known trait direction.
- GWAS C001 now cites both approximately 0.32 and 0.92 endpoints, but also includes a gene-burden citation despite describing GWAS evidence.
- Safety and retrieval limits are host-rendered from section metadata rather than generated claims with unrelated citations.
- The publication-year range, microbiota-balance sentence, and multi-disease IMPC list are omitted. Omission is not proof of corrected synthesis of those details; assess coverage separately.

## Priority checks

### C004: named variant and attached citations

The text names rs2066847, but the cited variant records list rs2066845, rs2066844, rs5743276, and rs2076754. The fifth citation is uniprot_literature with no variantRsId. Confirm the named variant is unsupported by this citation set and assess the extra source-type mismatch.

Human finding — Chris Lawrence, RN: confirmed that rs2066847 is not supported by C004's cited records. The named variant needs an appropriate supporting citation or removal from the claim. This confirmation addresses the missing variant citation; the extra source-type mismatch and remaining claim components are still pending human assessment.

### C006: odds-ratio lower bound

The text says approximately 1.92–2.93. The cited records report:

| Reference | Odds ratio | Frozen source pointer |
|---|---:|---|
| `rec_88c6798ade1f938f9fd127c8f9ac75146e2455f9a382145197eb98a8cccca3f5` | 2.9291000366210938 | `nod2_evidence_0.json` → `/data/disease/evidences/rows/32` |
| `rec_94ce301929a12bd01bf7125b2393fff6c92cb2173494ac3fd9e77c98765d9e2c` | 2.001800060272217 | `nod2_evidence_1.json` → `/data/disease/evidences/rows/50` |
| `rec_a0b081a7350e673c83ae949b526d148dc8c1b24c456f83291986c52ce1185cac` | 1.9215999841690063 | `nod2_evidence_1.json` → `/data/disease/evidences/rows/27` |
| `rec_a24846e9448a6b80f62e50aba8962413d1b3c3aa8fc293a5eb077f3d502c333a` | 1.9431999921798706 | `nod2_evidence_0.json` → `/data/disease/evidences/rows/95` |
| `rec_e04c1edd62e0ba7d64c46a63b3899b10342ea51160f77cbbc5803b26ae949b2e` | 1.9050999879837036 | `nod2_evidence_0.json` → `/data/disease/evidences/rows/99` |

The minimum cited value is 1.9050999879837036, which rounds to 1.91 at two decimals. Confirm whether the stated lower bound needs correction.

Human finding — Chris Lawrence, RN: confirmed that the cited value does not round to 1.92. The lower bound needs correction to 1.91 at two decimal places. This confirmation addresses the numeric lower bound, not the remaining components of C006.

### C001: source consistency

One attached record is gene_burden, while the sentence describes GWAS credible sets: `rec_c1dedaa82a1a9ba3dd958523199f9898565eeece83796013b54576c5c936080a`, `nod2_evidence_1.json`, `/data/disease/evidences/rows/90`. The range endpoints are supported by other attached GWAS records; assess this extraneous citation separately.

Human finding — Chris Lawrence, RN: confirmed that this cited record's source is gene_burden, not GWAS. C001 needs correction to align its citations with the source described in the claim. This confirmation addresses the source mismatch; the remaining claim components are still pending human assessment.

## C002 assistant pre-check — human assessment pending

Human spot-check — Chris Lawrence, RN: inspected the first cited record (`rec_02e783bfc42b1b8cabb6417739ad755a5da169680279569e17b2aa03e8f4c95f`) and confirmed the source disease, direct disease relation, datasourceId, and reviewed fields were correct. This is a human spot-check of one record; the complete 17-citation check below remains assistant-performed. Direct scope here means the source disease ID matches the selected IBD ID. Acceptance of the proposed wording revision remains pending.

All 17 cited references exist and are unique. Every cited record has target ENSG00000167207, selected disease MONDO_0005265, direct disease relation, source europepmc, and datatype literature. Each has a present, nonempty literature list; together they contain 17 distinct literature identifiers. Target, disease, datasource, datatype, mapped disease ID, and literature fields were also checked against each frozen cassette row at its provenance pointer; all matched.

Assistant assessment: supported as a description of the captured literature records. This does not verify the underlying papers' conclusions, peer-review status, study independence, or causality. “Direct” describes an exact disease-term match in this project, not direct experimental proof. One literature identifier is PPR32979; do not describe all identifiers as numeric PMIDs or infer that all publications are peer reviewed from this packet.

Suggested focused human review: inspect one representative cited record and judge whether “direct literature evidence links NOD2” stays within this limited source-record meaning. Prefer clearer wording such as “Captured Europe PMC literature records map NOD2 to the selected IBD term and contain multiple distinct literature identifiers.” No need to manually re-count all 17 citations; document reliance on the assistant pre-check and any spot-check, rather than marking all rows independently human verified.

| Citation | Literature identifier | Frozen source location (zero-based index) |
|---|---|---|
| `rec_02e783bfc42b1b8cabb6417739ad755a5da169680279569e17b2aa03e8f4c95f` | PPR32979 | `nod2_evidence_1.json` row index 83 |
| `rec_08a75328f56d7f3d932ad63ffbf175ee5df1b145d0e522ed20d20d9d6e258b5e` | 22742424 | `nod2_evidence_1.json` row index 84 |
| `rec_38470f82c89fe1416e59d6c2fc16b11c6e7e135cbb14ad5d0b376d10ef0e5ef1` | 35002226 | `nod2_evidence_1.json` row index 15 |
| `rec_3943c4a8dcbf938652da208a22f7eb6ca82391c3db95adfde91e6eaf4c820d41` | 37080976 | `nod2_evidence_1.json` row index 30 |
| `rec_48d66d5a7d897932053bf0f9c6f2751e50aed38fadf6dfbfa8ce2aafb23731f8` | 30818349 | `nod2_evidence_1.json` row index 66 |
| `rec_4bd3c82bdf026e9896c4684c5c79a0470d1a49dada8392db2c82686c2d6f4ff5` | 22719818 | `nod2_evidence_1.json` row index 59 |
| `rec_6ed3f25ad5c4ea4328c963810ea3d3a89b70f9156235a1565964661158fdfbcc` | 37229767 | `nod2_evidence_1.json` row index 28 |
| `rec_76e16c64d7def849d4a4e9b29c65e917c8f999605dbe066269c59ac5c1130b9c` | 30849075 | `nod2_evidence_1.json` row index 89 |
| `rec_977a36f5a97cd40e2d3344151730d2e725895209b98a722cf949f75c1b547a9f` | 34758847 | `nod2_evidence_1.json` row index 60 |
| `rec_9c4187d6a86f5def7247d6680fbb730b2d941af727865f2807cd33c2b6616fae` | 22269043 | `nod2_evidence_1.json` row index 72 |
| `rec_9d4674fc0c404f75c1588f59d7cd43d234b71eeb5328254e9cc84aa8aee99c36` | 39358938 | `nod2_evidence_1.json` row index 55 |
| `rec_a98a3285852b628af98786779c25b358d42eae0d77f294d54a68984a197cd8ff` | 30430799 | `nod2_evidence_1.json` row index 21 |
| `rec_adfa764e340d41cc58e83e371a324d4ac915535120be689ad877970a22f381a6` | 16840031 | `nod2_evidence_1.json` row index 78 |
| `rec_bb86c645c70e9c2b83ccad2d076c9642761f02215e6b416668da29a8a94d26af` | 26167078 | `nod2_evidence_2.json` row index 55 |
| `rec_c7451905971e5df80a5f2df9c26d13dca1baa17d070121b002399d6c6aa5d6ca` | 17570063 | `nod2_evidence_1.json` row index 77 |
| `rec_d83efa6b3401b2812b2f452118c058c321949c8479ee5fdd9fb5e4bbefbc6b4d` | 21218092 | `nod2_evidence_1.json` row index 82 |
| `rec_f98da3f6ddc4a04c628e4afbe705fd6ddd2d11b36523d88b16bd031631490803` | 33692434 | `nod2_evidence_0.json` row index 13 |

## Review tracker

A separate assistant-edited derivative is available in [corrected/dossier.md](corrected/dossier.md), with [changes and coverage assessment](corrected/review.md). The original model output remains unchanged and retains the errors documented here. Chris Lawrence, RN signed off on the corrected derivative and disclosed coverage limits on 2026-09-22; this is not a new generation or an unassisted model success.

Human assessments are recorded below as received; other checks remain pending. Existing baseline source checks can be reused; this review checks the new output and its citation choices.

| New claim | Human assessment |
|---|---|
| C001 | Needs correction: human confirmed the attached gene_burden record does not match the described GWAS source; remaining components pending |
| C002 | Assistant checked all 17 citations against packet and frozen rows; human confirmed first-record spot-check; proposed wording revision pending |
| C003 | Human confirmed all reviewed fields are accurate (Chris Lawrence, RN; confirmation interpreted as C003 following the explicit transition to this claim) |
| C004 | Needs correction: human confirmed the named rs2066847 variant is not supported by attached citations; remaining components pending |
| C005 | Human confirmed the listed checks are correct: rs2066847, eva source, LoF direction on target, score approximately 0.92, and Crohn's disease as descendant_of_selected (Chris Lawrence, RN). |
| C006 | Needs correction: human confirmed the cited lower value does not round to 1.92; remaining components pending |
| C007 | Human confirmed the current claim is accurate and its citation supports MDP sensing from bacterial peptidoglycan, NF-kappa-B/MAP kinase signaling, and gastrointestinal immunity (Chris Lawrence, RN). Human also confirmed the previous inflammation/microbiota statement carrying the "by similarity" qualifier is omitted; this resolves that omission-of-qualifier issue by removing the affected statement, not by retaining a qualified version. |
| C008 | Human confirmed SM Approved Drug = true, SM High-Quality Ligand = true, AB Approved Drug = false, and OC Approved Drug = false, and confirmed these are target-level annotations rather than approval for IBD (Chris Lawrence, RN). |

After assessing the eight claims, check factual coverage and prohibited inferences using the existing reference checklist, focusing on changed or omitted content. Record new errors as well as improvements; do not transfer the baseline sign-off. Keep generated files unchanged.
