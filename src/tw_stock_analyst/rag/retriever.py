"""RAG retriever for stock analysis."""

from typing import Optional
from ..vectordb.qdrant_client import StockVectorDB
from ..vectordb.embeddings import EmbeddingModel


class StockRetriever:
    """Retrieve relevant stock information from vector database."""

    def __init__(
        self,
        vector_db: StockVectorDB,
        embedding_model: EmbeddingModel
    ):
        """
        Initialize retriever.

        Args:
            vector_db: Vector database client
            embedding_model: Embedding model for queries
        """
        self.vector_db = vector_db
        self.embedding_model = embedding_model

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        stock_id: Optional[str] = None,
        data_type: Optional[str] = None
    ) -> list[dict]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: User query text
            top_k: Number of documents to retrieve
            stock_id: Filter by stock ID (optional)
            data_type: Filter by data type (optional)

        Returns:
            List of retrieved documents with scores
        """
        # Generate query embedding
        query_vector = self.embedding_model.encode(query).tolist()

        # Search vector database
        results = self.vector_db.search(
            query_vector=query_vector,
            limit=top_k,
            stock_id=stock_id,
            data_type=data_type
        )

        return results

    def format_context(self, results: list[dict]) -> str:
        """
        Format retrieved results into context for LLM.

        Args:
            results: List of retrieved documents

        Returns:
            Formatted context string
        """
        if not results:
            return "找不到相關的股市資料。"

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[資料 {i}] (相關度: {result['score']:.3f})")
            context_parts.append(result['text'])
            context_parts.append("")  # Empty line

        return "\n".join(context_parts)
