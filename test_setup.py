"""
Test script for SafeRoad-Guardian
Run basic tests to ensure everything is working
"""

import os
import sys
from pathlib import Path


def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
    except ImportError:
        print("✗ OpenCV import failed - run: pip install opencv-python")
        return False
    
    try:
        from ultralytics import YOLO
        print("✓ Ultralytics YOLO imported successfully")
    except ImportError:
        print("✗ Ultralytics import failed - run: pip install ultralytics")
        return False
    
    try:
        import chromadb
        print("✓ ChromaDB imported successfully")
    except ImportError:
        print("✗ ChromaDB import failed - run: pip install chromadb")
        return False
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✓ LangChain Google GenAI imported successfully")
    except ImportError:
        print("✗ LangChain Google GenAI import failed - run: pip install langchain-google-genai")
        return False
    
    try:
        from langgraph.graph import StateGraph
        print("✓ LangGraph imported successfully")
    except ImportError:
        print("✗ LangGraph import failed - run: pip install langgraph")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ Python-dotenv imported successfully")
    except ImportError:
        print("✗ Python-dotenv import failed - run: pip install python-dotenv")
        return False
    
    return True


def test_environment():
    """Test environment configuration."""
    print("\nTesting environment...")
    
    # Check for .env file
    if not os.path.exists(".env"):
        print("✗ .env file not found")
        print("  Create .env file and add: GEMINI_API_KEY=your_key_here")
        return False
    else:
        print("✓ .env file exists")
    
    # Load and check API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("✗ GEMINI_API_KEY not configured")
        print("  Add your actual API key to .env file")
        return False
    else:
        print("✓ GEMINI_API_KEY is configured")
    
    return True


def test_models():
    """Test that model files exist."""
    print("\nTesting model files...")
    
    models_dir = Path("models")
    
    pothole_model = models_dir / "pothole_model.pt"
    if not pothole_model.exists():
        print("✗ pothole_model.pt not found in models/")
        print("  Upload your trained model to models/pothole_model.pt")
        return False
    else:
        print("✓ pothole_model.pt found")
    
    sign_model = models_dir / "roadsign_best.pt"
    if not sign_model.exists():
        print("✗ roadsign_best.pt not found in models/")
        print("  Upload your trained model to models/roadsign_best.pt")
        return False
    else:
        print("✓ roadsign_best.pt found")
    
    return True


def test_structure():
    """Test project structure."""
    print("\nTesting project structure...")
    
    required_dirs = [
        "agents",
        "tools",
        "memory",
        "models",
        "sample_images"
    ]
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name}/ directory exists")
        else:
            print(f"✗ {dir_name}/ directory missing")
            return False
    
    required_files = [
        "main.py",
        "requirements.txt",
        ".gitignore",
        "README.md"
    ]
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"✓ {file_name} exists")
        else:
            print(f"✗ {file_name} missing")
            return False
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("SafeRoad-Guardian System Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Project Structure", test_structure()))
    results.append(("Package Imports", test_imports()))
    results.append(("Environment Config", test_environment()))
    results.append(("Model Files", test_models()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to run SafeRoad-Guardian.")
        print("\nTry running:")
        print("  python main.py sample_images/your_image.jpg")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
