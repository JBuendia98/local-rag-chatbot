import faiss
import numpy as np
from typing import List, Tuple


class VectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.documents: List[str] = []

    def add(self, embeddings: np.ndarray, docs: List[str]):
        if embeddings.shape[0] != len(docs):
            raise ValueError("Embeddings and documents length mismatch")

        self.index.add(embeddings)
        self.documents.extend(docs)

    def search(self, query_embedding: np.ndarray, k: int = 3) -> List[Tuple[str, float]]:
        distances, indices = self.index.search(query_embedding.reshape(1, -1), k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(dist)))

        return results
