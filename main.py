"""
SafeRoad-Guardian Main Application
Multi-agent system using LangGraph for road safety monitoring
"""

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, List, Annotated
import operator
import os
from dotenv import load_dotenv

# Import agents
from agents.supervisor import supervisor_node, route_supervisor
from agents.vision_agent import vision_node
from agents.prioritization_agent import prioritization_node, route_prioritization
from agents.report_agent import report_node

# Load environment variables
load_dotenv()


# Define the agent state
class AgentState(TypedDict):
    """State shared across all agents in the workflow."""
    image_path: str
    gps: str
    messages: Annotated[List[str], operator.add]
    hazards: str
    signs: str
    should_report: bool
    report: str
    error: bool


# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.getenv("GEMINI_API_KEY")
)


def create_graph():
    """
    Create the LangGraph workflow with all agents.
    
    Returns:
        Compiled LangGraph application
    """
    # Initialize the graph
    graph = StateGraph(AgentState)
    
    # Add nodes (agents)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("vision", vision_node)
    graph.add_node("prioritization", prioritization_node)
    graph.add_node("report", report_node)
    
    # Define the workflow edges
    graph.set_entry_point("supervisor")
    
    # Supervisor routes to vision or ends if error
    graph.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "vision": "vision",
            "END": END
        }
    )
    
    # Vision always goes to prioritization
    graph.add_edge("vision", "prioritization")
    
    # Prioritization decides whether to report or end
    graph.add_conditional_edges(
        "prioritization",
        route_prioritization,
        {
            "report": "report",
            "END": END
        }
    )
    
    # Report always ends the workflow
    graph.add_edge("report", END)
    
    # Compile the graph
    return graph.compile()


def run_analysis(image_path: str, gps: str = "6.9271,79.8612"):
    """
    Run the complete road safety analysis pipeline.
    
    Args:
        image_path: Path to the image to analyze
        gps: GPS coordinates (default: Colombo, Sri Lanka)
        
    Returns:
        Final state with analysis results
    """
    # Create the graph
    app = create_graph()
    
    # Initialize state
    initial_state = {
        "image_path": image_path,
        "gps": gps,
        "messages": [],
        "hazards": "",
        "signs": "",
        "should_report": False,
        "report": "",
        "error": False
    }
    
    # Run the workflow
    print(f"\n{'='*60}")
    print("Starting SafeRoad-Guardian Analysis Pipeline")
    print(f"{'='*60}\n")
    
    result = app.invoke(initial_state)
    
    return result


# Main execution
if __name__ == "__main__":
    import sys
    
    # Check if image path is provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        gps = sys.argv[2] if len(sys.argv) > 2 else "6.9271,79.8612"
    else:
        # Default test image
        image_path = "sample_images/pothole_colombo.jpg"
        gps = "6.9271,79.8612"
    
    # Run the analysis
    try:
        result = run_analysis(image_path, gps)
        
        # Display results
        if result.get("report"):
            print("\n" + result["report"] + "\n")
        
        # Check if we should report (not a duplicate)
        should_report = result.get("should_report", True)
        
        # Show voice alert and authority report if hazards detected AND should report
        hazards = result.get("hazards", "")
        signs = result.get("signs", "")
        
        # Voice alerts for HAZARDS (potholes, cracks)
        if hazards and "None" not in hazards and should_report:
            # Import here to trigger voice and authority after graph completes
            from tools.professional_voice import speak_professional
            from tools.authority_reporter import send_to_authority
            
            # Get Gemini-assessed severity (or default to HIGH)
            severity = result.get("severity", "HIGH")
            hazard_desc = "Road hazard detected"
            
            # Play voice alert
            speak_professional(hazard_desc, severity.lower(), play_audio=True)
            
            # Generate authority report with Gemini-assessed severity
            authority_report = send_to_authority(
                image_path=image_path,
                gps=gps,
                findings=f"{hazards} | {signs}",
                severity=severity
            )
        
        # Voice alerts for ROAD SIGNS (hospital, school, crossing)
        elif signs and "None" not in signs:
            from tools.professional_voice import speak_professional
            
            # Determine sign type and generate appropriate alert
            sign_type = signs.lower()
            
            if "hospital" in sign_type:
                speak_professional("Hospital crossing ahead. Reduce speed and no horn zone", "low", play_audio=True)
            elif "school" in sign_type:
                speak_professional("School zone ahead. Reduce speed and watch for children", "normal", play_audio=True)
            elif "crossing" in sign_type or "pedestrian" in sign_type:
                speak_professional("Pedestrian crossing ahead. Reduce speed and stay alert", "normal", play_audio=True)
            elif "stop" in sign_type:
                speak_professional("Stop sign ahead. Prepare to stop", "low", play_audio=True)
            elif "yield" in sign_type:
                speak_professional("Yield sign ahead. Prepare to give way", "low", play_audio=True)
            else:
                speak_professional("Road sign detected. Stay alert", "low", play_audio=True)
            
            print("\n📋 ====================================================================")
            print(f"   ROAD SIGN ALERT: {signs}")
            print("   Informational - No authority report needed")
            print("   ====================================================================\n")
        
        # Show duplicate message if hazards but already reported
        elif hazards and "None" not in hazards and not should_report:
            print("\n💾 ====================================================================")
            print("   MEMORY: Location already reported within 7 days")
            print("   Skipping duplicate authority notification")
            print("   ====================================================================\n")
        
        print("\n✓ Analysis completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
