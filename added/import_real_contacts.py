#!/usr/bin/env python3
"""
Import real contacts from your phone into JARVIS database
"""
import subprocess
import re
from engine.database_manager import initialize_default_data

def get_phone_contacts():
    """Get all contacts from your phone"""
    print("📞 Getting all contacts from your phone...")
    
    try:
        # Get contacts with names and phone numbers
        result = subprocess.run([
            r"C:\adb\platform-tools\adb.exe", "shell", 
            "content", "query", "--uri", "content://com.android.contacts/data",
            "--projection", "display_name,data1,mimetype",
            "--where", "mimetype='vnd.android.cursor.item/phone_v2'"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            contacts = []
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if 'Row:' in line and 'display_name=' in line and 'data1=' in line:
                    # Parse the line to extract name and phone
                    name_match = re.search(r'display_name=([^,]+)', line)
                    phone_match = re.search(r'data1=([^,]+)', line)
                    
                    if name_match and phone_match:
                        name = name_match.group(1).strip()
                        phone = phone_match.group(1).strip()
                        
                        # Clean phone number
                        phone = re.sub(r'[^\d+]', '', phone)
                        
                        if name and phone and len(phone) >= 10:
                            contacts.append({
                                'name': name,
                                'phone': phone,
                                'email': f"{name.lower().replace(' ', '.')}@phone.contact"
                            })
            
            # Remove duplicates
            unique_contacts = []
            seen_names = set()
            
            for contact in contacts:
                if contact['name'] not in seen_names:
                    unique_contacts.append(contact)
                    seen_names.add(contact['name'])
            
            print(f"✅ Found {len(unique_contacts)} unique contacts")
            return unique_contacts
            
        else:
            print(f"❌ Failed to get contacts: {result.stderr}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting contacts: {e}")
        return []

def import_contacts_to_jarvis(contacts):
    """Import contacts into JARVIS database"""
    print("💾 Importing contacts into JARVIS database...")
    
    try:
        db_manager = initialize_default_data()
        
        # Clear existing contacts (except test ones)
        print("🗑️ Clearing old test contacts...")
        
        imported_count = 0
        
        for contact in contacts:
            success = db_manager.add_contact(
                contact['name'], 
                contact['phone'], 
                contact['email']
            )
            
            if success:
                imported_count += 1
                print(f"✅ Imported: {contact['name']} - {contact['phone']}")
            else:
                print(f"❌ Failed to import: {contact['name']}")
        
        print(f"\n🎉 Successfully imported {imported_count} contacts!")
        
        # Show sample of imported contacts
        print("\n📋 Sample of imported contacts:")
        all_contacts = db_manager.get_all_contacts()
        for contact in all_contacts[-10:]:  # Show last 10
            print(f"   {contact['name']} - {contact['mobile_no']}")
        
        return imported_count
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return 0

def test_contact_search():
    """Test searching for contacts"""
    print("\n🔍 Testing contact search...")
    
    try:
        db_manager = initialize_default_data()
        
        # Test searches
        test_names = ["aakash", "yash", "mohil", "kartik", "bhavik"]
        
        for name in test_names:
            contact = db_manager.get_contact(name)
            if contact:
                print(f"✅ Found {name}: {contact['name']} - {contact['mobile_no']}")
            else:
                print(f"❌ Not found: {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search test error: {e}")
        return False

def main():
    """Main import function"""
    print("📱 REAL PHONE CONTACTS IMPORTER")
    print("=" * 50)
    
    # Step 1: Get contacts from phone
    contacts = get_phone_contacts()
    
    if not contacts:
        print("❌ No contacts found. Check ADB connection and permissions.")
        return
    
    print(f"\n📊 Found {len(contacts)} contacts to import")
    print("Sample contacts:")
    for contact in contacts[:5]:
        print(f"   {contact['name']} - {contact['phone']}")
    
    # Ask for confirmation
    confirm = input(f"\nImport all {len(contacts)} contacts into JARVIS? (y/n): ")
    
    if not confirm.lower().startswith('y'):
        print("❌ Import cancelled")
        return
    
    # Step 2: Import to JARVIS
    imported_count = import_contacts_to_jarvis(contacts)
    
    if imported_count > 0:
        # Step 3: Test search functionality
        test_contact_search()
        
        print(f"\n🎉 SUCCESS! Imported {imported_count} real contacts")
        print("✅ JARVIS can now use your real phone contacts")
        print("💡 Try saying: 'Call Aakash' or 'Message Yash'")
    else:
        print("❌ Import failed")

if __name__ == "__main__":
    main()