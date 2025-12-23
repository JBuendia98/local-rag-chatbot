from typing import List
from typing import List, Optional
from .embeddings import EmbeddingModel
from .vector_store import VectorStore

class Retriever:
    def __init__(
        self,
        vectorstore: VectorStore,
        embedding_model: EmbeddingModel,
        top_k: int = 3,
    ):
        self.vectorstore = vectorstore
        self.embedding_model = embedding_model
        self.top_k = top_k

    def retrieve(self, query: str, k: Optional[int] = None) -> List[str]:
        """
        Given a user query, return top-k relevant document chunks.
        """
        search_k = k if k is not None else self.top_k

        query_vector = self.embedding_model.embed([query])[0]
        
        results = self.vectorstore.search(query_vector, k=search_k)
        
        return [text for text, _ in results]
