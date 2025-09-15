#!/usr/bin/env python3
"""
Test Audio → Whisper → Ollama Pipeline
Tests the complete flow: Audio file → Whisper transcription → Ollama summary
"""

import whisper
import requests
import json
import os

def test_whisper_transcription(audio_file):
    """Test Whisper transcription"""
    print("🗣️ Testing Whisper Transcription...")
    print("=" * 50)
    
    try:
        # Load Whisper model
        print("📥 Loading Whisper model...")
        model = whisper.load_model("base")
        
        # Transcribe audio
        print(f"🔄 Transcribing: {audio_file}")
        result = model.transcribe(audio_file)
        transcript = result["text"].strip()
        
        print(f"✅ Transcription completed!")
        print(f"📝 Length: {len(transcript)} characters")
        print(f"📄 Transcript preview: {transcript[:200]}...")
        
        return transcript
        
    except Exception as e:
        print(f"❌ Whisper error: {e}")
        return None

def test_ollama_summary(transcript):
    """Test Ollama summarization"""
    print("\n🧠 Testing Ollama Summarization...")
    print("=" * 50)
    
    try:
        prompt = f"""Please analyze this meeting transcript and provide a comprehensive summary:

📋 MEETING SUMMARY
==================

🎯 KEY DECISIONS:
- [List important decisions made]

📝 ACTION ITEMS:
- [List tasks and assignments]

⏰ DEADLINES & DATES:
- [List mentioned deadlines]

👥 PARTICIPANTS & ROLES:
- [List participants mentioned]

💡 IMPORTANT POINTS:
- [List significant discussion points]

🔄 NEXT STEPS:
- [List planned follow-up actions]

TRANSCRIPT:
{transcript}

Please be thorough and capture all important information."""

        print("🔄 Sending to Ollama...")
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2:3b',
                'prompt': prompt,
                'stream': False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('response', 'Failed to generate summary')
            print("✅ Summary generated!")
            return summary
        else:
            print(f"❌ Ollama API error: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Ollama. Make sure it's running: ollama serve")
        return None
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return None

def main():
    """Test the complete Audio → Whisper → Ollama pipeline"""
    print("🎤 Audio → Whisper → Ollama Pipeline Test")
    print("=" * 60)
    
    # Find the latest meeting audio file
    audio_files = [f for f in os.listdir('.') if f.startswith('meeting_') and f.endswith('.wav')]
    
    if not audio_files:
        print("❌ No meeting audio files found")
        print("💡 Run the meeting recorder first to create an audio file")
        return
    
    # Use the latest file
    latest_file = sorted(audio_files)[-1]
    abs_audio_file = os.path.abspath(latest_file)
    print(f"📁 Using audio file: {latest_file}")
    print(f"📁 Full path: {abs_audio_file}")
    
    # Step 1: Whisper transcription
    transcript = test_whisper_transcription(abs_audio_file)
    
    if not transcript:
        print("❌ Transcription failed")
        return
    
    # Save transcript
    transcript_file = latest_file.replace('.wav', '_transcript.txt')
    with open(transcript_file, 'w', encoding='utf-8') as f:
        f.write(transcript)
    print(f"📄 Transcript saved: {transcript_file}")
    
    # Step 2: Ollama summarization
    summary = test_ollama_summary(transcript)
    
    if not summary:
        print("❌ Summarization failed")
        return
    
    # Save summary
    summary_file = latest_file.replace('.wav', '_summary.txt')
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"📋 Summary saved: {summary_file}")
    
    # Display results
    print("\n" + "=" * 60)
    print("📋 COMPLETE PIPELINE RESULTS")
    print("=" * 60)
    print(f"🎵 Audio file: {latest_file}")
    print(f"📄 Transcript: {transcript_file}")
    print(f"📋 Summary: {summary_file}")
    print("\n📝 TRANSCRIPT:")
    print("-" * 40)
    print(transcript)
    print("\n📋 SUMMARY:")
    print("-" * 40)
    print(summary)
    print("=" * 60)
    print("✅ Pipeline test completed successfully!")

if __name__ == "__main__":
    main()