"""
Vision Agent for SafeRoad-Guardian
Analyzes images using YOLO models to detect hazards and signs
"""

from typing import Dict, Any
from tools.vision_tools import detect_road_hazards, detect_and_assess_signs


def vision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Vision agent that processes images to detect hazards and road signs.
    
    Args:
        state: Current agent state containing image_path
        
    Returns:
        Updated state with detection results
    """
    image_path = state["image_path"]
    
    # Detect road hazards (potholes, etc.)
    hazards = detect_road_hazards(image_path)
    state["hazards"] = hazards
    
    # Detect and assess road signs
    signs = detect_and_assess_signs(image_path)
    state["signs"] = signs
    
    # Log to messages
    state["messages"].append(f"Vision Agent → {hazards}")
    state["messages"].append(f"Vision Agent → {signs}")
    
    return state
