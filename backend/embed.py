from sentence_transformers import SentenceTransformer

print("Loading model...")

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

print("Loaded!")

embedding = model.encode("browser credential theft")

print(f"Embedding length: {len(embedding)}")