import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple

class VectorStore:
    def __init__(self, dim: int, index_path: str = "faiss_index.bin", metadata_path: str = "metadata.pkl"):
        self.dim = dim
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.documents: List[str] = []

        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            print("Loading Vector Store from disk...")
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "rb") as f:
                self.documents = pickle.load(f)
        else:
            print("Creating new Vector Store...")
            self.index = faiss.IndexFlatL2(dim)

    def add(self, embeddings: np.ndarray, docs: List[str]):
        if embeddings.shape[0] != len(docs):
            raise ValueError("Embeddings and documents length mismatch")

        self.index.add(embeddings)
        self.documents.extend(docs)
        
        self._save()

    def _save(self):
        """Helper to save index and documents to disk"""
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.documents, f)

    def search(self, query_embedding: np.ndarray, k: int = 3) -> List[Tuple[str, float]]:
        distances, indices = self.index.search(query_embedding.reshape(1, -1), k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx >= 0 and idx < len(self.documents):
                results.append((self.documents[idx], float(dist)))

        return results