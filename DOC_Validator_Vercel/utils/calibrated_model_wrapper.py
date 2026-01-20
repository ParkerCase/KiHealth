"""
Calibrated Model Wrapper
========================
Wrapper class for applying Platt scaling to pre-fitted models.
This class is pickleable and can be saved/loaded.
"""

import numpy as np
from sklearn.linear_model import LogisticRegression


class CalibratedModelWrapper:
    """Wrapper that applies Platt scaling to base model predictions"""
    
    def __init__(self, base_model, platt_scaler):
        """
        Initialize calibrated model wrapper
        
        Parameters:
        -----------
        base_model : Trained model
            Pre-fitted model (e.g., RandomForestClassifier)
        platt_scaler : LogisticRegression
            Fitted Platt scaling model
        """
        self.base_model = base_model
        self.platt_scaler = platt_scaler
    
    def predict_proba(self, X):
        """Get calibrated probabilities"""
        uncalibrated = self.base_model.predict_proba(X)[:, 1]
        calibrated = self.platt_scaler.predict_proba(uncalibrated.reshape(-1, 1))[:, 1]
        # Return in same format as sklearn (2D array with [prob_class_0, prob_class_1])
        return np.column_stack([1 - calibrated, calibrated])
    
    def predict(self, X):
        """Get binary predictions"""
        proba = self.predict_proba(X)[:, 1]
        return (proba >= 0.5).astype(int)
    
    def __getstate__(self):
        """Custom pickle serialization"""
        return {
            'base_model': self.base_model,
            'platt_scaler': self.platt_scaler
        }
    
    def __setstate__(self, state):
        """Custom pickle deserialization"""
        self.base_model = state['base_model']
        self.platt_scaler = state['platt_scaler']
