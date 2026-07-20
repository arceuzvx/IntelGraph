from sentence_transformers import SentenceTransformer
from actian_vectorai import (
    VectorAIClient,
    PointStruct,
)

COLLECTION = "intelgraph"

model = SentenceTransformer("all-MiniLM-L6-v2")

doc = {
    "id": 1,
    "title": "Credentials from Password Stores",
    "description": (
        "Adversaries may steal credentials stored in web browsers "
        "and password managers."
    ),
    "platform": "Windows",
    "tactic": "Credential Access",
}

embedding = model.encode(doc["description"]).tolist()

with VectorAIClient("localhost:6574") as client:
    client.points.upsert(
        COLLECTION,
        [
            PointStruct(
                id=doc["id"],
                vector=embedding,
                payload={
                    "title": doc["title"],
                    "description": doc["description"],
                    "platform": doc["platform"],
                    "tactic": doc["tactic"],
                },
            )
        ],
    )

print("Inserted!")