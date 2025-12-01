"""
SafeRoad-Guardian Web Interface
Simple Streamlit app for easy access to road safety detection
"""

import streamlit as st
import os
from pathlib import Path
import tempfile
from PIL import Image
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run_analysis

# Page config
st.set_page_config(
    page_title="SafeRoad-Guardian",
    page_icon="🛣️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🛣️ SafeRoad-Guardian</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Road Safety Monitoring with Voice Alerts & Authority Reporting</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://raw.githubusercontent.com/ultralytics/assets/main/yolov8/banner-yolov8.png", width=250)
    st.header("About")
    st.markdown("""
    **SafeRoad-Guardian** uses:
    - 🤖 **4 AI Agents** (LangGraph)
    - 👁️ **Dual YOLO Models** (Pothole + Signs)
    - 🧠 **Google Gemini** (3 agents)
    - 💾 **ChromaDB Memory** (Deduplication)
    - 🔊 **Voice Alerts** (Gemini-powered)
    - 📱 **Authority Reports** (WhatsApp/Email ready)
    """)
    
    st.header("How It Works")
    st.markdown("""
    1. Upload road image
    2. Enter GPS coordinates
    3. Click "Analyze Road"
    4. Get instant results:
       - Hazard detection
       - Voice alert
       - Authority report
       - Memory check
    """)
    
    st.header("GitHub")
    st.markdown("[View Source Code](https://github.com/Hari-2782/SafeRoad-Guardian)")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📸 Upload Road Image")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a road image (JPG, PNG)",
        type=["jpg", "jpeg", "png"],
        help="Upload a photo of the road to analyze for hazards"
    )
    
    # GPS input
    gps_input = st.text_input(
        "📍 GPS Coordinates",
        placeholder="e.g., 35.6762,139.6503",
        help="Enter GPS coordinates in format: latitude,longitude"
    )
    
    # Sample images button
    st.markdown("---")
    st.subheader("Or Try Sample Images")
    
    sample_col1, sample_col2 = st.columns(2)
    
    with sample_col1:
        if st.button("🕳️ Sample Pothole (Tokyo)", use_container_width=True):
            uploaded_file = "sample_images/pothole/United_States_004347.jpg"
            gps_input = "35.6762,139.6503"
            st.success("Sample loaded!")
    
    with sample_col2:
        if st.button("🏥 Sample Sign (London)", use_container_width=True):
            uploaded_file = "sample_images/roadsign/test_17.jpg"
            gps_input = "51.5074,-0.1278"
            st.success("Sample loaded!")
    
    # Analyze button
    st.markdown("---")
    analyze_button = st.button("🚀 Analyze Road", type="primary", use_container_width=True)

with col2:
    st.header("📊 Analysis Results")
    
    if uploaded_file and gps_input and analyze_button:
        try:
            # Validate GPS
            if "," not in gps_input or len(gps_input.split(",")) != 2:
                st.error("❌ Invalid GPS format. Use: latitude,longitude")
                st.stop()
            
            # Save uploaded file temporarily
            if isinstance(uploaded_file, str):
                # Sample image path
                image_path = uploaded_file
            else:
                # Uploaded file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    image_path = tmp_file.name
            
            # Display image
            st.image(image_path, caption="Uploaded Image", use_container_width=True)
            
            # Run analysis
            with st.spinner("🔍 Analyzing road conditions..."):
                result = run_analysis(image_path, gps_input)
            
            # Display results
            if result.get("error"):
                st.error("❌ Analysis failed. Please check your inputs.")
            else:
                # Success message
                st.success("✅ Analysis completed successfully!")
                
                # Hazards
                hazards = result.get("hazards", "None")
                if "None" not in hazards:
                    st.error(f"⚠️ **HAZARD DETECTED:** {hazards}")
                else:
                    st.success("✅ No hazards detected")
                
                # Signs
                signs = result.get("signs", "None")
                if "None" not in signs:
                    st.info(f"🚸 **ROAD SIGNS:** {signs}")
                
                # Voice alert
                should_report = result.get("should_report", False)
                if should_report:
                    st.warning("🔊 **VOICE ALERT TRIGGERED**")
                    st.markdown("*Voice alert would play through speakers in actual usage*")
                
                # Memory check
                if not should_report and "None" not in hazards:
                    st.info("💾 **MEMORY:** Location already reported within 7 days")
                
                # Full report
                with st.expander("📄 View Full Report"):
                    report = result.get("report", "No report generated")
                    st.code(report, language="text")
                
                # Authority report (if generated)
                if should_report and "None" not in hazards:
                    with st.expander("📱 Authority Report (WhatsApp/Email Ready)"):
                        st.markdown(f"""
                        **GPS:** {gps_input}  
                        **Google Maps:** [Open Location](https://maps.google.com/?q={gps_input})  
                        **Severity:** HIGH  
                        **Findings:** {hazards} | {signs}  
                        **Photo:** Attached (base64 encoded)
                        
                        **Ready to send to:**
                        - Sri Lanka RDA: rda@transport.gov.lk
                        - India PWD: complaints@pwd.gov.in
                        - US 311: Via mobile app
                        - UK FixMyStreet: https://fixmystreet.com
                        """)
            
            # Cleanup temp file
            if not isinstance(uploaded_file, str):
                try:
                    os.unlink(image_path)
                except:
                    pass
                    
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)
    
    elif not uploaded_file:
        st.info("👈 Upload an image to get started")
    elif not gps_input:
        st.warning("📍 Please enter GPS coordinates")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with ❤️ using LangGraph, Gemini, YOLO, and ChromaDB</p>
    <p>SafeRoad-Guardian © 2025 | <a href='https://github.com/Hari-2782/SafeRoad-Guardian'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)
