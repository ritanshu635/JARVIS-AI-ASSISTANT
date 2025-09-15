#!/usr/bin/env python3
"""
Real Phone Integration - Import contacts and implement real phone functions
"""
import subprocess
import json
import time
import re
from engine.database_manager import initialize_default_data

class RealPhoneIntegration:
    def __init__(self):
        self.adb_path = r"C:\adb\platform-tools\adb.exe"
        self.db_manager = initialize_default_data()
    
    def import_real_contacts(self):
        """Import contacts from your actual phone"""
        print("📱 Importing real contacts from your phone...")
        
        try:
            # Get contacts from phone using ADB
            cmd = [self.adb_path, 'shell', 'content', 'query', '--uri', 'content://com.android.contacts/data', '--projection', 'display_name:data1:mimetype']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                contacts_data = result.stdout
                contacts = self._parse_contacts(contacts_data)
                
                # Clear existing test contacts
                print("🗑️ Clearing test contacts...")
                
                # Add real contacts to database
                added_count = 0
                for contact in contacts:
                    if contact['name'] and contact['phone']:
                        success = self.db_manager.add_contact(
                            contact['name'], 
                            contact['phone'], 
                            contact.get('email', '')
                        )
                        if success:
                            added_count += 1
                            print(f"✅ Added: {contact['name']} - {contact['phone']}")
                
                print(f"🎉 Imported {added_count} real contacts from your phone!")
                return True
            else:
                print(f"❌ Failed to get contacts: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Contact import error: {e}")
            return False
    
    def _parse_contacts(self, contacts_data):
        """Parse contacts data from ADB output"""
        contacts = []
        current_contact = {'name': '', 'phone': '', 'email': ''}
        
        for line in contacts_data.split('\n'):
            if 'Row:' in line:
                if current_contact['name'] or current_contact['phone']:
                    contacts.append(current_contact.copy())
                current_contact = {'name': '', 'phone': '', 'email': ''}
            
            elif 'display_name=' in line:
                name = line.split('display_name=')[1].split(',')[0].strip()
                current_contact['name'] = name
            
            elif 'data1=' in line and 'mimetype=vnd.android.cursor.item/phone_v2' in line:
                phone = line.split('data1=')[1].split(',')[0].strip()
                current_contact['phone'] = phone
            
            elif 'data1=' in line and 'mimetype=vnd.android.cursor.item/email_v2' in line:
                email = line.split('data1=')[1].split(',')[0].strip()
                current_contact['email'] = email
        
        # Add last contact
        if current_contact['name'] or current_contact['phone']:
            contacts.append(current_contact)
        
        # Filter out duplicates and empty contacts
        unique_contacts = []
        seen_names = set()
        
        for contact in contacts:
            if contact['name'] and contact['name'] not in seen_names and contact['phone']:
                unique_contacts.append(contact)
                seen_names.add(contact['name'])
        
        return unique_contacts
    
    def test_real_call(self, contact_name):
        """Test making a real call to a contact"""
        print(f"📞 Testing real call to {contact_name}...")
        
        # Get contact from database
        contact = self.db_manager.get_contact(contact_name)
        if not contact:
            print(f"❌ Contact {contact_name} not found")
            return False
        
        try:
            # Clean phone number
            phone = contact['mobile_no'].replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # Make actual call using ADB
            cmd = [self.adb_path, 'shell', 'am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{phone}']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ Successfully initiated call to {contact['name']} at {phone}")
                print("📱 Check your phone - the call should be starting!")
                return True
            else:
                print(f"❌ Call failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Call error: {e}")
            return False
    
    def test_real_sms(self, contact_name, message):
        """Test sending a real SMS"""
        print(f"📱 Testing real SMS to {contact_name}: {message}")
        
        # Get contact from database
        contact = self.db_manager.get_contact(contact_name)
        if not contact:
            print(f"❌ Contact {contact_name} not found")
            return False
        
        try:
            # Clean phone number and message
            phone = contact['mobile_no'].replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            clean_message = message.replace(' ', '%s')
            
            print(f"📱 Sending SMS to {phone}: {message}")
            
            # Use the original jarvis-main SMS method
            # Go back to home
            self._adb_key_event(4, 4)  # Back key 4 times
            time.sleep(1)
            
            # Press home key
            self._adb_key_event(3)  # Home key
            time.sleep(1)
            
            # Open SMS app (tap coordinates may need adjustment for your phone)
            self._adb_tap(136, 2220)  # SMS app icon
            time.sleep(2)
            
            # Start new message
            self._adb_tap(819, 2192)  # New message button
            time.sleep(1)
            
            # Enter phone number
            self._adb_input(phone)
            time.sleep(1)
            
            # Tap on contact
            self._adb_tap(601, 574)  # Contact selection
            time.sleep(1)
            
            # Tap message input field
            self._adb_tap(390, 2270)  # Message input
            time.sleep(1)
            
            # Type message
            self._adb_input(clean_message)
            time.sleep(1)
            
            # Send message
            self._adb_tap(957, 1397)  # Send button
            
            print(f"✅ SMS sent to {contact['name']}")
            return True
            
        except Exception as e:
            print(f"❌ SMS error: {e}")
            return False
    
    def test_real_whatsapp(self, contact_name, message="", action="message"):
        """Test real WhatsApp automation"""
        print(f"📱 Testing real WhatsApp {action} to {contact_name}")
        
        # Get contact from database
        contact = self.db_manager.get_contact(contact_name)
        if not contact:
            print(f"❌ Contact {contact_name} not found")
            return False
        
        try:
            phone = contact['mobile_no']
            if not phone.startswith('+91'):
                phone = '+91' + phone.replace(' ', '').replace('-', '')
            
            # Use WhatsApp URL scheme - exactly like jarvis-main
            from urllib.parse import quote
            encoded_message = quote(message) if message else ''
            
            whatsapp_url = f"whatsapp://send?phone={phone}&text={encoded_message}"
            
            # Open WhatsApp
            full_command = f'start "" "{whatsapp_url}"'
            subprocess.run(full_command, shell=True)
            time.sleep(5)
            
            # Run again for reliability
            subprocess.run(full_command, shell=True)
            time.sleep(2)
            
            # UI automation for different actions
            import pyautogui
            
            if action == "message":
                # Focus and send message
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(1)
                
                # Tab to send button (12 tabs for message)
                for i in range(12):
                    pyautogui.press('tab')
                    time.sleep(0.1)
                
                pyautogui.press('enter')
                print(f"✅ WhatsApp message sent to {contact['name']}")
                
            elif action == "call":
                # Tab to call button (7 tabs for call)
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(1)
                
                for i in range(7):
                    pyautogui.press('tab')
                    time.sleep(0.1)
                
                pyautogui.press('enter')
                print(f"✅ WhatsApp call initiated to {contact['name']}")
                
            elif action == "video_call":
                # Tab to video call button (6 tabs for video call)
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(1)
                
                for i in range(6):
                    pyautogui.press('tab')
                    time.sleep(0.1)
                
                pyautogui.press('enter')
                print(f"✅ WhatsApp video call initiated to {contact['name']}")
            
            return True
            
        except Exception as e:
            print(f"❌ WhatsApp error: {e}")
            return False
    
    def _adb_key_event(self, key_code, times=1):
        """Send key events via ADB"""
        for _ in range(times):
            cmd = [self.adb_path, 'shell', 'input', 'keyevent', str(key_code)]
            subprocess.run(cmd, capture_output=True)
            time.sleep(0.5)
    
    def _adb_tap(self, x, y):
        """Tap at coordinates via ADB"""
        cmd = [self.adb_path, 'shell', 'input', 'tap', str(x), str(y)]
        subprocess.run(cmd, capture_output=True)
        time.sleep(0.5)
    
    def _adb_input(self, text):
        """Input text via ADB"""
        cmd = [self.adb_path, 'shell', 'input', 'text', f'"{text}"']
        subprocess.run(cmd, capture_output=True)
        time.sleep(0.5)
    
    def get_phone_info(self):
        """Get your phone information"""
        try:
            # Get device model
            cmd = [self.adb_path, 'shell', 'getprop', 'ro.product.model']
            result = subprocess.run(cmd, capture_output=True, text=True)
            model = result.stdout.strip()
            
            # Get Android version
            cmd = [self.adb_path, 'shell', 'getprop', 'ro.build.version.release']
            result = subprocess.run(cmd, capture_output=True, text=True)
            android_version = result.stdout.strip()
            
            print(f"📱 Your Phone: {model}")
            print(f"🤖 Android Version: {android_version}")
            
            return {'model': model, 'android_version': android_version}
            
        except Exception as e:
            print(f"❌ Phone info error: {e}")
            return None

def main():
    """Main function to set up real phone integration"""
    print("🚀 JARVIS REAL PHONE INTEGRATION SETUP")
    print("=" * 60)
    
    phone_integration = RealPhoneIntegration()
    
    # Get phone info
    phone_info = phone_integration.get_phone_info()
    
    # Import real contacts
    print("\n📱 Step 1: Import Real Contacts")
    contacts_imported = phone_integration.import_real_contacts()
    
    if contacts_imported:
        # List imported contacts
        print("\n📋 Your Real Contacts:")
        contacts = phone_integration.db_manager.get_all_contacts()
        for i, contact in enumerate(contacts[-10:], 1):  # Show last 10
            print(f"   {i}. {contact['name']} - {contact['mobile_no']}")
        
        print(f"\n✅ Total contacts: {len(contacts)}")
        
        # Test functionality
        print("\n🧪 Step 2: Test Real Phone Functions")
        
        if contacts:
            test_contact = contacts[-1]['name']  # Use last contact for testing
            
            print(f"\n📞 Testing call to {test_contact}...")
            input("⚠️ This will make a REAL call! Press Enter to continue or Ctrl+C to skip...")
            
            try:
                phone_integration.test_real_call(test_contact)
            except KeyboardInterrupt:
                print("📞 Call test skipped")
            
            print(f"\n📱 Testing SMS to {test_contact}...")
            input("⚠️ This will send a REAL SMS! Press Enter to continue or Ctrl+C to skip...")
            
            try:
                phone_integration.test_real_sms(test_contact, "Hello from JARVIS! This is a test message.")
            except KeyboardInterrupt:
                print("📱 SMS test skipped")
            
            print(f"\n💬 Testing WhatsApp to {test_contact}...")
            input("⚠️ This will open WhatsApp! Press Enter to continue or Ctrl+C to skip...")
            
            try:
                phone_integration.test_real_whatsapp(test_contact, "Hello from JARVIS!", "message")
            except KeyboardInterrupt:
                print("💬 WhatsApp test skipped")
    
    print("\n🎉 Real phone integration setup complete!")
    print("💡 Now JARVIS will use your real contacts and phone functions!")

if __name__ == "__main__":
    main()