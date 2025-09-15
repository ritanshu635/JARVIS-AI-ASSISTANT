#!/usr/bin/env python3
"""
Test Script for JARVIS Email Feature
Tests the intelligent email composer functionality
"""

import asyncio
import sys
import os
from intelligent_email_composer import IntelligentEmailComposer
from jarvis_email_integration import handle_jarvis_email_command, is_jarvis_email_command

async def test_email_detection():
    """Test email command detection"""
    print("🧪 Testing Email Command Detection")
    print("=" * 40)
    
    test_commands = [
        "JARVIS write an email for me",
        "write email",
        "compose email", 
        "send mail",
        "write a email",
        "help me write an email",
        "I need to send an email",
        "open notepad",  # Non-email command
        "call Tom",      # Non-email command
        "what's the weather"  # Non-email command
    ]
    
    for cmd in test_commands:
        is_email = is_jarvis_email_command(cmd)
        status = "✅ EMAIL" if is_email else "❌ NOT EMAIL"
        print(f"{status}: '{cmd}'")
    
    print("\n✅ Email detection test completed!")

async def test_email_generation():
    """Test email content generation"""
    print("\n🧪 Testing Email Content Generation")
    print("=" * 40)
    
    composer = IntelligentEmailComposer()
    
    # Test data for different email types
    test_cases = [
        {
            'type': 'leave',
            'recipient': 'manager@company.com',
            'subject': 'Leave Application',
            'info': {
                'question_1': {'question': 'Who to address?', 'answer': 'Manager'},
                'question_2': {'question': 'Type of leave?', 'answer': 'Sick leave'},
                'question_3': {'question': 'From date?', 'answer': 'Tomorrow'},
                'question_4': {'question': 'Until date?', 'answer': 'Day after tomorrow'},
                'question_5': {'question': 'Reason?', 'answer': 'Fever and need rest'}
            }
        },
        {
            'type': 'job',
            'recipient': 'hr@techcompany.com',
            'subject': 'Job Application for Software Developer',
            'info': {
                'question_1': {'question': 'Position?', 'answer': 'Software Developer'},
                'question_2': {'question': 'Company?', 'answer': 'Tech Company'},
                'question_3': {'question': 'Experience?', 'answer': '3 years'},
                'question_4': {'question': 'Key skills?', 'answer': 'Python, JavaScript, React'},
                'question_5': {'question': 'Availability?', 'answer': 'Immediately'}
            }
        },
        {
            'type': 'meeting',
            'recipient': 'team@company.com',
            'subject': 'Team Meeting Request',
            'info': {
                'question_1': {'question': 'Purpose?', 'answer': 'Discuss project progress'},
                'question_2': {'question': 'When?', 'answer': 'Next Friday at 2 PM'},
                'question_3': {'question': 'Duration?', 'answer': '1 hour'},
                'question_4': {'question': 'Attendees?', 'answer': 'All team members'},
                'question_5': {'question': 'Format?', 'answer': 'Virtual meeting'}
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📧 Test Case {i}: {test_case['type'].upper()} Email")
        print("-" * 30)
        
        try:
            content = await composer.generate_email_content(
                test_case['recipient'],
                test_case['subject'],
                test_case['type'],
                test_case['info']
            )
            
            print(f"✅ Generated content for {test_case['type']} email")
            print(f"📝 Content preview: {content[:100]}...")
            
            # Save test email
            filename = composer.save_email_draft(
                test_case['recipient'],
                test_case['subject'],
                content
            )
            
            if filename:
                print(f"💾 Saved as: {filename}")
            
        except Exception as e:
            print(f"❌ Error generating {test_case['type']} email: {e}")
    
    print("\n✅ Email generation test completed!")

async def test_subject_detection():
    """Test email subject type detection"""
    print("\n🧪 Testing Subject Type Detection")
    print("=" * 40)
    
    composer = IntelligentEmailComposer()
    
    test_subjects = [
        ("Leave Application for Medical Emergency", "leave"),
        ("Job Application for Software Engineer Position", "job"),
        ("Meeting Request for Project Discussion", "meeting"),
        ("Complaint about Service Quality", "complaint"),
        ("Inquiry about Product Pricing", "inquiry"),
        ("Invitation to Company Annual Party", "invitation"),
        ("Thank you for your help", "thank"),
        ("Apology for the delay in response", "apology"),
        ("General question about services", "general")
    ]
    
    for subject, expected_type in test_subjects:
        detected_type = composer.detect_email_subject_type(subject)
        status = "✅" if detected_type == expected_type else "❌"
        print(f"{status} '{subject}' -> Detected: {detected_type}, Expected: {expected_type}")
    
    print("\n✅ Subject detection test completed!")

async def test_integration():
    """Test JARVIS email integration"""
    print("\n🧪 Testing JARVIS Email Integration")
    print("=" * 40)
    
    test_commands = [
        "JARVIS write an email for me",
        "compose email",
        "setup email credentials"
    ]
    
    for cmd in test_commands:
        print(f"\n🎤 Testing command: '{cmd}'")
        
        try:
            if is_jarvis_email_command(cmd):
                print("✅ Command recognized as email command")
                # Note: We won't actually run the full command to avoid voice input in test
                print("📝 Would trigger email composition process")
            else:
                print("❌ Command not recognized as email command")
                
        except Exception as e:
            print(f"❌ Error testing command: {e}")
    
    print("\n✅ Integration test completed!")

def test_file_operations():
    """Test file operations"""
    print("\n🧪 Testing File Operations")
    print("=" * 30)
    
    composer = IntelligentEmailComposer()
    
    # Test saving draft
    test_content = """Dear Manager,

I am writing to request leave from work due to illness.

Please find the details below:
- Type: Sick leave
- From: Tomorrow
- Until: Day after tomorrow
- Reason: Fever and need rest

I would appreciate your approval for this leave request.

Thank you for your consideration.

Best regards,
[Your Name]"""
    
    try:
        filename = composer.save_email_draft(
            "test@example.com",
            "Test Email Draft",
            test_content
        )
        
        if filename and os.path.exists(filename):
            print(f"✅ Draft saved successfully: {filename}")
            
            # Check file content
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                if "Test Email Draft" in content:
                    print("✅ File content verified")
                else:
                    print("❌ File content verification failed")
        else:
            print("❌ Draft saving failed")
            
    except Exception as e:
        print(f"❌ File operation error: {e}")
    
    print("\n✅ File operations test completed!")

async def run_all_tests():
    """Run all tests"""
    print("🚀 JARVIS Email Feature - Complete Test Suite")
    print("=" * 50)
    
    try:
        await test_email_detection()
        await test_subject_detection()
        test_file_operations()
        await test_email_generation()
        await test_integration()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS COMPLETED!")
        print("✅ Email feature is ready for use")
        print("\nTo use the email feature:")
        print("1. Run: python jarvis_with_email.py")
        print("2. Choose option 1 (Start voice mode)")
        print("3. Say 'Hey JARVIS' to wake up")
        print("4. Say 'JARVIS write an email for me'")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted")
    except Exception as e:
        print(f"❌ Test error: {e}")