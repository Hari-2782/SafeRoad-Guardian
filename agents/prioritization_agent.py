"""
Prioritization Agent for SafeRoad-Guardian
Decides whether to report based on memory and severity
"""

from typing import Dict, Any
from memory.memory_bank import was_recently_reported


def prioritization_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prioritization agent that determines if a hazard should be reported.
    Uses memory to avoid duplicate reports and assesses severity.
    
    Args:
        state: Current agent state with hazard detection results
        
    Returns:
        Updated state with prioritization decision
    """
    gps = state.get("gps", "unknown")
    hazards = state.get("hazards", "")
    
    # Check if this location was recently reported
    if was_recently_reported(gps, days=7):
        state["should_report"] = False
        state["messages"].append(
            "Prioritization Agent → Location recently reported (within 7 days) → suppressed"
        )
    else:
        # Check if there are actual hazards detected
        if "None" in hazards or "Error" in hazards:
            state["should_report"] = False
            state["messages"].append(
                "Prioritization Agent → No significant hazards detected → low priority"
            )
        else:
            state["should_report"] = True
            state["messages"].append(
                "Prioritization Agent → New high-priority hazard detected → proceed to report"
            )
    
    return state


def route_prioritization(state: Dict[str, Any]) -> str:
    """
    Routing function for prioritization agent.
    
    Args:
        state: Current state
        
    Returns:
        Next node to execute
    """
    if state.get("should_report", False):
        return "report"
    else:
        return "END"
