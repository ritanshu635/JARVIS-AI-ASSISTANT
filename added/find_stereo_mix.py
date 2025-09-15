#!/usr/bin/env python3
"""
Find the correct Stereo Mix device index
"""

import pyaudio

def find_stereo_mix():
    """Find the correct Stereo Mix device"""
    print("🔍 Scanning for Stereo Mix device...")
    
    audio = pyaudio.PyAudio()
    
    stereo_mix_devices = []
    
    print("\n📋 All Audio Devices:")
    print("-" * 60)
    
    for i in range(audio.get_device_count()):
        try:
            info = audio.get_device_info_by_index(i)
            device_name = info['name']
            max_inputs = info['maxInputChannels']
            max_outputs = info['maxOutputChannels']
            
            # Check if this might be Stereo Mix
            is_stereo_mix = 'stereo mix' in device_name.lower()
            is_input_device = max_inputs > 0
            
            status = ""
            if is_stereo_mix and is_input_device:
                status = " 🎯 STEREO MIX (WORKING!)"
                stereo_mix_devices.append(i)
            elif is_stereo_mix:
                status = " ⚠️ STEREO MIX (NO INPUTS)"
            elif is_input_device:
                status = " 🎤 INPUT DEVICE"
            
            print(f"{i:2d}: {device_name[:50]:<50} In:{max_inputs} Out:{max_outputs}{status}")
            
        except Exception as e:
            print(f"{i:2d}: ERROR - {e}")
    
    audio.terminate()
    
    print("\n" + "=" * 60)
    
    if stereo_mix_devices:
        print(f"✅ Found working Stereo Mix devices at indices: {stereo_mix_devices}")
        return stereo_mix_devices[0]  # Return the first working one
    else:
        print("❌ No working Stereo Mix device found")
        print("\n💡 Troubleshooting:")
        print("1. Make sure Stereo Mix is enabled in Sound Control Panel")
        print("2. Check that it's not muted")
        print("3. Try setting it as default recording device")
        print("4. Restart the computer")
        return None

def test_stereo_mix_device(device_index):
    """Test a specific Stereo Mix device"""
    print(f"\n🧪 Testing device {device_index}...")
    
    audio = pyaudio.PyAudio()
    
    try:
        # Get device info
        info = audio.get_device_info_by_index(device_index)
        print(f"📱 Device: {info['name']}")
        print(f"📊 Max inputs: {info['maxInputChannels']}")
        
        if info['maxInputChannels'] == 0:
            print("❌ Device has no input channels")
            return False
        
        print("🎵 Play some audio (YouTube, music) and press Enter...")
        input()
        
        # Try to open stream
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=min(2, info['maxInputChannels']),  # Use available channels
            rate=44100,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024
        )
        
        print("🔴 Recording 3 seconds...")
        
        frames = []
        for i in range(0, int(44100 / 1024 * 3)):  # 3 seconds
            data = stream.read(1024, exception_on_overflow=False)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        # Check audio level
        import numpy as np
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        max_amplitude = np.max(np.abs(audio_data))
        
        print(f"📊 Max amplitude: {max_amplitude}")
        
        if max_amplitude > 100:
            print("✅ SUCCESS! This device is capturing audio!")
            return True
        else:
            print("⚠️ Very low audio - check volume levels")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        audio.terminate()

if __name__ == "__main__":
    print("🔊 Stereo Mix Device Finder")
    print("=" * 40)
    
    # Find Stereo Mix
    stereo_mix_index = find_stereo_mix()
    
    if stereo_mix_index is not None:
        print(f"\n🎯 Testing Stereo Mix at index {stereo_mix_index}...")
        success = test_stereo_mix_device(stereo_mix_index)
        
        if success:
            print(f"\n🎉 PERFECT! Use device index {stereo_mix_index} for meeting recording")
            print(f"📝 Update your meeting assistant to use index: {stereo_mix_index}")
        else:
            print(f"\n❌ Device {stereo_mix_index} not working properly")
    
    print("\n✅ Scan completed!")