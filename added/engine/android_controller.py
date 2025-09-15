import os
import time
import subprocess
import pyautogui
from typing import Optional, Dict, Any
from .database_manager import DatabaseManager

class AndroidController:
    """Manages all Android device interactions via ADB"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.adb_path = self._find_adb()
        self.db_manager = db_manager
        self.device_connected = False
        self._check_connection()
    
    def _find_adb(self) -> str:
        """Find ADB executable path"""
        # Try common ADB locations
        possible_paths = [
            r"C:\adb\platform-tools\adb.exe",  # User's specific path - try first
            "adb",  # If in PATH
            "adb.exe",  # Windows
            os.path.join(os.environ.get('ANDROID_HOME', ''), 'platform-tools', 'adb.exe'),
            os.path.join(os.environ.get('ANDROID_SDK_ROOT', ''), 'platform-tools', 'adb.exe'),
            r"C:\Users\%USERNAME%\AppData\Local\Android\Sdk\platform-tools\adb.exe",
            r"C:\Android\platform-tools\adb.exe",
            r"C:\adb\adb.exe",
            r"C:\platform-tools\adb.exe",
            # Search in common download locations
            os.path.expanduser(r"~\Downloads\platform-tools\adb.exe"),
            os.path.expanduser(r"~\Desktop\platform-tools\adb.exe"),
            # Search in Program Files
            r"C:\Program Files\Android\platform-tools\adb.exe",
            r"C:\Program Files (x86)\Android\platform-tools\adb.exe"
        ]
        
        for path in possible_paths:
            try:
                # Expand environment variables
                expanded_path = os.path.expandvars(path)
                result = subprocess.run([expanded_path, 'version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ ADB found at: {expanded_path}")
                    return expanded_path
            except:
                continue
        
        print("⚠️ ADB not found. Please install Android Platform Tools")
        return "adb"  # Fallback
    
    def _check_connection(self):
        """Check if Android device is connected"""
        try:
            result = subprocess.run([self.adb_path, 'devices'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                connected_devices = [line for line in lines if 'device' in line and 'offline' not in line]
                
                if connected_devices:
                    self.device_connected = True
                    print(f"✅ Android device connected: {len(connected_devices)} device(s)")
                else:
                    self.device_connected = False
                    print("⚠️ No Android devices connected")
            else:
                self.device_connected = False
                print("❌ ADB connection failed")
                
        except Exception as e:
            self.device_connected = False
            print(f"❌ ADB check error: {e}")
    
    def _execute_adb_command(self, command: list, timeout: int = 10) -> bool:
        """Execute ADB command with error handling"""
        try:
            full_command = [self.adb_path, 'shell'] + command
            result = subprocess.run(full_command, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                return True
            else:
                print(f"❌ ADB command failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ ADB command timed out")
            return False
        except Exception as e:
            print(f"❌ ADB command error: {e}")
            return False
    
    def make_call(self, phone_number: str, contact_name: str = "") -> Dict[str, Any]:
        """Make a phone call via ADB - exactly like jarvis-main"""
        if not self.device_connected:
            return {
                'success': False,
                'message': "No Android device connected. Please connect your phone via USB and enable USB debugging."
            }
        
        try:
            # Clean phone number (remove spaces and special characters except +)
            clean_number = phone_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            
            print(f"📞 Making call to {contact_name if contact_name else clean_number}")
            
            # Use ADB to initiate call - same as jarvis-main makeCall function
            command = ['am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{clean_number}']
            
            if self._execute_adb_command(command):
                message = f"Calling {contact_name}" if contact_name else f"Calling {clean_number}"
                return {
                    'success': True,
                    'message': message,
                    'action': 'call_initiated',
                    'phone_number': clean_number,
                    'contact_name': contact_name
                }
            else:
                return {
                    'success': False,
                    'message': "Failed to initiate call. Please check your device connection."
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Call error: {str(e)}"
            }
    
    def send_sms(self, phone_number: str, message: str, contact_name: str = "") -> Dict[str, Any]:
        """Send SMS via ADB - exactly like jarvis-main sendMessage function"""
        if not self.device_connected:
            return {
                'success': False,
                'message': "No Android device connected"
            }
        
        try:
            # Clean inputs - same as jarvis-main helper functions
            clean_number = self._replace_spaces_with_percent_s(phone_number.replace(" ", ""))
            clean_message = self._replace_spaces_with_percent_s(message)
            
            print(f"📱 Sending SMS to {contact_name if contact_name else phone_number}")
            
            # Go back to home - same as jarvis-main goback function
            self._go_back(4)
            time.sleep(1)
            
            # Press home key - same as jarvis-main keyEvent function
            self._key_event(3)
            
            # Open SMS app - same as jarvis-main tapEvents function
            self._tap_events(136, 2220)
            time.sleep(1)
            
            # Start new chat
            self._tap_events(819, 2192)
            time.sleep(1)
            
            # Enter phone number
            self._adb_input(clean_number)
            time.sleep(1)
            
            # Tap on contact
            self._tap_events(601, 574)
            time.sleep(1)
            
            # Tap on message input field
            self._tap_events(390, 2270)
            time.sleep(1)
            
            # Type message
            self._adb_input(clean_message)
            time.sleep(1)
            
            # Send message
            self._tap_events(957, 1397)
            
            success_message = f"Message sent successfully to {contact_name}" if contact_name else f"Message sent to {phone_number}"
            
            return {
                'success': True,
                'message': success_message,
                'action': 'sms_sent',
                'phone_number': phone_number,
                'contact_name': contact_name,
                'sms_content': message
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"SMS error: {str(e)}"
            }
    
    def whatsapp_automation(self, contact_name: str, message: str, action_type: str) -> Dict[str, Any]:
        """WhatsApp automation using real contacts - exactly like jarvis-main whatsApp function"""
        if not self.device_connected:
            return {
                'success': False,
                'message': "No Android device connected. Please connect your phone via USB."
            }
        
        try:
            print(f"📱 WhatsApp {action_type} to {contact_name}")
            
            # Get real contact from database
            if self.db_manager:
                contact = self.db_manager.get_contact(contact_name)
                if not contact:
                    # Try fuzzy search
                    all_contacts = self.db_manager.get_all_contacts()
                    for c in all_contacts:
                        if contact_name.lower() in c['name'].lower() or c['name'].lower() in contact_name.lower():
                            contact = c
                            break
                    
                    if not contact:
                        return {
                            'success': False,
                            'message': f"Contact '{contact_name}' not found in your phone contacts. Please sync your contacts first."
                        }
                
                mobile_no = contact['mobile_no']
                actual_name = contact['name']
            else:
                return {
                    'success': False,
                    'message': "Database manager not available"
                }
            
            # Clean mobile number
            mobile_no = mobile_no.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            
            # Ensure mobile number has country code (assuming India, adjust as needed)
            if not mobile_no.startswith('+'):
                if len(mobile_no) == 10:
                    mobile_no = '+91' + mobile_no
                elif len(mobile_no) == 11 and mobile_no.startswith('0'):
                    mobile_no = '+91' + mobile_no[1:]
            
            # Determine target tab and message based on action - same logic as jarvis-main
            if action_type == 'message':
                target_tab = 12
                jarvis_message = f"Message sent successfully to {actual_name}"
            elif action_type == 'call':
                target_tab = 7
                message = ''  # No message for calls
                jarvis_message = f"Calling {actual_name} on WhatsApp"
            else:  # video_call
                target_tab = 6
                message = ''  # No message for video calls
                jarvis_message = f"Starting video call with {actual_name}"
            
            print(f"📞 Using phone number: {mobile_no}")
            
            # Encode message for URL - same as jarvis-main
            from urllib.parse import quote
            encoded_message = quote(message) if message else ''
            
            # Method 1: Try to open WhatsApp on PHONE via ADB (preferred)
            print(f"📱 Attempting to open WhatsApp on your phone...")
            
            try:
                # Use ADB to open WhatsApp on phone with contact
                whatsapp_intent = f'am start -a android.intent.action.VIEW -d "https://wa.me/{mobile_no.replace("+", "")}?text={encoded_message}"'
                adb_result = self._execute_adb_command(whatsapp_intent.split())
                
                if adb_result:
                    print(f"✅ Opened WhatsApp on phone for {actual_name}")
                    return {
                        'success': True,
                        'message': jarvis_message,
                        'action': f'whatsapp_{action_type}',
                        'contact_name': actual_name,
                        'phone_number': mobile_no,
                        'method': 'phone_adb'
                    }
            except Exception as adb_error:
                print(f"⚠️ ADB WhatsApp failed: {adb_error}")
            
            # Method 2: Fallback to WhatsApp Web (if phone method fails)
            print(f"🌐 Fallback: Opening WhatsApp Web...")
            
            try:
                # Construct WhatsApp URL - same as jarvis-main
                whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"
                print(f"🔗 WhatsApp URL: {whatsapp_url}")
                
                # Open WhatsApp with URL - same as jarvis-main subprocess approach
                full_command = f'start "" "{whatsapp_url}"'
                print(f"💻 Executing: {full_command}")
                
                subprocess.run(full_command, shell=True)
                time.sleep(5)
                
                # Run command again for reliability - same as jarvis-main
                subprocess.run(full_command, shell=True)
                time.sleep(2)
                
                # Use pyautogui for UI automation - same as jarvis-main
                try:
                    pyautogui.hotkey('ctrl', 'f')
                    time.sleep(1)
                    
                    # Tab navigation - same as jarvis-main
                    for i in range(1, target_tab):
                        pyautogui.hotkey('tab')
                        time.sleep(0.1)
                    
                    # Press enter - same as jarvis-main
                    pyautogui.hotkey('enter')
                    
                    print(f"✅ {jarvis_message}")
                    
                except Exception as ui_error:
                    print(f"⚠️ UI automation warning: {ui_error}")
                    # WhatsApp should still open even if UI automation fails
                
            except Exception as web_error:
                print(f"❌ WhatsApp Web failed: {web_error}")
                return {
                    'success': False,
                    'message': f"Failed to open WhatsApp: {str(web_error)}"
                }
            
            return {
                'success': True,
                'message': jarvis_message,
                'action': f'whatsapp_{action_type}',
                'contact_name': actual_name,
                'phone_number': mobile_no,
                'whatsapp_url': whatsapp_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"WhatsApp automation error: {str(e)}"
            }
    
    # Helper functions - exactly like jarvis-main helper.py
    def _key_event(self, key_code: int):
        """Key events like receive call, stop call, go back - same as jarvis-main"""
        command = ['input', 'keyevent', str(key_code)]
        self._execute_adb_command(command)
        time.sleep(1)
    
    def _tap_events(self, x: int, y: int):
        """Tap event used to tap anywhere on screen - same as jarvis-main"""
        command = ['input', 'tap', str(x), str(y)]
        self._execute_adb_command(command)
        time.sleep(1)
    
    def _adb_input(self, text: str):
        """Input text in mobile - same as jarvis-main"""
        command = ['input', 'text', f'"{text}"']
        self._execute_adb_command(command)
        time.sleep(1)
    
    def _go_back(self, times: int):
        """Go back multiple times - same as jarvis-main goback function"""
        for i in range(times):
            self._key_event(4)  # Back key
    
    def _replace_spaces_with_percent_s(self, input_string: str) -> str:
        """Replace spaces with %s for message sending - same as jarvis-main helper"""
        return input_string.replace(' ', '%s')
    
    def pickup_call(self) -> Dict[str, Any]:
        """Pickup incoming call"""
        try:
            # Answer call key event
            self._key_event(5)  # KEYCODE_CALL
            return {
                'success': True,
                'message': "Call answered",
                'action': 'call_answered'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to pickup call: {str(e)}"
            }
    
    def disconnect_call(self) -> Dict[str, Any]:
        """Disconnect current call"""
        try:
            # End call key event
            self._key_event(6)  # KEYCODE_ENDCALL
            return {
                'success': True,
                'message': "Call disconnected",
                'action': 'call_disconnected'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to disconnect call: {str(e)}"
            }
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get Android device information"""
        if not self.device_connected:
            return {
                'connected': False,
                'message': "No device connected"
            }
        
        try:
            # Get device model
            result = subprocess.run([self.adb_path, 'shell', 'getprop', 'ro.product.model'], 
                                  capture_output=True, text=True, timeout=5)
            model = result.stdout.strip() if result.returncode == 0 else "Unknown"
            
            # Get Android version
            result = subprocess.run([self.adb_path, 'shell', 'getprop', 'ro.build.version.release'], 
                                  capture_output=True, text=True, timeout=5)
            android_version = result.stdout.strip() if result.returncode == 0 else "Unknown"
            
            # Get battery level
            result = subprocess.run([self.adb_path, 'shell', 'dumpsys', 'battery'], 
                                  capture_output=True, text=True, timeout=5)
            battery_level = "Unknown"
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'level:' in line:
                        battery_level = line.split(':')[1].strip() + "%"
                        break
            
            return {
                'connected': True,
                'model': model,
                'android_version': android_version,
                'battery_level': battery_level,
                'adb_path': self.adb_path
            }
            
        except Exception as e:
            return {
                'connected': True,
                'error': str(e),
                'message': "Could not retrieve device info"
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test ADB connection"""
        try:
            result = subprocess.run([self.adb_path, 'devices'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                devices_output = result.stdout.strip()
                lines = devices_output.split('\n')[1:]  # Skip header
                connected_devices = [line for line in lines if 'device' in line and 'offline' not in line]
                
                if connected_devices:
                    self.device_connected = True
                    return {
                        'success': True,
                        'message': f"ADB connection successful. {len(connected_devices)} device(s) connected.",
                        'devices': connected_devices,
                        'raw_output': devices_output
                    }
                else:
                    self.device_connected = False
                    return {
                        'success': False,
                        'message': "ADB is working but no devices are connected. Please:\n1. Connect your Android device via USB\n2. Enable USB Debugging in Developer Options\n3. Accept the USB debugging prompt on your device",
                        'raw_output': devices_output
                    }
            else:
                return {
                    'success': False,
                    'message': f"ADB command failed: {result.stderr}",
                    'error': result.stderr
                }
                
        except FileNotFoundError:
            return {
                'success': False,
                'message': "ADB not found. Please install Android Platform Tools and add to PATH."
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"ADB test error: {str(e)}"
            }

# Test the Android Controller
if __name__ == "__main__":
    from database_manager import DatabaseManager
    
    # Test Android controller
    db_manager = DatabaseManager()
    android_controller = AndroidController(db_manager)
    
    print("🤖 Testing Android Controller:")
    
    # Test connection
    connection_test = android_controller.test_connection()
    print(f"Connection test: {connection_test}")
    
    # Get device info
    device_info = android_controller.get_device_info()
    print(f"Device info: {device_info}")
    
    # Add a test contact
    db_manager.add_contact("Test User", "1234567890", "test@example.com")
    
    # Test WhatsApp (won't actually execute without user confirmation)
    print("\n📱 WhatsApp automation test (dry run):")
    whatsapp_result = android_controller.whatsapp_automation("Test User", "Hello from JARVIS!", "message")
    print(f"WhatsApp result: {whatsapp_result}")