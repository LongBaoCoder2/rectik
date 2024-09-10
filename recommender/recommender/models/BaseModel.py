from pydantic import BaseModel
from typing import Any

class BaseModel(BaseModel):
    """Base class for any recommendation model."""
    model_name: str

    def train(self, data: Any):
        """Train the recommendation model."""
        raise NotImplementedError("Training method should be implemented by subclasses.")

    def predict(self, user_id: int, item_id: int) -> float:
        """Predict the interaction score between a user and an item."""
        raise NotImplementedError("Prediction method should be implemented by subclasses.")