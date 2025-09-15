#!/usr/bin/env python3
"""
Contact Sync Utility for JARVIS
Extracts real contacts from your Android phone and imports them into JARVIS database
"""

import os
import sys
from engine.contact_extractor import ContactExtractor
from engine.android_controller import AndroidController

def main():
    print("🤖 JARVIS Contact Sync Utility")
    print("=" * 50)
    
    # Initialize contact extractor
    adb_path = r"C:\adb\platform-tools\adb.exe"  # Your ADB path
    extractor = ContactExtractor(adb_path)
    
    # Check ADB connection first
    android_controller = AndroidController()
    connection_test = android_controller.test_connection()
    
    if not connection_test['success']:
        print("❌ Android device not connected!")
        print("\n📱 Please ensure:")
        print("1. Your Android phone is connected via USB")
        print("2. USB Debugging is enabled in Developer Options")
        print("3. You've accepted the USB debugging prompt on your phone")
        print("4. ADB is properly installed")
        print(f"\nConnection error: {connection_test['message']}")
        return False
    
    print(f"✅ {connection_test['message']}")
    
    # Show current contacts
    current_contacts = extractor.list_current_contacts()
    print(f"\n📋 Current contacts in JARVIS database: {len(current_contacts)}")
    
    if current_contacts:
        print("First 5 contacts:")
        for i, contact in enumerate(current_contacts[:5]):
            print(f"  {i+1}. {contact['name']}: {contact['mobile_no']}")
        
        if len(current_contacts) > 5:
            print(f"  ... and {len(current_contacts) - 5} more")
    
    # Ask user what they want to do
    print("\n🔄 Contact Sync Options:")
    print("1. Sync contacts from phone (automatic extraction)")
    print("2. Import from CSV file (manual export)")
    print("3. Clear all contacts and start fresh")
    print("4. Show all current contacts")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == '1':
        print("\n🔄 Starting automatic contact extraction...")
        success = extractor.sync_contacts()
        if success:
            print("✅ Contact sync completed successfully!")
            new_contacts = extractor.list_current_contacts()
            print(f"📊 Total contacts now: {len(new_contacts)}")
        else:
            print("❌ Contact sync failed. Try manual CSV import (option 2)")
    
    elif choice == '2':
        print("\n📁 Manual CSV Import")
        print("\nInstructions:")
        print("1. On your Android phone, open Contacts app")
        print("2. Go to Settings/Menu > Import/Export > Export")
        print("3. Export contacts to a CSV file")
        print("4. Transfer the CSV file to this computer")
        print("5. Place it in the unified-jarvis folder")
        
        csv_path = input("\nEnter CSV file path (or press Enter for 'contacts.csv'): ").strip()
        if not csv_path:
            csv_path = 'contacts.csv'
        
        if os.path.exists(csv_path):
            contacts = extractor._parse_csv_file(csv_path)
            if contacts:
                success = extractor.import_contacts_to_database(contacts)
                if success:
                    print("✅ CSV import completed successfully!")
                else:
                    print("❌ CSV import failed")
            else:
                print("❌ No contacts found in CSV file")
        else:
            print(f"❌ File not found: {csv_path}")
    
    elif choice == '3':
        confirm = input("⚠️ Are you sure you want to clear all contacts? (yes/no): ").lower().strip()
        if confirm == 'yes':
            if extractor.clear_contacts():
                print("✅ All contacts cleared")
            else:
                print("❌ Failed to clear contacts")
        else:
            print("❌ Operation cancelled")
    
    elif choice == '4':
        print(f"\n📋 All contacts in database ({len(current_contacts)}):")
        for i, contact in enumerate(current_contacts):
            email_info = f" ({contact['email']})" if contact['email'] else ""
            print(f"  {i+1:3d}. {contact['name']}: {contact['mobile_no']}{email_info}")
    
    elif choice == '5':
        print("👋 Goodbye!")
        return True
    
    else:
        print("❌ Invalid choice")
    
    return True

def test_contact_functionality():
    """Test contact-based functionality"""
    print("\n🧪 Testing Contact Functionality")
    print("=" * 40)
    
    from engine.database_manager import DatabaseManager
    
    db = DatabaseManager()
    contacts = db.get_all_contacts()
    
    if not contacts:
        print("❌ No contacts found. Please sync contacts first.")
        return
    
    print(f"✅ Found {len(contacts)} contacts")
    
    # Test contact search
    test_names = ["tom", "john", "mary", "test"]
    
    for name in test_names:
        contact = db.get_contact(name)
        if contact:
            print(f"✅ Found contact for '{name}': {contact['name']} - {contact['mobile_no']}")
            
            # Test WhatsApp automation (dry run)
            android_controller = AndroidController(db)
            result = android_controller.whatsapp_automation(contact['name'], "Hello from JARVIS!", "message")
            print(f"   WhatsApp test: {result['message']}")
            break
    else:
        print("❌ No test contacts found. Try with your actual contact names.")

if __name__ == "__main__":
    try:
        main()
        
        # Ask if user wants to test functionality
        test = input("\n🧪 Do you want to test contact functionality? (y/n): ").lower().strip()
        if test == 'y':
            test_contact_functionality()
            
    except KeyboardInterrupt:
        print("\n\n👋 Sync cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()