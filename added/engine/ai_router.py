import os
import requests
import json
import time
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import cohere
import groq
# New import for code analysis feature
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

load_dotenv()

class AIRouter:
    """Manages multiple AI backends with intelligent fallback system"""
    
    def __init__(self):
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama2:7b-chat')
        
        # Initialize API clients
        self.groq_client = None
        self.cohere_client = None
        # New OpenAI client for code analysis
        self.openai_client = None
        
        self._initialize_clients()
        self._test_connections()
    
    def _initialize_clients(self):
        """Initialize API clients with error handling"""
        try:
            groq_api_key = os.getenv('GroqAPI')
            if groq_api_key:
                self.groq_client = groq.Groq(api_key=groq_api_key)
                print("✅ Groq client initialized")
        except Exception as e:
            print(f"⚠️ Groq client initialization failed: {e}")
        
        try:
            cohere_api_key = os.getenv('CohereAPI')
            if cohere_api_key:
                self.cohere_client = cohere.Client(api_key=cohere_api_key)
                print("✅ Cohere client initialized")
        except Exception as e:
            print(f"⚠️ Cohere client initialization failed: {e}")
        
        # Initialize OpenAI client for code analysis
        try:
            if OPENAI_AVAILABLE:
                openai_api_key = os.getenv('OpenAI_API_KEY')
                if openai_api_key:
                    self.openai_client = openai.OpenAI(api_key=openai_api_key)
                    print("✅ OpenAI client initialized")
        except Exception as e:
            print(f"⚠️ OpenAI client initialization failed: {e}")
    
    def _test_connections(self):
        """Test all AI service connections"""
        print("🔍 Testing AI service connections...")
        
        # Test Ollama
        if self._test_ollama():
            print("✅ Ollama connection successful")
        else:
            print("⚠️ Ollama not available - install and run: ollama serve")
        
        # Test Groq
        if self._test_groq():
            print("✅ Groq API connection successful")
        else:
            print("⚠️ Groq API not available")
        
        # Test Cohere
        if self._test_cohere():
            print("✅ Cohere API connection successful")
        else:
            print("⚠️ Cohere API not available")
        
        # Test OpenAI
        if self._test_openai():
            print("✅ OpenAI API connection successful")
        else:
            print("⚠️ OpenAI API not available")
    
    def _test_ollama(self) -> bool:
        """Test Ollama connection"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _test_groq(self) -> bool:
        """Test Groq API connection"""
        try:
            if not self.groq_client:
                return False
            # Simple test query
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model="mixtral-8x7b-32768",
                max_tokens=1
            )
            return True
        except:
            return False
    
    def _test_cohere(self) -> bool:
        """Test Cohere API connection"""
        try:
            if not self.cohere_client:
                return False
            # Simple test query
            response = self.cohere_client.generate(
                model='command-r-plus',
                prompt='test',
                max_tokens=1
            )
            return True
        except:
            return False
    
    def _test_openai(self) -> bool:
        """Test OpenAI API connection"""
        try:
            if not self.openai_client or not OPENAI_AVAILABLE:
                return False
            # Simple test query
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except:
            return False
    
    async def process_query(self, query: str, query_type: str = "general") -> Dict[str, Any]:
        """Process query with intelligent AI routing"""
        start_time = time.time()
        
        try:
            # Try Cohere first (working API)
            result = await self._try_cohere(query, query_type)
            if result:
                result['processing_time'] = time.time() - start_time
                result['ai_model'] = "cohere-command-r"
                return result
            
            # Try Ollama second (local, fast, private)
            if query_type in ["general", "content", "code"]:
                result = await self._try_ollama(query, query_type)
                if result:
                    result['processing_time'] = time.time() - start_time
                    result['ai_model'] = f"ollama-{self.ollama_model}"
                    return result
            
            # Fallback to Groq (if API key gets fixed)
            result = await self._try_groq(query, query_type)
            if result:
                result['processing_time'] = time.time() - start_time
                result['ai_model'] = "groq-mixtral"
                return result
            
            # If all AI services fail, return offline response
            return {
                'response': "I'm sorry, all AI services are currently unavailable. Please check your internet connection and try again.",
                'success': False,
                'processing_time': time.time() - start_time,
                'ai_model': 'offline'
            }
            
        except Exception as e:
            print(f"❌ AI Router error: {e}")
            return {
                'response': f"An error occurred while processing your request: {str(e)}",
                'success': False,
                'processing_time': time.time() - start_time,
                'ai_model': 'error'
            }
    
    async def _try_ollama(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        """Try processing with Ollama"""
        try:
            system_prompt = self._get_system_prompt(query_type)
            
            payload = {
                "model": self.ollama_model,
                "prompt": f"{system_prompt}\n\nUser: {query}\nAssistant:",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2048
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'response': result.get('response', '').strip(),
                    'success': True
                }
            
        except Exception as e:
            print(f"Ollama error: {e}")
        
        return None
    
    async def _try_groq(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        """Try processing with Groq"""
        try:
            if not self.groq_client:
                return None
            
            system_prompt = self._get_system_prompt(query_type)
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                model="mixtral-8x7b-32768",
                max_tokens=2048,
                temperature=0.7
            )
            
            return {
                'response': response.choices[0].message.content.strip(),
                'success': True
            }
            
        except Exception as e:
            print(f"Groq error: {e}")
        
        return None
    
    async def _try_cohere(self, query: str, query_type: str) -> Optional[Dict[str, Any]]:
        """Try processing with Cohere"""
        try:
            if not self.cohere_client:
                return None
            
            system_prompt = self._get_system_prompt(query_type)
            full_prompt = f"{system_prompt}\n\nUser: {query}\nAssistant:"
            
            response = self.cohere_client.generate(
                model='command-r-plus',
                prompt=full_prompt,
                max_tokens=2048,
                temperature=0.7
            )
            
            return {
                'response': response.generations[0].text.strip(),
                'success': True
            }
            
        except Exception as e:
            print(f"Cohere error: {e}")
        
        return None
    
    def _get_system_prompt(self, query_type: str) -> str:
        """Get appropriate system prompt based on query type"""
        prompts = {
            "general": "You are JARVIS, a helpful AI assistant. Provide clear, concise, and accurate responses. Be friendly and professional.",
            
            "content": "You are JARVIS, an expert content writer. Create high-quality content including letters, essays, articles, and documents. Focus on clarity, structure, and engaging writing.",
            
            "code": "You are JARVIS, a programming assistant. Help with coding tasks, debugging, and technical explanations. Provide clean, well-commented code with explanations.",
            
            "realtime": "You are JARVIS, an AI assistant with access to current information. Provide up-to-date and accurate information based on the user's query.",
            
            "classification": "You are JARVIS, a command classifier. Analyze user input and determine the appropriate action or intent. Be precise and consistent in your classifications."
        }
        
        return prompts.get(query_type, prompts["general"])
    
    async def classify_intent(self, query: str) -> Dict[str, Any]:
        """Classify user intent for command routing"""
        classification_prompt = """
        You are a command classifier for JARVIS assistant. Analyze the user's input and classify it into one of these categories:

        1. "open [app/website]" - Opening applications or websites
        2. "close [app]" - Closing applications  
        3. "play [song/video]" - Playing media content
        4. "call [contact]" - Making phone calls
        5. "message [contact]" - Sending messages
        6. "whatsapp [contact]" - WhatsApp actions
        7. "system [command]" - System commands (volume, shutdown, etc.)
        8. "search [query]" - Web searches
        9. "general" - General conversation/questions
        10. "content [type]" - Content generation requests
        11. "help_with_code" - Code analysis and error detection
        12. "code_success" - Confirmation that code is working

        Respond with just the classification and any extracted parameters.
        Examples:
        - "open chrome" → "open chrome"
        - "call john" → "call john"  
        - "what's the weather" → "general"
        - "write a letter" → "content letter"
        - "jarvis help me with my code" → "help_with_code"
        - "check my code" → "help_with_code"
        - "thank you jarvis my code is running successfully now" → "code_success"
        """
        
        try:
            result = await self.process_query(
                f"{classification_prompt}\n\nClassify this: {query}",
                "classification"
            )
            
            if result['success']:
                classification = result['response'].lower().strip()
                return {
                    'intent': classification,
                    'success': True,
                    'confidence': 0.9  # Placeholder confidence score
                }
            
        except Exception as e:
            print(f"Intent classification error: {e}")
        
        # Default fallback
        return {
            'intent': 'general',
            'success': False,
            'confidence': 0.5
        }
    
    async def generate_content(self, content_type: str, topic: str, **kwargs) -> Dict[str, Any]:
        """Generate specific types of content"""
        content_prompts = {
            "letter": f"Write a professional letter about {topic}. Include proper formatting with date, salutation, body paragraphs, and closing.",
            "essay": f"Write a well-structured essay about {topic}. Include an introduction, body paragraphs with supporting arguments, and a conclusion.",
            "email": f"Write a professional email about {topic}. Keep it concise and clear.",
            "code": f"Write clean, well-commented code for {topic}. Include explanations and best practices.",
            "article": f"Write an informative article about {topic}. Make it engaging and well-researched.",
            "summary": f"Create a comprehensive summary of {topic}. Highlight key points and important details."
        }
        
        prompt = content_prompts.get(content_type, f"Create content about {topic}")
        
        # Add any additional parameters
        if kwargs.get('length'):
            prompt += f" Make it approximately {kwargs['length']} words."
        if kwargs.get('tone'):
            prompt += f" Use a {kwargs['tone']} tone."
        if kwargs.get('audience'):
            prompt += f" Target audience: {kwargs['audience']}."
        
        return await self.process_query(prompt, "content")
    
    async def analyze_code_with_openai(self, code_text: str) -> Dict[str, Any]:
        """Analyze code using OpenAI API and return 3-line mistake explanation"""
        try:
            if not self.openai_client or not OPENAI_AVAILABLE:
                return {
                    'success': False,
                    'mistakes': ["OpenAI API not available", "Please check your API key configuration", "Using fallback analysis instead"]
                }
            
            prompt = f"""Analyze this code and identify mistakes. Provide EXACTLY 3 lines explaining the errors:

{code_text}

Format your response as exactly 3 lines:
Line 1: [First mistake explanation]
Line 2: [Second mistake explanation] 
Line 3: [Third mistake explanation]

Keep each line concise and specific about the actual errors in the code."""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a code reviewer. Analyze code and explain mistakes in exactly 3 lines."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content.strip()
            
            # Split into exactly 3 lines
            lines = analysis.split('\n')
            mistakes = []
            for line in lines:
                if line.strip():
                    mistakes.append(line.strip())
                if len(mistakes) >= 3:
                    break
            
            # Ensure we have exactly 3 lines
            while len(mistakes) < 3:
                mistakes.append("No additional issues found")
            
            return {
                'success': True,
                'mistakes': mistakes[:3]  # Ensure exactly 3 lines
            }
            
        except Exception as e:
            print(f"❌ OpenAI code analysis error: {e}")
            return {
                'success': False,
                'mistakes': [
                    "Code analysis failed due to API error",
                    "Please check your internet connection and API key", 
                    "Try again or fix the code manually"
                ]
            }
    
    def get_service_status(self) -> Dict[str, bool]:
        """Get status of all AI services"""
        return {
            'ollama': self._test_ollama(),
            'groq': self._test_groq(),
            'cohere': self._test_cohere(),
            'openai': self._test_openai()
        }

# Test the AI Router
if __name__ == "__main__":
    import asyncio
    
    async def test_ai_router():
        router = AIRouter()
        
        # Test general query
        result = await router.process_query("Hello, how are you?", "general")
        print(f"General query result: {result}")
        
        # Test intent classification
        intent = await router.classify_intent("open chrome browser")
        print(f"Intent classification: {intent}")
        
        # Test content generation
        content = await router.generate_content("letter", "job application", tone="professional")
        print(f"Content generation: {content}")
        
        # Check service status
        status = router.get_service_status()
        print(f"Service status: {status}")
    
    asyncio.run(test_ai_router())