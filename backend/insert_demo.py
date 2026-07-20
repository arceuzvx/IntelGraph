"""
IntelGraph — Insert demo.

Inserts a single MITRE ATT&CK-style document into the collection.

Before inserting, the script verifies that the collection exists using
the documented ``collections.get_info()`` method.

Documentation references:
    client.collections.get_info():
        https://docs.vectoraidb.actian.com/docs/fundamentals/collections/get-collection-info-task
        Section: "Get collection metadata"

    client.points.upsert():
        https://docs.vectoraidb.actian.com/docs/fundamentals/points/insert-points-task
        Section: "Insert a single point"
        Signature: client.points.upsert(collection_name, [PointStruct(...)])

    PointStruct:
        https://docs.vectoraidb.actian.com/docs/fundamentals/points/insert-points-task
        PointStruct(id=int, vector=list[float], payload=dict)

    client.points.count():
        https://docs.vectoraidb.actian.com/home/quickstart/quickstart
        Step 2: "count = client.points.count('products')"
"""

from actian_vectorai import (
    CollectionNotFoundError,
    PointStruct,
    VectorAIClient,
    VectorAIError,
)

from constants import COLLECTION_NAME, VECTORAI_HOST
from embed import embed


# ---------------------------------------------------------------------------
# Demo document — one MITRE ATT&CK technique
# ---------------------------------------------------------------------------
DEMO_DOC: dict = {
    "id": 1,
    "title": "Credentials from Password Stores",
    "description": (
        "Adversaries may steal credentials stored in web browsers "
        "and password managers."
    ),
    "platform": "Windows",
    "tactic": "Credential Access",
}


def main() -> None:
    """Generate an embedding for the demo document and upsert it."""
    try:
        with VectorAIClient(VECTORAI_HOST) as client:
            # ---------------------------------------------------------------
            # Step 1: Verify collection exists using documented get_info()
            # ---------------------------------------------------------------
            try:
                info = client.collections.get_info(COLLECTION_NAME)
                print(f"Collection '{COLLECTION_NAME}' verified.")
                print(f"  Status: {info.status}")
            except CollectionNotFoundError:
                print(
                    f"Collection '{COLLECTION_NAME}' not found. "
                    f"Run create_collection.py first."
                )
                raise SystemExit(1)

            # ---------------------------------------------------------------
            # Step 2: Generate embedding from the description
            # ---------------------------------------------------------------
            vector = embed(DEMO_DOC["description"])
            print(f"Embedding generated ({len(vector)} dimensions).")

            # ---------------------------------------------------------------
            # Step 3: Upsert the point
            # ---------------------------------------------------------------
            point = PointStruct(
                id=DEMO_DOC["id"],
                vector=vector,
                payload={
                    "title": DEMO_DOC["title"],
                    "description": DEMO_DOC["description"],
                    "platform": DEMO_DOC["platform"],
                    "tactic": DEMO_DOC["tactic"],
                },
            )
            client.points.upsert(COLLECTION_NAME, [point])
            print("Inserted 1 point.")

            # ---------------------------------------------------------------
            # Step 4: Verify point count
            # ---------------------------------------------------------------
            count = client.points.count(COLLECTION_NAME)
            print(f"Total points in collection: {count}")

    except VectorAIError as exc:
        print(f"Error: {exc.message}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()