"""
Supervisor Agent for SafeRoad-Guardian
Orchestrates the multi-agent workflow
"""

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.getenv("GEMINI_API_KEY")
)


def supervisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Supervisor agent that coordinates the overall workflow.
    Uses Gemini LLM for intelligent workflow decisions.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with supervisor's decisions
    """
    # Use Gemini LLM to generate context-aware workflow message
    image_name = state.get("image_path", "unknown").split("/")[-1].split("\\")[-1]
    gps = state.get("gps", "unknown")
    
    try:
        # Gemini generates intelligent workflow initiation message
        prompt = f"Generate a brief professional message (max 10 words) for initiating road safety analysis for image: {image_name} at GPS: {gps}"
        response = llm.invoke(prompt)
        workflow_msg = response.content if hasattr(response, 'content') else str(response)
        state["messages"].append(f"Supervisor Agent (Gemini) → {workflow_msg}")
    except:
        state["messages"].append("Supervisor Agent → Initiating road safety analysis pipeline")
    
    # Determine workflow based on image availability
    if "image_path" not in state or not state["image_path"]:
        state["messages"].append("Supervisor Agent → ERROR: No image provided")
        state["error"] = True
    else:
        state["messages"].append(f"Supervisor Agent → Validated input: {state['image_path']}")
        state["error"] = False
    
    return state


def route_supervisor(state: Dict[str, Any]) -> str:
    """
    Routing function for the supervisor.
    
    Args:
        state: Current state
        
    Returns:
        Next node to execute
    """
    if state.get("error"):
        return "END"
    return "vision"
