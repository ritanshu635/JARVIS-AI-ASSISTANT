#!/usr/bin/env python3
"""
Test the email functionality in the main JARVIS system
"""

import asyncio
from final_jarvis import FinalJarvis

async def test_main_jarvis_email():
    """Test email functionality in main JARVIS"""
    print("🧪 Testing email functionality in main JARVIS system...")
    
    try:
        # Initialize main JARVIS
        jarvis = FinalJarvis()
        
        # Test the voice command that triggers email reading
        test_command = "jarvis read my emails for me"
        print(f"\n🎤 Testing command: '{test_command}'")
        
        # Process the command through the main system
        await jarvis.understand_and_execute(test_command)
        
        print("\n✅ Main JARVIS email functionality test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_main_jarvis_email())