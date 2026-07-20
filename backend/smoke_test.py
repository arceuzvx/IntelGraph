"""
IntelGraph — Smoke test.

Runs the complete backend workflow in a single process and prints
PASS only if every step succeeds.

Steps:
    1. Health check
    2. Create or verify collection (get_or_create)
    3. Verify collection exists (get_info)
    4. Insert one demo point (upsert)
    5. Verify point count (count)
    6. Semantic search (search with with_payload=True)
    7. Print retrieved result
    8. Print PASS

Documentation references:
    client.health_check():
        https://docs.vectoraidb.actian.com/docs/fundamentals/collections/get-collection-info-task
    client.collections.get_or_create():
        https://docs.vectoraidb.actian.com/docs/fundamentals/collections/create-collection-task
    client.collections.get_info():
        https://docs.vectoraidb.actian.com/docs/fundamentals/collections/get-collection-info-task
    client.points.upsert():
        https://docs.vectoraidb.actian.com/docs/fundamentals/points/insert-points-task
    client.points.count():
        https://docs.vectoraidb.actian.com/home/quickstart/quickstart
    client.points.search():
        https://docs.vectoraidb.actian.com/docs/fundamentals/search/basic-search-task
"""

from actian_vectorai import (
    Distance,
    PointStruct,
    VectorAIClient,
    VectorAIError,
    VectorParams,
)

from constants import COLLECTION_NAME, VECTOR_SIZE, VECTORAI_HOST
from embed import embed


def run_smoke_test() -> None:
    """Execute every backend operation in sequence.

    Raises ``SystemExit(1)`` on the first failure.  Prints ``PASS``
    at the end only if every step succeeds.
    """
    try:
        with VectorAIClient(VECTORAI_HOST) as client:

            # ------------------------------------------------------------------
            # Step 1: Health check
            # ------------------------------------------------------------------
            print("[1/7] Health check ...")
            health = client.health_check()
            print(f"       {health['title']} v{health['version']}")

            # ------------------------------------------------------------------
            # Step 2: Create or verify collection
            # ------------------------------------------------------------------
            print("[2/7] Create or verify collection ...")
            created = client.collections.get_or_create(
                name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.Cosine,
                ),
            )
            print(f"       {'Created' if created else 'Already exists'}.")

            # ------------------------------------------------------------------
            # Step 3: Verify collection with get_info()
            # ------------------------------------------------------------------
            print("[3/7] Verify collection via get_info() ...")
            info = client.collections.get_info(COLLECTION_NAME)
            print(f"       Status: {info.status}")
            print(f"       Points: {info.points_count}")

            # ------------------------------------------------------------------
            # Step 4: Insert one demo point
            # ------------------------------------------------------------------
            print("[4/7] Inserting demo point ...")
            description = (
                "Adversaries may steal credentials stored in web browsers "
                "and password managers."
            )
            vector = embed(description)
            point = PointStruct(
                id=1,
                vector=vector,
                payload={
                    "title": "Credentials from Password Stores",
                    "description": description,
                    "platform": "Windows",
                    "tactic": "Credential Access",
                },
            )
            client.points.upsert(COLLECTION_NAME, [point])
            print("       Upsert successful.")

            # ------------------------------------------------------------------
            # Step 5: Verify point count
            # ------------------------------------------------------------------
            print("[5/7] Verifying point count ...")
            count = client.points.count(COLLECTION_NAME)
            print(f"       Total points: {count}")
            if count < 1:
                print("FAIL — point count is 0 after upsert.")
                raise SystemExit(1)

            # ------------------------------------------------------------------
            # Step 6: Semantic search
            # ------------------------------------------------------------------
            query = "browser credential theft"
            print(f'[6/7] Searching: "{query}" ...')
            query_vector = embed(query)
            results = client.points.search(
                COLLECTION_NAME,
                vector=query_vector,
                limit=5,
                with_payload=True,
            )

            if not results:
                print("FAIL — search returned no results.")
                raise SystemExit(1)

            # ------------------------------------------------------------------
            # Step 7: Print retrieved result
            # ------------------------------------------------------------------
            print("[7/7] Top result:")
            top = results[0]
            payload = top.payload or {}
            print(f"       Score:       {top.score:.4f}")
            print(f"       Title:       {payload.get('title', 'N/A')}")
            print(f"       Description: {payload.get('description', 'N/A')}")
            print(f"       Platform:    {payload.get('platform', 'N/A')}")
            print(f"       Tactic:      {payload.get('tactic', 'N/A')}")

    except VectorAIError as exc:
        print(f"\nFAIL — VectorAI error: {exc.message}")
        raise SystemExit(1) from exc

    # -----------------------------------------------------------------------
    # PASS — every step succeeded
    # -----------------------------------------------------------------------
    print("\nPASS")


if __name__ == "__main__":
    run_smoke_test()
