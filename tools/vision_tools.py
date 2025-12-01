"""
Vision Tools for SafeRoad-Guardian
Two custom tools for detecting road hazards and assessing road signs
"""

from ultralytics import YOLO
from typing import Dict, List
import cv2
import numpy as np

# Load YOLO models
pothole_model = YOLO("models/pothole_model.pt")        # your first model
sign_model = YOLO("models/roadsign_best.pt")          # your second model


def detect_road_hazards(image_path: str) -> str:
    """
    Detect potholes and other road hazards using YOLO model.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        String description of detected hazards
    """
    img = cv2.imread(image_path)
    if img is None:
        return "Hazards: Error reading image"
    
    results = pothole_model(img)[0]
    detections = []
    
    for box in results.boxes:
        label = results.names[int(box.cls)]
        conf = box.conf.item()
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        size = (x2 - x1) * (y2 - y1)
        detections.append(f"{label} (conf {conf:.2f}, size {size}px)")
    
    return "Hazards: " + (" | ".join(detections) if detections else "None")


def detect_and_assess_signs(image_path: str) -> str:
    """
    Detect road signs and assess their condition using YOLO model.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        String description of detected signs and their condition
    """
    img = cv2.imread(image_path)
    if img is None:
        return "Signs: Error reading image"
    
    results = sign_model(img)[0]
    detections = []
    
    for box in results.boxes:
        label = results.names[int(box.cls)]
        conf = box.conf.item()
        
        # Extract crop for condition assessment
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        crop = img[y1:y2, x1:x2]
        
        if crop.size > 0:
            # Simple "faded" logic based on brightness
            brightness = np.mean(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY))
            condition = "faded" if brightness < 80 else "good"
        else:
            condition = "unknown"
        
        detections.append(f"{label} ({condition}, conf {conf:.2f})")
    
    return "Signs: " + (" | ".join(detections) if detections else "None")
