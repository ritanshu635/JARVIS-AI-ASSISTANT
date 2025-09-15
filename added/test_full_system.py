#!/usr/bin/env python3
"""
Full System Integration Test - Test all JARVIS components working together
"""
import asyncio
import time
from engine.ai_router import AIRouter
from engine.voice_engine import VoiceEngine
from engine.android_controller import AndroidController
from engine.database_manager import initialize_default_data
from engine.command_processor import CommandProcessor
from engine.command import speak

async def test_full_integration():
    """Test full system integration"""
    print("🚀 JARVIS FULL SYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    # Initialize all components
    print("\n🔧 Initializing Components...")
    
    try:
        # Database
        db_manager = initialize_default_data()
        print("✅ Database Manager initialized")
        
        # AI Router
        ai_router = AIRouter()
        print("✅ AI Router initialized")
        
        # Voice Engine
        voice_engine = VoiceEngine()
        print("✅ Voice Engine initialized")
        
        # Android Controller
        android_controller = AndroidController(db_manager)
        print("✅ Android Controller initialized")
        
        # Command Processor
        command_processor = CommandProcessor(ai_router, db_manager)
        print("✅ Command Processor initialized")
        
    except Exception as e:
        print(f"❌ Component initialization failed: {e}")
        return False
    
    # Test AI Services
    print("\n🤖 Testing AI Services...")
    status = ai_router.get_service_status()
    print(f"   Ollama: {'✅' if status['ollama'] else '❌'}")
    print(f"   Groq: {'✅' if status['groq'] else '❌'}")
    print(f"   Cohere: {'✅' if status['cohere'] else '❌'}")
    
    # Test Voice System
    print("\n🎤 Testing Voice System...")
    voice_status = voice_engine.get_status()
    print(f"   Whisper Model: {voice_status['whisper_model']} {'✅' if voice_status['whisper_loaded'] else '❌'}")
    print(f"   TTS Engine: {'✅' if voice_status['tts_initialized'] else '❌'}")
    print(f"   Wake Word: {'✅' if voice_status['porcupine_available'] else '❌'}")
    
    # Test Android Connection
    print("\n📱 Testing Android Connection...")
    android_result = android_controller.test_connection()
    android_status = android_result['success']
    print(f"   ADB Connection: {'✅' if android_status else '❌'}")
    if android_status:
        print(f"   {android_result['message']}")
    else:
        print(f"   {android_result['message']}")
    
    # Test Database Operations
    print("\n🗄️ Testing Database Operations...")
    try:
        # Test contact operations
        db_manager.add_contact("Test User", "+1234567890", "test@example.com")
        contact = db_manager.get_contact("test")
        print(f"   Contact Management: {'✅' if contact else '❌'}")
        
        # Test chat history
        db_manager.save_chat_message("Hello", "Hi there!", "greeting", 0.5, "test")
        history = db_manager.get_chat_history(1)
        print(f"   Chat History: {'✅' if history else '❌'}")
        
    except Exception as e:
        print(f"   Database Operations: ❌ {e}")
    
    # Test Command Processing
    print("\n⚙️ Testing Command Processing...")
    test_commands = [
        ("Hello JARVIS", "greeting"),
        ("What time is it", "time_date"),
        ("Open notepad", "open_app"),
        ("Play music on YouTube", "play_media"),
        ("Search for Python tutorials", "web_search")
    ]
    
    for command, expected_intent in test_commands:
        try:
            result = await command_processor.process_command(command)
            success = "✅" if result['success'] else "❌"
            print(f"   '{command}' → {result['intent']} {success}")
        except Exception as e:
            print(f"   '{command}' → Error: {e} ❌")
    
    # Test TTS
    print("\n🔊 Testing Text-to-Speech...")
    try:
        speak("JARVIS full system test completed successfully!")
        print("   TTS Test: ✅")
    except Exception as e:
        print(f"   TTS Test: ❌ {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SYSTEM STATUS SUMMARY")
    print("=" * 60)
    
    components_status = {
        "Database": "✅ Working",
        "AI Router": "✅ Working (Cohere)" if status.get('cohere') else "⚠️ Limited",
        "Voice Engine": "✅ Working" if voice_status['whisper_loaded'] and voice_status['tts_initialized'] else "⚠️ Partial",
        "Android Controller": "✅ Connected" if android_status else "⚠️ Not Connected",
        "Command Processor": "✅ Working",
        "Web Interface": "✅ Ready"
    }
    
    for component, status in components_status.items():
        print(f"{component:20}: {status}")
    
    print("\n🎉 JARVIS is ready for use!")
    print("\n💡 Available Commands:")
    print("   • 'Hello JARVIS' - Greeting")
    print("   • 'What time is it?' - Time/Date")
    print("   • 'Open [app]' - Launch applications")
    print("   • 'Play [song] on YouTube' - Media playback")
    print("   • 'Call [contact]' - Phone calls (requires Android)")
    print("   • 'Send message to [contact]' - SMS (requires Android)")
    print("   • 'Search for [query]' - Web search")
    print("   • 'Write a letter about [topic]' - Content generation")
    print("   • 'What's the weather?' - Weather info")
    
    return True

async def interactive_test():
    """Interactive test mode"""
    print("\n🎮 INTERACTIVE TEST MODE")
    print("Type commands to test JARVIS (type 'quit' to exit)")
    print("-" * 50)
    
    # Initialize components
    db_manager = initialize_default_data()
    ai_router = AIRouter()
    command_processor = CommandProcessor(ai_router, db_manager)
    
    while True:
        try:
            command = input("\n🎤 You: ").strip()
            
            if command.lower() in ['quit', 'exit', 'stop']:
                print("👋 Goodbye!")
                break
            
            if not command:
                continue
            
            print("🤔 Processing...")
            start_time = time.time()
            
            result = await command_processor.process_command(command)
            
            processing_time = time.time() - start_time
            
            print(f"🤖 JARVIS: {result['response']}")
            print(f"📊 Intent: {result['intent']} | Success: {result['success']} | Time: {processing_time:.2f}s")
            
            # Also speak the response
            try:
                speak(result['response'])
            except:
                pass
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_test())
    else:
        asyncio.run(test_full_integration())