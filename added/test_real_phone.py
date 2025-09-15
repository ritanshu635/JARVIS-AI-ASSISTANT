#!/usr/bin/env python3
"""
Test real phone functionality - contacts, calls, WhatsApp
"""
import subprocess
import time
import os

def test_adb_connection():
    """Test ADB connection with your phone"""
    print("📱 Testing ADB connection with your phone...")
    
    try:
        # Check devices
        result = subprocess.run([r"C:\adb\platform-tools\adb.exe", "devices"], 
                              capture_output=True, text=True, timeout=10)
        
        print("ADB Devices Output:")
        print(result.stdout)
        
        if "device" in result.stdout:
            print("✅ Phone connected successfully!")
            return True
        else:
            print("❌ Phone not connected properly")
            return False
            
    except Exception as e:
        print(f"❌ ADB test failed: {e}")
        return False

def get_real_contacts():
    """Get real contacts from your phone"""
    print("📞 Attempting to get real contacts from your phone...")
    
    try:
        # Try to get contacts using ADB
        result = subprocess.run([
            r"C:\adb\platform-tools\adb.exe", "shell", 
            "content", "query", "--uri", "content://com.android.contacts/contacts",
            "--projection", "display_name"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Successfully accessed contacts!")
            print("Sample contacts output:")
            print(result.stdout[:500])  # Show first 500 chars
            return True
        else:
            print(f"❌ Could not access contacts: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Contact access failed: {e}")
        return False

def test_real_call():
    """Test making a real call"""
    print("📞 Testing real call functionality...")
    
    # Ask user for permission first
    print("⚠️ This will attempt to make a real call!")
    print("💡 Make sure you have a test number ready")
    
    test_number = input("Enter a test number to call (or press Enter to skip): ").strip()
    
    if not test_number:
        print("⏭️ Skipping call test")
        return False
    
    try:
        print(f"📞 Attempting to call {test_number}...")
        
        # Use ADB to make call
        result = subprocess.run([
            r"C:\adb\platform-tools\adb.exe", "shell", 
            "am", "start", "-a", "android.intent.action.CALL", 
            "-d", f"tel:{test_number}"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Call command sent successfully!")
            print("📱 Check your phone - call should be starting")
            
            # Wait a moment then ask user
            time.sleep(3)
            success = input("Did the call start on your phone? (y/n): ").lower().startswith('y')
            
            if success:
                print("🎉 Real calling is working!")
                return True
            else:
                print("❌ Call didn't work properly")
                return False
        else:
            print(f"❌ Call command failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Call test failed: {e}")
        return False

def test_whatsapp_access():
    """Test WhatsApp access"""
    print("📱 Testing WhatsApp access...")
    
    try:
        # Try to open WhatsApp
        result = subprocess.run([
            r"C:\adb\platform-tools\adb.exe", "shell", 
            "am", "start", "-n", "com.whatsapp/com.whatsapp.HomeActivity"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ WhatsApp opened successfully!")
            print("📱 Check your phone - WhatsApp should be open")
            
            time.sleep(2)
            success = input("Did WhatsApp open on your phone? (y/n): ").lower().startswith('y')
            
            if success:
                print("🎉 WhatsApp access is working!")
                return True
            else:
                print("❌ WhatsApp didn't open properly")
                return False
        else:
            print(f"❌ WhatsApp open failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ WhatsApp test failed: {e}")
        return False

def check_phone_permissions():
    """Check what permissions we need"""
    print("🔐 Checking phone permissions needed...")
    
    permissions_needed = [
        "Phone calls - CALL_PHONE permission",
        "Contacts access - READ_CONTACTS permission", 
        "SMS access - SEND_SMS permission",
        "WhatsApp automation - Accessibility permissions"
    ]
    
    print("📋 Permissions that might be needed:")
    for i, perm in enumerate(permissions_needed, 1):
        print(f"   {i}. {perm}")
    
    print("\n💡 To enable these:")
    print("   1. Go to Settings > Apps > ADB/USB Debugging")
    print("   2. Grant all permissions when prompted")
    print("   3. For WhatsApp: Settings > Accessibility > Enable for automation")

def main():
    """Main test function"""
    print("🧪 REAL PHONE FUNCTIONALITY TEST")
    print("=" * 50)
    
    # Test 1: ADB Connection
    adb_working = test_adb_connection()
    
    if not adb_working:
        print("❌ ADB not working. Please check USB debugging is enabled.")
        return
    
    # Test 2: Contacts Access
    print("\n" + "-" * 30)
    contacts_working = get_real_contacts()
    
    # Test 3: Call Functionality
    print("\n" + "-" * 30)
    call_working = test_real_call()
    
    # Test 4: WhatsApp Access
    print("\n" + "-" * 30)
    whatsapp_working = test_whatsapp_access()
    
    # Test 5: Check Permissions
    print("\n" + "-" * 30)
    check_phone_permissions()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 REAL PHONE TEST RESULTS")
    print("=" * 50)
    print(f"ADB Connection:     {'✅' if adb_working else '❌'}")
    print(f"Contacts Access:    {'✅' if contacts_working else '❌'}")
    print(f"Call Functionality: {'✅' if call_working else '❌'}")
    print(f"WhatsApp Access:    {'✅' if whatsapp_working else '❌'}")
    
    if all([adb_working, contacts_working, call_working, whatsapp_working]):
        print("\n🎉 All real phone features are working!")
        print("✅ Ready to integrate with JARVIS")
    else:
        print("\n⚠️ Some features need attention")
        print("💡 Check the error messages above for solutions")

if __name__ == "__main__":
    main()