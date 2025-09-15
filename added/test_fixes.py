#!/usr/bin/env python3
"""Quick test for the fixes"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from final_jarvis import FinalJarvis

async def test_fixes():
    """Test the specific fixes"""
    print("🧪 Testing JARVIS fixes...")
    
    jarvis = FinalJarvis()
    
    # Test 1: Play any video
    print("\n🎬 Testing 'play any video'...")
    await jarvis.play_youtube_video("any video")
    
    # Test 2: Ollama response
    print("\n🧠 Testing Ollama response...")
    response = await jarvis.get_ollama_response("What is the capital of India?")
    if response:
        print(f"✅ Ollama response: {response[:100]}...")
    else:
        print("❌ Ollama not responding")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_fixes())