#!/usr/bin/env python3
"""
Test script to verify JARVIS functionality without starting the web interface
"""
import asyncio
import os
from dotenv import load_dotenv
from engine.ai_router import AIRouter
from engine.database_manager import initialize_default_data

load_dotenv()

async def test_jarvis_functionality():
    print("🧪 TESTING JARVIS CORE FUNCTIONALITY")
    print("=" * 60)
    
    # Initialize components
    print("🔧 Initializing components...")
    db_manager = initialize_default_data()
    ai_router = AIRouter()
    
    print("✅ Components initialized\n")
    
    # Test database
    print("📊 Testing Database:")
    contacts = db_manager.get_all_contacts()
    print(f"   Contacts in database: {len(contacts)}")
    
    # Add a test contact
    db_manager.add_contact("Test User", "+1234567890", "test@example.com")
    test_contact = db_manager.get_contact("test")
    print(f"   Test contact: {test_contact}")
    
    # Test system commands
    chrome_path = db_manager.get_system_command("chrome")
    print(f"   Chrome path: {chrome_path}")
    
    # Test web commands
    youtube_url = db_manager.get_web_command("youtube")
    print(f"   YouTube URL: {youtube_url}")
    print()
    
    # Test AI Router
    print("🤖 Testing AI Router:")
    
    # Test service status
    status = ai_router.get_service_status()
    print(f"   Service Status: {status}")
    
    # Test queries
    test_queries = [
        ("Hello, how are you?", "general"),
        ("What time is it?", "general"),
        ("Open Chrome", "general"),
        ("Call John", "general"),
        ("Write a short poem", "content")
    ]
    
    for query, query_type in test_queries:
        print(f"\n   🔍 Testing: '{query}'")
        try:
            # Test intent classification
            intent = await ai_router.classify_intent(query)
            print(f"      Intent: {intent['intent']}")
            
            # Test AI response
            result = await ai_router.process_query(query, query_type)
            if result['success']:
                print(f"      Response: {result['response'][:100]}...")
                print(f"      Model: {result['ai_model']}")
                print(f"      Time: {result['processing_time']:.2f}s")
            else:
                print(f"      ❌ Failed: {result['response']}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 FUNCTIONALITY TEST COMPLETE")
    
    # Cleanup
    db_manager.close_connections()

if __name__ == "__main__":
    asyncio.run(test_jarvis_functionality())