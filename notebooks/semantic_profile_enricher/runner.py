from __future__ import annotations

"""Runtime entry point for the semantic profile enrichment graph."""

from typing import Any

from .graph import build_semantic_enrichment_graph


class SemanticProfileEnricher:
    """Facade that compiles and executes the LangGraph enrichment pipeline."""

    def __init__(self) -> None:
        self.graph = build_semantic_enrichment_graph()
        self.app = self.graph.compile()

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Enrich a candidate payload and return the enriched JSON."""
        result = self.app.invoke({"raw_input": payload})
        return result["enriched_payload"]


def enrich_profile(payload: dict[str, Any]) -> dict[str, Any]:
    """Convenience function to enrich a candidate payload."""
    return SemanticProfileEnricher().run(payload)


if __name__ == "__main__":
    import json
    import sys

    raw_input = sys.stdin.read()
    if not raw_input.strip():
        raise SystemExit("Provide candidate JSON via stdin.")
    payload = json.loads(raw_input)
    enriched = enrich_profile(payload)
    json.dump(enriched, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")

