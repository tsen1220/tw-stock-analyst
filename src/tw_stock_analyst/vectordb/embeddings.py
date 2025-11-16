"""Embedding generation using Sentence Transformers."""

from typing import Union
from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingModel:
    """Wrapper for sentence transformer embedding model."""

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize embedding model.

        Args:
            model_name: Name of the sentence transformer model
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.dimension}")

    def encode(self, text: Union[str, list[str]]) -> np.ndarray:
        """
        Generate embeddings for text.

        Args:
            text: Single text string or list of texts

        Returns:
            Embedding vector(s) as numpy array
        """
        embeddings = self.model.encode(text, convert_to_numpy=True)
        return embeddings

    def get_dimension(self) -> int:
        """Get embedding vector dimension."""
        return self.dimension
