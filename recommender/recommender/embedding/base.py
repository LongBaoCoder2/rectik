from pydantic import BaseModel
import numpy as np

class BaseEmbedding(BaseModel):
    """Base class for embeddings in the recommendation system."""
    model_name: str = ""
    embedding_size: int = 768
    device: str = "cpu"

    def get_embedding(self, item_id: int) -> np.ndarray:
        """Retrieve the embedding for a given item."""
        raise NotImplementedError("Method to retrieve embeddings should be implemented.")

    def update_embedding(self, item_id: int, new_embedding: np.ndarray):
        """Update the embedding for a given item."""
        raise NotImplementedError("Method to update embeddings should be implemented.")

    def similarity(self, vector_1, vector_2):
        """Calculate the similarity between two vectors."""
        raise NotImplementedError("Method to calculate similarity should be implemented.")
    

