"""
Model Loader with Toggle Function
==================================
Loads either the pure data-driven model or the literature-calibrated model.

CRITICAL: This allows instant switching between models while preserving
the original pure data-driven model.
"""

import os
import joblib
import sys
from pathlib import Path
from typing import Optional

# Get base directory
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"

# Add utils to path for importing CalibratedModelWrapper
sys.path.insert(0, str(Path(__file__).parent))
from calibrated_model_wrapper import CalibratedModelWrapper


def load_tkr_model(use_literature_calibration: bool = False) -> object:
    """
    Load TKR prediction model.
    
    Parameters:
    -----------
    use_literature_calibration : bool, default=False
        If True, load literature-calibrated model
        If False, load pure data-driven model (original)
    
    Returns:
    --------
    model : Trained model object
        Random Forest model (calibrated or uncalibrated)
    
    Raises:
    -------
    FileNotFoundError
        If model file does not exist
    """
    if use_literature_calibration:
        # Load calibrated model components and recreate wrapper
        base_path = MODELS_DIR / "random_forest_literature_calibrated_base.pkl"
        platt_path = MODELS_DIR / "random_forest_literature_calibrated_platt.pkl"
        model_name = "Literature-Calibrated Model"
        
        if not base_path.exists() or not platt_path.exists():
            raise FileNotFoundError(
                f"Calibrated model components not found:\n"
                f"  Base: {base_path}\n"
                f"  Platt: {platt_path}\n"
                f"Please run notebooks/9_literature_calibrated_model.py first."
            )
        
        try:
            base_model = joblib.load(base_path)
            platt_scaler = joblib.load(platt_path)
            model = CalibratedModelWrapper(base_model, platt_scaler)
            print(f"✓ Loaded: {model_name}")
            print(f"  Base model: {base_path}")
            print(f"  Platt scaler: {platt_path}")
            return model
        except Exception as e:
            raise Exception(f"Failed to load calibrated model: {e}")
    else:
        model_path = MODELS_DIR / "random_forest_best.pkl"
        model_name = "Pure Data-Driven Model (Original)"
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                f"Please ensure the model has been trained and saved."
            )
        
        try:
            model = joblib.load(model_path)
            print(f"✓ Loaded: {model_name}")
            print(f"  Path: {model_path}")
            return model
        except Exception as e:
            raise Exception(f"Failed to load model from {model_path}: {e}")


def load_preprocessing_objects() -> tuple:
    """
    Load preprocessing objects (scaler, imputer, feature names).
    
    Returns:
    --------
    scaler : StandardScaler
    imputer : IterativeImputer (or None if not needed)
    feature_names : list
    """
    scaler_path = MODELS_DIR / "scaler.pkl"
    imputer_path = MODELS_DIR / "imputer_numeric.pkl"
    features_path = MODELS_DIR / "feature_names.pkl"
    
    scaler = None
    imputer = None
    feature_names = None
    
    if scaler_path.exists():
        scaler = joblib.load(scaler_path)
        print(f"✓ Loaded scaler: {scaler_path}")
    else:
        print(f"⚠️  Scaler not found: {scaler_path}")
    
    if imputer_path.exists():
        imputer = joblib.load(imputer_path)
        print(f"✓ Loaded imputer: {imputer_path}")
    else:
        print(f"⚠️  Imputer not found: {imputer_path}")
    
    if features_path.exists():
        feature_names = joblib.load(features_path)
        print(f"✓ Loaded feature names: {features_path}")
    else:
        print(f"⚠️  Feature names not found: {features_path}")
    
    return scaler, imputer, feature_names


def get_model_info(use_literature_calibration: bool = False) -> dict:
    """
    Get information about the model.
    
    Parameters:
    -----------
    use_literature_calibration : bool, default=False
        Which model to get info for
    
    Returns:
    --------
    info : dict
        Model information dictionary
    """
    if use_literature_calibration:
        model_path = MODELS_DIR / "random_forest_literature_calibrated.pkl"
        model_type = "Literature-Calibrated"
    else:
        model_path = MODELS_DIR / "random_forest_best.pkl"
        model_type = "Pure Data-Driven (Original)"
    
    info = {
        "model_type": model_type,
        "model_path": str(model_path),
        "exists": model_path.exists(),
    }
    
    if model_path.exists():
        import os
        from datetime import datetime
        stat = os.stat(model_path)
        info["file_size_mb"] = stat.st_size / (1024 * 1024)
        info["modified_date"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
    
    return info


if __name__ == "__main__":
    # Test loading both models
    print("Testing model loader...\n")
    
    print("1. Loading original model:")
    try:
        model_original = load_tkr_model(use_literature_calibration=False)
        print(f"   Model type: {type(model_original).__name__}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    print("2. Loading literature-calibrated model:")
    try:
        model_calibrated = load_tkr_model(use_literature_calibration=True)
        print(f"   Model type: {type(model_calibrated).__name__}\n")
    except FileNotFoundError:
        print("   ⚠️  Literature-calibrated model not found (run notebooks/9_literature_calibrated_model.py first)\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    print("3. Model information:")
    info_original = get_model_info(use_literature_calibration=False)
    print(f"   Original: {info_original}")
    
    info_calibrated = get_model_info(use_literature_calibration=True)
    print(f"   Calibrated: {info_calibrated}")
