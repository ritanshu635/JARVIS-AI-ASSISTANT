#!/usr/bin/env python3
"""
JARVIS Email Integration
Integrates the intelligent email composer with the main JARVIS system
"""

import asyncio
from intelligent_email_composer import IntelligentEmailComposer
from engine.command import speak

class JarvisEmailIntegration:
    """Integration class for email functionality in JARVIS"""
    
    def __init__(self):
        self.email_composer = IntelligentEmailComposer()
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the email system"""
        if not self.is_initialized:
            print("📧 Initializing JARVIS Email System...")
            speak("Initializing email system")
            self.is_initialized = True
    
    async def handle_email_command(self, command):
        """Handle email-related voice commands"""
        try:
            command_lower = command.lower()
            
            # Check for email composition triggers
            email_triggers = [
                'write email', 'write an email', 'compose email', 'send email',
                'write a email', 'email', 'write mail', 'send mail'
            ]
            
            if any(trigger in command_lower for trigger in email_triggers):
                await self.initialize()
                
                # Check if microphone calibration is needed
                if not hasattr(self.email_composer, 'calibrated'):
                    self.email_composer.calibrate_microphone()
                    self.email_composer.calibrated = True
                
                # Start email composition
                speak("I will write an email for you sir. Let me ask you some questions.")
                await self.email_composer.compose_email_interactive()
                
                return {
                    'success': True,
                    'message': 'Email composition completed',
                    'action': 'email_composed'
                }
            
            # Check for email setup commands
            elif 'setup email' in command_lower or 'configure email' in command_lower:
                await self.initialize()
                self.email_composer.setup_email_credentials()
                
                return {
                    'success': True,
                    'message': 'Email credentials configured',
                    'action': 'email_setup'
                }
            
            else:
                return {
                    'success': False,
                    'message': 'Email command not recognized',
                    'action': None
                }
                
        except Exception as e:
            error_msg = f"Error handling email command: {str(e)}"
            print(f"❌ {error_msg}")
            speak("Sorry, I encountered an error with the email system.")
            
            return {
                'success': False,
                'message': error_msg,
                'action': None
            }
    
    def is_email_command(self, command):
        """Check if a command is email-related"""
        command_lower = command.lower()
        
        email_keywords = [
            'email', 'mail', 'write email', 'send email', 'compose email',
            'write mail', 'send mail', 'write a email', 'write an email'
        ]
        
        return any(keyword in command_lower for keyword in email_keywords)

# Global instance for easy access
jarvis_email = JarvisEmailIntegration()

async def handle_jarvis_email_command(command):
    """Main function to handle email commands from JARVIS"""
    return await jarvis_email.handle_email_command(command)

def is_jarvis_email_command(command):
    """Check if command is email-related"""
    return jarvis_email.is_email_command(command)

# Test function
async def test_email_integration():
    """Test the email integration"""
    print("🧪 Testing JARVIS Email Integration")
    print("=" * 40)
    
    test_commands = [
        "JARVIS write an email for me",
        "write email",
        "compose email",
        "send mail",
        "setup email credentials"
    ]
    
    for cmd in test_commands:
        print(f"\n🧪 Testing command: '{cmd}'")
        
        if is_jarvis_email_command(cmd):
            print("✅ Command recognized as email command")
            result = await handle_jarvis_email_command(cmd)
            print(f"📝 Result: {result}")
        else:
            print("❌ Command not recognized as email command")

if __name__ == "__main__":
    try:
        asyncio.run(test_email_integration())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
    except Exception as e:
        print(f"❌ Test error: {e}")