import os
import re
import asyncio
from typing import Dict, List, Optional, Any, Callable
from .ai_router import AIRouter
from .database_manager import DatabaseManager

class CommandProcessor:
    """Processes user commands and routes them to appropriate handlers"""
    
    def __init__(self, ai_router: AIRouter, db_manager: DatabaseManager):
        self.ai_router = ai_router
        self.db_manager = db_manager
        self.handlers = {}
        self._register_handlers()
        
        # Command patterns for quick classification
        self.patterns = {
            'open_app': [
                r'(?:open|launch|start)\s+(.+)',
                r'(?:run|execute)\s+(.+)',
            ],
            'close_app': [
                r'(?:close|quit|exit|stop)\s+(.+)',
                r'(?:kill|terminate)\s+(.+)',
            ],
            'play_media': [
                r'play\s+(.+?)\s+(?:on|in)\s+(youtube|spotify)',
                r'(?:play|stream)\s+(.+)',
            ],
            'phone_call': [
                r'(?:call|phone|dial)\s+(.+)',
                r'make\s+(?:a\s+)?(?:phone\s+)?call\s+(?:to\s+)?(.+)',
            ],
            'send_message': [
                r'(?:send|text)\s+(?:a\s+)?(?:message|sms)\s+(?:to\s+)?(.+)',
                r'message\s+(.+)',
            ],
            'whatsapp': [
                r'whatsapp\s+(.+)',
                r'(?:send|make)\s+(?:a\s+)?(?:whatsapp|wa)\s+(?:message|call|video\s+call)\s+(?:to\s+)?(.+)',
            ],
            'system_command': [
                r'(?:mute|unmute)',
                r'volume\s+(?:up|down)',
                r'(?:shutdown|restart|sleep|hibernate)',
                r'(?:minimize|maximize)\s+(?:all|windows?)',
                r'brightness\s+(?:up|down)',
            ],
            'web_search': [
                r'(?:search|google|find)\s+(?:for\s+)?(.+?)\s+(?:on|in)\s+(google|youtube|bing)',
                r'(?:look\s+up|search\s+for)\s+(.+)',
            ],
            'file_operations': [
                r'(?:open|show)\s+recycle\s+bin',
                r'empty\s+recycle\s+bin',
                r'delete\s+(.+)',
            ],
            'content_generation': [
                r'(?:write|create|generate)\s+(?:a\s+)?(?:letter|email|essay|article|code|summary)\s+(?:about\s+)?(.+)',
                r'(?:compose|draft)\s+(.+)',
            ],
            'weather': [
                r'(?:weather|temperature)\s+(?:in\s+)?(.+)?',
                r'(?:what\'s|how\'s)\s+the\s+weather',
            ],
            'time_date': [
                r'(?:what\s+time|current\s+time|time)',
                r'(?:what\s+date|current\s+date|date|today)',
            ],
            'greeting': [
                r'(?:hello|hi|hey)\s+(?:jarvis|assistant)?',
                r'(?:good\s+morning|good\s+afternoon|good\s+evening)',
            ]
        }
    
    def _register_handlers(self):
        """Register command handlers"""
        self.handlers = {
            'open_app': self._handle_open_app,
            'close_app': self._handle_close_app,
            'play_media': self._handle_play_media,
            'phone_call': self._handle_phone_call,
            'send_message': self._handle_send_message,
            'whatsapp': self._handle_whatsapp,
            'system_command': self._handle_system_command,
            'web_search': self._handle_web_search,
            'file_operations': self._handle_file_operations,
            'content_generation': self._handle_content_generation,
            'weather': self._handle_weather,
            'time_date': self._handle_time_date,
            'greeting': self._handle_greeting,
            'general': self._handle_general
        }
    
    async def process_command(self, command: str) -> Dict[str, Any]:
        """Main command processing function"""
        try:
            # Clean and normalize the command
            command = command.strip().lower()
            
            if not command:
                return {
                    'response': "I didn't hear anything. Please try again.",
                    'success': False,
                    'intent': 'empty'
                }
            
            # First try pattern matching for quick classification
            intent, extracted_data = self._classify_with_patterns(command)
            
            # If pattern matching fails, use AI classification
            if intent == 'unknown':
                ai_result = await self.ai_router.classify_intent(command)
                if ai_result['success']:
                    intent = self._parse_ai_classification(ai_result['intent'])
                    extracted_data = {'query': command}
                else:
                    intent = 'general'
                    extracted_data = {'query': command}
            
            # Execute the appropriate handler
            handler = self.handlers.get(intent, self.handlers['general'])
            result = await handler(command, extracted_data)
            
            # Save to chat history
            self.db_manager.save_chat_message(
                user_input=command,
                response=result.get('response', ''),
                intent=intent,
                processing_time=result.get('processing_time'),
                ai_model=result.get('ai_model')
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error processing your command: {str(e)}"
            print(f"❌ Command processing error: {e}")
            return {
                'response': error_msg,
                'success': False,
                'intent': 'error',
                'error': str(e)
            }
    
    def _classify_with_patterns(self, command: str) -> tuple[str, Dict[str, Any]]:
        """Classify command using regex patterns"""
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    extracted_data = {
                        'query': command,
                        'match': match.group(0),
                        'groups': groups
                    }
                    
                    # Extract specific data based on intent
                    if intent in ['open_app', 'close_app'] and groups:
                        extracted_data['app_name'] = groups[0].strip()
                    elif intent == 'play_media' and groups:
                        extracted_data['media_name'] = groups[0].strip()
                        if len(groups) > 1:
                            extracted_data['platform'] = groups[1].strip()
                    elif intent in ['phone_call', 'send_message', 'whatsapp'] and groups:
                        extracted_data['contact_name'] = groups[0].strip()
                    elif intent == 'web_search' and groups:
                        extracted_data['search_query'] = groups[0].strip()
                        if len(groups) > 1:
                            extracted_data['search_engine'] = groups[1].strip()
                    elif intent == 'content_generation' and groups:
                        extracted_data['content_topic'] = groups[0].strip()
                    
                    return intent, extracted_data
        
        return 'unknown', {'query': command}
    
    def _parse_ai_classification(self, ai_classification: str) -> str:
        """Parse AI classification result into intent"""
        ai_classification = ai_classification.lower().strip()
        
        # Map AI classifications to our intents
        if 'open' in ai_classification:
            return 'open_app'
        elif 'close' in ai_classification:
            return 'close_app'
        elif 'play' in ai_classification:
            return 'play_media'
        elif 'call' in ai_classification:
            return 'phone_call'
        elif 'message' in ai_classification or 'sms' in ai_classification:
            return 'send_message'
        elif 'whatsapp' in ai_classification:
            return 'whatsapp'
        elif 'system' in ai_classification:
            return 'system_command'
        elif 'search' in ai_classification:
            return 'web_search'
        elif 'content' in ai_classification or 'write' in ai_classification:
            return 'content_generation'
        elif 'weather' in ai_classification:
            return 'weather'
        elif 'time' in ai_classification or 'date' in ai_classification:
            return 'time_date'
        elif 'hello' in ai_classification or 'greeting' in ai_classification:
            return 'greeting'
        else:
            return 'general'
    
    # Handler Methods
    async def _handle_open_app(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle opening applications"""
        app_name = data.get('app_name', '').strip()
        
        if not app_name:
            return {
                'response': "Which application would you like me to open?",
                'success': False,
                'intent': 'open_app',
                'action': 'clarification_needed'
            }
        
        # Check system commands first
        app_path = self.db_manager.get_system_command(app_name)
        if app_path:
            return {
                'response': f"Opening {app_name}",
                'success': True,
                'intent': 'open_app',
                'action': 'open_system_app',
                'app_name': app_name,
                'app_path': app_path
            }
        
        # Check web commands
        url = self.db_manager.get_web_command(app_name)
        if url:
            return {
                'response': f"Opening {app_name}",
                'success': True,
                'intent': 'open_app',
                'action': 'open_website',
                'app_name': app_name,
                'url': url
            }
        
        # Try generic system open
        return {
            'response': f"Attempting to open {app_name}",
            'success': True,
            'intent': 'open_app',
            'action': 'open_generic',
            'app_name': app_name
        }
    
    async def _handle_close_app(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle closing applications"""
        app_name = data.get('app_name', '').strip()
        
        return {
            'response': f"Closing {app_name}" if app_name else "Closing application",
            'success': True,
            'intent': 'close_app',
            'action': 'close_app',
            'app_name': app_name
        }
    
    async def _handle_play_media(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle media playback"""
        media_name = data.get('media_name', '').strip()
        platform = data.get('platform', 'youtube').strip()
        
        return {
            'response': f"Playing {media_name} on {platform}",
            'success': True,
            'intent': 'play_media',
            'action': 'play_media',
            'media_name': media_name,
            'platform': platform
        }
    
    async def _handle_phone_call(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle phone calls"""
        contact_name = data.get('contact_name', '').strip()
        
        if not contact_name:
            return {
                'response': "Who would you like me to call?",
                'success': False,
                'intent': 'phone_call',
                'action': 'clarification_needed'
            }
        
        # Look up contact
        contact = self.db_manager.get_contact(contact_name)
        if contact:
            return {
                'response': f"Calling {contact['name']}",
                'success': True,
                'intent': 'phone_call',
                'action': 'make_call',
                'contact': contact
            }
        else:
            return {
                'response': f"I couldn't find {contact_name} in your contacts. Please add them first.",
                'success': False,
                'intent': 'phone_call',
                'action': 'contact_not_found',
                'contact_name': contact_name
            }
    
    async def _handle_send_message(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sending messages"""
        contact_name = data.get('contact_name', '').strip()
        
        if not contact_name:
            return {
                'response': "Who would you like to send a message to?",
                'success': False,
                'intent': 'send_message',
                'action': 'clarification_needed'
            }
        
        contact = self.db_manager.get_contact(contact_name)
        if contact:
            return {
                'response': f"What message would you like to send to {contact['name']}?",
                'success': True,
                'intent': 'send_message',
                'action': 'get_message_content',
                'contact': contact
            }
        else:
            return {
                'response': f"I couldn't find {contact_name} in your contacts.",
                'success': False,
                'intent': 'send_message',
                'action': 'contact_not_found',
                'contact_name': contact_name
            }
    
    async def _handle_whatsapp(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WhatsApp actions"""
        # Extract contact name and message from command
        contact_name = ""
        message = ""
        
        # Parse different WhatsApp command formats
        if "send message to" in command or "message" in command:
            # Format: "send message to Tom on WhatsApp as hello"
            if " to " in command and " as " in command:
                parts = command.split(" to ")[1].split(" as ")
                contact_name = parts[0].replace("on whatsapp", "").strip()
                message = parts[1].strip() if len(parts) > 1 else ""
            elif " to " in command:
                # Format: "send message to Tom"
                contact_name = command.split(" to ")[1].replace("on whatsapp", "").strip()
        elif "whatsapp" in command:
            # Format: "whatsapp Tom hello"
            words = command.replace("whatsapp", "").strip().split()
            if words:
                contact_name = words[0]
                message = " ".join(words[1:]) if len(words) > 1 else ""
        
        # Determine WhatsApp action type
        action_type = 'message'  # default
        if 'call' in command and 'video' not in command:
            action_type = 'call'
            message = ""
        elif 'video call' in command:
            action_type = 'video_call'
            message = ""
        
        if not contact_name:
            return {
                'response': f"Who would you like to WhatsApp {action_type.replace('_', ' ')}?",
                'success': False,
                'intent': 'whatsapp',
                'action': 'clarification_needed'
            }
        
        contact = self.db_manager.get_contact(contact_name)
        if contact:
            return {
                'response': f"Sending WhatsApp {action_type.replace('_', ' ')} to {contact['name']}" + (f": {message}" if message else ""),
                'success': True,
                'intent': 'whatsapp',
                'action': f'whatsapp_{action_type}',
                'contact': contact,
                'message': message
            }
        else:
            return {
                'response': f"I couldn't find {contact_name} in your contacts.",
                'success': False,
                'intent': 'whatsapp',
                'action': 'contact_not_found',
                'contact_name': contact_name
            }
    
    async def _handle_system_command(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system commands"""
        if 'mute' in command and 'unmute' not in command:
            action = 'mute'
        elif 'unmute' in command:
            action = 'unmute'
        elif 'volume up' in command:
            action = 'volume_up'
        elif 'volume down' in command:
            action = 'volume_down'
        elif 'brightness up' in command:
            action = 'brightness_up'
        elif 'brightness down' in command:
            action = 'brightness_down'
        elif 'shutdown' in command:
            action = 'shutdown'
        elif 'restart' in command:
            action = 'restart'
        elif 'sleep' in command:
            action = 'sleep'
        elif 'hibernate' in command:
            action = 'hibernate'
        elif 'minimize' in command:
            action = 'minimize_all'
        elif 'maximize' in command:
            action = 'maximize_all'
        else:
            action = 'unknown_system_command'
        
        return {
            'response': f"Executing {action.replace('_', ' ')} command",
            'success': True,
            'intent': 'system_command',
            'action': action
        }
    
    async def _handle_file_operations(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operations"""
        if 'open recycle bin' in command or 'show recycle bin' in command:
            action = 'open_recycle_bin'
            response = "Opening Recycle Bin"
        elif 'empty recycle bin' in command:
            action = 'empty_recycle_bin'
            response = "Emptying Recycle Bin"
        elif 'delete' in command:
            action = 'delete_file'
            response = "Deleting file"
        else:
            action = 'unknown_file_operation'
            response = "Unknown file operation"
        
        return {
            'response': response,
            'success': True,
            'intent': 'file_operations',
            'action': action
        }
    
    async def _handle_web_search(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web searches"""
        search_query = data.get('search_query', '').strip()
        search_engine = data.get('search_engine', 'google').strip()
        
        if not search_query:
            return {
                'response': "What would you like me to search for?",
                'success': False,
                'intent': 'web_search',
                'action': 'clarification_needed'
            }
        
        return {
            'response': f"Searching for {search_query} on {search_engine}",
            'success': True,
            'intent': 'web_search',
            'action': 'web_search',
            'search_query': search_query,
            'search_engine': search_engine
        }
    
    async def _handle_content_generation(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle content generation requests"""
        topic = data.get('content_topic', '').strip()
        
        # Determine content type
        content_type = 'general'
        if 'letter' in command:
            content_type = 'letter'
        elif 'email' in command:
            content_type = 'email'
        elif 'essay' in command:
            content_type = 'essay'
        elif 'code' in command:
            content_type = 'code'
        elif 'article' in command:
            content_type = 'article'
        elif 'summary' in command:
            content_type = 'summary'
        
        if not topic:
            return {
                'response': f"What would you like me to write the {content_type} about?",
                'success': False,
                'intent': 'content_generation',
                'action': 'clarification_needed'
            }
        
        # Generate content using AI
        try:
            result = await self.ai_router.generate_content(content_type, topic)
            if result['success']:
                return {
                    'response': result['response'],
                    'success': True,
                    'intent': 'content_generation',
                    'action': 'content_generated',
                    'content_type': content_type,
                    'topic': topic,
                    'ai_model': result.get('ai_model')
                }
            else:
                return {
                    'response': f"I'm sorry, I couldn't generate the {content_type} right now. Please try again later.",
                    'success': False,
                    'intent': 'content_generation',
                    'action': 'generation_failed'
                }
        except Exception as e:
            return {
                'response': f"An error occurred while generating content: {str(e)}",
                'success': False,
                'intent': 'content_generation',
                'action': 'generation_error'
            }
    
    async def _handle_weather(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle weather queries"""
        location = data.get('groups', [''])[0] if data.get('groups') else ''
        
        # Use AI to get weather information
        weather_query = f"What's the current weather in {location}" if location else "What's the current weather"
        result = await self.ai_router.process_query(weather_query, "realtime")
        
        return {
            'response': result['response'],
            'success': result['success'],
            'intent': 'weather',
            'action': 'weather_info',
            'location': location,
            'ai_model': result.get('ai_model')
        }
    
    async def _handle_time_date(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle time and date queries"""
        from datetime import datetime
        
        now = datetime.now()
        
        if 'time' in command:
            response = f"The current time is {now.strftime('%I:%M %p')}"
        elif 'date' in command:
            response = f"Today is {now.strftime('%A, %B %d, %Y')}"
        else:
            response = f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}"
        
        return {
            'response': response,
            'success': True,
            'intent': 'time_date',
            'action': 'time_date_info'
        }
    
    async def _handle_greeting(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greetings"""
        from datetime import datetime
        
        hour = datetime.now().hour
        nickname = os.getenv('NickName', 'there')
        
        if hour < 12:
            greeting = f"Good morning, {nickname}!"
        elif hour < 17:
            greeting = f"Good afternoon, {nickname}!"
        else:
            greeting = f"Good evening, {nickname}!"
        
        responses = [
            f"{greeting} How can I assist you today?",
            f"Hello {nickname}! What can I help you with?",
            f"{greeting} I'm here and ready to help.",
            f"Hi {nickname}! What would you like me to do?"
        ]
        
        import random
        response = random.choice(responses)
        
        return {
            'response': response,
            'success': True,
            'intent': 'greeting',
            'action': 'greeting_response'
        }
    
    async def _handle_general(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general queries using AI"""
        result = await self.ai_router.process_query(command, "general")
        
        return {
            'response': result['response'],
            'success': result['success'],
            'intent': 'general',
            'action': 'ai_response',
            'ai_model': result.get('ai_model'),
            'processing_time': result.get('processing_time')
        }

# Test the Command Processor
if __name__ == "__main__":
    import asyncio
    from .database_manager import DatabaseManager
    
    async def test_command_processor():
        # Initialize components
        ai_router = AIRouter()
        db_manager = DatabaseManager()
        processor = CommandProcessor(ai_router, db_manager)
        
        # Test commands
        test_commands = [
            "open chrome",
            "call john",
            "play music on youtube",
            "what's the weather",
            "hello jarvis",
            "write a letter about job application"
        ]
        
        for command in test_commands:
            print(f"\n🎤 Command: {command}")
            result = await processor.process_command(command)
            print(f"📝 Response: {result['response']}")
            print(f"🎯 Intent: {result['intent']}")
            print(f"✅ Success: {result['success']}")
    
    asyncio.run(test_command_processor())