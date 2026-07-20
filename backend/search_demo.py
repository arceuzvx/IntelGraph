from sentence_transformers import SentenceTransformer
from actian_vectorai import VectorAIClient

COLLECTION = "intelgraph"

model = SentenceTransformer("all-MiniLM-L6-v2")

query = "browser credential theft"

query_vector = model.encode(query).tolist()

with VectorAIClient("localhost:6574") as client:
    results = client.points.search(
        COLLECTION,
        vector=query_vector,
        limit=5,
    )

for result in results:
    print(f"Score: {result.score:.4f}")
    print(result.payload)
    print("-" * 40)