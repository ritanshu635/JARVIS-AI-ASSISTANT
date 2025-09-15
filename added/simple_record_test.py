#!/usr/bin/env python3
"""
Simple Recording Test - Just record and save audio
"""

from simple_meeting_recorder import SimpleMeetingRecorder
import time

def main():
    print("🎤 Simple Desktop Audio Recording Test")
    print("=" * 50)
    
    recorder = SimpleMeetingRecorder()
    
    print("📋 This will:")
    print("1. Record desktop audio for 10 seconds")
    print("2. Save the audio file")
    print("3. Skip Whisper/Ollama processing for now")
    print()
    
    input("👆 Press Enter to start recording...")
    
    # Start recording
    print("\n🎙️ Starting recording...")
    result = recorder.start_recording()
    print(f"Result: {result}")
    
    if "✅" in result:
        print("\n🔴 Recording for 10 seconds...")
        print("💡 Play some audio/video with speech")
        
        for i in range(10, 0, -1):
            print(f"   {i} seconds...")
            time.sleep(1)
        
        print("\n🛑 Stopping recording...")
        
        # Stop recording manually without processing
        recorder.is_recording = False
        if recorder.stream:
            recorder.stream.stop_stream()
            recorder.stream.close()
        
        if hasattr(recorder, 'recording_thread'):
            recorder.recording_thread.join(timeout=3)
        
        if recorder.audio_frames:
            # Save audio file
            from datetime import datetime
            import wave
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"test_meeting_{timestamp}.wav"
            
            with wave.open(audio_filename, 'wb') as wf:
                wf.setnchannels(recorder.channels)
                wf.setsampwidth(recorder.audio.get_sample_size(recorder.format))
                wf.setframerate(recorder.rate)
                wf.writeframes(b''.join(recorder.audio_frames))
            
            duration = len(recorder.audio_frames) * recorder.chunk / recorder.rate
            print(f"✅ Audio saved: {audio_filename} ({duration:.1f} seconds)")
            
            # Check audio quality
            import numpy as np
            audio_data = np.frombuffer(b''.join(recorder.audio_frames), dtype=np.int16)
            max_amplitude = np.max(np.abs(audio_data))
            print(f"📊 Max amplitude: {max_amplitude}")
            
            if max_amplitude > 1000:
                print("✅ Good audio levels detected!")
                print("🎯 Your desktop audio recording is working!")
            else:
                print("⚠️ Low audio levels - check Stereo Mix volume")
        else:
            print("❌ No audio recorded")
    
    else:
        print("❌ Failed to start recording")

if __name__ == "__main__":
    main()