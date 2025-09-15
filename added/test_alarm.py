#!/usr/bin/env python3
"""Test the alarm parsing functionality"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from final_jarvis import FinalJarvis

def test_alarm_parsing():
    """Test the alarm time parsing"""
    print("🧪 Testing alarm time parsing...")
    
    jarvis = FinalJarvis()
    
    # Test various time formats
    test_cases = [
        "6:30 a.m.",
        "7:30 AM",
        "6:30 am",
        "7 PM",
        "19:30",
        "8:45 p.m.",
        "12:00 AM",
        "12:00 PM"
    ]
    
    for test_time in test_cases:
        hour, minute = jarvis.parse_time_input(test_time)
        if hour is not None and minute is not None:
            print(f"✅ '{test_time}' → {hour:02d}:{minute:02d} (24-hour format)")
        else:
            print(f"❌ '{test_time}' → Failed to parse")
    
    print("\n✅ Alarm parsing test completed!")

if __name__ == "__main__":
    test_alarm_parsing()