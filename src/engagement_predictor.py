"""
engagement_predictor.py

This module loads a pretrained engagement model and scaler, and provides
a function to predict engagement level from a feature vector.
"""

import numpy as np
import joblib
import tensorflow as tf

# Load scaler and model once at import time to avoid repeated I/O
SCALER = joblib.load('scaler.save')  # Path to the saved StandardScaler
MODEL = tf.keras.models.load_model('engagement_mlp_model.h5')  # Path to the saved Keras model

def predict_engagement(feature_vector: np.ndarray) -> str:
    """
    Predicts engagement level from a 1D feature vector.

    Args:
        feature_vector (np.ndarray): 1D array of shape (n_features,).

    Returns:
        str: One of "low", "normal", or "high" representing engagement level.
    """
    # Ensure proper shape for scaler
    x = SCALER.transform(feature_vector.reshape(1, -1))  # shape = (1, n_features)
    # Predict probabilities for each class
    proba = MODEL.predict(x, verbose=0)[0]               # e.g. [p0, p1, p2]
    # Determine class label index (0, 1, or 2)
    label = int(np.argmax(proba))
    # Map numeric label to string
    label_map = {0: "low", 1: "normal", 2: "high"}
    return label_map.get(label, "normal")
