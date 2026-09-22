# Scope notes from the captured API

The entity query resolves inflammatory bowel disease to MONDO_0005265 and NOD2
to ENSG00000167207. The legacy EFO_0003767 lookup returns null in this capture.
Crohn disease MONDO_0005011 appears in the selected disease's descendant list.
This membership is captured directly, not inferred from similar names. See
`entities.json` and the frozen `entities.json` cassette.

The evidence query explicitly requests `enableIndirect: true`. Each row retains
`disease.id` and `disease.name`; `diseaseFromSource*` fields retain additional raw
source labels/mappings where available. The assembler classifies the row's
resolved `disease.id`: selected ID means direct; a frozen descendant ID means
descendant_of_selected. It rejects unexpected out-of-scope disease evidence.
Within the first 300 NOD2 rows, 31 are direct and 269 are descendants. This is an
observation about the captured subset, not the whole 4,003-row result.

Clinical indications use the same exact disease labels. Descendant membership
does not promote approval to the parent indication. Target annotations have
target_context scope rather than direct disease scope. NOD2's empty safety list
has complete_empty retrieval and unknown interpretation; evidence and clinical
sections are truncated and carry unavailable interpretation. No absence of
clinical development or evidence of safety is inferred from these responses.
