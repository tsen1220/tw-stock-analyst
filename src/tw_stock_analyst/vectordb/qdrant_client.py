"""Qdrant vector database client."""

from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
import hashlib
import uuid

from ..config import settings


class StockVectorDB:
    """Qdrant client for stock analysis data."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: Optional[str] = None
    ):
        """
        Initialize Qdrant client.

        Args:
            host: Qdrant server host (default: from config)
            port: Qdrant server port (default: from config)
            collection_name: Name of the collection (default: from config)
        """
        # Use config values as defaults
        if host is None:
            host = settings.qdrant.host
        if port is None:
            port = settings.qdrant.port
        if collection_name is None:
            collection_name = settings.qdrant.collection_name

        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.vector_size = None  # Will be set when collection is created

    def create_collection(self, vector_size: int = 384) -> bool:
        """
        Create collection if it doesn't exist.

        Args:
            vector_size: Dimension of embedding vectors

        Returns:
            True if created or already exists
        """
        try:
            self.vector_size = vector_size  # Store vector size

            collections = self.client.get_collections().collections
            if any(col.name == self.collection_name for col in collections):
                print(f"Collection '{self.collection_name}' already exists")
                return True

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                ),
            )
            print(f"Collection '{self.collection_name}' created successfully")
            return True

        except Exception as e:
            print(f"Error creating collection: {e}")
            return False

    def insert_stock_data(
        self,
        text: str,
        vector: list[float],
        stock_id: str,
        stock_name: str,
        date: str,
        data_type: str,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Insert stock data into vector database.

        Args:
            text: Text description
            vector: Embedding vector
            stock_id: Stock code
            stock_name: Stock name
            date: Date of data
            data_type: Type of data (technical/fundamental)
            metadata: Additional metadata

        Returns:
            Point ID
        """
        unique_key = f"{stock_id}_{date}_{data_type}"
        # Generate UUID from SHA256 hash (take first 32 hex chars = 128 bits)
        hash_hex = hashlib.sha256(unique_key.encode()).hexdigest()[:32]
        point_id = str(uuid.UUID(hex=hash_hex))

        payload = {
            "text": text,
            "stock_id": stock_id,
            "stock_name": stock_name,
            "date": date,
            "data_type": data_type,
        }

        if metadata:
            payload["metadata"] = metadata

        point = PointStruct(
            id=point_id,
            vector=vector,
            payload=payload
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        return point_id

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
        stock_id: Optional[str] = None,
        data_type: Optional[str] = None,
        filter_conditions: Optional[dict] = None
    ) -> list[dict]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query embedding vector
            limit: Number of results to return
            stock_id: Filter by stock ID (optional)
            data_type: Filter by data type (optional)
            filter_conditions: Custom filter conditions (optional)
                Example: {"must": [{"key": "date", "match": {"value": "2024-01-01"}}]}

        Returns:
            List of search results with text and metadata
        """
        # Build filters
        filters = []
        if stock_id:
            filters.append(
                FieldCondition(key="stock_id", match=MatchValue(value=stock_id))
            )
        if data_type:
            filters.append(
                FieldCondition(key="data_type", match=MatchValue(value=data_type))
            )

        # Add custom filter conditions
        if filter_conditions and "must" in filter_conditions:
            for condition in filter_conditions["must"]:
                filters.append(
                    FieldCondition(
                        key=condition["key"],
                        match=MatchValue(value=condition["match"]["value"])
                    )
                )

        query_filter = Filter(must=filters) if filters else None

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=query_filter
        )

        return [
            {
                "id": str(result.id),
                "score": result.score,
                "text": result.payload.get("text", ""),
                "stock_id": result.payload.get("stock_id", ""),
                "stock_name": result.payload.get("stock_name", ""),
                "date": result.payload.get("date", ""),
                "data_type": result.payload.get("data_type", ""),
                "metadata": result.payload.get("metadata", {})
            }
            for result in results
        ]

    def get_collection_info(self) -> dict:
        """Get collection information."""
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            return {"error": str(e)}

    def delete_collection(self) -> bool:
        """Delete the collection."""
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            print(f"Collection '{self.collection_name}' deleted")
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False
