# 🔊 Windows Audio Setup for Meeting Assistant

## Problem: Capturing Google Meet Audio

By default, most audio recording libraries only capture microphone input, not the audio coming from your speakers (Google Meet participants). To record both your voice AND the meeting audio, you need to enable "Stereo Mix" or use virtual audio cables.

## 🎯 Solution Options

### Option 1: Enable Stereo Mix (Recommended)

**Step 1: Enable Stereo Mix**
1. Right-click the speaker icon in your system tray
2. Select "Open Sound settings"
3. Click "Sound Control Panel" on the right
4. Go to the "Recording" tab
5. Right-click in empty space and check "Show Disabled Devices"
6. You should see "Stereo Mix" - right-click it and select "Enable"
7. Set "Stereo Mix" as the default recording device

**Step 2: Test the Setup**
```bash
cd added
python system_audio_capture.py
```

### Option 2: Virtual Audio Cable (Advanced)

**Install VB-Audio Virtual Cable:**
1. Download from: https://vb-audio.com/Cable/
2. Install the virtual cable
3. Set "CABLE Output" as your default playback device
4. Set "CABLE Input" as your recording device in the meeting assistant

### Option 3: OBS Virtual Camera (Alternative)

**Use OBS Studio:**
1. Install OBS Studio
2. Add "Audio Output Capture" source
3. Use OBS virtual camera for recording

## 🔧 Troubleshooting

### "No Stereo Mix Available"
Some modern sound cards don't have Stereo Mix. Try:
1. Update your audio drivers
2. Check manufacturer's website for audio software
3. Use Option 2 (Virtual Audio Cable)

### "Permission Denied" Errors
1. Run Command Prompt as Administrator
2. Try: `python setup_meeting_assistant.py`

### "No Audio Devices Found"
1. Check Windows microphone permissions:
   - Settings > Privacy > Microphone
   - Allow apps to access microphone
2. Test with Windows Voice Recorder first

### "Audio Quality Poor"
1. Increase sample rate in `system_audio_capture.py`:
   ```python
   self.rate = 48000  # Higher quality
   ```
2. Use external microphone for better voice capture

## 🎤 Testing Your Setup

### Quick Test
```bash
# Test system audio capture
python system_audio_capture.py

# Test full meeting assistant
python test_meeting_assistant.py
```

### Live Test with Google Meet
1. Join a test Google Meet
2. Say: "Jarvis, attend the meeting for me"
3. Play some audio or speak
4. Say: "Jarvis, you can leave the meeting"
5. Check the generated transcript

## 📊 Expected Results

**Good Setup:**
- Transcript includes both your voice and meeting participants
- Audio file has clear sound from both sources
- No "No audio data recorded" errors

**Poor Setup:**
- Only your voice in transcript
- Meeting participants' audio missing
- Silent audio files

## 🔍 Debug Commands

### Check Available Audio Devices
```python
import sounddevice as sd
print(sd.query_devices())
```

### Test Microphone
```python
import sounddevice as sd
import numpy as np

# Record 3 seconds
audio = sd.rec(int(3 * 44100), samplerate=44100, channels=2)
sd.wait()
print(f"Audio captured: {audio.shape}")
print(f"Max amplitude: {np.max(np.abs(audio))}")
```

### Check Windows Audio Settings
```bash
# List audio devices (PowerShell)
Get-WmiObject -Class Win32_SoundDevice | Select-Object Name, Status
```

## 🎯 Optimal Configuration

**For Best Results:**
1. **Enable Stereo Mix** - Captures system audio
2. **Use good microphone** - Clear voice capture
3. **Close other audio apps** - Avoid conflicts
4. **Test before important meetings** - Ensure everything works

**Audio Settings:**
- Sample Rate: 44100 Hz (standard)
- Channels: 2 (stereo)
- Format: 16-bit PCM

## 🚨 Important Notes

### Privacy Considerations
- The meeting assistant records ALL system audio
- Make sure participants consent to recording
- Check your company's recording policies

### Performance Tips
- Close unnecessary applications during recording
- Use SSD storage for better file I/O
- Ensure sufficient disk space (1MB per minute)

### Meeting Platform Compatibility
- ✅ Google Meet
- ✅ Zoom
- ✅ Microsoft Teams
- ✅ Discord
- ✅ Any browser-based meeting

## 🆘 Still Having Issues?

### Contact Support Checklist
1. What's your Windows version?
2. What audio hardware do you have?
3. Can you see "Stereo Mix" in recording devices?
4. What error messages do you get?
5. Does the test script work?

### Common Error Solutions

**"Module not found: sounddevice"**
```bash
pip install sounddevice soundfile
```

**"ASIO driver not found"**
```bash
# Use DirectSound instead
import sounddevice as sd
sd.default.hostapi = 'DirectSound'
```

**"Buffer underrun/overrun"**
```python
# Increase buffer size in system_audio_capture.py
self.chunk = 2048  # Larger buffer
```

---

**Remember: The key is capturing BOTH your microphone AND the system audio (Google Meet participants). Test thoroughly before your important meetings!** 🎯