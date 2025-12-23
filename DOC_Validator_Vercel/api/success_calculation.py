"""
Success Probability Calculation for Surgical Outcomes
Based on ≥30 points WOMAC improvement = "Successful Outcome"

PROBAST Compliance: This module only transforms model outputs, 
does not modify model predictions or training data.
"""

# Success thresholds (WOMAC improvement in points)
SUCCESS_THRESHOLDS = {
    "EXCELLENT": 40,      # ≥40 points improvement
    "SUCCESSFUL": 30,     # 30-39 points improvement (surgeon-defined threshold)
    "MODERATE": 20,       # 20-29 points improvement
    "LIMITED": 10,        # 10-19 points improvement
    "MINIMAL": 0          # <10 points improvement
}

SUCCESS_CATEGORIES = {
    "EXCELLENT": "Excellent Outcome",
    "SUCCESSFUL": "Successful Outcome",
    "MODERATE": "Moderate Improvement",
    "LIMITED": "Limited Improvement",
    "MINIMAL": "Minimal Improvement"
}

CATEGORY_COLORS = {
    "Excellent Outcome": {"text": "text-green-600", "bg": "bg-green-50"},
    "Successful Outcome": {"text": "text-blue-600", "bg": "bg-blue-50"},
    "Moderate Improvement": {"text": "text-yellow-600", "bg": "bg-yellow-50"},
    "Limited Improvement": {"text": "text-orange-600", "bg": "bg-orange-50"},
    "Minimal Improvement": {"text": "text-red-600", "bg": "bg-red-50"},
}

CATEGORY_DESCRIPTIONS = {
    "Excellent Outcome": "Substantial improvement in pain, stiffness, and function expected",
    "Successful Outcome": "Significant improvement in symptoms and daily activities expected",
    "Moderate Improvement": "Noticeable improvement in symptoms expected",
    "Limited Improvement": "Some improvement in symptoms expected",
    "Minimal Improvement": "Limited improvement in symptoms expected",
}


def calculate_success_category(womac_improvement: float) -> str:
    """
    Calculate success category based on WOMAC improvement.
    
    Args:
        womac_improvement: Predicted WOMAC improvement in points
        
    Returns:
        Success category string
    """
    if womac_improvement >= SUCCESS_THRESHOLDS["EXCELLENT"]:
        return SUCCESS_CATEGORIES["EXCELLENT"]
    elif womac_improvement >= SUCCESS_THRESHOLDS["SUCCESSFUL"]:
        return SUCCESS_CATEGORIES["SUCCESSFUL"]
    elif womac_improvement >= SUCCESS_THRESHOLDS["MODERATE"]:
        return SUCCESS_CATEGORIES["MODERATE"]
    elif womac_improvement >= SUCCESS_THRESHOLDS["LIMITED"]:
        return SUCCESS_CATEGORIES["LIMITED"]
    else:
        return SUCCESS_CATEGORIES["MINIMAL"]


def get_success_probability(womac_improvement: float) -> float:
    """
    Convert WOMAC improvement to success probability (0-100%).
    Based on how much improvement exceeds 30-point threshold.
    
    Args:
        womac_improvement: Predicted WOMAC improvement in points
        
    Returns:
        Success probability (0-100)
    """
    if womac_improvement >= SUCCESS_THRESHOLDS["SUCCESSFUL"]:
        # Successful or better: 70-100% probability
        excess_improvement = womac_improvement - SUCCESS_THRESHOLDS["SUCCESSFUL"]
        # Scale from 70% to 100% based on excess improvement
        # Max excess is ~20 points (40-30), so scale by 20
        probability = 70 + (excess_improvement / 20) * 30
        return min(probability, 100.0)
    elif womac_improvement >= SUCCESS_THRESHOLDS["MODERATE"]:
        # Moderate: 40-70% probability
        progress_to_success = (womac_improvement - SUCCESS_THRESHOLDS["MODERATE"]) / 10
        return 40 + (progress_to_success * 30)
    elif womac_improvement >= SUCCESS_THRESHOLDS["LIMITED"]:
        # Limited: 20-40% probability
        progress_to_moderate = (womac_improvement - SUCCESS_THRESHOLDS["LIMITED"]) / 10
        return 20 + (progress_to_moderate * 20)
    else:
        # Minimal: 0-20% probability
        if womac_improvement < 0:
            return 0.0
        return max((womac_improvement / SUCCESS_THRESHOLDS["LIMITED"]) * 20, 0.0)


def get_category_color(category: str) -> dict:
    """
    Get color styling for success category.
    
    Args:
        category: Success category string
        
    Returns:
        Dictionary with text and bg color classes
    """
    return CATEGORY_COLORS.get(category, {"text": "text-gray-600", "bg": "bg-gray-50"})


def get_category_description(category: str) -> str:
    """
    Get description for success category.
    
    Args:
        category: Success category string
        
    Returns:
        Description string
    """
    return CATEGORY_DESCRIPTIONS.get(category, "Outcome prediction available")


def calculate_success_metrics(womac_improvement: float) -> dict:
    """
    Calculate all success metrics for a given WOMAC improvement.
    
    Args:
        womac_improvement: Predicted WOMAC improvement in points
        
    Returns:
        Dictionary with success_category, success_probability, category_color, category_description
    """
    category = calculate_success_category(womac_improvement)
    probability = get_success_probability(womac_improvement)
    colors = get_category_color(category)
    description = get_category_description(category)
    
    return {
        "success_category": category,
        "success_probability": round(probability, 1),
        "category_color": colors,
        "category_description": description,
        # Keep WOMAC data for internal use but mark as internal
        "_womac_improvement": round(womac_improvement, 1),
    }

