from pydantic import BaseModel
from torch.utils.data import Dataset, DataLoader
import numpy as np

class DataConfig(BaseModel):
    data_path: str
    batch_size: int
    shuffle: bool = True

class RecommendationDataset(Dataset):
    """Custom dataset for recommendation systems."""
    def __init__(self, user_item_matrix):
        self.user_item_matrix = user_item_matrix

    def __len__(self):
        return self.user_item_matrix.shape[0]

    def __getitem__(self, idx):
        return self.user_item_matrix[idx]

class BaseDataCollection:
    def __init__(self, config: DataConfig):
        self.config = config
        self.data_path = config.data_path
        self.batch_size = config.batch_size
        self.shuffle = config.shuffle
        self.train_data, self.test_data = self.load_data()
        
    def load_data(self):
        """Load train/test data (replace this with real data loading logic)."""
        # For simplicity, let's use a dummy user-item interaction matrix (numpy array)
        user_item_matrix = np.load(self.data_path)
        
        # Split into training and testing
        split_index = int(0.8 * len(user_item_matrix))
        train_data = user_item_matrix[:split_index]
        test_data = user_item_matrix[split_index:]
        
        return train_data, test_data

    def get_data_loader(self, data, batch_size):
        """Create DataLoader from dataset."""
        dataset = RecommendationDataset(data)
        return DataLoader(dataset, batch_size=batch_size, shuffle=self.shuffle)

    def get_train_loader(self):
        return self.get_data_loader(self.train_data, self.batch_size)

    def get_test_loader(self):
        return self.get_data_loader(self.test_data, self.batch_size)
