"""
Professional Voice Alert System for SafeRoad-Guardian
Emergency-style voice alerts like premium car navigation systems
"""

import os
import time
import tempfile
from pathlib import Path
from typing import Optional
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from google import generativeai as genai
    from google.generativeai import GenerativeModel
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def speak_professional(hazard: str, severity: str = "normal", play_audio: bool = False) -> str:
    """
    Generate and optionally play professional voice alert.
    Uses Gemini to generate natural emergency-style text.
    
    Args:
        hazard: Description of the hazard (e.g., "Deep pothole detected")
        severity: "low", "normal", "high", or "critical"
        play_audio: Whether to actually play audio (requires pygame)
        
    Returns:
        The alert text that would be spoken
    """
    # Map severity to emergency language
    severity_map = {
        "low": "CAUTION",
        "normal": "WARNING", 
        "high": "DANGER",
        "critical": "CRITICAL DANGER"
    }
    severity_text = severity_map.get(severity.lower(), "WARNING")
    
    # Generate natural alert text using Gemini
    alert_text = generate_alert_text(hazard, severity_text)
    
    # Print the alert
    print("\n" + "🔊 " + "="*68)
    print(f"   VOICE ALERT: {alert_text}")
    print("   " + "="*68 + "\n")
    
    # Play audio if requested and available
    if play_audio and PYGAME_AVAILABLE and REQUESTS_AVAILABLE:
        try:
            play_alert_audio(alert_text)
        except Exception as e:
            print(f"   ⚠️  Audio playback failed: {e}")
            print(f"   📢 Text alert: {alert_text}\n")
    elif play_audio:
        print("   ℹ️  Audio playback requires: pip install pygame requests")
        print(f"   📢 Text alert: {alert_text}\n")
    
    return alert_text


def generate_alert_text(hazard: str, severity_text: str) -> str:
    """
    Generate natural emergency-style alert text.
    
    Args:
        hazard: Hazard description
        severity_text: Severity level text
        
    Returns:
        Natural alert text
    """
    # Try using Gemini for natural text generation
    if GENAI_AVAILABLE:
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key and api_key != "your_gemini_api_key_here":
                genai.configure(api_key=api_key)
                model = GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""You are an emergency road safety alert system. Generate a SHORT, CLEAR voice alert (maximum 8-10 words) like a premium car navigation system.

Hazard: {hazard}
Severity: {severity_text}

Requirements:
- Professional and calm tone
- Clear and direct
- Emergency-appropriate language
- NO quotes, NO explanations
- Just the alert text

Example: "Caution. Large pothole detected ahead."
"""
                
                response = model.generate_content(prompt)
                alert = response.text.strip().strip('"').strip("'").strip('`')
                
                # Clean up any markdown or extra formatting
                if '\n' in alert:
                    alert = alert.split('\n')[0]
                
                return alert
        except Exception as e:
            print(f"   ⚠️  Gemini generation failed: {e}")
    
    # Fallback to template-based generation
    templates = {
        "CAUTION": f"Caution. {hazard}.",
        "WARNING": f"Warning. {hazard} detected ahead.",
        "DANGER": f"Danger. {hazard}. Use caution.",
        "CRITICAL DANGER": f"Critical danger. {hazard}. Immediate attention required."
    }
    
    return templates.get(severity_text, f"Alert. {hazard}.")


def play_alert_audio(text: str) -> None:
    """
    Convert text to speech and play audio.
    
    Args:
        text: Text to convert to speech
    """
    if not PYGAME_AVAILABLE or not REQUESTS_AVAILABLE:
        return
    
    # Use Google Translate TTS (free, no API key needed)
    # In production, use proper TTS API
    text_encoded = text.replace(' ', '+')
    tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q={text_encoded}"
    
    # Download audio
    response = requests.get(tts_url, headers={
        'User-Agent': 'Mozilla/5.0'
    })
    
    if response.status_code != 200:
        raise Exception(f"TTS API returned status {response.status_code}")
    
    # Save to temporary file
    temp_dir = tempfile.gettempdir()
    audio_file = Path(temp_dir) / "saferoad_alert.mp3"
    
    with open(audio_file, "wb") as f:
        f.write(response.content)
    
    # Play audio
    pygame.mixer.init()
    pygame.mixer.music.load(str(audio_file))
    pygame.mixer.music.play()
    
    # Wait for playback to complete
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    
    # Cleanup
    pygame.mixer.quit()
    try:
        audio_file.unlink()
    except:
        pass


def alert_with_countdown(hazard: str, severity: str = "high", seconds: int = 5) -> None:
    """
    Generate voice alert with visual countdown.
    
    Args:
        hazard: Hazard description
        severity: Severity level
        seconds: Countdown duration
    """
    alert_text = speak_professional(hazard, severity, play_audio=False)
    
    print(f"   ⏱️  Alert countdown: ", end='', flush=True)
    for i in range(seconds, 0, -1):
        print(f"{i}... ", end='', flush=True)
        time.sleep(1)
    print("GO!\n")


def test_voice_system():
    """Test the voice alert system."""
    print("\n🔊 Testing SafeRoad-Guardian Voice Alert System\n")
    print("="*70)
    
    # Test different severity levels
    test_cases = [
        ("Small crack detected", "low"),
        ("Pothole ahead", "normal"),
        ("Large pothole detected", "high"),
        ("Critical road damage", "critical")
    ]
    
    for hazard, severity in test_cases:
        speak_professional(hazard, severity)
        time.sleep(1)
    
    print("="*70)
    print("✅ Voice system test complete!\n")


if __name__ == "__main__":
    # Run test when executed directly
    test_voice_system()
