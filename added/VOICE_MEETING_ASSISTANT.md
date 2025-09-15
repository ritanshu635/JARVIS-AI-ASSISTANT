# 🎤 Voice-Activated Meeting Assistant

## Overview
This feature allows Jarvis to attend Google Meet meetings for you using voice commands. It records desktop audio from your Realtek speakers, transcribes with Whisper, and summarizes with Ollama.

## 🚀 Features
- **Voice Activation**: "Jarvis attend the meeting for me"
- **Voice Deactivation**: "OK you can leave the meeting Jarvis"
- **Desktop Audio Recording**: Captures Google Meet participants from your speakers
- **Whisper Transcription**: Converts speech to text
- **Ollama Summarization**: Generates meeting summaries with key points
- **Hackathon Ready**: Impressive demo feature!

## 🎯 Voice Commands

### Start Recording
Say any of these:
- "Jarvis attend the meeting for me"
- "Jarvis attend meeting for me"
- "Attend the meeting for me"

### Stop Recording
Say any of these:
- "OK you can leave the meeting Jarvis"
- "You can leave the meeting Jarvis"
- "Jarvis leave the meeting"
- "Stop meeting Jarvis"

### Check Status
- "Meeting status"

## 🔧 Setup Instructions

### 1. Check Your Setup
```bash
python check_audio_setup.py
```

### 2. Test the Feature
```bash
python test_voice_meeting.py
```

### 3. Use with JARVIS
```bash
python main.py
```

## 📋 How It Works

1. **Voice Listening**: Continuously listens for voice commands
2. **Meeting Recording**: Records desktop audio from your Realtek speakers
3. **Transcription**: Uses Whisper to convert audio to text
4. **Summarization**: Uses Ollama to create meeting summary
5. **Output**: Saves transcript and summary files

## 🎵 Audio Setup (Your Realtek Audio)

Your system uses:
- **Speaker**: 3- Realtek(R) Audio (24-bit, 48000 Hz)
- **Recording**: Stereo Mix from Realtek device
- **Format**: High-quality audio capture

## 📁 Generated Files

After each meeting:
- `meeting_YYYYMMDD_HHMMSS_transcript.txt` - Full transcript
- `meeting_YYYYMMDD_HHMMSS_summary.txt` - AI-generated summary

## 🧠 Summary Format

The Ollama summary includes:
- 🎯 **Key Decisions**
- 📝 **Action Items**
- ⏰ **Deadlines & Dates**
- 👥 **Participants & Roles**
- 💡 **Important Points**
- 🔄 **Next Steps**

## 🛠️ Troubleshooting

### No Audio Recorded
- Check if Stereo Mix is enabled in Windows Sound settings
- Ensure Google Meet audio is playing through speakers
- Verify Realtek audio drivers are updated

### Voice Commands Not Working
- Check microphone permissions
- Speak clearly and at normal volume
- Ensure internet connection for Google Speech Recognition

### Ollama Not Responding
- Start Ollama: `ollama serve`
- Install a model: `ollama pull llama3.2:3b`

## 🏆 Hackathon Appeal

This feature is perfect for hackathons because:
- **Practical**: Solves real meeting fatigue problem
- **Impressive**: Voice-activated AI assistant
- **Modern Tech Stack**: Whisper + Ollama + Voice Recognition
- **Demo-Friendly**: Easy to show judges
- **Relatable**: Everyone hates long meetings!

## 🔄 Integration

The meeting assistant integrates with:
- Main JARVIS system (`main.py`)
- Voice engine for TTS responses
- Web interface for status display
- Database for chat history

## 📞 Usage Example

```
You: "Jarvis attend the meeting for me"
Jarvis: "Meeting recording started! I'm listening to Google Meet audio."

[Meeting happens - Jarvis records desktop audio]

You: "OK you can leave the meeting Jarvis"
Jarvis: "Meeting processed! Here's your summary..."

[Displays key points, action items, deadlines, etc.]
```

## 🎯 Perfect for Demos

1. Start Google Meet with test participants
2. Say "Jarvis attend the meeting for me"
3. Let meeting audio play for 30 seconds
4. Say "OK you can leave the meeting Jarvis"
5. Show the generated summary to judges
6. Judges will be impressed! 🏆