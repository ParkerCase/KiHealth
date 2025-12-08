"""
VAS to WOMAC conversion function (literature-based fallback)
Based on: Tubach 2005, Salaffi 2003
"""

import numpy as np

def vas_to_womac(vas_score, scale='0-10'):
    """
    Convert VAS pain score to approximate WOMAC total score
    Based on literature (Tubach 2005, Salaffi 2003)
    
    Args:
        vas_score: VAS pain rating
        scale: '0-10' or '0-100'
    
    Returns:
        Estimated WOMAC total score (0-96)
    """
    if scale == '0-100':
        vas_score = vas_score / 10
    
    # Linear approximation: WOMAC ≈ 8×VAS + 15
    womac_approx = (vas_score * 8) + 15
    
    # Clip to valid range
    womac_approx = np.clip(womac_approx, 0, 96)
    
    return womac_approx

def vas_to_womac_pain_subscale(vas_score, scale='0-10'):
    """
    Convert VAS pain score to approximate WOMAC pain subscale (0-20)
    Based on Tubach et al. 2005
    
    Args:
        vas_score: VAS pain rating
        scale: '0-10' or '0-100'
    
    Returns:
        Estimated WOMAC pain subscale (0-20)
    """
    if scale == '0-100':
        vas_score = vas_score / 10
    
    # Convert to 0-100 scale for formula
    vas_100 = vas_score * 10
    
    # Tubach formula: WOMAC_pain = 0.18 × VAS_100 + 2.5
    womac_pain = (0.18 * vas_100) + 2.5
    
    # Clip to valid range
    womac_pain = np.clip(womac_pain, 0, 20)
    
    return womac_pain
