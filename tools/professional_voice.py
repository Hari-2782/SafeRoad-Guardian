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


def speak_professional(hazard: str, severity: str = "normal", play_audio: bool = False, return_audio_path: bool = False) -> str:
    """
    Generate and optionally play professional voice alert.
    Uses Gemini to generate natural emergency-style text.
    
    Args:
        hazard: Description of the hazard (e.g., "Deep pothole detected")
        severity: "low", "normal", "high", or "critical"
        play_audio: Whether to actually play audio (requires pygame)
        return_audio_path: If True, return tuple (text, audio_path) for web apps
        
    Returns:
        The alert text that would be spoken, or tuple (text, audio_path) if return_audio_path=True
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
    
    audio_path = None
    
    # Play audio if requested and available
    if (play_audio or return_audio_path) and REQUESTS_AVAILABLE:
        try:
            audio_path = download_alert_audio(alert_text)
            if play_audio and PYGAME_AVAILABLE:
                play_audio_file(audio_path)
        except Exception as e:
            print(f"   ⚠️  Audio generation failed: {e}")
            print(f"   📢 Text alert: {alert_text}\n")
    elif play_audio:
        print("   ℹ️  Audio playback requires: pip install requests")
        print(f"   📢 Text alert: {alert_text}\n")
    
    if return_audio_path:
        return (alert_text, audio_path)
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


def download_alert_audio(text: str) -> str:
    """
    Convert text to speech and download audio file.
    
    Args:
        text: Text to convert to speech
        
    Returns:
        Path to audio file
    """
    if not REQUESTS_AVAILABLE:
        return None
    
    # Try multiple TTS services in order
    audio_file = None
    
    # Method 1: Google Translate TTS with better headers
    try:
        import urllib.parse
        text_encoded = urllib.parse.quote(text)
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q={text_encoded}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://translate.google.com/'
        }
        
        response = requests.get(tts_url, headers=headers, timeout=10)
        
        if response.status_code == 200 and len(response.content) > 100:
            # Save to temporary file with unique name
            temp_dir = tempfile.gettempdir()
            audio_file = Path(temp_dir) / f"saferoad_alert_{int(time.time() * 1000)}.mp3"
            
            with open(audio_file, "wb") as f:
                f.write(response.content)
            
            return str(audio_file)
    except Exception as e:
        print(f"   ⚠️  TTS attempt 1 failed: {e}")
    
    # Method 2: Try alternative Google TTS endpoint
    try:
        import urllib.parse
        text_encoded = urllib.parse.quote(text)
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={text_encoded}&tl=en&total=1&idx=0&textlen={len(text)}&client=gtx"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://translate.google.com/'
        }
        
        response = requests.get(tts_url, headers=headers, timeout=10)
        
        if response.status_code == 200 and len(response.content) > 100:
            temp_dir = tempfile.gettempdir()
            audio_file = Path(temp_dir) / f"saferoad_alert_{int(time.time() * 1000)}.mp3"
            
            with open(audio_file, "wb") as f:
                f.write(response.content)
            
            return str(audio_file)
    except Exception as e:
        print(f"   ⚠️  TTS attempt 2 failed: {e}")
    
    # If all methods fail, return None
    print(f"   ⚠️  All TTS methods failed. Audio not available.")
    return None


def play_audio_file(audio_path: str) -> None:
    """
    Play audio file using pygame.
    
    Args:
        audio_path: Path to audio file
    """
    if not PYGAME_AVAILABLE or not audio_path:
        return
    
    # Play audio
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    
    # Wait for playback to complete
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    
    # Cleanup
    pygame.mixer.quit()
    try:
        Path(audio_path).unlink()
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
