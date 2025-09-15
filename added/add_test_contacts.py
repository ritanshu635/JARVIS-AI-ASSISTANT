#!/usr/bin/env python3
"""
Add test contacts for JARVIS testing
"""
from engine.database_manager import initialize_default_data

def add_test_contacts():
    """Add some test contacts"""
    print("📞 Adding test contacts...")
    
    db_manager = initialize_default_data()
    
    # Add test contacts
    test_contacts = [
        ("Tom", "9876543210", "tom@example.com"),
        ("John", "9876543211", "john@example.com"),
        ("Sarah", "9876543212", "sarah@example.com"),
        ("Mike", "9876543213", "mike@example.com"),
        ("Lisa", "9876543214", "lisa@example.com")
    ]
    
    for name, phone, email in test_contacts:
        success = db_manager.add_contact(name, phone, email)
        if success:
            print(f"✅ Added contact: {name} - {phone}")
        else:
            print(f"❌ Failed to add: {name}")
    
    # List all contacts
    print("\n📋 All contacts in database:")
    contacts = db_manager.get_all_contacts()
    for contact in contacts:
        print(f"   {contact['name']} - {contact['mobile_no']}")
    
    print(f"\n🎉 Total contacts: {len(contacts)}")

if __name__ == "__main__":
    add_test_contacts()