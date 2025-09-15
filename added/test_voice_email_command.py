#!/usr/bin/env python3
"""
Test voice email command with final_jarvis.py
"""

import asyncio
from final_jarvis import FinalJarvis

async def test_voice_email_command():
    """Test the voice email command processing"""
    print("🧪 Testing voice email command...")
    
    try:
        # Initialize JARVIS
        jarvis = FinalJarvis()
        
        # Simulate the voice command
        test_command = "jarvis read my emails for me"
        print(f"\n🎤 Simulating command: '{test_command}'")
        
        # Process the command
        await jarvis.understand_and_execute(test_command)
        
        print("\n✅ Voice email command test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_voice_email_command())