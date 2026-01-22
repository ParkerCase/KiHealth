"""
Calibrated Model Wrapper
========================
Wrapper class for applying calibration (Platt scaling or isotonic) to pre-fitted models.
This class is pickleable and can be saved/loaded.
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression


class CalibratedModelWrapper:
    """Wrapper that applies calibration (Platt scaling or isotonic) to base model predictions"""
    
    def __init__(self, base_model, calibrator):
        """
        Initialize calibrated model wrapper
        
        Parameters:
        -----------
        base_model : Trained model
            Pre-fitted model (e.g., RandomForestClassifier)
        calibrator : LogisticRegression or IsotonicRegression
            Fitted calibration model (Platt scaling or isotonic)
        """
        self.base_model = base_model
        self.calibrator = calibrator
        # Detect calibration type
        self.is_isotonic = isinstance(calibrator, IsotonicRegression)
        self.is_platt = isinstance(calibrator, LogisticRegression)
    
    def predict_proba(self, X):
        """Get calibrated probabilities using Platt scaling or isotonic calibration"""
        uncalibrated = self.base_model.predict_proba(X)[:, 1]
        
        if self.is_isotonic:
            # Isotonic calibration: direct transformation (1D array)
            calibrated = self.calibrator.predict(uncalibrated)
        elif self.is_platt:
            # Platt scaling: use LogisticRegression
            uncalibrated_2d = uncalibrated.reshape(-1, 1)
            
            # Use decision_function + sigmoid for version-agnostic Platt scaling
            # This works across all scikit-learn versions and avoids multi_class issues
            try:
                decision = self.calibrator.decision_function(uncalibrated_2d)
                # Apply sigmoid manually: P = 1 / (1 + exp(-decision))
                calibrated = 1.0 / (1.0 + np.exp(-decision.flatten()))
            except AttributeError:
                # Fallback: try predict_proba if decision_function doesn't exist
                try:
                    calibrated_proba = self.calibrator.predict_proba(uncalibrated_2d)
                    if calibrated_proba.ndim == 2:
                        calibrated = calibrated_proba[:, 1] if calibrated_proba.shape[1] > 1 else calibrated_proba[:, 0]
                    else:
                        calibrated = calibrated_proba
                except Exception:
                    # Last resort: use coefficients directly
                    coef = self.calibrator.coef_[0][0] if hasattr(self.calibrator, 'coef_') else 1.0
                    intercept = self.calibrator.intercept_[0] if hasattr(self.calibrator, 'intercept_') else 0.0
                    linear = coef * uncalibrated + intercept
                    calibrated = 1.0 / (1.0 + np.exp(-linear))
        else:
            # Unknown calibrator type - try to use it directly
            try:
                calibrated = self.calibrator.predict(uncalibrated)
            except:
                # Fallback: return uncalibrated
                calibrated = uncalibrated
        
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
            'calibrator': self.calibrator
        }
    
    def __setstate__(self, state):
        """Custom pickle deserialization"""
        self.base_model = state['base_model']
        self.calibrator = state['calibrator']
        # Re-detect calibration type
        self.is_isotonic = isinstance(self.calibrator, IsotonicRegression)
        self.is_platt = isinstance(self.calibrator, LogisticRegression)
