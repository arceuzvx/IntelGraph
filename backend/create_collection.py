"""
IntelGraph — Collection creation.

Creates the 'intelgraph' collection using the idempotent
``get_or_create()`` method.

Documentation references:
    client.collections.get_or_create():
        https://docs.vectoraidb.actian.com/docs/fundamentals/collections/create-collection-task
        Section: "Get or create collection"
        "Use get_or_create() to ensure a collection exists before your
         application starts working with it."

    VectorParams / Distance:
        https://docs.vectoraidb.actian.com/sdks/python/reference
        VectorParams(size=int, distance=Distance.Cosine)

    client.collections.get_info():
        https://docs.vectoraidb.actian.com/docs/fundamentals/collections/get-collection-info-task
        Section: "Get collection metadata"
        Returns object with .status and .points_count fields.
"""

from actian_vectorai import (
    Distance,
    VectorAIClient,
    VectorAIError,
    VectorParams,
)

from constants import COLLECTION_NAME, VECTOR_SIZE, VECTORAI_HOST


def main() -> None:
    """Create the IntelGraph collection or confirm it already exists.

    Uses ``get_or_create()`` which returns True if a new collection was
    created, False if it already existed.  After that, ``get_info()``
    is called to verify the collection is in the 'Ready' state.
    """
    try:
        with VectorAIClient(VECTORAI_HOST) as client:
            created = client.collections.get_or_create(
                name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.Cosine,
                ),
            )

            if created:
                print(f"Collection '{COLLECTION_NAME}' created.")
            else:
                print(f"Collection '{COLLECTION_NAME}' already exists.")

            # Verify with the documented get_info() inspection method
            info = client.collections.get_info(COLLECTION_NAME)
            print(f"  Status:       {info.status}")
            print(f"  Point count:  {info.points_count}")

    except VectorAIError as exc:
        print(f"Error: {exc.message}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()