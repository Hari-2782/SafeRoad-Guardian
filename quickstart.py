"""
Quick Start Script for SafeRoad-Guardian
Runs a simple demo with basic checks
"""

import os
import sys
from pathlib import Path


def print_banner():
    """Print welcome banner."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║          🛣️  SAFEROAD-GUARDIAN QUICK START  🛣️           ║
    ║                                                           ║
    ║     AI-Powered Road Safety Monitoring System             ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)


def check_prerequisites():
    """Check if basic prerequisites are met."""
    print("\n[1/4] Checking prerequisites...")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("❌ Python 3.8+ required")
    else:
        print("  ✓ Python version OK")
    
    # Check .env file
    if not Path(".env").exists():
        issues.append("❌ .env file not found - copy from .env.example")
    else:
        print("  ✓ .env file exists")
    
    # Check model files
    if not Path("models/pothole_model.pt").exists():
        issues.append("❌ pothole_model.pt missing in models/ folder")
    else:
        print("  ✓ Pothole model found")
    
    if not Path("models/road_sign_model.pt").exists():
        issues.append("❌ road_sign_model.pt missing in models/ folder")
    else:
        print("  ✓ Road sign model found")
    
    return issues


def check_dependencies():
    """Check if required packages are installed."""
    print("\n[2/4] Checking dependencies...")
    
    required_packages = [
        ('ultralytics', 'YOLO'),
        ('cv2', 'OpenCV'),
        ('chromadb', 'ChromaDB'),
        ('langgraph', 'LangGraph'),
        ('langchain_google_genai', 'LangChain Google GenAI'),
        ('dotenv', 'Python-dotenv')
    ]
    
    missing = []
    
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {name} installed")
        except ImportError:
            missing.append(name)
            print(f"  ❌ {name} NOT installed")
    
    return missing


def check_environment():
    """Check environment configuration."""
    print("\n[3/4] Checking environment configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "your_gemini_api_key_here":
        print("  ❌ GEMINI_API_KEY not configured")
        return False
    else:
        print("  ✓ GEMINI_API_KEY configured")
        return True


def find_sample_image():
    """Find a sample image to test with."""
    sample_dir = Path("sample_images")
    
    if not sample_dir.exists():
        return None
    
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        images = list(sample_dir.glob(ext))
        if images:
            return str(images[0])
    
    return None


def run_demo():
    """Run a demo analysis."""
    print("\n[4/4] Running demo analysis...")
    
    sample_image = find_sample_image()
    
    if not sample_image:
        print("\n  ℹ️  No sample images found in sample_images/ folder")
        print("  Please add a test image and run:")
        print("    python main.py sample_images/your_image.jpg")
        return
    
    print(f"\n  Using sample image: {sample_image}")
    print("  Starting analysis...\n")
    print("  " + "="*60 + "\n")
    
    try:
        from main import run_analysis
        result = run_analysis(sample_image)
        
        print("\n  " + "="*60)
        print("\n  ✅ Demo completed successfully!")
        print("\n  Next steps:")
        print("    1. Add your own images to sample_images/")
        print("    2. Run: python main.py sample_images/your_image.jpg")
        print("    3. Check memory_db/ for saved reports")
        print("    4. See README.md for full documentation")
        
    except Exception as e:
        print(f"\n  ❌ Error during demo: {e}")
        print("\n  Troubleshooting:")
        print("    - Ensure model weights are in models/ folder")
        print("    - Check that .env has valid GEMINI_API_KEY")
        print("    - Run: python test_setup.py for detailed checks")


def main():
    """Main entry point."""
    print_banner()
    
    # Check prerequisites
    prereq_issues = check_prerequisites()
    
    if prereq_issues:
        print("\n⚠️  Issues found:")
        for issue in prereq_issues:
            print(f"  {issue}")
        print("\nPlease fix these issues and try again.")
        print("See SETUP.md for detailed instructions.")
        return 1
    
    # Check dependencies
    missing_deps = check_dependencies()
    
    if missing_deps:
        print("\n⚠️  Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nInstall them with:")
        print("  pip install -r requirements.txt")
        return 1
    
    # Check environment
    if not check_environment():
        print("\n⚠️  Environment not configured")
        print("\nSteps:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your GEMINI_API_KEY to .env")
        print("  3. Get API key from: https://makersuite.google.com/app/apikey")
        return 1
    
    # Run demo
    run_demo()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
