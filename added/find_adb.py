#!/usr/bin/env python3
"""
Find ADB executable on the system
"""
import os
import subprocess
import glob

def find_adb():
    """Find ADB executable"""
    print("🔍 Searching for ADB executable...")
    
    # Try common locations
    possible_paths = [
        "adb",  # If in PATH
        "adb.exe",  # Windows
        r"C:\adb\adb.exe",
        r"C:\adb\platform-tools\adb.exe",
        r"C:\platform-tools\adb.exe",
        r"C:\Android\platform-tools\adb.exe",
        r"C:\Program Files\Android\platform-tools\adb.exe",
        r"C:\Program Files (x86)\Android\platform-tools\adb.exe",
        os.path.expanduser(r"~\Downloads\platform-tools\adb.exe"),
        os.path.expanduser(r"~\Desktop\platform-tools\adb.exe"),
        os.path.expanduser(r"~\AppData\Local\Android\Sdk\platform-tools\adb.exe"),
    ]
    
    # Also search in common drives
    for drive in ['C:', 'D:', 'E:']:
        possible_paths.extend([
            f"{drive}\\adb\\adb.exe",
            f"{drive}\\platform-tools\\adb.exe",
            f"{drive}\\Android\\platform-tools\\adb.exe"
        ])
    
    found_paths = []
    
    for path in possible_paths:
        try:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                # Test if it's actually ADB
                try:
                    result = subprocess.run([expanded_path, 'version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and 'Android Debug Bridge' in result.stdout:
                        found_paths.append(expanded_path)
                        print(f"✅ Found ADB at: {expanded_path}")
                except:
                    continue
        except:
            continue
    
    # Also try to find using glob patterns
    print("\n🔍 Searching with glob patterns...")
    search_patterns = [
        "C:\\**\\adb.exe",
        "D:\\**\\adb.exe",
        os.path.expanduser("~\\**\\adb.exe")
    ]
    
    for pattern in search_patterns:
        try:
            matches = glob.glob(pattern, recursive=True)
            for match in matches[:5]:  # Limit to first 5 matches
                if os.path.exists(match):
                    try:
                        result = subprocess.run([match, 'version'], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0 and 'Android Debug Bridge' in result.stdout:
                            if match not in found_paths:
                                found_paths.append(match)
                                print(f"✅ Found ADB at: {match}")
                    except:
                        continue
        except Exception as e:
            print(f"⚠️ Search pattern {pattern} failed: {e}")
    
    if found_paths:
        print(f"\n🎉 Found {len(found_paths)} ADB installation(s):")
        for i, path in enumerate(found_paths, 1):
            print(f"   {i}. {path}")
        
        # Test the first one
        print(f"\n🧪 Testing first ADB installation: {found_paths[0]}")
        try:
            result = subprocess.run([found_paths[0], 'devices'], 
                                  capture_output=True, text=True, timeout=10)
            print(f"ADB devices output:\n{result.stdout}")
            
            return found_paths[0]
        except Exception as e:
            print(f"❌ Test failed: {e}")
    else:
        print("❌ No ADB installations found")
        print("\n💡 To install ADB:")
        print("1. Download from: https://developer.android.com/studio/releases/platform-tools")
        print("2. Extract to C:\\adb\\")
        print("3. Add C:\\adb\\ to your system PATH")
    
    return None

if __name__ == "__main__":
    find_adb()