#!/usr/bin/env python3
"""
Screen Analyzer Module for JARVIS
Takes screenshots and describes them using OpenAI GPT Vision
"""

import os
import base64
import pyautogui
from PIL import Image
import io
import openai
from typing import Optional
from engine.command import speak

class ScreenAnalyzer:
    """Screen analysis functionality using OpenAI Vision"""
    
    def __init__(self):
        # Set OpenAI API key
       OPEN AI KEY
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Screenshot settings
        self.screenshot_path = "temp_screenshot.png"
    
    def take_screenshot(self) -> Optional[str]:
        """Take a screenshot and save it"""
        try:
            print("📸 Taking screenshot...")
            screenshot = pyautogui.screenshot()
            
            # Resize if too large (to reduce API costs)
            max_size = (1024, 768)
            screenshot.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save screenshot
            screenshot.save(self.screenshot_path, "PNG")
            print(f"✅ Screenshot saved: {self.screenshot_path}")
            return self.screenshot_path
            
        except Exception as e:
            print(f"❌ Error taking screenshot: {e}")
            return None
    
    def encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """Encode image to base64 for OpenAI API"""
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
        except Exception as e:
            print(f"❌ Error encoding image: {e}")
            return None
    
    def analyze_screen_with_gpt(self, image_path: str) -> Optional[str]:
        """Send screenshot to GPT-4 Vision for analysis"""
        try:
            print("🤖 Analyzing screen with GPT-4 Vision...")
            
            # Encode image
            base64_image = self.encode_image_to_base64(image_path)
            if not base64_image:
                return None
            
            # Create the prompt for detailed description
            prompt = """Please describe what you see on this screen in 8-10 clear, detailed sentences. 
            Focus on the main elements, applications, content, and what the user appears to be doing. 
            Include details about windows, text, buttons, menus, and any visible content.
            Keep each sentence under 20 words. Be specific and helpful."""
            
            # Make API call
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using the more cost-effective vision model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "low"  # Lower detail for faster/cheaper processing
                                }
                            }
                        ]
                    }
                ],
                max_tokens=400,  # Increased tokens for detailed response
                temperature=0.3  # Lower temperature for more consistent responses
            )
            
            description = response.choices[0].message.content.strip()
            print(f"✅ GPT Analysis: {description}")
            return description
            
        except Exception as e:
            print(f"❌ Error analyzing with GPT: {e}")
            return None
    
    def cleanup_screenshot(self):
        """Remove temporary screenshot file"""
        try:
            if os.path.exists(self.screenshot_path):
                os.remove(self.screenshot_path)
                print("🗑️ Cleaned up screenshot file")
        except Exception as e:
            print(f"⚠️ Could not cleanup screenshot: {e}")
    
    def describe_screen(self) -> bool:
        """Main method to take screenshot and describe it in 8-10 lines"""
        try:
            speak("Taking a screenshot of your screen")
            
            # Take screenshot
            screenshot_path = self.take_screenshot()
            if not screenshot_path:
                speak("Sorry, I couldn't take a screenshot")
                return False
            
            speak("Analyzing your screen with artificial intelligence")
            
            # Analyze with GPT
            description = self.analyze_screen_with_gpt(screenshot_path)
            
            # Cleanup
            self.cleanup_screenshot()
            
            if description:
                print(f"\n📋 Screen Description:\n{description}")
                speak("Here's what I see on your screen:")
                speak(description)
                return True
            else:
                speak("Sorry, I couldn't analyze your screen at the moment")
                return False
                
        except Exception as e:
            print(f"❌ Error describing screen: {e}")
            speak("I encountered an error while analyzing your screen")
            self.cleanup_screenshot()
            return False
    
    def get_screen_text_description(self) -> Optional[str]:
        """Get screen description as text without speaking"""
        try:
            screenshot_path = self.take_screenshot()
            if not screenshot_path:
                return None
            
            description = self.analyze_screen_with_gpt(screenshot_path)
            self.cleanup_screenshot()
            
            return description
            
        except Exception as e:
            print(f"❌ Error getting screen description: {e}")
            self.cleanup_screenshot()
            return None
