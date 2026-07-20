"""
IntelGraph — Search demo.

Performs a semantic search against the 'intelgraph' collection using
a natural-language query and pretty-prints the results.

Documentation references:
    client.points.search():
        https://docs.vectoraidb.actian.com/docs/fundamentals/search/basic-search-task
        Signature: client.points.search(collection, vector=..., limit=..., with_payload=True)
        Returns: list of results, each with .id, .score, .payload

    with_payload parameter:
        https://docs.vectoraidb.actian.com/docs/fundamentals/search/basic-search-task
        "payload: Metadata dictionary (only if with_payload=True)."
"""

from actian_vectorai import VectorAIClient, VectorAIError

from constants import COLLECTION_NAME, VECTORAI_HOST
from embed import embed

# ---------------------------------------------------------------------------
# Demo query — natural language instead of technique IDs
# ---------------------------------------------------------------------------
QUERY: str = "browser credential theft"
TOP_K: int = 5


def main() -> None:
    """Embed the query, search the collection, and pretty-print results."""
    try:
        with VectorAIClient(VECTORAI_HOST) as client:
            query_vector = embed(QUERY)
            print(f'Query: "{QUERY}"')
            print(f"Searching top {TOP_K} results ...\n")

            results = client.points.search(
                COLLECTION_NAME,
                vector=query_vector,
                limit=TOP_K,
                with_payload=True,
            )

            if not results:
                print("No results found.")
                return

            for i, result in enumerate(results, start=1):
                payload = result.payload or {}
                print(f"[{i}] Score: {result.score:.4f}")
                print(f"    Title:       {payload.get('title', 'N/A')}")
                print(f"    Description: {payload.get('description', 'N/A')}")
                print(f"    Platform:    {payload.get('platform', 'N/A')}")
                print(f"    Tactic:      {payload.get('tactic', 'N/A')}")
                print("-" * 60)

    except VectorAIError as exc:
        print(f"Error: {exc.message}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()