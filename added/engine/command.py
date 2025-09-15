import pyttsx3
import eel
import time

def speak(text):
    """Text-to-speech function - fixed version"""
    try:
        text = str(text).strip()
        if not text:
            return
            
        print(f"🔊 Speaking: {text}")
        
        # Initialize engine with proper settings
        engine = pyttsx3.init('sapi5')
        
        # Set properties
        voices = engine.getProperty('voices')
        if voices and len(voices) > 0:
            engine.setProperty('voice', voices[0].id)  # Use David voice
        
        engine.setProperty('rate', 174)  # Speech rate
        engine.setProperty('volume', 1.0)  # Max volume
        
        # Speak the text
        engine.say(text)
        engine.runAndWait()
        
        # Clean up
        engine.stop()
        
    except Exception as e:
        print(f"❌ TTS error: {e}")
        print(f"🔊 Fallback: {text}")  # Fallback to print

def takeCommand(query):
    """Process a text command - simplified version"""
    try:
        # This will be enhanced later with proper command processing
        return f"I received your command: {query}"
    except Exception as e:
        print(f"❌ Command processing error: {e}")
        return "Sorry, I couldn't process that command."