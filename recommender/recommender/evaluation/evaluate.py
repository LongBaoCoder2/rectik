from typing import List
from sklearn.metrics import precision_score, recall_score, mean_squared_error

# Define individual functions for each evaluation metric
def precision_at_k(true_labels: List[int], predicted_labels: List[int], k: int) -> float:
    """Calculate Precision@K."""
    relevant = predicted_labels[:k]
    precision = precision_score(true_labels, relevant, average='binary')
    return precision

import numpy as np

def recall_at_k(true_labels: np.ndarray, predicted_labels: np.ndarray, k: int) -> float:
    """
    Calculate Recall@K.

    Parameters:
        true_labels (np.ndarray): 1D array of true relevant item identifiers.
        predicted_labels (np.ndarray): 1D array of predicted item identifiers, ranked by relevance.
        k (int): Number of top predictions to consider.

    Returns:
        float: The proportion of relevant items retrieved in the top K predictions.
    """
    # Ensure inputs are NumPy arrays
    true_labels = np.asarray(true_labels)
    predicted_labels = np.asarray(predicted_labels)

    # Get the set of true relevant items
    true_set = set(true_labels)

    # Get the set of predicted items in the top K
    predicted_set = set(predicted_labels[:k])

    # Calculate the number of relevant items retrieved in the top K
    relevant_retrieved = len(true_set.intersection(predicted_set))
    
    # Calculate recall (relevant items retrieved / total relevant items)
    recall = relevant_retrieved / len(true_set) if len(true_set) > 0 else 0.0

    return recall


def calculate_mse(true_ratings: List[float], predicted_ratings: List[float]) -> float:
    """Calculate Mean Squared Error (MSE) between true and predicted ratings."""
    mse = mean_squared_error(true_ratings, predicted_ratings)
    return mse