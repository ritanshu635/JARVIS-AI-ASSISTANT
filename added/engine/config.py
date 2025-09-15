import os
from dotenv import load_dotenv

load_dotenv()

# Assistant configuration - same as jarvis-main but with environment variable support
ASSISTANT_NAME = os.getenv('AssistantName', 'jarvis').lower()
USER_NAME = os.getenv('NickName', 'boss')
INPUT_LANGUAGE = os.getenv('InputLanguage', 'English')

# Voice configuration
TTS_RATE = int(os.getenv('TTS_RATE', '174'))
TTS_VOICE = int(os.getenv('TTS_VOICE', '0'))

# AI configuration
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2:7b-chat')
WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')

# Database configuration
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'jarvis_unified')

# Android configuration
ADB_PATH = os.getenv('ADB_PATH', 'adb')

# API Keys
GROQ_API_KEY = os.getenv('GroqAPI')
COHERE_API_KEY = os.getenv('CohereAPI')
HUGGINGFACE_API_KEY = os.getenv('HuggingFaceAPI')

# Application settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Wake word settings
WAKE_WORDS = ['jarvis', 'alexa']  # Same as jarvis-main

# System paths
ASSETS_PATH = "www/assets"
AUDIO_PATH = f"{ASSETS_PATH}/audio"
IMAGES_PATH = f"{ASSETS_PATH}/images"

# Default responses - same style as jarvis-main
PROFESSIONAL_RESPONSES = [
    "Task completed successfully, sir.",
    "Done, sir. Anything else I can help you with?",
    "Command executed, sir.",
    "At your service, sir.",
    "Task accomplished, sir.",
    "Ready for the next command, sir.",
    "Operation completed, sir.",
    "Standing by for further instructions, sir."
]

GREETING_RESPONSES = [
    f"Hello {USER_NAME}, how can I assist you today?",
    f"Good to see you, {USER_NAME}. What can I do for you?",
    f"At your service, {USER_NAME}. How may I help?",
    f"Ready to assist, {USER_NAME}. What do you need?"
]

ERROR_RESPONSES = [
    "I apologize, but I encountered an error.",
    "Something went wrong, sir. Please try again.",
    "I'm having trouble with that request.",
    "There seems to be an issue. Let me try again."
]

# Feature flags
ENABLE_FACE_AUTH = True
ENABLE_WAKE_WORD = True
ENABLE_ANDROID_INTEGRATION = True
ENABLE_VOICE_RECOGNITION = True
ENABLE_WEB_INTERFACE = True

# Timeouts and limits
VOICE_TIMEOUT = 10  # seconds
COMMAND_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
AUDIO_CHUNK_SIZE = 1024
SAMPLE_RATE = 16000

# File paths
DATABASE_PATH = "jarvis.db"
CHAT_LOG_PATH = "ChatLog.json"
COOKIES_PATH = "engine/cookies.json"
BACKUP_PATH = "backups/"

# Export configuration
__all__ = [
    'ASSISTANT_NAME', 'USER_NAME', 'INPUT_LANGUAGE',
    'TTS_RATE', 'TTS_VOICE', 'OLLAMA_URL', 'OLLAMA_MODEL',
    'WHISPER_MODEL', 'MONGO_URL', 'DB_NAME', 'ADB_PATH',
    'GROQ_API_KEY', 'COHERE_API_KEY', 'HUGGINGFACE_API_KEY',
    'DEBUG', 'LOG_LEVEL', 'WAKE_WORDS', 'ASSETS_PATH',
    'PROFESSIONAL_RESPONSES', 'GREETING_RESPONSES', 'ERROR_RESPONSES',
    'ENABLE_FACE_AUTH', 'ENABLE_WAKE_WORD', 'ENABLE_ANDROID_INTEGRATION',
    'VOICE_TIMEOUT', 'COMMAND_TIMEOUT', 'MAX_RETRIES',
    'DATABASE_PATH', 'CHAT_LOG_PATH', 'COOKIES_PATH'
]