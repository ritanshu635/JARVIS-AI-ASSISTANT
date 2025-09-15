# 🤖 Jarvis Meeting Assistant

## Overview
The Meeting Assistant is a powerful feature that allows Jarvis to attend meetings on your behalf, record the audio, transcribe it using OpenAI's Whisper, and provide intelligent summaries using Ollama (local LLM).

## 🎯 Key Features

### Voice-Activated Meeting Recording
- **Start Recording**: "Jarvis, attend the meeting for me"
- **Stop Recording**: "Jarvis, you can leave the meeting"
- **Check Status**: "Meeting status"

### Automatic Processing Pipeline
1. **Audio Recording**: Captures meeting audio in real-time
2. **Transcription**: Uses Whisper AI for accurate speech-to-text
3. **Summarization**: Ollama processes transcript into structured summary
4. **File Management**: Saves transcripts and summaries automatically

### Intelligent Summary Format
```
📋 MEETING SUMMARY
==================

🎯 KEY DECISIONS:
- Important decisions made during the meeting

📝 ACTION ITEMS:
- Tasks assigned with responsible persons

⏰ DEADLINES & DATES:
- All mentioned deadlines and important dates

👥 PARTICIPANTS & ROLES:
- Participants and their responsibilities

💡 IMPORTANT POINTS:
- Other significant discussion points

🔄 NEXT STEPS:
- Planned follow-up actions
```

## 🚀 Quick Start

### 1. Setup
```bash
# Run the setup script
python setup_meeting_assistant.py

# Or install manually:
pip install openai-whisper pyaudio requests torch torchaudio

# Install and start Ollama
# Download from: https://ollama.ai/
ollama serve
ollama pull llama3
```

### 2. Test the Feature
```bash
# Run the test suite
python test_meeting_assistant.py

# Or test with main Jarvis
python final_jarvis.py
```

### 3. Use in Meetings
1. Join your Google Meet/Zoom meeting
2. Say: **"Jarvis, attend the meeting for me"**
3. Jarvis starts recording audio
4. When meeting ends, say: **"Jarvis, you can leave the meeting"**
5. Jarvis processes and provides summary

## 🛠️ Technical Architecture

### Components
- **meeting_assistant.py**: Core meeting recording and processing logic
- **Whisper Integration**: OpenAI's Whisper for speech recognition
- **Ollama Integration**: Local LLM for intelligent summarization
- **Audio Processing**: PyAudio for real-time audio capture

### File Structure
```
added/
├── meeting_assistant.py          # Main meeting assistant module
├── setup_meeting_assistant.py    # Setup and dependency checker
├── test_meeting_assistant.py     # Test suite
├── final_jarvis.py              # Updated main Jarvis (with meeting commands)
└── MEETING_ASSISTANT_README.md   # This file
```

### Generated Files
- `meeting_YYYYMMDD_HHMMSS.wav` - Original audio (auto-deleted)
- `meeting_YYYYMMDD_HHMMSS_transcript.txt` - Full transcript
- `meeting_YYYYMMDD_HHMMSS_summary.txt` - AI-generated summary

## 🎤 Voice Commands

### Natural Language Support
The system understands various ways to express the same command:

**Start Recording:**
- "Jarvis, attend the meeting for me"
- "Jarvis, attend meeting"
- "Start recording the meeting"

**Stop Recording:**
- "Jarvis, you can leave the meeting"
- "Jarvis, stop meeting"
- "End meeting recording"

**Check Status:**
- "Meeting status"
- "Are you recording?"

## 🔧 Configuration

### Whisper Model Options
```python
# In meeting_assistant.py, line 25:
self.whisper_model = whisper.load_model("base")  # Default

# Options: "tiny", "base", "small", "medium", "large"
# Larger models = better accuracy, slower processing
```

### Ollama Model Configuration
```python
# In meeting_assistant.py, line 156:
'model': 'llama3'  # Default model

# Can use: llama3, llama2, codellama, mistral, etc.
```

### Audio Settings
```python
# In meeting_assistant.py, lines 18-22:
self.channels = 2        # Stereo recording
self.rate = 44100       # Sample rate
self.chunk = 1024       # Buffer size
```

## 🐛 Troubleshooting

### Common Issues

**1. "Could not connect to Ollama"**
```bash
# Start Ollama server
ollama serve

# Install llama3 model
ollama pull llama3
```

**2. "Error starting recording"**
```bash
# Check microphone permissions
# On Windows: Settings > Privacy > Microphone
# Ensure Python has microphone access
```

**3. "Whisper model loading failed"**
```bash
# Reinstall whisper
pip uninstall openai-whisper
pip install openai-whisper

# Or try with specific torch version
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**4. "PyAudio installation failed"**
```bash
# Windows: Install Visual C++ Build Tools
# Or use conda:
conda install pyaudio

# Linux:
sudo apt-get install portaudio19-dev python3-pyaudio
```

### Debug Mode
```python
# Enable debug logging in meeting_assistant.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🏆 Hackathon Appeal

### Why This Feature Wins
1. **Solves Real Problems**: Meeting fatigue is universal
2. **Cutting-Edge Tech**: Whisper + Local LLM integration
3. **Privacy-First**: All processing happens locally
4. **Natural Interface**: Voice commands feel futuristic
5. **Practical Value**: Saves hours of meeting time

### Demo Script
```
1. "Hey everyone, let me show you Jarvis Meeting Assistant"
2. Start a fake meeting (play meeting audio)
3. "Jarvis, attend the meeting for me"
4. Let it record for 30 seconds
5. "Jarvis, you can leave the meeting"
6. Show the generated summary
7. "And that's how Jarvis saves me from boring meetings!"
```

## 📈 Future Enhancements

### Planned Features
- **Multi-language Support**: Whisper supports 99 languages
- **Speaker Identification**: Who said what
- **Action Item Extraction**: Automatic task creation
- **Calendar Integration**: Auto-schedule follow-ups
- **Sentiment Analysis**: Meeting mood tracking
- **Real-time Transcription**: Live captions during meetings

### Integration Ideas
- **Slack/Teams Bots**: Auto-post summaries
- **Email Integration**: Send summaries to participants
- **CRM Integration**: Log meeting notes automatically
- **Analytics Dashboard**: Meeting insights and trends

## 🤝 Contributing

### Adding New Features
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Add your changes to `meeting_assistant.py`
4. Update tests in `test_meeting_assistant.py`
5. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to all functions
- Include error handling
- Write unit tests

## 📄 License
This project is part of the Jarvis AI Assistant system.

---

**Made with ❤️ for the hackathon by the Jarvis team**

*"Why attend boring meetings when Jarvis can do it for you?"*