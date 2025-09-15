#!/usr/bin/env python3
"""Test the play any video fix"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from final_jarvis import FinalJarvis

async def test_play_video():
    """Test the play any video fix"""
    print("🧪 Testing 'play any video' fix...")
    
    jarvis = FinalJarvis()
    
    # Test the extract_search_term method
    print("\n🔍 Testing extract_search_term:")
    result = jarvis.extract_search_term("play any video")
    print(f"Input: 'play any video' → Output: '{result}'")
    
    # Test the play_youtube_video method
    print("\n🎬 Testing play_youtube_video with 'any video':")
    await jarvis.play_youtube_video("any video")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_play_video())