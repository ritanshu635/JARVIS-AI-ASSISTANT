import subprocess
import json
import csv
import os
import re
from typing import List, Dict, Optional
from .database_manager import DatabaseManager

class ContactExtractor:
    """Extract real contacts from Android phone via ADB"""
    
    def __init__(self, adb_path: str = "adb"):
        self.adb_path = adb_path
        self.db_manager = DatabaseManager()
    
    def extract_contacts_via_adb(self) -> List[Dict]:
        """Extract contacts directly from Android phone using ADB"""
        print("📱 Extracting contacts from your Android phone...")
        
        try:
            # Method 1: Try to get contacts via content provider
            contacts = self._extract_via_content_provider()
            if contacts:
                return contacts
            
            # Method 2: Try to export contacts to CSV and read
            contacts = self._extract_via_csv_export()
            if contacts:
                return contacts
            
            # Method 3: Manual CSV import (user exports manually)
            print("⚠️ Automatic extraction failed. Please export contacts manually.")
            return self._import_manual_csv()
            
        except Exception as e:
            print(f"❌ Contact extraction error: {e}")
            return []
    
    def _extract_via_content_provider(self) -> List[Dict]:
        """Extract contacts using Android content provider"""
        try:
            # Query contacts content provider
            cmd = [
                self.adb_path, 'shell', 
                'content', 'query', 
                '--uri', 'content://com.android.contacts/contacts',
                '--projection', 'display_name'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print("❌ Content provider query failed")
                return []
            
            # Parse the output
            contacts = []
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if 'display_name=' in line:
                    name_match = re.search(r'display_name=([^,]+)', line)
                    if name_match:
                        name = name_match.group(1).strip()
                        if name and name != 'null':
                            # Get phone number for this contact
                            phone = self._get_phone_for_contact(name)
                            if phone:
                                contacts.append({
                                    'name': name,
                                    'phone': phone,
                                    'email': ''
                                })
            
            print(f"✅ Extracted {len(contacts)} contacts via content provider")
            return contacts
            
        except Exception as e:
            print(f"❌ Content provider extraction failed: {e}")
            return []
    
    def _get_phone_for_contact(self, contact_name: str) -> Optional[str]:
        """Get phone number for a specific contact"""
        try:
            # Query phone numbers
            cmd = [
                self.adb_path, 'shell',
                'content', 'query',
                '--uri', 'content://com.android.contacts/data',
                '--projection', 'data1',
                '--where', f"display_name='{contact_name}' AND mimetype='vnd.android.cursor.item/phone_v2'"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'data1=' in line:
                        phone_match = re.search(r'data1=([^,]+)', line)
                        if phone_match:
                            phone = phone_match.group(1).strip()
                            if phone and phone != 'null':
                                return self._clean_phone_number(phone)
            
            return None
            
        except Exception as e:
            print(f"❌ Phone extraction failed for {contact_name}: {e}")
            return None
    
    def _extract_via_csv_export(self) -> List[Dict]:
        """Try to export contacts to CSV via ADB"""
        try:
            print("📤 Attempting to export contacts to CSV...")
            
            # Create a script to export contacts
            export_script = '''
            content query --uri content://com.android.contacts/contacts \\
            --projection display_name,has_phone_number > /sdcard/contacts_temp.txt
            '''
            
            # Write script to device
            cmd = [self.adb_path, 'shell', 'echo', f'"{export_script}"', '>', '/sdcard/export_contacts.sh']
            subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            # Execute script
            cmd = [self.adb_path, 'shell', 'sh', '/sdcard/export_contacts.sh']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Pull the exported file
                cmd = [self.adb_path, 'pull', '/sdcard/contacts_temp.txt', 'contacts_temp.txt']
                subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                # Parse the file
                if os.path.exists('contacts_temp.txt'):
                    contacts = self._parse_exported_contacts('contacts_temp.txt')
                    os.remove('contacts_temp.txt')  # Clean up
                    return contacts
            
            return []
            
        except Exception as e:
            print(f"❌ CSV export failed: {e}")
            return []
    
    def _import_manual_csv(self) -> List[Dict]:
        """Import contacts from manually exported CSV file"""
        print("\n📋 Manual CSV Import Instructions:")
        print("1. On your Android phone, go to Contacts app")
        print("2. Go to Settings/Menu > Import/Export > Export")
        print("3. Export contacts to a CSV file")
        print("4. Transfer the CSV file to this computer")
        print("5. Place the CSV file in the unified-jarvis folder and name it 'contacts.csv'")
        
        csv_path = input("\n📁 Enter the path to your contacts CSV file (or press Enter if it's 'contacts.csv'): ").strip()
        
        if not csv_path:
            csv_path = 'contacts.csv'
        
        if not os.path.exists(csv_path):
            print(f"❌ File not found: {csv_path}")
            return []
        
        return self._parse_csv_file(csv_path)
    
    def _parse_csv_file(self, csv_path: str) -> List[Dict]:
        """Parse CSV file and extract contacts"""
        try:
            contacts = []
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                # Try to detect CSV format
                sample = file.read(1024)
                file.seek(0)
                
                # Common CSV formats from different phones
                if 'Name,Phone' in sample or 'Display Name' in sample:
                    reader = csv.DictReader(file)
                    for row in reader:
                        name = row.get('Name') or row.get('Display Name') or row.get('Given Name', '').strip()
                        phone = row.get('Phone') or row.get('Phone 1 - Value') or row.get('Mobile', '').strip()
                        email = row.get('Email') or row.get('E-mail 1 - Value', '').strip()
                        
                        if name and phone:
                            contacts.append({
                                'name': name,
                                'phone': self._clean_phone_number(phone),
                                'email': email
                            })
                else:
                    # Try generic CSV parsing
                    reader = csv.reader(file)
                    headers = next(reader, [])
                    
                    # Find name and phone columns
                    name_col = self._find_column_index(headers, ['name', 'display', 'given'])
                    phone_col = self._find_column_index(headers, ['phone', 'mobile', 'number'])
                    email_col = self._find_column_index(headers, ['email', 'mail'])
                    
                    if name_col is not None and phone_col is not None:
                        for row in reader:
                            if len(row) > max(name_col, phone_col):
                                name = row[name_col].strip()
                                phone = row[phone_col].strip()
                                email = row[email_col].strip() if email_col is not None and len(row) > email_col else ''
                                
                                if name and phone:
                                    contacts.append({
                                        'name': name,
                                        'phone': self._clean_phone_number(phone),
                                        'email': email
                                    })
            
            print(f"✅ Parsed {len(contacts)} contacts from CSV")
            return contacts
            
        except Exception as e:
            print(f"❌ CSV parsing error: {e}")
            return []
    
    def _find_column_index(self, headers: List[str], keywords: List[str]) -> Optional[int]:
        """Find column index by keywords"""
        for i, header in enumerate(headers):
            for keyword in keywords:
                if keyword.lower() in header.lower():
                    return i
        return None
    
    def _clean_phone_number(self, phone: str) -> str:
        """Clean and format phone number"""
        # Remove all non-digit characters except +
        phone = re.sub(r'[^\d+]', '', phone)
        
        # Add country code if missing (assuming India +91)
        if phone and not phone.startswith('+'):
            if len(phone) == 10:
                phone = '+91' + phone
            elif len(phone) == 11 and phone.startswith('0'):
                phone = '+91' + phone[1:]
        
        return phone
    
    def _parse_exported_contacts(self, file_path: str) -> List[Dict]:
        """Parse exported contacts file"""
        try:
            contacts = []
            
            with open(file_path, 'r') as file:
                for line in file:
                    if 'display_name=' in line:
                        name_match = re.search(r'display_name=([^,]+)', line)
                        if name_match:
                            name = name_match.group(1).strip()
                            if name and name != 'null':
                                # For now, we'll need phone numbers separately
                                contacts.append({
                                    'name': name,
                                    'phone': '',  # Will be filled later
                                    'email': ''
                                })
            
            return contacts
            
        except Exception as e:
            print(f"❌ Export parsing error: {e}")
            return []
    
    def import_contacts_to_database(self, contacts: List[Dict]) -> bool:
        """Import extracted contacts to database"""
        try:
            print(f"💾 Importing {len(contacts)} contacts to database...")
            
            success_count = 0
            for contact in contacts:
                if self.db_manager.add_contact(
                    contact['name'], 
                    contact['phone'], 
                    contact.get('email', '')
                ):
                    success_count += 1
            
            print(f"✅ Successfully imported {success_count}/{len(contacts)} contacts")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Database import error: {e}")
            return False
    
    def sync_contacts(self) -> bool:
        """Main method to sync contacts from phone to database"""
        print("🔄 Starting contact synchronization...")
        
        # Extract contacts
        contacts = self.extract_contacts_via_adb()
        
        if not contacts:
            print("❌ No contacts extracted")
            return False
        
        # Import to database
        return self.import_contacts_to_database(contacts)
    
    def list_current_contacts(self) -> List[Dict]:
        """List contacts currently in database"""
        return self.db_manager.get_all_contacts()
    
    def clear_contacts(self) -> bool:
        """Clear all contacts from database"""
        try:
            cursor = self.db_manager.sqlite_conn.cursor()
            cursor.execute("DELETE FROM contacts")
            self.db_manager.sqlite_conn.commit()
            print("✅ All contacts cleared from database")
            return True
        except Exception as e:
            print(f"❌ Error clearing contacts: {e}")
            return False

# Test the contact extractor
if __name__ == "__main__":
    # Find ADB path
    adb_path = r"C:\adb\platform-tools\adb.exe"  # User's specific path
    
    extractor = ContactExtractor(adb_path)
    
    print("🤖 Contact Extractor Test")
    print("Current contacts in database:")
    current_contacts = extractor.list_current_contacts()
    for contact in current_contacts[:5]:  # Show first 5
        print(f"  - {contact['name']}: {contact['mobile_no']}")
    
    print(f"\nTotal contacts in database: {len(current_contacts)}")
    
    # Ask user if they want to sync
    sync = input("\nDo you want to sync contacts from your phone? (y/n): ").lower().strip()
    if sync == 'y':
        extractor.sync_contacts()