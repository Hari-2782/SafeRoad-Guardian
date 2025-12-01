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

# Initialize session state
if 'sample_image' not in st.session_state:
    st.session_state.sample_image = None
if 'sample_gps' not in st.session_state:
    st.session_state.sample_gps = None

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📸 Upload Road Image")
    
    # File upload with better error handling
    uploaded_file = st.file_uploader(
        "Choose a road image (JPG, PNG)",
        type=["jpg", "jpeg", "png"],
        help="Upload a photo of the road to analyze for hazards",
        accept_multiple_files=False
    )
    
    # Show upload status
    if uploaded_file is not None:
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        if file_size_mb > 10:
            st.warning(f"⚠️ Large file ({file_size_mb:.1f}MB). Processing may be slow.")
        else:
            st.success(f"✅ File uploaded: {uploaded_file.name} ({file_size_mb:.2f}MB)")
    
    # GPS input - use session state value if available
    default_gps = st.session_state.sample_gps if st.session_state.sample_gps else ""
    gps_input = st.text_input(
        "📍 GPS Coordinates",
        value=default_gps,
        placeholder="e.g., 35.6762,139.6503",
        help="Enter GPS coordinates in format: latitude,longitude"
    )
    
    # Sample images button
    st.markdown("---")
    st.subheader("Or Try Sample Images")
    
    sample_col1, sample_col2 = st.columns(2)
    
    with sample_col1:
        if st.button("🕳️ Sample Pothole (Tokyo)", width="stretch"):
            st.session_state.sample_image = "sample_images/pothole/United_States_004347.jpg"
            st.session_state.sample_gps = "35.6762,139.6503"
            st.rerun()
    
    with sample_col2:
        if st.button("🏥 Sample Sign (London)", width="stretch"):
            st.session_state.sample_image = "sample_images/roadsign/test_17.jpg"
            st.session_state.sample_gps = "51.5074,-0.1278"
            st.rerun()
    
    # Analyze button
    st.markdown("---")
    analyze_button = st.button("🚀 Analyze Road", type="primary", width="stretch")

with col2:
    st.header("📊 Analysis Results")
    
    # Use session state sample image if no file uploaded
    final_image = uploaded_file if uploaded_file else st.session_state.sample_image
    final_gps = gps_input if gps_input else st.session_state.sample_gps
    
    if final_image and final_gps and analyze_button:
        try:
            # Validate GPS
            if "," not in final_gps or len(final_gps.split(",")) != 2:
                st.error("❌ Invalid GPS format. Use: latitude,longitude")
                st.stop()
            
            # Save uploaded file temporarily
            if isinstance(final_image, str):
                # Sample image path
                image_path = final_image
                if not os.path.exists(image_path):
                    st.error(f"❌ Sample image not found: {image_path}")
                    st.stop()
            else:
                # Uploaded file - save to temp
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                        tmp_file.write(final_image.getvalue())
                        image_path = tmp_file.name
                except Exception as e:
                    st.error(f"❌ Failed to process uploaded file: {str(e)}")
                    st.stop()
            
            # Display image
            try:
                st.image(image_path, caption="Analyzing this image...", use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ Could not display image preview: {str(e)}")
            
            # Run analysis
            with st.spinner("🔍 Analyzing road conditions..."):
                result = run_analysis(image_path, final_gps, for_web=True)
            
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
                
                # Voice alert with audio playback
                should_report = result.get("should_report", False)
                voice_alert = result.get("voice_alert")
                audio_path = result.get("audio_path")
                
                if voice_alert:
                    st.warning(f"🔊 **VOICE ALERT:** {voice_alert}")
                    
                    # Play audio if available
                    if audio_path and os.path.exists(audio_path):
                        try:
                            with open(audio_path, "rb") as audio_file:
                                audio_bytes = audio_file.read()
                            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                        except Exception as e:
                            st.caption("🔇 Audio playback unavailable (text alert shown above)")
                    else:
                        st.caption("🔇 Audio generation unavailable (text alert shown above)")
                
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
