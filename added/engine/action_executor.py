import asyncio
import os
import webbrowser
from typing import Dict, Any
from .android_controller import AndroidController
from .system_controller import SystemController
from .database_manager import DatabaseManager
from .command import speak

class ActionExecutor:
    """Executes all JARVIS actions - calls, messages, system control, etc."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.android_controller = AndroidController(self.db_manager)
        self.system_controller = SystemController()
    
    async def execute_action(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action based on command processing result"""
        
        action = result.get('action')
        intent = result.get('intent')
        
        try:
            # Phone and messaging actions
            if action == 'make_call':
                return await self._execute_phone_call(result)
            
            elif action == 'get_message_content':
                return await self._execute_sms_message(result)
            
            elif action.startswith('whatsapp_'):
                return await self._execute_whatsapp_action(result)
            
            # System control actions
            elif action == 'open_system_app':
                return self._execute_open_app(result)
            
            elif action == 'open_website':
                return self._execute_open_website(result)
            
            elif action == 'open_generic':
                return self._execute_open_generic(result)
            
            elif action == 'close_app':
                return self._execute_close_app(result)
            
            elif action in ['mute', 'unmute', 'volume_up', 'volume_down']:
                return self._execute_volume_control(action)
            
            elif action in ['brightness_up', 'brightness_down']:
                return self._execute_brightness_control(action)
            
            elif action in ['shutdown', 'restart', 'sleep', 'hibernate']:
                return self._execute_power_action(action)
            
            elif action in ['minimize_all', 'maximize_all']:
                return self._execute_window_action(action)
            
            elif action == 'play_media':
                return self._execute_play_media(result)
            
            elif action == 'web_search':
                return self._execute_web_search(result)
            
            # File operations
            elif action == 'open_recycle_bin':
                return self._execute_file_operation('open_recycle_bin')
            
            elif action == 'empty_recycle_bin':
                return self._execute_file_operation('empty_recycle_bin')
            
            # Default response for unhandled actions
            else:
                response = result.get('response', 'Action completed')
                speak(response)
                return {'success': True, 'message': response, 'executed': False}
        
        except Exception as e:
            error_msg = f"Error executing action: {str(e)}"
            speak("Sorry, I encountered an error executing that action")
            return {'success': False, 'message': error_msg}
    
    async def _execute_phone_call(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute phone call"""
        contact = result.get('contact')
        if not contact:
            speak("Contact information not found")
            return {'success': False, 'message': 'No contact information'}
        
        speak(f"Calling {contact['name']}")
        call_result = self.android_controller.make_call(
            contact['mobile_no'], 
            contact['name']
        )
        
        speak(call_result['message'])
        return call_result
    
    async def _execute_sms_message(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SMS message sending"""
        contact = result.get('contact')
        if not contact:
            speak("Contact information not found")
            return {'success': False, 'message': 'No contact information'}
        
        # For now, use a default message. In a full implementation, 
        # you'd get the message from voice input or GUI
        message = "Hello from JARVIS!"
        
        speak(f"Sending message to {contact['name']}")
        sms_result = self.android_controller.send_sms(
            contact['mobile_no'],
            message,
            contact['name']
        )
        
        speak(sms_result['message'])
        return sms_result
    
    async def _execute_whatsapp_action(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute WhatsApp action"""
        contact = result.get('contact')
        message = result.get('message', '')
        action_type = result.get('action', '').replace('whatsapp_', '')
        
        if not contact:
            speak("Contact information not found")
            return {'success': False, 'message': 'No contact information'}
        
        speak(f"Opening WhatsApp for {contact['name']}")
        whatsapp_result = self.android_controller.whatsapp_automation(
            contact['name'],
            message,
            action_type
        )
        
        speak(whatsapp_result['message'])
        return whatsapp_result
    
    def _execute_open_app(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute opening system application"""
        app_name = result.get('app_name')
        app_path = result.get('app_path')
        
        if not app_path:
            speak(f"Could not find {app_name}")
            return {'success': False, 'message': f'App path not found for {app_name}'}
        
        try:
            os.startfile(app_path)
            speak(f"Opening {app_name}")
            return {'success': True, 'message': f'Opened {app_name}'}
        except Exception as e:
            speak(f"Failed to open {app_name}")
            return {'success': False, 'message': str(e)}
    
    def _execute_open_website(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute opening website"""
        app_name = result.get('app_name')
        url = result.get('url')
        
        if not url:
            speak(f"Could not find URL for {app_name}")
            return {'success': False, 'message': f'URL not found for {app_name}'}
        
        try:
            webbrowser.open(url)
            speak(f"Opening {app_name}")
            return {'success': True, 'message': f'Opened {app_name}'}
        except Exception as e:
            speak(f"Failed to open {app_name}")
            return {'success': False, 'message': str(e)}
    
    def _execute_open_generic(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generic application opening"""
        app_name = result.get('app_name')
        
        system_result = self.system_controller.open_application(app_name)
        speak(system_result['message'])
        return system_result
    
    def _execute_close_app(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute closing application"""
        app_name = result.get('app_name')
        
        if not app_name:
            speak("Please specify which application to close")
            return {'success': False, 'message': 'No app name specified'}
        
        system_result = self.system_controller.close_application(app_name)
        speak(system_result['message'])
        return system_result
    
    def _execute_volume_control(self, action: str) -> Dict[str, Any]:
        """Execute volume control"""
        volume_action = action.replace('volume_', '').replace('_', ' ')
        
        system_result = self.system_controller.control_volume(volume_action)
        speak(system_result['message'])
        return system_result
    
    def _execute_brightness_control(self, action: str) -> Dict[str, Any]:
        """Execute brightness control"""
        brightness_action = action.replace('brightness_', '')
        
        system_result = self.system_controller.control_brightness(brightness_action)
        speak(system_result['message'])
        return system_result
    
    def _execute_power_action(self, action: str) -> Dict[str, Any]:
        """Execute power action"""
        system_result = self.system_controller.system_power(action)
        speak(system_result['message'])
        return system_result
    
    def _execute_window_action(self, action: str) -> Dict[str, Any]:
        """Execute window management action"""
        window_action = action.replace('_all', '_all').replace('_', ' ')
        
        system_result = self.system_controller.window_management(action)
        speak(system_result['message'])
        return system_result
    
    def _execute_play_media(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute media playback"""
        media_name = result.get('media_name')
        platform = result.get('platform', 'youtube')
        
        if not media_name:
            speak("Please specify what to play")
            return {'success': False, 'message': 'No media name specified'}
        
        if platform.lower() == 'youtube':
            system_result = self.system_controller.play_youtube(media_name)
            speak(f"Playing {media_name} on YouTube")
            return system_result
        else:
            speak(f"Platform {platform} not supported yet")
            return {'success': False, 'message': f'Platform {platform} not supported'}
    
    def _execute_web_search(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web search"""
        search_query = result.get('search_query')
        search_engine = result.get('search_engine', 'google')
        
        if not search_query:
            speak("Please specify what to search for")
            return {'success': False, 'message': 'No search query specified'}
        
        system_result = self.system_controller.search_web(search_query, search_engine)
        speak(system_result['message'])
        return system_result
    
    def _execute_file_operation(self, operation: str) -> Dict[str, Any]:
        """Execute file operation"""
        system_result = self.system_controller.file_operations(operation)
        speak(system_result['message'])
        return system_result

# Test the action executor
if __name__ == "__main__":
    import asyncio
    
    async def test_action_executor():
        executor = ActionExecutor()
        
        # Test opening an app
        result = {
            'action': 'open_generic',
            'app_name': 'notepad'
        }
        
        action_result = await executor.execute_action(result)
        print(f"Action result: {action_result}")
    
    asyncio.run(test_action_executor())