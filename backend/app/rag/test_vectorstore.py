from embeddings import EmbeddingModel
from vector_store import VectorStore

texts = [
    "SGFD is a technology company focused on AI defence.",
    "The company was founded by John Doe.",
    "Revenue reached 1 billion last year."
]

model = EmbeddingModel()
embeddings = model.embed(texts)

store = VectorStore(dim=embeddings.shape[1])
store.add(embeddings, texts)

query = "Who founded the company?"
query_embedding = model.embed([query])

results = store.search(query_embedding, k=2)

print("Search results:")
for doc, dist in results:
    print("-", doc, "(distance:", dist, ")")
