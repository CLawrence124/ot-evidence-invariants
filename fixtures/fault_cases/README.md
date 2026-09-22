# Synthetic faults

Faults are in-memory mutations of copies of frozen fixtures, never edits to the
real cassettes. `tests/unit/test_contracts.py` implements four named cases:

1. Retain only a descendant evidence row, then assert direct evidence.
2. Relabel a clinical record to `SYNTHETIC_UNRELATED`, set APPROVAL, and assert
   approval for selected IBD. This is fabricated test data, not a biomedical fact.
3. Remove TNF safety rows, then assert the target is safe.
4. Cite `rec_nonexistent`.

The fault definitions are executable tests rather than duplicated JSON fixtures
that could drift. The real cassette checksums remain unchanged.
