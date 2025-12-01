"""
SafeRoad-Guardian Tools Package
Vision detection tools using YOLO models
"""

from .vision_tools import detect_road_hazards, detect_and_assess_signs
from .authority_reporter import send_to_authority, check_if_authority_notified, generate_authority_email
from .professional_voice import speak_professional, alert_with_countdown

__all__ = [
    'detect_road_hazards',
    'detect_and_assess_signs',
    'send_to_authority',
    'check_if_authority_notified',
    'generate_authority_email',
    'speak_professional',
    'alert_with_countdown'
]
