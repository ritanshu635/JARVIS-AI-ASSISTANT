#!/usr/bin/env python3
"""
Test and fix TTS issues
"""
import pyttsx3
import time

def test_tts_basic():
    """Test basic TTS functionality"""
    print("🔊 Testing basic TTS...")
    
    try:
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty('voices')
        print(f"📢 Available voices: {len(voices)}")
        
        for i, voice in enumerate(voices):
            print(f"   {i}: {voice.name} - {voice.id}")
        
        # Test with different settings
        engine.setProperty('rate', 150)  # Slower rate
        engine.setProperty('volume', 1.0)  # Max volume
        
        if voices:
            engine.setProperty('voice', voices[0].id)  # Use first voice
        
        test_text = "Hello, this is a TTS test. Can you hear me?"
        print(f"🎤 Speaking: {test_text}")
        
        engine.say(test_text)
        engine.runAndWait()
        
        print("✅ Basic TTS test completed")
        return True
        
    except Exception as e:
        print(f"❌ Basic TTS failed: {e}")
        return False

def test_tts_advanced():
    """Test TTS with different configurations"""
    print("\n🔧 Testing advanced TTS configurations...")
    
    try:
        # Try different initialization methods
        engines_to_try = [
            ('sapi5', 'Windows SAPI5'),
            ('espeak', 'eSpeak'),
            (None, 'Default')
        ]
        
        for engine_name, description in engines_to_try:
            try:
                print(f"\n🧪 Testing {description}...")
                
                if engine_name:
                    engine = pyttsx3.init(engine_name)
                else:
                    engine = pyttsx3.init()
                
                # Configure engine
                engine.setProperty('rate', 174)
                engine.setProperty('volume', 0.9)
                
                voices = engine.getProperty('voices')
                if voices:
                    # Try different voices
                    for i, voice in enumerate(voices[:2]):  # Test first 2 voices
                        print(f"   Testing voice {i}: {voice.name}")
                        engine.setProperty('voice', voice.id)
                        
                        test_text = f"Testing voice {i+1}. Hello from JARVIS!"
                        print(f"   🎤 Speaking: {test_text}")
                        
                        engine.say(test_text)
                        engine.runAndWait()
                        
                        time.sleep(1)
                
                print(f"   ✅ {description} working")
                return True
                
            except Exception as e:
                print(f"   ❌ {description} failed: {e}")
                continue
        
        return False
        
    except Exception as e:
        print(f"❌ Advanced TTS test failed: {e}")
        return False

def test_tts_threading():
    """Test TTS with threading issues fix"""
    print("\n🧵 Testing TTS threading fix...")
    
    try:
        import threading
        
        def speak_in_thread(text):
            try:
                engine = pyttsx3.init('sapi5')
                engine.setProperty('rate', 174)
                engine.setProperty('volume', 1.0)
                
                voices = engine.getProperty('voices')
                if voices:
                    engine.setProperty('voice', voices[0].id)
                
                print(f"🎤 Speaking in thread: {text}")
                engine.say(text)
                engine.runAndWait()
                engine.stop()
                
            except Exception as e:
                print(f"❌ Thread TTS error: {e}")
        
        # Test in main thread
        text1 = "Testing main thread TTS"
        engine = pyttsx3.init('sapi5')
        engine.setProperty('rate', 174)
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        
        print(f"🎤 Speaking in main thread: {text1}")
        engine.say(text1)
        engine.runAndWait()
        
        time.sleep(1)
        
        # Test in separate thread
        text2 = "Testing separate thread TTS"
        thread = threading.Thread(target=speak_in_thread, args=(text2,))
        thread.start()
        thread.join()
        
        print("✅ Threading TTS test completed")
        return True
        
    except Exception as e:
        print(f"❌ Threading TTS failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 PYTTSX3 TTS DIAGNOSTIC TEST")
    print("=" * 50)
    
    # Test 1: Basic functionality
    basic_success = test_tts_basic()
    
    # Test 2: Advanced configurations
    if not basic_success:
        advanced_success = test_tts_advanced()
    else:
        advanced_success = True
    
    # Test 3: Threading issues
    threading_success = test_tts_threading()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TTS TEST RESULTS")
    print("=" * 50)
    print(f"Basic TTS:      {'✅' if basic_success else '❌'}")
    print(f"Advanced TTS:   {'✅' if advanced_success else '❌'}")
    print(f"Threading TTS:  {'✅' if threading_success else '❌'}")
    
    if basic_success or advanced_success:
        print("\n💡 TTS is working! The issue might be in the JARVIS implementation.")
        print("🔧 Suggested fixes:")
        print("   1. Ensure engine.runAndWait() is called")
        print("   2. Check volume settings")
        print("   3. Avoid threading conflicts")
        print("   4. Use proper engine initialization")
    else:
        print("\n❌ TTS system has issues. Try:")
        print("   1. Reinstall pyttsx3: pip uninstall pyttsx3 && pip install pyttsx3")
        print("   2. Check Windows speech settings")
        print("   3. Try alternative TTS libraries")

if __name__ == "__main__":
    main()