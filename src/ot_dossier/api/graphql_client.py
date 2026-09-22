"""Explicit opt-in capture; normal dossier generation never uses the network."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import httpx

ENDPOINT = "https://api.platform.opentargets.org/api/v4/graphql"
ROOT = Path(__file__).resolve().parents[3]
TARGETS = {"NOD2": "ENSG00000167207", "TNF": "ENSG00000232810"}
DISEASE = "MONDO_0005265"


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def request(client: httpx.Client, query: str, variables: dict) -> dict:
    """Three attempts for transport/429/5xx only; GraphQL errors stay visible."""
    for attempt in range(3):
        try:
            response = client.post(ENDPOINT, json={"query": query, "variables": variables})
            if response.status_code == 429 or response.status_code >= 500:
                response.raise_for_status()
            response.raise_for_status()
            body = response.json()
            if not isinstance(body, dict):
                raise ValueError("Expected a GraphQL JSON object")
            return body
        except (httpx.TransportError, httpx.HTTPStatusError) as exc:
            retryable = not isinstance(exc, httpx.HTTPStatusError) or exc.response.status_code == 429 or exc.response.status_code >= 500
            if not retryable or attempt == 2:
                raise
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def capture(destination: Path, page_size: int = 100, max_pages: int = 3) -> None:
    if not 1 <= page_size <= 100 or not 1 <= max_pages <= 10:
        raise ValueError("page_size must be 1..100 and max_pages 1..10")
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("Use a new empty directory; frozen cassettes are never overwritten")
    queries = ROOT / "src/ot_dossier/api/queries"
    with httpx.Client(timeout=30) as client:
        def save(name: str, query_name: str, variables: dict) -> dict:
            query = (queries / f"{query_name}.graphql").read_text()
            body = request(client, query, variables)
            cassette = {"format_version": 1, "endpoint": ENDPOINT,
                        "retrieved_at": datetime.now(timezone.utc).isoformat(),
                        "request": {"query": query, "variables": variables}, "response": body}
            (destination / f"{name}.json").write_text(json.dumps(cassette, indent=2) + "\n")
            return body

        entities = save("entities", "entities", {})
        data = entities.get("data") or {}
        if entities.get("errors") or not data.get("disease") or data["disease"]["id"] != DISEASE:
            raise ValueError("Entity resolution changed or failed; inspect entities.json before proceeding")
        for symbol, target in TARGETS.items():
            if data[symbol.lower()] != {"id": target, "approvedSymbol": symbol}:
                raise ValueError(f"Unexpected target identity: {symbol}")
            save(f"{symbol.lower()}_context", "target_context", {"target": target})
            cursor = None
            seen = set()
            for index in range(max_pages):
                body = save(f"{symbol.lower()}_evidence_{index}", "evidence",
                            {"disease": DISEASE, "targets": [target], "size": page_size, "cursor": cursor})
                disease = (body.get("data") or {}).get("disease") or {}
                page = disease.get("evidences") or {}
                next_cursor = page.get("cursor")
                if body.get("errors") or not page.get("rows") or not next_cursor:
                    break
                if next_cursor in seen:
                    raise ValueError("Upstream repeated a pagination cursor")
                seen.add(next_cursor)
                cursor = next_cursor
        after = save("entities_after", "entities", {})
        if after.get("errors") or (after.get("data") or {}).get("meta") != data["meta"]:
            raise ValueError("Release changed during capture; do not use this snapshot")
    manifest = {"format_version": 1, "max_pages": max_pages, "page_size": page_size,
                "release": data["meta"], "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(destination.glob("*.json"))}}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture public API responses into a NEW directory")
    parser.add_argument("destination", type=Path)
    parser.add_argument("--max-pages", type=int, default=3)
    args = parser.parse_args()
    capture(args.destination, max_pages=args.max_pages)
