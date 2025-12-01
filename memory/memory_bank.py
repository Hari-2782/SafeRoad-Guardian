"""
Memory Bank for SafeRoad-Guardian
Uses ChromaDB to store and retrieve road hazard reports
"""

import chromadb
from datetime import datetime, timedelta
from typing import Dict, List, Optional


# Initialize ChromaDB persistent client
client = chromadb.PersistentClient(path="memory_db")
collection = client.get_or_create_collection("road_hazards")


def save_report(gps: str, hazards: str, signs: str, image_path: str) -> None:
    """
    Save a hazard report to the memory bank.
    
    Args:
        gps: GPS coordinates (e.g., "6.9271,79.8612")
        hazards: Hazard detection results
        signs: Sign detection results
        image_path: Path to the analyzed image
    """
    timestamp = datetime.now().isoformat()
    doc_id = f"{gps}_{timestamp}"
    
    collection.add(
        ids=[doc_id],
        documents=[f"Hazards: {hazards} | Signs: {signs}"],
        metadatas=[{
            "gps": gps,
            "image": image_path,
            "timestamp": timestamp,
            "hazards": hazards,
            "signs": signs
        }]
    )
    print(f"✓ Report saved to memory bank: {doc_id}")


def was_recently_reported(gps: str, days: int = 7) -> bool:
    """
    Check if a location was recently reported within the specified number of days.
    
    Args:
        gps: GPS coordinates to check
        days: Number of days to look back (default: 7)
        
    Returns:
        True if location was recently reported, False otherwise
    """
    try:
        results = collection.query(
            query_texts=[f"GPS: {gps}"],
            n_results=10
        )
        
        if not results["ids"][0]:
            return False
        
        # Check if any result is within the time window
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for metadata in results["metadatas"][0]:
            if metadata and "timestamp" in metadata:
                report_date = datetime.fromisoformat(metadata["timestamp"])
                if report_date > cutoff_date and metadata.get("gps") == gps:
                    return True
        
        return False
    
    except Exception as e:
        print(f"Warning: Error checking recent reports: {e}")
        return False


def get_location_history(gps: str, limit: int = 5) -> List[Dict]:
    """
    Get historical reports for a specific location.
    
    Args:
        gps: GPS coordinates
        limit: Maximum number of reports to retrieve
        
    Returns:
        List of report metadata dictionaries
    """
    try:
        results = collection.query(
            query_texts=[f"GPS: {gps}"],
            n_results=limit
        )
        
        if results["metadatas"][0]:
            return results["metadatas"][0]
        return []
    
    except Exception as e:
        print(f"Warning: Error retrieving location history: {e}")
        return []


def get_all_reports(limit: int = 100) -> List[Dict]:
    """
    Get all stored reports.
    
    Args:
        limit: Maximum number of reports to retrieve
        
    Returns:
        List of all report metadata
    """
    try:
        results = collection.get(limit=limit)
        if results["metadatas"]:
            return results["metadatas"]
        return []
    
    except Exception as e:
        print(f"Warning: Error retrieving all reports: {e}")
        return []
