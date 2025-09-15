#!/usr/bin/env python3
"""
Import contacts from contacts.csv file into JARVIS database
"""

import csv
import os
from engine.database_manager import DatabaseManager

def import_contacts_from_csv(csv_file_path: str = "contacts.csv"):
    """Import contacts from CSV file"""
    
    print(f"📋 Importing contacts from {csv_file_path}")
    
    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file not found: {csv_file_path}")
        return False
    
    # Initialize database
    db_manager = DatabaseManager()
    
    # Clear existing contacts
    try:
        cursor = db_manager.sqlite_conn.cursor()
        cursor.execute("DELETE FROM contacts")
        db_manager.sqlite_conn.commit()
        print("🗑️ Cleared existing contacts")
    except Exception as e:
        print(f"⚠️ Warning: Could not clear existing contacts: {e}")
    
    # Read and import contacts
    imported_count = 0
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            # Try to detect if file has headers
            sample = file.read(1024)
            file.seek(0)
            
            # Check if first line looks like headers
            first_line = file.readline().strip()
            file.seek(0)
            
            has_headers = 'name' in first_line.lower() or 'phone' in first_line.lower()
            
            if has_headers:
                reader = csv.DictReader(file)
                for row in reader:
                    # Try different column name variations
                    name = (row.get('Name') or 
                           row.get('name') or 
                           row.get('Display Name') or 
                           row.get('Given Name') or '').strip()
                    
                    phone = (row.get('Phone Number') or 
                            row.get('Phone') or 
                            row.get('phone') or 
                            row.get('Mobile') or 
                            row.get('Phone 1 - Value') or '').strip()
                    
                    email = (row.get('Email') or 
                            row.get('email') or 
                            row.get('E-mail 1 - Value') or '').strip()
                    
                    if name and phone:
                        # Clean phone number
                        phone = clean_phone_number(phone)
                        
                        if db_manager.add_contact(name, phone, email):
                            imported_count += 1
                            print(f"✅ Added: {name} - {phone}")
                        else:
                            print(f"❌ Failed to add: {name}")
            else:
                # No headers, assume first column is name, second is phone
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= 2:
                        name = row[0].strip()
                        phone = row[1].strip()
                        email = row[2].strip() if len(row) > 2 else ''
                        
                        if name and phone:
                            # Clean phone number
                            phone = clean_phone_number(phone)
                            
                            if db_manager.add_contact(name, phone, email):
                                imported_count += 1
                                print(f"✅ Added: {name} - {phone}")
                            else:
                                print(f"❌ Failed to add: {name}")
        
        print(f"\n🎉 Successfully imported {imported_count} contacts!")
        
        # Show imported contacts
        all_contacts = db_manager.get_all_contacts()
        print(f"\n📋 Total contacts in database: {len(all_contacts)}")
        
        if all_contacts:
            print("📞 Imported contacts:")
            for contact in all_contacts:
                email_info = f" ({contact['email']})" if contact['email'] else ""
                print(f"  - {contact['name']}: {contact['mobile_no']}{email_info}")
        
        return imported_count > 0
        
    except Exception as e:
        print(f"❌ Error importing contacts: {e}")
        return False

def clean_phone_number(phone: str) -> str:
    """Clean and format phone number"""
    import re
    
    # Remove all non-digit characters except +
    phone = re.sub(r'[^\d+]', '', phone)
    
    # Add country code if missing (assuming India +91, adjust as needed)
    if phone and not phone.startswith('+'):
        if len(phone) == 10:
            phone = '+91' + phone
        elif len(phone) == 11 and phone.startswith('0'):
            phone = '+91' + phone[1:]
    
    return phone

if __name__ == "__main__":
    print("🤖 JARVIS Contact CSV Importer")
    print("=" * 35)
    
    # Check if contacts.csv exists
    csv_files = ['contacts.csv', '../contacts.csv']
    csv_file = None
    
    for file_path in csv_files:
        if os.path.exists(file_path):
            csv_file = file_path
            break
    
    if not csv_file:
        print("❌ contacts.csv file not found!")
        print("Please ensure contacts.csv is in the current directory or parent directory")
        
        # Ask user for custom path
        custom_path = input("Enter path to your contacts CSV file (or press Enter to skip): ").strip()
        if custom_path and os.path.exists(custom_path):
            csv_file = custom_path
        else:
            print("❌ No valid CSV file found. Exiting.")
            exit(1)
    
    print(f"📁 Found CSV file: {csv_file}")
    
    # Import contacts
    success = import_contacts_from_csv(csv_file)
    
    if success:
        print("\n✅ Contact import completed successfully!")
        print("🚀 You can now use JARVIS with your real contacts!")
        print("\nTry commands like:")
        print("  - 'call Tom'")
        print("  - 'message Tom'")
        print("  - 'whatsapp Tom hello'")
    else:
        print("\n❌ Contact import failed!")