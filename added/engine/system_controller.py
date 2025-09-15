import os
import subprocess
import webbrowser
import pyautogui
import platform
import time
import shutil
from typing import Dict, Any, List

class SystemController:
    """Handles all system-level operations like volume, brightness, apps, etc."""
    
    def __init__(self):
        self.system = platform.system()
    
    def control_volume(self, action: str) -> Dict[str, Any]:
        """Control system volume"""
        try:
            if self.system == "Windows":
                if action == 'mute':
                    # Use nircmd for volume control (if available) or pyautogui
                    try:
                        pyautogui.press('volumemute')
                        return {'success': True, 'message': 'Volume muted'}
                    except:
                        # Fallback to Windows volume mixer
                        os.system('nircmd.exe mutesysvolume 1')
                        return {'success': True, 'message': 'Volume muted'}
                elif action == 'unmute':
                    try:
                        pyautogui.press('volumemute')
                        return {'success': True, 'message': 'Volume unmuted'}
                    except:
                        os.system('nircmd.exe mutesysvolume 0')
                        return {'success': True, 'message': 'Volume unmuted'}
                elif action == 'up':
                    try:
                        for _ in range(5):
                            pyautogui.press('volumeup')
                        return {'success': True, 'message': 'Volume increased'}
                    except:
                        os.system('nircmd.exe changesysvolume 2000')
                        return {'success': True, 'message': 'Volume increased'}
                elif action == 'down':
                    try:
                        for _ in range(5):
                            pyautogui.press('volumedown')
                        return {'success': True, 'message': 'Volume decreased'}
                    except:
                        os.system('nircmd.exe changesysvolume -2000')
                        return {'success': True, 'message': 'Volume decreased'}
            
            return {'success': False, 'message': 'Volume control not supported on this system'}
        except Exception as e:
            return {'success': False, 'message': f'Volume control error: {str(e)}'}
    
    def control_brightness(self, action: str) -> Dict[str, Any]:
        """Control screen brightness"""
        try:
            if self.system == "Windows":
                if action == 'up':
                    # Use PowerShell to increase brightness
                    cmd = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,100)"
                    subprocess.run(['powershell', '-Command', cmd], capture_output=True)
                    return {'success': True, 'message': 'Brightness increased'}
                elif action == 'down':
                    cmd = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,30)"
                    subprocess.run(['powershell', '-Command', cmd], capture_output=True)
                    return {'success': True, 'message': 'Brightness decreased'}
            else:
                return {'success': False, 'message': 'Brightness control not supported on this system'}
        except Exception as e:
            return {'success': False, 'message': f'Brightness control error: {str(e)}'}
    
    def open_application(self, app_name: str) -> Dict[str, Any]:
        """Open an application"""
        try:
            # Try built-in system commands first
            if self.system == "Windows":
                # Common Windows applications
                apps = {
                    'notepad': 'notepad.exe',
                    'calculator': 'calc.exe',
                    'paint': 'mspaint.exe',
                    'chrome': 'chrome.exe',
                    'firefox': 'firefox.exe',
                    'edge': 'msedge.exe',
                    'explorer': 'explorer.exe',
                    'cmd': 'cmd.exe',
                    'powershell': 'powershell.exe',
                    'task manager': 'taskmgr.exe',
                    'control panel': 'control.exe',
                    'settings': 'ms-settings:',
                    'recycle bin': 'explorer.exe shell:RecycleBinFolder'
                }
                
                app_lower = app_name.lower()
                if app_lower in apps:
                    if app_lower == 'recycle bin':
                        os.system('explorer.exe shell:RecycleBinFolder')
                    elif app_lower == 'settings':
                        os.system('start ms-settings:')
                    else:
                        os.startfile(apps[app_lower])
                    return {'success': True, 'message': f'Opened {app_name}'}
                else:
                    # Try generic start
                    try:
                        os.system(f'start "" "{app_name}"')
                        return {'success': True, 'message': f'Attempted to open {app_name}'}
                    except:
                        return {'success': False, 'message': f'Could not open {app_name}'}
                
        except Exception as e:
            return {'success': False, 'message': f'Failed to open {app_name}: {str(e)}'}
    
    def close_application(self, app_name: str) -> Dict[str, Any]:
        """Close an application"""
        try:
            # Use taskkill for Windows
            if self.system == "Windows":
                # Common process names
                processes = {
                    'chrome': 'chrome.exe',
                    'firefox': 'firefox.exe',
                    'edge': 'msedge.exe',
                    'notepad': 'notepad.exe',
                    'calculator': 'calc.exe',
                    'paint': 'mspaint.exe',
                    'explorer': 'explorer.exe',
                    'cmd': 'cmd.exe',
                    'powershell': 'powershell.exe'
                }
                
                app_lower = app_name.lower()
                process_name = processes.get(app_lower, f'{app_name}.exe')
                
                result = subprocess.run(['taskkill', '/f', '/im', process_name], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    return {'success': True, 'message': f'Closed {app_name}'}
                else:
                    return {'success': False, 'message': f'Could not close {app_name} - it may not be running'}
                
        except Exception as e:
            return {'success': False, 'message': f'Failed to close {app_name}: {str(e)}'}
    
    def system_power(self, action: str) -> Dict[str, Any]:
        """System power operations"""
        try:
            if self.system == "Windows":
                if action == 'shutdown':
                    os.system('shutdown /s /t 5')
                    return {'success': True, 'message': 'Shutting down in 5 seconds'}
                elif action == 'restart':
                    os.system('shutdown /r /t 5')
                    return {'success': True, 'message': 'Restarting in 5 seconds'}
                elif action == 'sleep':
                    os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
                    return {'success': True, 'message': 'Going to sleep'}
                elif action == 'hibernate':
                    os.system('shutdown /h')
                    return {'success': True, 'message': 'Hibernating'}
            
            return {'success': False, 'message': f'Power action {action} not supported'}
            
        except Exception as e:
            return {'success': False, 'message': f'Power operation error: {str(e)}'}
    
    def window_management(self, action: str) -> Dict[str, Any]:
        """Window management operations"""
        try:
            if action == 'minimize_all':
                pyautogui.hotkey('win', 'd')
                return {'success': True, 'message': 'Minimized all windows'}
            elif action == 'maximize_current':
                pyautogui.hotkey('win', 'up')
                return {'success': True, 'message': 'Maximized current window'}
            elif action == 'restore_all':
                pyautogui.hotkey('win', 'd')
                time.sleep(0.5)
                pyautogui.hotkey('win', 'd')
                return {'success': True, 'message': 'Restored all windows'}
            
            return {'success': False, 'message': f'Window action {action} not supported'}
            
        except Exception as e:
            return {'success': False, 'message': f'Window management error: {str(e)}'}
    
    def open_website(self, url: str) -> Dict[str, Any]:
        """Open a website"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            return {'success': True, 'message': f'Opened {url}'}
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to open website: {str(e)}'}
    
    def search_web(self, query: str, engine: str = 'google') -> Dict[str, Any]:
        """Search the web"""
        try:
            search_urls = {
                'google': f'https://www.google.com/search?q={query}',
                'youtube': f'https://www.youtube.com/results?search_query={query}',
                'bing': f'https://www.bing.com/search?q={query}',
                'duckduckgo': f'https://duckduckgo.com/?q={query}'
            }
            
            url = search_urls.get(engine.lower(), search_urls['google'])
            webbrowser.open(url)
            
            return {'success': True, 'message': f'Searching for {query} on {engine}'}
            
        except Exception as e:
            return {'success': False, 'message': f'Web search error: {str(e)}'}
    
    def play_youtube(self, query: str) -> Dict[str, Any]:
        """Play video on YouTube"""
        try:
            import pywhatkit as kit
            kit.playonyt(query)
            return {'success': True, 'message': f'Playing {query} on YouTube'}
            
        except Exception as e:
            return {'success': False, 'message': f'YouTube play error: {str(e)}'}
    
    def file_operations(self, action: str, path: str = None) -> Dict[str, Any]:
        """File and folder operations"""
        try:
            if action == 'open_recycle_bin':
                os.system('explorer.exe shell:RecycleBinFolder')
                return {'success': True, 'message': 'Opened Recycle Bin'}
            
            elif action == 'empty_recycle_bin':
                # Ask for confirmation
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()  # Hide the main window
                
                confirm = messagebox.askyesno("Confirm", "Are you sure you want to empty the Recycle Bin?")
                root.destroy()
                
                if confirm:
                    os.system('rd /s /q %systemdrive%\\$Recycle.bin')
                    return {'success': True, 'message': 'Recycle Bin emptied'}
                else:
                    return {'success': False, 'message': 'Operation cancelled'}
            
            elif action == 'delete_file' and path:
                if os.path.exists(path):
                    # Move to recycle bin instead of permanent delete
                    import send2trash
                    send2trash.send2trash(path)
                    return {'success': True, 'message': f'Moved {path} to Recycle Bin'}
                else:
                    return {'success': False, 'message': f'File not found: {path}'}
            
            return {'success': False, 'message': f'File operation {action} not supported'}
            
        except Exception as e:
            return {'success': False, 'message': f'File operation error: {str(e)}'}
    
    def screenshot(self, save_path: str = None) -> Dict[str, Any]:
        """Take a screenshot"""
        try:
            if not save_path:
                save_path = f"screenshot_{int(time.time())}.png"
            
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            
            return {'success': True, 'message': f'Screenshot saved as {save_path}'}
            
        except Exception as e:
            return {'success': False, 'message': f'Screenshot error: {str(e)}'}

# Test the system controller
if __name__ == "__main__":
    controller = SystemController()
    
    # Test volume control
    print("Testing volume control...")
    result = controller.control_volume('up')
    print(f"Volume up: {result}")
    
    # Test app opening
    print("Testing app opening...")
    result = controller.open_application('notepad')
    print(f"Open notepad: {result}")
    
    time.sleep(2)
    
    # Test app closing
    print("Testing app closing...")
    result = controller.close_application('notepad')
    print(f"Close notepad: {result}")