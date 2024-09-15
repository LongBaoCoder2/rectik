import numpy as np
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from pydantic import PrivateAttr
from typing import Any

from recommender.recommender.embedding.base import BaseEmbedding

class CLIPEncoder(BaseEmbedding):
    _processor: CLIPProcessor = PrivateAttr()  # Declare as a private attribute
    _model: CLIPModel = PrivateAttr()          # Declare as a private attribute

    def __init__(self, model_name="openai/clip-vit-base-patch32", embedding_size: int = 512, device: str = "cpu"):
        # Initialize the parent class with model_name and embedding_size
        super().__init__(model_name=model_name, embedding_size=embedding_size)
        self._model = CLIPModel.from_pretrained(self.model_name).to(self.device)
        self._processor = CLIPProcessor.from_pretrained(self.model_name)

    def _encode_image(self, image: str | Any) -> np.ndarray:
        """Encodes an image using CLIP and returns the image embedding."""
        # image = Image.open(image).convert("RGB")
        if isinstance(image, str):
            try:
                image = Image.open(image).convert("RGB")
            except: 
                raise ValueError(f"Invalid image path: {image}")
        inputs = self._processor(images=image, return_tensors="pt").to(self.device)
        with torch.inference_mode():
            image_features = self._model.get_image_features(**inputs)
        return image_features.cpu().numpy()

    def get_embedding(self, image_path: str) -> np.ndarray:
        """Retrieve the embedding for a given image."""
        return self._encode_image(image_path)
    
    def _similarity(self, image_tensor_1: torch.Tensor, image_tensor_2: torch.Tensor):
        image_tensor_1 = torch.tensor(image_tensor_1, dtype=torch.float32, device=self.device)
        image_tensor_2 = torch.tensor(image_tensor_2, dtype=torch.float32, device=self.device)
        return torch.nn.functional.cosine_similarity(image_tensor_1, image_tensor_2, dim=1)
                                      

    def similarity(self, image_1: str | Any, image_2: str | Any):
        embedding_a = self._encode_image(image_1)
        embedding_b = self._encode_image(image_2)
        return self.model.similarity(embedding_a, embedding_b)

    def update_embedding(self, item_id: int, new_embedding: np.ndarray):
        """Placeholder for updating embeddings (not implemented in this example)."""
        pass



def main():
    encoder = CLIPEncoder(model_name="openai/clip-vit-base-patch32", embedding_size=512, device="cuda" if torch.cuda.is_available() else "cpu")

    # Sample text for which to get embeddings
    sample_text = "This is a sample sentence for SBERT encoding."

    # Get the embedding for the sample text
    embedding = encoder.get_embedding(sample_text)
    
    # Output the embedding shape and values
    print("Embedding shape:", embedding.shape)
    print("Embedding values:", embedding)

if __name__ == "__main__":
    main()