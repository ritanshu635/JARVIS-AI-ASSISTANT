#!/usr/bin/env python3
"""
Voice Test Script - Test both speech recognition and text-to-speech
"""
import pyttsx3
import speech_recognition as sr
import time

def test_text_to_speech():
    """Test text-to-speech functionality"""
    print("🔊 Testing Text-to-Speech...")
    
    try:
        # Initialize TTS engine
        engine = pyttsx3.init('sapi5')
        
        # Get available voices
        voices = engine.getProperty('voices')
        if voices:
            print(f"📢 Available voices: {len(voices)}")
            engine.setProperty('voice', voices[0].id)
        
        # Set speech rate
        engine.setProperty('rate', 174)
        
        # Test message
        test_message = "Hello! This is JARVIS testing text to speech functionality. Can you hear me clearly?"
        
        print(f"🎤 Speaking: {test_message}")
        engine.say(test_message)
        engine.runAndWait()
        
        print("✅ Text-to-Speech test completed")
        return True
        
    except Exception as e:
        print(f"❌ Text-to-Speech error: {e}")
        return False

def test_speech_recognition():
    """Test speech recognition functionality"""
    print("🎧 Testing Speech Recognition...")
    
    try:
        # Initialize recognizer and microphone
        r = sr.Recognizer()
        
        with sr.Microphone() as source:
            print("🔧 Adjusting for ambient noise... Please wait.")
            r.adjust_for_ambient_noise(source, duration=2)
            print("✅ Microphone calibrated")
            
            print("🎤 Please speak something clearly (you have 5 seconds)...")
            print("💡 Try saying: 'Hello JARVIS, can you hear me?'")
            
            # Listen for audio
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            
            print("🔄 Processing speech...")
            
            # Recognize speech using Google's service
            text = r.recognize_google(audio, language='en-US')
            
            print(f"✅ I heard: '{text}'")
            
            # Speak back what was heard
            engine = pyttsx3.init('sapi5')
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
            engine.setProperty('rate', 174)
            
            response = f"I heard you say: {text}"
            print(f"🔊 Speaking back: {response}")
            engine.say(response)
            engine.runAndWait()
            
            return True, text
            
    except sr.WaitTimeoutError:
        print("❌ No speech detected within timeout period")
        return False, "No speech detected"
    except sr.UnknownValueError:
        print("❌ Could not understand the speech")
        return False, "Speech not understood"
    except sr.RequestError as e:
        print(f"❌ Speech recognition service error: {e}")
        return False, f"Service error: {e}"
    except Exception as e:
        print(f"❌ Speech recognition error: {e}")
        return False, f"Error: {e}"

def main():
    """Main test function"""
    print("🧪 JARVIS VOICE SYSTEM TEST")
    print("=" * 50)
    
    # Test 1: Text-to-Speech
    print("\n1️⃣ Testing Text-to-Speech...")
    tts_success = test_text_to_speech()
    
    if tts_success:
        input("\n⏸️ Press Enter after you confirm you can hear the speech...")
    
    # Test 2: Speech Recognition
    print("\n2️⃣ Testing Speech Recognition...")
    stt_success, recognized_text = test_speech_recognition()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Text-to-Speech: {'✅ WORKING' if tts_success else '❌ FAILED'}")
    print(f"Speech Recognition: {'✅ WORKING' if stt_success else '❌ FAILED'}")
    
    if stt_success:
        print(f"Last recognized text: '{recognized_text}'")
    
    if tts_success and stt_success:
        print("\n🎉 Both voice systems are working perfectly!")
        
        # Final test - interactive
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 174)
        
        final_message = "Excellent! Both speech recognition and text to speech are working perfectly. JARVIS voice system is ready for use!"
        print(f"🔊 Final message: {final_message}")
        engine.say(final_message)
        engine.runAndWait()
        
    else:
        print("\n⚠️ Some voice systems need attention. Check the errors above.")
    
    print("\n🏁 Voice test completed!")

if __name__ == "__main__":
    main()