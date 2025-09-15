# JARVIS Intelligent Email Composer

## Overview
The Intelligent Email Composer is a new feature for your JARVIS system that allows you to compose professional emails using voice commands. The system uses AI (Ollama) to generate email content based on your responses to intelligent follow-up questions.

## Features

### 🎤 Voice-Controlled
- Uses speech recognition to listen to your commands
- Responds with text-to-speech (pyttsx3)
- Natural conversation flow

### 🧠 AI-Powered Content Generation
- Uses Ollama for intelligent email content generation
- Adapts content based on email type and context
- Professional formatting and tone

### 📧 Smart Email Types
The system automatically detects email types and asks relevant questions:

- **Leave Applications**: Asks about dates, reason, who to address
- **Job Applications**: Asks about position, experience, skills
- **Meeting Requests**: Asks about purpose, timing, attendees
- **Complaints**: Asks about issue details, resolution sought
- **Inquiries**: Asks about specific information needed
- **Invitations**: Asks about event details, RSVP info
- **Thank You**: Asks about what you're thanking for
- **Apologies**: Asks about what you're apologizing for

### 📝 Email Management
- Preview generated emails before sending
- Save drafts automatically
- Send emails via Gmail SMTP
- Professional formatting

## Installation & Setup

### 1. Dependencies
Make sure you have all required packages installed:
```bash
pip install speech-recognition pyttsx3 requests asyncio
```

### 2. Gmail Setup (for sending emails)
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use this app password (not your regular password) when setting up email credentials

### 3. Ollama Setup
Make sure Ollama is running:
```bash
ollama serve
```

## Usage

### Method 1: Integrated with Main JARVIS
```bash
python jarvis_with_email.py
```
1. Choose option 1 (Start voice mode)
2. Say "Hey JARVIS" to wake up
3. Say "JARVIS write an email for me"

### Method 2: Standalone Email Composer
```bash
python intelligent_email_composer.py
```
1. Choose option 1 (Compose email with voice)
2. Follow the voice prompts

### Method 3: Test the Feature
```bash
python test_email_feature.py
```
This runs comprehensive tests to verify everything works.

## Voice Commands

### Activation Commands
- "JARVIS write an email for me"
- "write email"
- "compose email"
- "send mail"
- "help me write an email"

### Setup Commands
- "setup email credentials"
- "configure email"

## How It Works

### 1. Email Composition Flow
```
1. You: "JARVIS write an email for me"
2. JARVIS: "I will write an email for you sir. Whom should I send this email to?"
3. You: "manager@company.com"
4. JARVIS: "What should be the subject of this email?"
5. You: "Leave Application"
6. JARVIS: "I detected this is a leave email. Let me ask some relevant questions."
7. JARVIS asks follow-up questions based on email type
8. JARVIS generates professional email content using AI
9. JARVIS previews the email and asks for confirmation
10. You can choose to send, save as draft, or regenerate
```

### 2. Smart Follow-up Questions
Based on the subject, JARVIS asks intelligent questions:

**For "Leave Application":**
- Who should I address this to?
- What type of leave?
- From which date?
- Until which date?
- What's the reason?

**For "Job Application":**
- What position are you applying for?
- What company?
- How many years of experience?
- What are your key skills?
- When are you available to start?

### 3. AI Content Generation
The system uses your responses to generate professional email content:
- Proper greeting and closing
- Professional tone and structure
- All relevant information included
- Formatted for business communication

## File Structure

```
added/
├── intelligent_email_composer.py    # Main email composer
├── jarvis_email_integration.py      # Integration with JARVIS
├── jarvis_with_email.py            # Enhanced JARVIS with email
├── test_email_feature.py           # Test suite
└── EMAIL_COMPOSER_README.md        # This file
```

## Configuration

### Email Settings
The system will prompt you to set up:
- Gmail address
- Gmail app password
- SMTP settings (pre-configured for Gmail)

### Voice Settings
- Microphone calibration (automatic)
- Speech recognition timeout (configurable)
- TTS voice and speed (uses system defaults)

## Troubleshooting

### Common Issues

1. **Speech Recognition Not Working**
   - Check microphone permissions
   - Run microphone calibration
   - Ensure internet connection (Google Speech API)

2. **Email Sending Fails**
   - Verify Gmail app password (not regular password)
   - Check 2-factor authentication is enabled
   - Ensure "Less secure app access" is disabled (use app password instead)

3. **AI Content Generation Fails**
   - Ensure Ollama is running: `ollama serve`
   - Check if model is available: `ollama list`
   - Falls back to template-based generation if AI fails

4. **Voice Commands Not Recognized**
   - Speak clearly and at normal pace
   - Ensure wake word "JARVIS" is pronounced clearly
   - Check for background noise

### Debug Mode
Run with debug output:
```bash
python -u jarvis_with_email.py
```

## Examples

### Example 1: Leave Application
```
You: "JARVIS write an email for me"
JARVIS: "Whom should I send this email to?"
You: "manager@company.com"
JARVIS: "What should be the subject?"
You: "Sick Leave Application"
JARVIS: "Who should I address this to?"
You: "My manager"
JARVIS: "What type of leave?"
You: "Sick leave"
JARVIS: "From which date?"
You: "Tomorrow"
JARVIS: "Until which date?"
You: "Day after tomorrow"
JARVIS: "What's the reason?"
You: "I have fever and need rest"

Generated Email:
---
Dear Manager,

I am writing to request sick leave from work.

Please find the details below:
- Type: Sick leave
- From: Tomorrow
- Until: Day after tomorrow
- Reason: I have fever and need rest

I would appreciate your approval for this leave request.

Thank you for your consideration.

Best regards,
[Your Name]
---
```

### Example 2: Job Application
```
You: "JARVIS write an email for me"
JARVIS: "Whom should I send this email to?"
You: "hr@techcompany.com"
JARVIS: "What should be the subject?"
You: "Application for Software Developer Position"

[JARVIS asks job-related questions and generates professional application email]
```

## Advanced Features

### Custom Email Templates
You can modify the `subject_questions` dictionary in `intelligent_email_composer.py` to add new email types or customize questions.

### Integration with Contacts
The system can be extended to integrate with your existing contacts database for auto-completion of email addresses.

### Multiple AI Backends
The system uses the existing AI Router which supports:
- Ollama (local, private)
- Groq API (fast, cloud-based)
- Cohere API (reliable, cloud-based)

## Security & Privacy

- **Local Processing**: When using Ollama, all AI processing happens locally
- **No Email Storage**: Emails are only saved as drafts locally if requested
- **Secure SMTP**: Uses TLS encryption for email sending
- **App Passwords**: Uses secure Gmail app passwords, not account passwords

## Future Enhancements

Planned features:
- Email templates library
- Contact integration
- Email scheduling
- Multi-language support
- Email thread management
- Attachment support

## Support

If you encounter issues:
1. Run the test suite: `python test_email_feature.py`
2. Check the troubleshooting section above
3. Verify all dependencies are installed
4. Ensure Ollama is running and accessible

## License

This email composer is part of your JARVIS system and follows the same licensing terms.