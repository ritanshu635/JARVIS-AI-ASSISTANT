#!/usr/bin/env python3
"""Test the recipe feature"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from final_jarvis import FinalJarvis

async def test_recipe():
    """Test the recipe functionality"""
    print("🧪 Testing recipe feature...")
    
    jarvis = FinalJarvis()
    
    # Test dish name extraction
    print("\n🔍 Testing dish name extraction:")
    dish1 = jarvis.extract_dish_name("tell me the recipe to make burger")
    dish2 = jarvis.extract_dish_name("how to cook pasta")
    print(f"'tell me the recipe to make burger' → '{dish1}'")
    print(f"'how to cook pasta' → '{dish2}'")
    
    # Test recipe request
    print("\n🍔 Testing recipe request for burger:")
    await jarvis.handle_recipe_request("tell me the recipe to make burger")
    
    print("\n✅ Recipe test completed!")

if __name__ == "__main__":
    asyncio.run(test_recipe())