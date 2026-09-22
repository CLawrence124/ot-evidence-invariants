"""Check fixed raw-source observations independently of the production assembler.

This is NOT human verification or generated-dossier entailment scoring.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = json.loads((ROOT / "reference/ibd_nod2/reference_facts.json").read_text())


def pointer(value, path):
    for part in path.lstrip("/").split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


@pytest.mark.parametrize("fact", REFERENCE["facts"], ids=lambda f: f["id"])
def test_prespecified_source_fact(fact):
    for check in fact["checks"]:
        cassette = json.loads((ROOT / "fixtures/cassettes/26.06" / check["cassette"]).read_text())
        assert not cassette["response"].get("errors")
        actual = pointer(cassette["response"], check["pointer"])
        operation = check.get("operation", "equals")
        if operation == "length":
            assert len(actual) == check["expected"]
        elif operation == "contains":
            assert check["expected"] in actual
        else:
            assert actual == check["expected"]
