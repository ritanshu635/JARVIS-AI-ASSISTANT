import os
import re
import time

def extract_yt_term(command):
    """Extract YouTube search term from command - exactly like jarvis-main"""
    # Define a regular expression pattern to capture the song name
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    # Use re.search to find the match in the command
    match = re.search(pattern, command, re.IGNORECASE)
    # If a match is found, return the extracted song name; otherwise, return None
    return match.group(1) if match else None

def remove_words(input_string, words_to_remove):
    """Remove specific words from input string - exactly like jarvis-main"""
    # Split the input string into words
    words = input_string.split()

    # Remove unwanted words
    filtered_words = [word for word in words if word.lower() not in words_to_remove]

    # Join the remaining words back into a string
    result_string = ' '.join(filtered_words)

    return result_string

# ADB helper functions - exactly like jarvis-main helper.py
def keyEvent(key_code):
    """Key events like receive call, stop call, go back - same as jarvis-main"""
    command = f'adb shell input keyevent {key_code}'
    os.system(command)
    time.sleep(1)

def tapEvents(x, y):
    """Tap event used to tap anywhere on screen - same as jarvis-main"""
    command = f'adb shell input tap {x} {y}'
    os.system(command)
    time.sleep(1)

def adbInput(message):
    """Input Event is used to insert text in mobile - same as jarvis-main"""
    command = f'adb shell input text "{message}"'
    os.system(command)
    time.sleep(1)

def goback(times):
    """Go complete back - same as jarvis-main"""
    for i in range(times):
        keyEvent(4)  # Back key code

def replace_spaces_with_percent_s(input_string):
    """Replace space in string with %s for complete message send - same as jarvis-main"""
    return input_string.replace(' ', '%s')

# Additional helper functions for enhanced functionality
def clean_phone_number(phone_number):
    """Clean and format phone number"""
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone_number)
    
    # Add country code if not present
    if not cleaned.startswith('+'):
        if cleaned.startswith('91'):
            cleaned = '+' + cleaned
        elif len(cleaned) == 10:
            cleaned = '+91' + cleaned
    
    return cleaned

def format_contact_name(name):
    """Format contact name for display"""
    return name.title().strip()

def extract_search_term(command, platform="google"):
    """Extract search term from search commands"""
    patterns = {
        'google': [
            r'(?:search|google|find)\s+(?:for\s+)?(.+?)\s+(?:on|in)\s+google',
            r'(?:search|google|find)\s+(?:for\s+)?(.+)',
            r'(?:look\s+up)\s+(.+)'
        ],
        'youtube': [
            r'(?:search|find)\s+(?:for\s+)?(.+?)\s+(?:on|in)\s+youtube',
            r'youtube\s+search\s+(.+)'
        ]
    }
    
    for pattern in patterns.get(platform, patterns['google']):
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None

def extract_app_name(command):
    """Extract application name from open commands"""
    patterns = [
        r'(?:open|launch|start|run)\s+(.+)',
        r'(?:execute)\s+(.+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None

def extract_contact_name(command):
    """Extract contact name from communication commands"""
    patterns = [
        r'(?:call|phone|dial)\s+(.+)',
        r'(?:message|text|sms)\s+(.+)',
        r'(?:whatsapp|wa)\s+(.+)',
        r'(?:send\s+message\s+to|call)\s+(.+)',
        r'(?:make\s+call\s+to)\s+(.+)'
    ]
    
    # Remove common words
    words_to_remove = ['make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
    
    for pattern in patterns:
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            contact_name = match.group(1).strip()
            return remove_words(contact_name, words_to_remove).strip()
    
    return None

def is_question(text):
    """Check if text is a question"""
    question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'which', 'whose', 'whom']
    text_lower = text.lower().strip()
    
    # Check for question words at the beginning
    for word in question_words:
        if text_lower.startswith(word):
            return True
    
    # Check for question mark
    if text.strip().endswith('?'):
        return True
    
    return False

def get_time_greeting():
    """Get appropriate greeting based on time of day"""
    from datetime import datetime
    
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 21:
        return "Good evening"
    else:
        return "Good night"

def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def sanitize_filename(filename):
    """Sanitize filename for safe file operations"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

def parse_voice_command(command):
    """Parse voice command and extract intent and entities"""
    command = command.lower().strip()
    
    result = {
        'original': command,
        'intent': 'unknown',
        'entities': {},
        'confidence': 0.0
    }
    
    # Simple intent classification
    if any(word in command for word in ['open', 'launch', 'start', 'run']):
        result['intent'] = 'open_app'
        result['entities']['app_name'] = extract_app_name(command)
        result['confidence'] = 0.8
        
    elif any(word in command for word in ['play', 'stream']) and 'youtube' in command:
        result['intent'] = 'play_youtube'
        result['entities']['search_term'] = extract_yt_term(command)
        result['confidence'] = 0.9
        
    elif any(word in command for word in ['call', 'phone', 'dial']):
        result['intent'] = 'make_call'
        result['entities']['contact_name'] = extract_contact_name(command)
        result['confidence'] = 0.8
        
    elif any(word in command for word in ['message', 'text', 'sms']):
        result['intent'] = 'send_message'
        result['entities']['contact_name'] = extract_contact_name(command)
        result['confidence'] = 0.8
        
    elif 'whatsapp' in command:
        result['intent'] = 'whatsapp'
        result['entities']['contact_name'] = extract_contact_name(command)
        if 'call' in command:
            result['entities']['action'] = 'call'
        elif 'video' in command:
            result['entities']['action'] = 'video_call'
        else:
            result['entities']['action'] = 'message'
        result['confidence'] = 0.9
        
    elif any(word in command for word in ['search', 'google', 'find', 'look up']):
        result['intent'] = 'web_search'
        result['entities']['search_term'] = extract_search_term(command)
        result['confidence'] = 0.7
        
    elif any(word in command for word in ['weather', 'temperature']):
        result['intent'] = 'weather'
        result['confidence'] = 0.8
        
    elif any(word in command for word in ['time', 'date']):
        result['intent'] = 'time_date'
        result['confidence'] = 0.9
        
    elif any(word in command for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        result['intent'] = 'greeting'
        result['confidence'] = 0.9
        
    elif is_question(command):
        result['intent'] = 'question'
        result['confidence'] = 0.6
        
    else:
        result['intent'] = 'general'
        result['confidence'] = 0.5
    
    return result

# Export all functions
__all__ = [
    'extract_yt_term', 'remove_words', 'keyEvent', 'tapEvents', 'adbInput', 
    'goback', 'replace_spaces_with_percent_s', 'clean_phone_number',
    'format_contact_name', 'extract_search_term', 'extract_app_name',
    'extract_contact_name', 'is_question', 'get_time_greeting',
    'format_duration', 'sanitize_filename', 'parse_voice_command'
]