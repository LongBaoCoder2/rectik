from pydantic import BaseModel
from typing import List
import numpy as np

class BaseEmbedding(BaseModel):
    """Base class for embeddings in the recommendation system."""
    embedding_size: int

    def get_embedding(self, item_id: int) -> np.ndarray:
        """Retrieve the embedding for a given item."""
        raise NotImplementedError("Method to retrieve embeddings should be implemented.")

    def update_embedding(self, item_id: int, new_embedding: np.ndarray):
        """Update the embedding for a given item."""
        raise NotImplementedError("Method to update embeddings should be implemented.")
