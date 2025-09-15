import os
import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
import eel
try:
    import pyaudio
except ImportError:
    pyaudio = None
try:
    import pyautogui
except ImportError:
    pyautogui = None
try:
    from .command import speak
except ImportError:
    def speak(text):
        print(f"🔊 {text}")
try:
    from .config import ASSISTANT_NAME
except ImportError:
    ASSISTANT_NAME = "Jarvis"
try:
    import pywhatkit as kit
except ImportError:
    kit = None
try:
    import pvporcupine
except ImportError:
    pvporcupine = None
try:
    from .helper import extract_yt_term, remove_words
except ImportError:
    def extract_yt_term(query):
        return query.replace("play", "").strip()
    def remove_words(query, words):
        for word in words:
            query = query.replace(word, "")
        return query.strip()
from .database_manager import DatabaseManager
from .ai_router import AIRouter
import asyncio

# Initialize database connection
db_manager = DatabaseManager()

@eel.expose
def playAssistantSound():
    """Play assistant startup sound - simplified version without playsound"""
    try:
        print("🎵 JARVIS startup sound (audio playback disabled)")
        # Could implement with pygame or other audio library later
    except Exception as e:
        print(f"⚠️ Could not play start sound: {e}")

def openCommand(query):
    """Open applications or websites - exactly like jarvis-main"""
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query = query.lower()

    app_name = query.strip()

    if app_name != "":
        try:
            # Check system commands first
            app_path = db_manager.get_system_command(app_name)
            
            if app_path:
                speak("Opening " + app_name)
                os.startfile(app_path)
            else:
                # Check web commands
                url = db_manager.get_web_command(app_name)
                
                if url:
                    speak("Opening " + app_name)
                    webbrowser.open(url)
                else:
                    # Try generic system open
                    speak("Opening " + app_name)
                    try:
                        os.system('start ' + app_name)
                    except:
                        speak("not found")
        except Exception as e:
            speak("something went wrong")
            print(f"❌ Open command error: {e}")

def PlayYoutube(query):
    """Play YouTube videos - exactly like jarvis-main"""
    search_term = extract_yt_term(query)
    speak("Playing " + search_term + " on YouTube")
    kit.playonyt(search_term)

def hotword():
    """Wake word detection - exactly like jarvis-main"""
    porcupine = None
    paud = None
    audio_stream = None
    try:
        # Pre-trained keywords - same as jarvis-main
        porcupine = pvporcupine.create(keywords=["jarvis", "alexa"]) 
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        
        # Loop for streaming - same as jarvis-main
        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)

            # Processing keyword from mic - same as jarvis-main
            keyword_index = porcupine.process(keyword)

            # Check if keyword detected - same as jarvis-main
            if keyword_index >= 0:
                print("hotword detected")

                # Press shortcut key win+j - same as jarvis-main
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except Exception as e:
        print(f"❌ Hotword detection error: {e}")
    finally:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()

def findContact(query):
    """Find contacts - exactly like jarvis-main"""
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        contact = db_manager.get_contact(query)
        
        if contact:
            mobile_number_str = str(contact['mobile_no'])
            
            if not mobile_number_str.startswith('+91'):
                mobile_number_str = '+91' + mobile_number_str

            return mobile_number_str, contact['name']
        else:
            speak('contact not found')
            return 0, 0
            
    except Exception as e:
        speak('not exist in contacts')
        print(f"❌ Find contact error: {e}")
        return 0, 0

def whatsApp(mobile_no, message, flag, name):
    """WhatsApp automation - exactly like jarvis-main"""
    try:
        if flag == 'message':
            target_tab = 12
            jarvis_message = "message sent successfully to " + name
        elif flag == 'call':
            target_tab = 7
            message = ''
            jarvis_message = "calling " + name
        else:  # video call
            target_tab = 6
            message = ''
            jarvis_message = "starting video call with " + name

        # Encode the message for URL - same as jarvis-main
        from urllib.parse import quote
        encoded_message = quote(message) if message else ''
        print(encoded_message)
        
        # Construct the URL - same as jarvis-main
        whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

        # Construct the full command - same as jarvis-main
        full_command = f'start "" "{whatsapp_url}"'

        # Open WhatsApp with the constructed URL - same as jarvis-main
        subprocess.run(full_command, shell=True)
        time.sleep(5)
        subprocess.run(full_command, shell=True)
        
        # UI automation - same as jarvis-main
        pyautogui.hotkey('ctrl', 'f')

        for i in range(1, target_tab):
            pyautogui.hotkey('tab')

        pyautogui.hotkey('enter')
        speak(jarvis_message)
        
    except Exception as e:
        speak("WhatsApp automation failed")
        print(f"❌ WhatsApp error: {e}")

def chatBot(query):
    """Chat bot using AI - enhanced version with fallback to HugChat like jarvis-main"""
    try:
        # Try our AI router first
        ai_router = AIRouter()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(ai_router.process_query(query, "general"))
        
        if result['success']:
            response = result['response']
            print(response)
            speak(response)
            return response
        else:
            # Fallback to original jarvis-main approach
            raise Exception("AI router failed, using fallback")
            
    except Exception as e:
        print(f"⚠️ AI router failed, trying HugChat fallback: {e}")
        try:
            # Original jarvis-main chatBot implementation as fallback
            from hugchat import hugchat
            user_input = query.lower()
            chatbot = hugchat.ChatBot(cookie_path="engine\\cookies.json")
            id = chatbot.new_conversation()
            chatbot.change_conversation(id)
            response = chatbot.chat(user_input)
            print(response)
            speak(response)
            return response
        except Exception as e2:
            print(f"❌ HugChat also failed: {e2}")
            fallback_response = "I'm sorry, I'm having trouble processing your request right now."
            speak(fallback_response)
            return fallback_response

def makeCall(name, mobileNo):
    """Make phone call via ADB - exactly like jarvis-main"""
    try:
        mobileNo = mobileNo.replace(" ", "")
        speak("Calling " + name)
        command = 'adb shell am start -a android.intent.action.CALL -d tel:' + mobileNo
        os.system(command)
    except Exception as e:
        speak("Failed to make call")
        print(f"❌ Make call error: {e}")

def sendMessage(message, mobileNo, name):
    """Send SMS via ADB - exactly like jarvis-main"""
    try:
        from .helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput
        
        message = replace_spaces_with_percent_s(message)
        mobileNo = replace_spaces_with_percent_s(mobileNo)
        speak("sending message")
        
        # Same sequence as jarvis-main
        goback(4)
        time.sleep(1)
        keyEvent(3)
        # open sms app
        tapEvents(136, 2220)
        time.sleep(1)
        # start chat
        tapEvents(819, 2192)
        time.sleep(1)
        # search mobile no
        adbInput(mobileNo)
        time.sleep(1)
        # tap on name
        tapEvents(601, 574)
        time.sleep(1)
        # tap on input
        tapEvents(390, 2270)
        time.sleep(1)
        # message
        adbInput(message)
        time.sleep(1)
        # send
        tapEvents(957, 1397)
        speak("message sent successfully to " + name)
        
    except Exception as e:
        speak("Failed to send message")
        print(f"❌ Send message error: {e}")

# Additional features from other implementations
def get_weather(location=""):
    """Get weather information"""
    try:
        ai_router = AIRouter()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        weather_query = f"What's the current weather in {location}" if location else "What's the current weather"
        result = loop.run_until_complete(ai_router.process_query(weather_query, "realtime"))
        
        if result['success']:
            speak(result['response'])
            return result['response']
        else:
            fallback = "I'm sorry, I couldn't get the weather information right now."
            speak(fallback)
            return fallback
            
    except Exception as e:
        print(f"❌ Weather error: {e}")
        fallback = "Weather service is currently unavailable."
        speak(fallback)
        return fallback

def system_control(command):
    """System control commands"""
    try:
        if "mute" in command:
            pyautogui.press('volumemute')
            speak("System muted")
        elif "unmute" in command:
            pyautogui.press('volumemute')
            speak("System unmuted")
        elif "volume up" in command:
            pyautogui.press('volumeup')
            speak("Volume increased")
        elif "volume down" in command:
            pyautogui.press('volumedown')
            speak("Volume decreased")
        elif "minimize all" in command:
            pyautogui.hotkey('win', 'd')
            speak("All windows minimized")
        elif "shutdown" in command:
            speak("Shutting down the system")
            os.system("shutdown /s /t 1")
        elif "restart" in command:
            speak("Restarting the system")
            os.system("shutdown /r /t 1")
        else:
            speak("System command not recognized")
            
    except Exception as e:
        speak("System control failed")
        print(f"❌ System control error: {e}")

def web_search(query, engine="google"):
    """Perform web search"""
    try:
        if engine.lower() == "youtube":
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        else:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
        speak(f"Searching for {query} on {engine}")
        webbrowser.open(search_url)
        
    except Exception as e:
        speak("Search failed")
        print(f"❌ Web search error: {e}")

# Export all functions for use by command processor
__all__ = [
    'playAssistantSound', 'openCommand', 'PlayYoutube', 'hotword',
    'findContact', 'whatsApp', 'chatBot', 'makeCall', 'sendMessage',
    'get_weather', 'system_control', 'web_search'
]