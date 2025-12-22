from pathlib import Path

from loader import load_documents
from embeddings import EmbeddingModel
from vector_store import VectorStore
from retriever import Retriever

if __name__ == "__main__":
    data_dir = Path(__file__).parent.parent / "data"

    docs = load_documents(data_dir)

    embedder = EmbeddingModel()
    vectors = embedder.embed(docs)

    store = VectorStore(dim=vectors.shape[1])
    store.add(vectors, docs)

    retriever = Retriever(store, embedder, top_k=2)

    query = "Who founded the company and what do they sell?"
    results = retriever.retrieve(query)

    print("Retrieved context:")
    for r in results:
        print("-", r)
