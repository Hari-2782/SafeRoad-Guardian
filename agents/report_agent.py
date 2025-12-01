"""
Report Agent for SafeRoad-Guardian
Generates comprehensive reports and saves to memory
"""

from typing import Dict, Any
from memory.memory_bank import save_report
from datetime import datetime
from tools.authority_reporter import send_to_authority, check_if_authority_notified
from tools.professional_voice import speak_professional


def report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Report agent that generates comprehensive hazard reports.
    
    Args:
        state: Current agent state with all detection results
        
    Returns:
        Updated state with generated report
    """
    gps = state.get("gps", "unknown")
    image_path = state.get("image_path", "")
    hazards = state.get("hazards", "None")
    signs = state.get("signs", "None")
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create comprehensive report
    report_lines = [
        "=" * 60,
        "SAFEROAD-GUARDIAN HAZARD REPORT",
        "=" * 60,
        f"Timestamp: {timestamp}",
        f"Location (GPS): {gps}",
        f"Image Source: {image_path}",
        "-" * 60,
        "DETECTION RESULTS:",
        hazards,
        signs,
        "-" * 60,
        "AGENT WORKFLOW LOG:",
    ]
    
    # Add all messages from workflow
    for msg in state["messages"]:
        report_lines.append(f"  • {msg}")
    
    report_lines.append("=" * 60)
    
    full_report = "\n".join(report_lines)
    
    # Save to memory
    save_report(gps, hazards, signs, image_path)
    
    # Add to state
    state["report"] = full_report
    state["messages"].append(f"Report Agent → Generated and saved comprehensive report for {gps}")
    
    # Print report to console
    print("\n" + full_report + "\n")
    
    # Voice alerts and authority reporting are handled in main.py after graph completes
    # to avoid duplication and ensure proper output sequencing
    
    return state
