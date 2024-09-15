import torch
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from pydantic import PrivateAttr

from recommender.recommender.embedding.base import BaseEmbedding

class SBERTEncoder(BaseEmbedding):
    _model: SentenceTransformer = PrivateAttr()

    def __init__(self, model_name="all-MiniLM-L6-v2", embedding_size: int=768, device: str = 'cpu'):
        super().__init__(model_name=model_name, embedding_size=embedding_size, device=device)
        self._model = SentenceTransformer(self.model_name).to(self.device)

    def _encode_text(self, text):
        with torch.inference_mode():
            text_features = self._model.encode(text, convert_to_tensor=True)
        return text_features.cpu().numpy()
    
    def similarity(self, sentences_1 : str | List[str], sentences_2 : str | List[str]):
        embedding_a = self._encode_text(sentences_1)
        embedding_b = self._encode_text(sentences_2)
        return self.model.similarity(embedding_a, embedding_b)

    def get_embedding(self, item_id: int) -> np.ndarray:
        return self._encode_text(item_id)
    
    def update_embedding(self, item_id: int, new_embedding: np.ndarray):
        pass


def main():
    # Instantiate SBERTEncoder for inference
    encoder = SBERTEncoder(model_name="all-MiniLM-L6-v2", device="cuda" if torch.cuda.is_available() else "cpu")

    # Sample text for which to get embeddings
    sample_text = "This is a sample sentence for SBERT encoding."

    # Get the embedding for the sample text
    embedding = encoder.get_embedding(sample_text)
    print("embedding: ", embedding)
    sentences1 = [
        "The new movie is awesome",
        "The cat sits outside",
        "A man is playing guitar",
    ]

    sentences2 = [
        "The dog plays in the garden",
        "The new movie is so great",
        "A woman watches TV",
    ]

    similarity = encoder.similarity(sentences1, sentences2)
    print("similarity: ", similarity)


if __name__ == "__main__":
    main()