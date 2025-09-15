#!/usr/bin/env python3
"""
Test the integrated email functionality in final_jarvis.py
"""

import asyncio
from final_jarvis import FinalJarvis

async def test_email_functionality():
    """Test the email reading functionality"""
    print("🧪 Testing integrated email functionality...")
    
    try:
        # Initialize JARVIS
        jarvis = FinalJarvis()
        
        # Test email reading
        print("\n📧 Testing email reading...")
        await jarvis.handle_email_reading()
        
        print("\n✅ Email functionality test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_email_functionality())