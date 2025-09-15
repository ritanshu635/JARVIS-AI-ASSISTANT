#!/usr/bin/env python3
"""
Audio Setup Checker for Voice Meeting Assistant
Verifies your Realtek audio setup is ready for meeting recording
"""

import pyaudio
import speech_recognition as sr
import requests

def check_audio_devices():
    """Check available audio devices"""
    print("🔍 Checking Audio Devices...")
    print("=" * 50)
    
    try:
        audio = pyaudio.PyAudio()
        
        print("📱 Available Audio Devices:")
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            device_name = device_info['name']
            max_inputs = device_info['maxInputChannels']
            max_outputs = device_info['maxOutputChannels']
            
            print(f"  {i}: {device_name}")
            print(f"     Input channels: {max_inputs}, Output channels: {max_outputs}")
            
            # Check if this is Realtek and has input capability
            if "realtek" in device_name.lower() and max_inputs > 0:
                print(f"     ✅ This looks like your Realtek input device!")
            elif "stereo mix" in device_name.lower():
                print(f"     ✅ Found Stereo Mix device!")
        
        audio.terminate()
        return True
        
    except Exception as e:
        print(f"❌ Error checking audio devices: {e}")
        return False

def check_microphone():
    """Check microphone for voice commands"""
    print("\n🎤 Checking Microphone for Voice Commands...")
    print("=" * 50)
    
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        print("🎙️ Adjusting for ambient noise...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("✅ Microphone ready for voice commands!")
        return True
        
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        return False

def check_ollama_connection():
    """Check if Ollama is running"""
    print("\n🧠 Checking Ollama Connection...")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama is running!")
            print(f"📚 Available models: {len(models)}")
            
            # Check for recommended models
            model_names = [model.get('name', '') for model in models]
            if any('llama' in name.lower() for name in model_names):
                print("✅ Llama model found - perfect for meeting summaries!")
            else:
                print("⚠️ Consider installing llama3.2:3b for better summaries:")
                print("   Run: ollama pull llama3.2:3b")
            
            return True
        else:
            print(f"❌ Ollama responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama")
        print("💡 Start Ollama by running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Ollama check error: {e}")
        return False

def check_whisper():
    """Check if Whisper is available"""
    print("\n🗣️ Checking Whisper...")
    print("=" * 50)
    
    try:
        import whisper
        print("✅ Whisper is installed!")
        
        # Try loading a model
        print("📥 Testing Whisper model loading...")
        model = whisper.load_model("base")
        print("✅ Whisper base model loaded successfully!")
        return True
        
    except ImportError:
        print("❌ Whisper not installed")
        print("💡 Install with: pip install openai-whisper")
        return False
    except Exception as e:
        print(f"❌ Whisper error: {e}")
        return False

def main():
    """Run all checks"""
    print("🤖 Voice Meeting Assistant - Audio Setup Check")
    print("=" * 60)
    print("🔧 Checking if your system is ready for voice-activated meeting recording...")
    print()
    
    checks = []
    
    # Run all checks
    checks.append(("Audio Devices", check_audio_devices()))
    checks.append(("Microphone", check_microphone()))
    checks.append(("Whisper", check_whisper()))
    checks.append(("Ollama", check_ollama_connection()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SETUP SUMMARY")
    print("=" * 60)
    
    all_good = True
    for check_name, result in checks:
        status = "✅ READY" if result else "❌ NEEDS ATTENTION"
        print(f"{check_name:15} : {status}")
        if not result:
            all_good = False
    
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 ALL SYSTEMS GO!")
        print("✅ Your setup is ready for voice-activated meeting recording!")
        print()
        print("🚀 Next steps:")
        print("1. Run: python test_voice_meeting.py")
        print("2. Or start JARVIS: python main.py")
        print("3. Say: 'Jarvis attend the meeting for me'")
    else:
        print("⚠️ SOME ISSUES FOUND")
        print("Please fix the issues above before using the meeting assistant.")
        print()
        print("💡 Common fixes:")
        print("- Enable Stereo Mix in Windows Sound settings")
        print("- Start Ollama: ollama serve")
        print("- Install missing packages: pip install openai-whisper")
    
    print("=" * 60)

if __name__ == "__main__":
    main()