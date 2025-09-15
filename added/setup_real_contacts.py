#!/usr/bin/env python3
"""
Setup Script for Real Contact Integration
Guides user through setting up JARVIS with real phone contacts
"""

import os
import sys
import subprocess
from engine.android_controller import AndroidController
from engine.database_manager import DatabaseManager

def main():
    print("🤖 JARVIS Real Contact Setup")
    print("=" * 40)
    print("This script will help you set up JARVIS with your real phone contacts")
    print()
    
    # Step 1: Check ADB connection
    print("📱 Step 1: Checking Android Device Connection")
    print("-" * 45)
    
    android_controller = AndroidController()
    connection_test = android_controller.test_connection()
    
    if connection_test['success']:
        print(f"✅ {connection_test['message']}")
        device_info = android_controller.get_device_info()
        if device_info['connected']:
            print(f"📱 Device: {device_info.get('model', 'Unknown')}")
            print(f"🤖 Android: {device_info.get('android_version', 'Unknown')}")
            print(f"🔋 Battery: {device_info.get('battery_level', 'Unknown')}")
    else:
        print("❌ Android device not connected!")
        print("\n📋 Setup Instructions:")
        print("1. Connect your Android phone to this computer via USB cable")
        print("2. On your phone, go to Settings > About Phone")
        print("3. Tap 'Build Number' 7 times to enable Developer Options")
        print("4. Go to Settings > Developer Options")
        print("5. Enable 'USB Debugging'")
        print("6. When prompted on your phone, allow USB debugging for this computer")
        print("7. Run this setup script again")
        
        input("\nPress Enter after completing these steps...")
        return False
    
    # Step 2: Check current contacts
    print(f"\n📋 Step 2: Checking Current Contacts")
    print("-" * 35)
    
    db_manager = DatabaseManager()
    contacts = db_manager.get_all_contacts()
    
    print(f"📊 Contacts in JARVIS database: {len(contacts)}")
    
    if contacts:
        print("📞 Sample contacts:")
        for i, contact in enumerate(contacts[:5]):
            print(f"  {i+1}. {contact['name']}: {contact['mobile_no']}")
        if len(contacts) > 5:
            print(f"  ... and {len(contacts) - 5} more")
    
    # Step 3: Contact sync options
    print(f"\n🔄 Step 3: Contact Synchronization")
    print("-" * 35)
    
    if len(contacts) == 0:
        print("⚠️ No contacts found. You need to import your contacts.")
        sync_choice = 'y'
    else:
        sync_choice = input("Do you want to sync/update contacts from your phone? (y/n): ").lower().strip()
    
    if sync_choice == 'y':
        print("\n🔄 Starting contact sync...")
        
        # Run contact sync
        try:
            result = subprocess.run([sys.executable, 'sync_contacts.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Contact sync completed!")
                
                # Check updated contacts
                updated_contacts = db_manager.get_all_contacts()
                print(f"📊 Total contacts now: {len(updated_contacts)}")
            else:
                print("❌ Contact sync failed")
                print(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Contact sync timed out")
            return False
        except Exception as e:
            print(f"❌ Contact sync error: {e}")
            return False
    
    # Step 4: Test functionality
    print(f"\n🧪 Step 4: Testing Contact Functionality")
    print("-" * 40)
    
    # Get updated contact list
    final_contacts = db_manager.get_all_contacts()
    
    if len(final_contacts) == 0:
        print("❌ No contacts available for testing")
        return False
    
    print(f"✅ {len(final_contacts)} contacts available for testing")
    
    # Test with a sample contact
    test_contact = final_contacts[0]
    print(f"🎯 Testing with contact: {test_contact['name']}")
    
    # Test contact lookup
    found_contact = db_manager.get_contact(test_contact['name'])
    if found_contact:
        print(f"✅ Contact lookup successful: {found_contact['name']} - {found_contact['mobile_no']}")
    else:
        print("❌ Contact lookup failed")
        return False
    
    # Test WhatsApp automation (dry run)
    print("📱 Testing WhatsApp automation...")
    whatsapp_result = android_controller.whatsapp_automation(
        test_contact['name'], 
        "Test message from JARVIS setup", 
        "message"
    )
    
    if whatsapp_result['success']:
        print(f"✅ WhatsApp test successful: {whatsapp_result['message']}")
    else:
        print(f"⚠️ WhatsApp test warning: {whatsapp_result['message']}")
    
    # Step 5: Final instructions
    print(f"\n🎉 Step 5: Setup Complete!")
    print("-" * 25)
    
    print("✅ JARVIS is now configured with your real contacts!")
    print(f"📊 Total contacts: {len(final_contacts)}")
    print()
    print("🚀 You can now use commands like:")
    print(f"  - 'call {test_contact['name']}'")
    print(f"  - 'message {test_contact['name']}'")
    print(f"  - 'whatsapp {test_contact['name']} hello'")
    print(f"  - 'whatsapp call {test_contact['name']}'")
    print()
    print("🧪 To test the functionality:")
    print("  - Run: python test_real_contacts.py")
    print("  - Or run: python main.py")
    print()
    print("📋 To manage contacts:")
    print("  - Run: python sync_contacts.py")
    
    # Ask if user wants to test now
    test_now = input("\nDo you want to test contact functionality now? (y/n): ").lower().strip()
    
    if test_now == 'y':
        print("\n🧪 Starting contact test...")
        try:
            subprocess.run([sys.executable, 'test_real_contacts.py'])
        except Exception as e:
            print(f"❌ Test error: {e}")
    
    return True

def check_requirements():
    """Check if all required packages are installed"""
    
    print("📦 Checking Requirements")
    print("-" * 25)
    
    required_packages = [
        'sqlite3',
        'subprocess',
        'pyautogui',
        'pyttsx3'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install <package_name>")
        return False
    
    print("✅ All requirements satisfied")
    return True

if __name__ == "__main__":
    try:
        print("🔍 Checking requirements...")
        if not check_requirements():
            sys.exit(1)
        
        print("\n" + "=" * 50)
        success = main()
        
        if success:
            print("\n🎉 Setup completed successfully!")
            print("JARVIS is ready to use with your real contacts!")
        else:
            print("\n❌ Setup failed. Please check the errors above.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        import traceback
        traceback.print_exc()