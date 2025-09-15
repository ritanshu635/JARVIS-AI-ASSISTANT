#!/usr/bin/env python3
"""
Test script for Unified JARVIS Assistant
This script tests all components without the web interface
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_database():
    """Test database functionality"""
    print("\n🗄️ Testing Database Manager...")
    try:
        from engine.database_manager import DatabaseManager, initialize_default_data
        
        db = initialize_default_data()
        
        # Test contact operations
        db.add_contact("Test User", "1234567890", "test@example.com")
        contact = db.get_contact("test")
        print(f"✅ Contact test: {contact}")
        
        # Test system commands
        chrome_path = db.get_system_command("chrome")
        print(f"✅ System command test: chrome -> {chrome_path}")
        
        # Test web commands
        youtube_url = db.get_web_command("youtube")
        print(f"✅ Web command test: youtube -> {youtube_url}")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_ai_router():
    """Test AI router functionality"""
    print("\n🤖 Testing AI Router...")
    try:
        from engine.ai_router import AIRouter
        
        ai_router = AIRouter()
        
        # Test service status
        status = ai_router.get_service_status()
        print(f"✅ AI Services status: {status}")
        
        # Test simple query
        async def test_query():
            result = await ai_router.process_query("Hello, how are you?", "general")
            print(f"✅ AI Query test: {result['response'][:100]}...")
            return result['success']
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(test_query())
        
        return success
    except Exception as e:
        print(f"❌ AI Router test failed: {e}")
        return False

def test_voice_engine():
    """Test voice engine functionality"""
    print("\n🎤 Testing Voice Engine...")
    try:
        from engine.voice_engine import VoiceEngine
        
        voice_engine = VoiceEngine()
        
        # Test status
        status = voice_engine.get_status()
        print(f"✅ Voice Engine status: {status}")
        
        # Test TTS
        print("🔊 Testing text-to-speech...")
        voice_engine.speak("Hello, this is a test of the voice system.")
        
        # Test microphone (optional)
        print("🎤 Testing microphone...")
        mic_test = voice_engine.test_microphone()
        print(f"✅ Microphone test: {'Passed' if mic_test else 'Failed'}")
        
        return True
    except Exception as e:
        print(f"❌ Voice Engine test failed: {e}")
        return False

def test_android_controller():
    """Test Android controller functionality"""
    print("\n📱 Testing Android Controller...")
    try:
        from engine.android_controller import AndroidController
        from engine.database_manager import DatabaseManager
        
        db = DatabaseManager()
        android = AndroidController(db)
        
        # Test connection
        connection_test = android.test_connection()
        print(f"✅ ADB Connection test: {connection_test}")
        
        # Test device info
        device_info = android.get_device_info()
        print(f"✅ Device info: {device_info}")
        
        return True
    except Exception as e:
        print(f"❌ Android Controller test failed: {e}")
        return False

def test_command_processor():
    """Test command processor functionality"""
    print("\n⚙️ Testing Command Processor...")
    try:
        from engine.command_processor import CommandProcessor
        from engine.ai_router import AIRouter
        from engine.database_manager import DatabaseManager
        
        ai_router = AIRouter()
        db_manager = DatabaseManager()
        processor = CommandProcessor(ai_router, db_manager)
        
        # Test commands
        test_commands = [
            "hello jarvis",
            "what time is it",
            "open chrome",
            "play music on youtube"
        ]
        
        async def test_commands_async():
            for command in test_commands:
                print(f"🎤 Testing command: '{command}'")
                result = await processor.process_command(command)
                print(f"📝 Response: {result['response']}")
                print(f"🎯 Intent: {result['intent']}")
                print(f"✅ Success: {result['success']}")
                print("-" * 50)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(test_commands_async())
        
        return True
    except Exception as e:
        print(f"❌ Command Processor test failed: {e}")
        return False

def test_face_auth():
    """Test face authentication (optional)"""
    print("\n🔍 Testing Face Authentication...")
    try:
        from engine.auth.recoganize import ListFaces, face_authenticator
        
        faces = ListFaces()
        print(f"✅ Known faces: {faces}")
        
        if not faces:
            print("⚠️ No faces registered. Face authentication will be skipped.")
            print("💡 To add faces, run: python -c \"from engine.auth.recoganize import AddFace; AddFace('your_name')\"")
        
        return True
    except Exception as e:
        print(f"❌ Face Authentication test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 UNIFIED JARVIS SYSTEM TEST")
    print("=" * 50)
    
    tests = [
        ("Database Manager", test_database),
        ("AI Router", test_ai_router),
        ("Voice Engine", test_voice_engine),
        ("Android Controller", test_android_controller),
        ("Command Processor", test_command_processor),
        ("Face Authentication", test_face_auth),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔄 Running {test_name} test...")
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print(f"\n⏹️ Test interrupted by user")
            break
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Unified JARVIS system is ready!")
        print("\n🚀 To start JARVIS, run: python main.py")
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
        print("\n💡 Common issues:")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Install Ollama: https://ollama.ai/download")
        print("   - Setup MongoDB: https://www.mongodb.com/try/download/community")
        print("   - Connect Android device with USB debugging enabled")

if __name__ == "__main__":
    main()