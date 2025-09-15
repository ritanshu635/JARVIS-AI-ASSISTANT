// JARVIS Unified Interface JavaScript

class JarvisInterface {
    constructor() {
        this.isListening = false;
        this.isProcessing = false;
        this.chatHistory = [];
        this.settings = {
            assistantName: 'Jarvis',
            voiceRate: 174,
            wakeWordEnabled: false
        };
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSettings();
        this.startInitialization();
    }

    bindEvents() {
        // Input events
        document.getElementById('textInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('micBtn').addEventListener('click', () => {
            this.toggleVoiceInput();
        });

        // Navigation events
        document.getElementById('settingsBtn').addEventListener('click', () => {
            this.openSettings();
        });

        document.getElementById('chatHistoryBtn').addEventListener('click', () => {
            this.toggleChatHistory();
        });

        document.getElementById('closeChatBtn').addEventListener('click', () => {
            this.toggleChatHistory();
        });

        // Auth events
        document.getElementById('skipAuth').addEventListener('click', () => {
            this.skipAuthentication();
        });

        // Settings events
        document.getElementById('saveSettings').addEventListener('click', () => {
            this.saveSettings();
        });

        document.getElementById('voiceRate').addEventListener('input', (e) => {
            document.getElementById('voiceRateValue').textContent = e.target.value;
        });

        // JARVIS core click
        document.getElementById('jarvisCore').addEventListener('click', () => {
            this.activateJarvis();
        });
    }

    async startInitialization() {
        this.updateStatus('Initializing JARVIS systems...');
        
        try {
            // Simulate initialization delay
            await this.delay(2000);
            
            // Check if Eel is available
            if (typeof eel !== 'undefined') {
                // Initialize backend connection
                await this.initializeBackend();
            } else {
                console.warn('Eel not available, running in demo mode');
            }
            
            this.hideLoadingScreen();
            this.showFaceAuth();
            
        } catch (error) {
            console.error('Initialization error:', error);
            this.hideLoadingScreen();
            this.showMainInterface();
        }
    }

    async initializeBackend() {
        try {
            // Test backend connection
            if (eel.test_connection) {
                await eel.test_connection()();
            }
            
            // Load chat history
            if (eel.get_chat_history) {
                this.chatHistory = await eel.get_chat_history()() || [];
            }
            
            // Check AI service status
            if (eel.get_ai_status) {
                const status = await eel.get_ai_status()();
                this.updateAIStatus(status);
            }
            
        } catch (error) {
            console.error('Backend initialization error:', error);
        }
    }

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        loadingScreen.style.opacity = '0';
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 500);
    }

    showFaceAuth() {
        const faceAuthScreen = document.getElementById('faceAuthScreen');
        faceAuthScreen.style.display = 'flex';
        faceAuthScreen.classList.add('fade-in');
        
        // Auto-skip after 5 seconds if no face auth
        setTimeout(() => {
            if (faceAuthScreen.style.display !== 'none') {
                this.skipAuthentication();
            }
        }, 5000);
    }

    skipAuthentication() {
        const faceAuthScreen = document.getElementById('faceAuthScreen');
        faceAuthScreen.style.display = 'none';
        this.showMainInterface();
    }

    showMainInterface() {
        const mainInterface = document.getElementById('mainInterface');
        mainInterface.style.display = 'flex';
        mainInterface.classList.add('fade-in');
        
        this.updateStatus('Ready');
        this.speak(`Hello ${this.settings.assistantName} is ready. How can I help you?`);
    }

    updateStatus(status) {
        const statusElement = document.getElementById('statusDisplay').querySelector('.status-text');
        statusElement.textContent = status;
        
        // Remove all status classes
        statusElement.classList.remove('listening', 'thinking', 'speaking');
        
        // Add appropriate class based on status
        if (status.toLowerCase().includes('listening')) {
            statusElement.classList.add('listening');
        } else if (status.toLowerCase().includes('thinking') || status.toLowerCase().includes('processing')) {
            statusElement.classList.add('thinking');
        } else if (status.toLowerCase().includes('speaking')) {
            statusElement.classList.add('speaking');
        }
    }

    async sendMessage() {
        const input = document.getElementById('textInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        input.value = '';
        this.addChatMessage('user', message);
        this.updateStatus('Processing...');
        this.isProcessing = true;
        
        try {
            let response;
            
            if (typeof eel !== 'undefined' && eel.process_command) {
                // Send to backend
                response = await eel.process_command(message)();
            } else {
                // Demo mode response
                response = await this.getDemoResponse(message);
            }
            
            this.addChatMessage('assistant', response);
            this.showResponse(response);
            this.speak(response);
            
        } catch (error) {
            console.error('Message processing error:', error);
            const errorMsg = 'Sorry, I encountered an error processing your request.';
            this.addChatMessage('assistant', errorMsg);
            this.showResponse(errorMsg);
            this.speak(errorMsg);
        } finally {
            this.isProcessing = false;
            this.updateStatus('Ready');
        }
    }

    async getDemoResponse(message) {
        // Simulate processing delay
        await this.delay(1000);
        
        const lowerMessage = message.toLowerCase();
        
        if (lowerMessage.includes('time')) {
            return `The current time is ${new Date().toLocaleTimeString()}.`;
        } else if (lowerMessage.includes('date')) {
            return `Today is ${new Date().toLocaleDateString()}.`;
        } else if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
            return 'Hello! I am JARVIS, your AI assistant. How can I help you today?';
        } else if (lowerMessage.includes('what can you do')) {
            return 'I can help you with various tasks like opening applications, playing music, making calls, sending messages, answering questions, and much more. Just ask me!';
        } else if (lowerMessage.includes('open')) {
            const app = lowerMessage.replace('open', '').trim();
            return `I would open ${app} for you, but I'm currently in demo mode. Please connect to the backend for full functionality.`;
        } else {
            return 'I understand your request. In demo mode, I have limited functionality. Please connect to the full JARVIS backend for complete features.';
        }
    }

    toggleVoiceInput() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    async startListening() {
        this.isListening = true;
        const micBtn = document.getElementById('micBtn');
        micBtn.classList.add('recording');
        micBtn.innerHTML = '<i class="bi bi-mic-fill"></i>';
        
        this.updateStatus('Listening...');
        this.showVoiceVisualization();
        
        try {
            if (typeof eel !== 'undefined' && eel.start_voice_input) {
                const result = await eel.start_voice_input()();
                if (result && result.text) {
                    document.getElementById('textInput').value = result.text;
                    this.sendMessage();
                }
            } else {
                // Demo mode - simulate voice input
                await this.delay(3000);
                this.updateStatus('Voice input not available in demo mode');
            }
        } catch (error) {
            console.error('Voice input error:', error);
            this.updateStatus('Voice input failed');
        } finally {
            this.stopListening();
        }
    }

    stopListening() {
        this.isListening = false;
        const micBtn = document.getElementById('micBtn');
        micBtn.classList.remove('recording');
        micBtn.innerHTML = '<i class="bi bi-mic"></i>';
        
        this.hideVoiceVisualization();
        if (!this.isProcessing) {
            this.updateStatus('Ready');
        }
    }

    showVoiceVisualization() {
        document.getElementById('voiceVisualization').style.display = 'block';
    }

    hideVoiceVisualization() {
        document.getElementById('voiceVisualization').style.display = 'none';
    }

    showResponse(text) {
        const responseDisplay = document.getElementById('responseDisplay');
        const responseText = responseDisplay.querySelector('.response-text');
        
        responseText.textContent = text;
        responseDisplay.style.display = 'block';
        responseDisplay.classList.add('fade-in');
        
        // Hide after 5 seconds
        setTimeout(() => {
            responseDisplay.style.display = 'none';
            responseDisplay.classList.remove('fade-in');
        }, 5000);
    }

    async speak(text) {
        this.updateStatus('Speaking...');
        
        try {
            if (typeof eel !== 'undefined' && eel.speak_text) {
                await eel.speak_text(text)();
            } else {
                // Demo mode - simulate speaking
                console.log('Speaking:', text);
                await this.delay(text.length * 50); // Simulate speaking time
            }
        } catch (error) {
            console.error('Speech error:', error);
        } finally {
            if (!this.isProcessing) {
                this.updateStatus('Ready');
            }
        }
    }

    addChatMessage(sender, message) {
        const chatMessage = {
            sender,
            message,
            timestamp: new Date().toISOString()
        };
        
        this.chatHistory.push(chatMessage);
        this.updateChatHistory();
        
        // Save to backend if available
        if (typeof eel !== 'undefined' && eel.save_chat_message) {
            eel.save_chat_message(sender, message)();
        }
    }

    updateChatHistory() {
        const chatHistoryElement = document.getElementById('chatHistory');
        chatHistoryElement.innerHTML = '';
        
        this.chatHistory.slice(-20).forEach(msg => {
            const messageElement = document.createElement('div');
            messageElement.className = `chat-message ${msg.sender}`;
            messageElement.innerHTML = `
                <div class="message-content">${msg.message}</div>
                <div class="message-time">${new Date(msg.timestamp).toLocaleTimeString()}</div>
            `;
            chatHistoryElement.appendChild(messageElement);
        });
        
        // Scroll to bottom
        chatHistoryElement.scrollTop = chatHistoryElement.scrollHeight;
    }

    toggleChatHistory() {
        const sidebar = document.getElementById('chatSidebar');
        sidebar.classList.toggle('open');
    }

    openSettings() {
        const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
        modal.show();
        
        // Update AI service status
        this.checkAIServices();
    }

    async checkAIServices() {
        const cohereStatus = document.getElementById('cohereStatus');
        const ollamaStatus = document.getElementById('ollamaStatus');
        
        cohereStatus.textContent = 'Checking...';
        ollamaStatus.textContent = 'Checking...';
        
        try {
            if (typeof eel !== 'undefined' && eel.get_ai_status) {
                const status = await eel.get_ai_status()();
                this.updateAIStatus(status);
            } else {
                // Demo mode
                cohereStatus.textContent = 'Demo Mode';
                cohereStatus.className = 'status-indicator checking';
                ollamaStatus.textContent = 'Demo Mode';
                ollamaStatus.className = 'status-indicator checking';
            }
        } catch (error) {
            console.error('AI status check error:', error);
            cohereStatus.textContent = 'Error';
            cohereStatus.className = 'status-indicator offline';
            ollamaStatus.textContent = 'Error';
            ollamaStatus.className = 'status-indicator offline';
        }
    }

    updateAIStatus(status) {
        const cohereStatus = document.getElementById('cohereStatus');
        const ollamaStatus = document.getElementById('ollamaStatus');
        
        if (status.cohere) {
            cohereStatus.textContent = 'Online';
            cohereStatus.className = 'status-indicator online';
        } else {
            cohereStatus.textContent = 'Offline';
            cohereStatus.className = 'status-indicator offline';
        }
        
        if (status.ollama) {
            ollamaStatus.textContent = 'Online';
            ollamaStatus.className = 'status-indicator online';
        } else {
            ollamaStatus.textContent = 'Offline';
            ollamaStatus.className = 'status-indicator offline';
        }
    }

    loadSettings() {
        const saved = localStorage.getItem('jarvisSettings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
        }
        
        // Apply settings to UI
        document.getElementById('assistantName').value = this.settings.assistantName;
        document.getElementById('voiceRate').value = this.settings.voiceRate;
        document.getElementById('voiceRateValue').textContent = this.settings.voiceRate;
        document.getElementById('wakeWordEnabled').checked = this.settings.wakeWordEnabled;
    }

    saveSettings() {
        this.settings.assistantName = document.getElementById('assistantName').value;
        this.settings.voiceRate = parseInt(document.getElementById('voiceRate').value);
        this.settings.wakeWordEnabled = document.getElementById('wakeWordEnabled').checked;
        
        localStorage.setItem('jarvisSettings', JSON.stringify(this.settings));
        
        // Send to backend if available
        if (typeof eel !== 'undefined' && eel.update_settings) {
            eel.update_settings(this.settings)();
        }
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
        modal.hide();
        
        this.showResponse('Settings saved successfully!');
    }

    activateJarvis() {
        if (!this.isProcessing && !this.isListening) {
            this.startListening();
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Quick command function
function sendQuickCommand(command) {
    document.getElementById('textInput').value = command;
    jarvisInterface.sendMessage();
}

// Initialize JARVIS Interface when page loads
let jarvisInterface;
document.addEventListener('DOMContentLoaded', () => {
    jarvisInterface = new JarvisInterface();
});

// Expose functions for Eel callbacks
window.updateStatus = (status) => {
    if (jarvisInterface) {
        jarvisInterface.updateStatus(status);
    }
};

window.addChatMessage = (sender, message) => {
    if (jarvisInterface) {
        jarvisInterface.addChatMessage(sender, message);
    }
};

window.showResponse = (text) => {
    if (jarvisInterface) {
        jarvisInterface.showResponse(text);
    }
};