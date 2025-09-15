#!/usr/bin/env python3
"""
Demo Script for JARVIS Email Composer
Shows how the email composition works with sample data
"""

import asyncio
from standalone_email_composer import StandaloneEmailComposer

async def demo_email_generation():
    """Demo the email generation without voice input"""
    print("🎬 JARVIS Email Composer Demo")
    print("=" * 40)
    
    # Initialize composer
    composer = StandaloneEmailComposer()
    
    # Demo data for different email types
    demo_scenarios = [
        {
            'name': 'Leave Application',
            'recipient': 'manager@company.com',
            'subject': 'Sick Leave Application',
            'type': 'leave',
            'info': {
                'question_1': {'question': 'Who to address?', 'answer': 'Manager'},
                'question_2': {'question': 'Type of leave?', 'answer': 'Sick leave'},
                'question_3': {'question': 'From date?', 'answer': 'Tomorrow'},
                'question_4': {'question': 'Until date?', 'answer': 'Day after tomorrow'},
                'question_5': {'question': 'Reason?', 'answer': 'I have fever and need rest'}
            }
        },
        {
            'name': 'Job Application',
            'recipient': 'hr@techcompany.com',
            'subject': 'Application for Software Developer Position',
            'type': 'job',
            'info': {
                'question_1': {'question': 'Position?', 'answer': 'Software Developer'},
                'question_2': {'question': 'Company?', 'answer': 'Tech Company'},
                'question_3': {'question': 'Experience?', 'answer': '3 years in Python and JavaScript'},
                'question_4': {'question': 'Key skills?', 'answer': 'Python, React, Node.js, databases'},
                'question_5': {'question': 'Availability?', 'answer': 'Can start immediately'}
            }
        },
        {
            'name': 'Meeting Request',
            'recipient': 'team@company.com',
            'subject': 'Team Meeting for Project Discussion',
            'type': 'meeting',
            'info': {
                'question_1': {'question': 'Purpose?', 'answer': 'Discuss quarterly project progress'},
                'question_2': {'question': 'When?', 'answer': 'Next Friday at 2 PM'},
                'question_3': {'question': 'Duration?', 'answer': '1 hour'},
                'question_4': {'question': 'Attendees?', 'answer': 'All team members and project leads'},
                'question_5': {'question': 'Format?', 'answer': 'Virtual meeting via Teams'}
            }
        }
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n📧 Demo {i}: {scenario['name']}")
        print("-" * 50)
        
        composer.speak(f"Generating {scenario['name']} email demo")
        
        try:
            # Generate email content
            content = await composer.generate_email_content_with_ollama(
                scenario['recipient'],
                scenario['subject'],
                scenario['type'],
                scenario['info']
            )
            
            # Preview the email
            composer.preview_email(scenario['recipient'], scenario['subject'], content)
            
            # Save as draft
            filename = composer.save_email_draft(scenario['recipient'], scenario['subject'], content)
            
            print(f"✅ {scenario['name']} demo completed!")
            
            # Ask if user wants to continue
            if i < len(demo_scenarios):
                input(f"\nPress Enter to continue to demo {i+1}...")
            
        except Exception as e:
            print(f"❌ Error in demo {i}: {e}")
    
    print("\n🎉 All demos completed!")
    composer.speak("All email demos completed sir. Check the generated draft files.")

def show_usage_instructions():
    """Show how to use the email composer"""
    print("\n📖 JARVIS Email Composer - Usage Instructions")
    print("=" * 55)
    
    print("\n🎤 Voice Mode Usage:")
    print("1. Run: python standalone_email_composer.py")
    print("2. Choose option 1 (Voice mode)")
    print("3. Say 'JARVIS' clearly when prompted")
    print("4. Follow the voice prompts:")
    print("   - Provide recipient email address")
    print("   - Provide email subject")
    print("   - Answer follow-up questions")
    print("   - Review generated email")
    print("   - Choose to send, save, or regenerate")
    
    print("\n📧 Email Types Supported:")
    print("- Leave Application (asks about dates, reason)")
    print("- Job Application (asks about position, skills)")
    print("- Meeting Request (asks about purpose, timing)")
    print("- Complaint (asks about issue, resolution)")
    print("- Inquiry (asks about information needed)")
    print("- Invitation (asks about event details)")
    print("- Thank You (asks what you're thanking for)")
    print("- Apology (asks what you're apologizing for)")
    
    print("\n🔧 Setup Requirements:")
    print("✅ speech-recognition (installed)")
    print("✅ pyttsx3 (installed)")
    print("✅ requests (installed)")
    print("✅ Ollama running (connected)")
    
    print("\n📧 Gmail Setup (for sending emails):")
    print("1. Enable 2-factor authentication on Gmail")
    print("2. Go to Google Account → Security → App passwords")
    print("3. Generate app password for 'Mail'")
    print("4. Use this app password in the script (not regular password)")
    
    print("\n🎯 Voice Commands:")
    print("- 'JARVIS' - Wake up the system")
    print("- Speak clearly and at normal pace")
    print("- Wait for prompts before speaking")
    print("- Say 'yes' to send, 'save' to save draft, 'no' to regenerate")

async def main():
    """Main demo function"""
    print("🎬 JARVIS Email Composer - Demo & Instructions")
    print("=" * 50)
    
    print("\n📋 What would you like to see?")
    print("1. Run email generation demos")
    print("2. Show usage instructions")
    print("3. Test voice recognition")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        await demo_email_generation()
    
    elif choice == '2':
        show_usage_instructions()
    
    elif choice == '3':
        print("\n🎤 Voice Recognition Test")
        print("=" * 25)
        
        composer = StandaloneEmailComposer()
        composer.speak("Voice recognition test sir. Please say something.")
        
        result = composer.listen_for_speech("Say something to test the microphone:", timeout=10)
        
        if result:
            print(f"✅ Voice recognition working! You said: {result}")
            composer.speak(f"I heard you say: {result}")
        else:
            print("❌ No speech detected or recognition failed")
            composer.speak("Voice recognition test completed sir.")
    
    elif choice == '4':
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted")
    except Exception as e:
        print(f"❌ Demo error: {e}")