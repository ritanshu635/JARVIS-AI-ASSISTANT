#!/usr/bin/env python3
"""
Test script to check API connectivity and functionality
"""
import os
import asyncio
from dotenv import load_dotenv
from engine.ai_router import AIRouter

load_dotenv()

async def test_apis():
    print("🧪 TESTING API CONNECTIVITY")
    print("=" * 50)
    
    # Initialize AI Router
    ai_router = AIRouter()
    
    # Get service status
    status = ai_router.get_service_status()
    print(f"📊 Service Status:")
    print(f"   Ollama: {'✅' if status['ollama'] else '❌'}")
    print(f"   Groq: {'✅' if status['groq'] else '❌'}")
    print(f"   Cohere: {'✅' if status['cohere'] else '❌'}")
    print()
    
    # Test a simple query
    print("🤖 Testing AI Query: 'Hello, how are you?'")
    result = await ai_router.process_query("Hello, how are you?", "general")
    
    if result['success']:
        print(f"✅ Response received from {result['ai_model']}")
        print(f"📝 Response: {result['response'][:100]}...")
        print(f"⏱️ Processing time: {result['processing_time']:.2f}s")
    else:
        print(f"❌ Query failed: {result['response']}")
    
    print()
    
    # Test intent classification
    print("🎯 Testing Intent Classification: 'open chrome browser'")
    intent = await ai_router.classify_intent("open chrome browser")
    print(f"📋 Classified as: {intent['intent']}")
    print(f"✅ Success: {intent['success']}")
    
    print()
    print("=" * 50)
    print("🏁 API Test Complete")

if __name__ == "__main__":
    asyncio.run(test_apis())