from actian_vectorai import (
    VectorAIClient,
    VectorParams,
    Distance,
)

COLLECTION = "intelgraph"

with VectorAIClient("localhost:6574") as client:

    if client.collections.exists(COLLECTION):
        print("Collection already exists.")
    else:
        client.collections.create(
            COLLECTION,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.Cosine,
            ),
        )
        print("Collection created!")