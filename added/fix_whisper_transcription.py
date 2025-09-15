#!/usr/bin/env python3
"""
Fix Whisper Transcription Issue
Test transcription with the latest audio file
"""

import whisper
import os
import requests

def test_whisper_fix():
    """Test Whisper transcription with different approaches"""
    
    # Find latest audio file
    audio_files = [f for f in os.listdir('.') if f.startswith('meeting_') and f.endswith('.wav')]
    if not audio_files:
        print("❌ No audio files found")
        return
    
    latest_file = sorted(audio_files)[-1]
    print(f"🎵 Testing with: {latest_file}")
    
    # Load Whisper model
    print("📥 Loading Whisper model...")
    model = whisper.load_model("base")
    
    # Method 1: Direct filename
    try:
        print("🔄 Method 1: Direct filename...")
        result = model.transcribe(latest_file)
        transcript = result["text"].strip()
        print(f"✅ Success! Transcript: {transcript}")
        
        if transcript:
            # Test Ollama
            print("\n🧠 Testing Ollama summarization...")
            summary = test_ollama(transcript)
            print(f"📋 Summary: {summary}")
            
            # Save files
            transcript_file = latest_file.replace('.wav', '_transcript.txt')
            summary_file = latest_file.replace('.wav', '_summary.txt')
            
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            print(f"✅ Files saved: {transcript_file}, {summary_file}")
            return True
        else:
            print("⚠️ No speech detected in audio")
            
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    # Method 2: Copy to temp file
    try:
        print("🔄 Method 2: Copy to temp file...")
        import shutil
        temp_file = "temp_audio.wav"
        shutil.copy2(latest_file, temp_file)
        
        result = model.transcribe(temp_file)
        transcript = result["text"].strip()
        print(f"✅ Success! Transcript: {transcript}")
        
        os.remove(temp_file)
        return True
        
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    return False

def test_ollama(transcript):
    """Test Ollama summarization"""
    try:
        prompt = f"""Analyze this meeting transcript and provide a summary:

📋 MEETING SUMMARY
==================

🎯 KEY POINTS:
- [List main discussion points]

📝 ACTION ITEMS:
- [List any tasks mentioned]

💡 IMPORTANT DETAILS:
- [List other significant information]

TRANSCRIPT:
{transcript}

Please provide a clear summary."""

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2:3b',
                'prompt': prompt,
                'stream': False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'Failed to generate summary')
        else:
            return f"Ollama API error: {response.status_code}"
            
    except Exception as e:
        return f"Ollama error: {e}"

if __name__ == "__main__":
    print("🔧 Fixing Whisper Transcription Issue")
    print("=" * 50)
    test_whisper_fix()