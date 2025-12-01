"""
Prioritization Agent for SafeRoad-Guardian
Decides whether to report based on memory and severity
Uses Gemini LLM for intelligent severity assessment
"""

from typing import Dict, Any
from memory.memory_bank import was_recently_reported
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini LLM for severity assessment
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.getenv("GEMINI_API_KEY")
)


def prioritization_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prioritization agent that determines if a hazard should be reported.
    Uses Gemini LLM for intelligent severity assessment and memory for deduplication.
    
    Args:
        state: Current agent state with hazard detection results
        
    Returns:
        Updated state with prioritization decision
    """
    gps = state.get("gps", "unknown")
    hazards = state.get("hazards", "")
    signs = state.get("signs", "")
    
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
            # Use Gemini to assess severity intelligently
            try:
                prompt = f"""Analyze this road safety detection and provide severity (HIGH/MEDIUM/LOW) in ONE WORD ONLY:
Hazards: {hazards}
Signs: {signs}
GPS: {gps}

Consider: pothole size, confidence scores, sign conditions. Reply with just: HIGH, MEDIUM, or LOW"""
                
                response = llm.invoke(prompt)
                severity = response.content if hasattr(response, 'content') else "HIGH"
                severity = severity.strip().upper().split()[0]  # Extract first word
                
                if severity not in ["HIGH", "MEDIUM", "LOW"]:
                    severity = "HIGH"  # Default to HIGH if unclear
                
                state["severity"] = severity
                state["messages"].append(
                    f"Prioritization Agent (Gemini) → Severity assessed as {severity} → proceed to report"
                )
            except Exception as e:
                # Fallback severity assessment
                state["severity"] = "HIGH"
                state["messages"].append(
                    f"Prioritization Agent → New high-priority hazard detected → proceed to report"
                )
            
            state["should_report"] = True
    
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
