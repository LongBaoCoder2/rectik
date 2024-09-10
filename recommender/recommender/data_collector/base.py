from pydantic import BaseModel, Field
from typing import List, Dict

class BaseCollector(BaseModel):
    """Base class for collecting and preprocessing data."""
    data_source: str = Field(..., description="Source of the dataset (e.g., CSV, database).")

    def load_data(self) -> Dict[str, List]:
        """Load the data from the data source."""
        raise NotImplementedError("Data loading method should be implemented by subclasses.")

    def preprocess_data(self, raw_data: Dict[str, List]) -> Dict[str, List]:
        """Preprocess raw data (e.g., text tokenization, normalization)."""
        raise NotImplementedError("Data preprocessing method should be implemented.")