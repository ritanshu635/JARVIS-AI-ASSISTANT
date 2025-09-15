#!/usr/bin/env python3
"""
Setup script for Meeting Assistant
Ensures all dependencies are installed and Ollama is configured
"""

import subprocess
import sys
import os
import requests

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def check_ollama():
    """Check if Ollama is installed and running"""
    print("\n🧠 Checking Ollama...")
    
    # Check if ollama command exists
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            print(f"Version: {result.stdout.strip()}")
        else:
            print("❌ Ollama command not found")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        print("Please install Ollama from: https://ollama.ai/")
        return False
    
    # Check if Ollama is running
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama is running!")
            
            # Check for llama3 model
            model_names = [model.get('name', '') for model in models.get('models', [])]
            if any('llama3' in name for name in model_names):
                print("✅ llama3 model is available")
            else:
                print("⚠️  llama3 model not found. Installing...")
                try:
                    subprocess.run(['ollama', 'pull', 'llama3'], check=True)
                    print("✅ llama3 model installed")
                except subprocess.CalledProcessError:
                    print("❌ Failed to install llama3 model")
                    return False
            
            return True
        else:
            print(f"❌ Ollama responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama is not running. Start it with: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def setup_meeting_assistant():
    """Setup the meeting assistant"""
    print("🤖 Setting up Meeting Assistant for Jarvis")
    print("=" * 50)
    
    # Check Python packages
    required_packages = [
        'openai-whisper',
        'pyaudio',
        'sounddevice',
        'soundfile',
        'requests',
        'torch',
        'torchaudio'
    ]
    
    print("📦 Checking Python packages...")
    all_installed = True
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is already installed")
        except ImportError:
            print(f"⚠️  {package} not found. Installing...")
            if not install_package(package):
                all_installed = False
    
    if not all_installed:
        print("❌ Some packages failed to install. Please install them manually.")
        return False
    
    # Check Ollama
    if not check_ollama():
        print("\n❌ Ollama setup incomplete. Please:")
        print("1. Install Ollama from https://ollama.ai/")
        print("2. Run 'ollama serve' in a terminal")
        print("3. Run 'ollama pull llama3' to install the model")
        return False
    
    # Test Whisper model loading
    print("\n🎤 Testing Whisper model...")
    try:
        import whisper
        model = whisper.load_model("base")
        print("✅ Whisper model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading Whisper model: {e}")
        return False
    
    print("\n🎉 Meeting Assistant setup completed successfully!")
    print("\nYou can now use these commands:")
    print("- 'Jarvis attend the meeting for me' - Start recording")
    print("- 'Jarvis you can leave the meeting' - Stop and process")
    print("- 'meeting status' - Check recording status")
    
    return True

if __name__ == "__main__":
    success = setup_meeting_assistant()
    
    if success:
        print("\n🚀 Ready to use Meeting Assistant!")
        
        # Ask if user wants to run a test
        test_input = input("\nWould you like to run a quick test? (y/n): ").lower()
        if test_input == 'y':
            print("Running test...")
            os.system(f"{sys.executable} test_meeting_assistant.py")
    else:
        print("\n❌ Setup failed. Please resolve the issues above.")
        sys.exit(1)