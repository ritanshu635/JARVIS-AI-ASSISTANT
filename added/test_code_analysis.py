#!/usr/bin/env python3
"""
Test script for the new AI Code Reviewer feature
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.ai_router import AIRouter

async def test_code_analysis():
    """Test the code analysis functionality"""
    print("🧪 Testing AI Code Reviewer Feature")
    print("=" * 50)
    
    # Initialize AI Router
    try:
        ai_router = AIRouter()
        print("✅ AI Router initialized")
    except Exception as e:
        print(f"❌ Failed to initialize AI Router: {e}")
        return
    
    # Test OpenAI connection
    print("\n🔍 Testing OpenAI connection...")
    if ai_router._test_openai():
        print("✅ OpenAI API connection successful")
    else:
        print("❌ OpenAI API not available - check your API key in .env file")
        print("💡 Add your OpenAI API key to the .env file: OpenAI_API_KEY=your_key_here")
        return
    
    # Test code analysis with sample C++ code
    print("\n🧠 Testing code analysis with sample C++ code...")
    
    sample_code = """
#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int, int> hashMap;
        for (int i = 0; i < nums.size(); i--) {
            int complement = target + nums[i];
            if (hashMap.find(complement) != hashMap.end()) {
                return {hashMap[complement], i};
            }
            hashMap[nums[i]] = i;
        }
        return {};
    }
};
"""
    
    try:
        result = await ai_router.analyze_code_with_openai(sample_code)
        
        if result['success']:
            print("✅ Code analysis successful!")
            print("\n📝 Analysis Results:")
            for i, mistake in enumerate(result['mistakes'], 1):
                print(f"   Line {i}: {mistake}")
        else:
            print("❌ Code analysis failed")
            print(f"   Mistakes: {result['mistakes']}")
            
    except Exception as e:
        print(f"❌ Code analysis error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("   - If OpenAI connection works, the feature is ready!")
    print("   - Make sure to install: pip install -r code_analysis_requirements.txt")
    print("   - Add your OpenAI API key to .env file")
    print("   - Test by saying: 'Jarvis help me with my code'")

if __name__ == "__main__":
    asyncio.run(test_code_analysis())