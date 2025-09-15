#!/usr/bin/env python3
"""
JARVIS Web Interface Backend
Complete backend for website1 folder
"""

import os
import sys
import subprocess
import threading
import time
from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

# Add parent directory to path to import JARVIS
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, template_folder='.', static_folder='.')
app.config['SECRET_KEY'] = 'jarvis-website1-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
jarvis_process = None
jarvis_running = False

def run_jarvis():
    """Run the JARVIS script in a separate process"""
    global jarvis_process, jarvis_running
    
    try:
        # Path to the JARVIS script
        jarvis_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'final_jarvis.py')
        
        print(f"🤖 Starting JARVIS from: {jarvis_path}")
        
        # Start JARVIS process
        jarvis_process = subprocess.Popen(
            [sys.executable, jarvis_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        jarvis_running = True
        socketio.emit('jarvis_status', {'status': 'running', 'message': 'JARVIS is now online'})
        
        # Read output in real-time
        for line in iter(jarvis_process.stdout.readline, ''):
            if line:
                print(line.strip())
                # Check if JARVIS is speaking
                if any(keyword in line.lower() for keyword in ['speaking', 'saying', 'jarvis:', 'hello']):
                    socketio.emit('speaking_animation', {'active': True})
                    # Stop speaking animation after 3 seconds
                    threading.Timer(3.0, lambda: socketio.emit('speaking_animation', {'active': False})).start()
                
                # Check if user said stop
                if 'stop' in line.lower() and jarvis_running:
                    print("🛑 Stop command detected, terminating JARVIS...")
                    break
        
        jarvis_process.wait()
        
    except Exception as e:
        print(f"❌ Error running JARVIS: {e}")
        socketio.emit('jarvis_status', {'status': 'error', 'message': f'Error: {str(e)}'})
    finally:
        jarvis_running = False
        jarvis_process = None
        socketio.emit('jarvis_status', {'status': 'stopped', 'message': 'JARVIS has stopped'})
        print("🛑 JARVIS stopped")

@app.route('/')
def index():
    """Serve the main interface"""
    return render_template('index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve asset files"""
    return send_from_directory('assets', filename)

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print("🌐 Web client connected")
    emit('jarvis_status', {'status': 'stopped' if not jarvis_running else 'running', 'message': 'Connected to JARVIS Web Interface'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print("🌐 Web client disconnected")

@socketio.on('start_jarvis')
def handle_start_jarvis():
    """Start JARVIS"""
    global jarvis_running
    
    if not jarvis_running:
        print("🚀 Starting JARVIS...")
        emit('jarvis_status', {'status': 'starting', 'message': 'Starting JARVIS...'})
        
        # Start JARVIS in a separate thread
        jarvis_thread = threading.Thread(target=run_jarvis, daemon=True)
        jarvis_thread.start()
    else:
        emit('jarvis_status', {'status': 'running', 'message': 'JARVIS is already running!'})

@socketio.on('stop_jarvis')
def handle_stop_jarvis():
    """Stop JARVIS"""
    global jarvis_process, jarvis_running
    
    if jarvis_running and jarvis_process:
        print("🛑 Stopping JARVIS...")
        emit('jarvis_status', {'status': 'stopping', 'message': 'Stopping JARVIS...'})
        
        try:
            jarvis_process.terminate()
            jarvis_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            jarvis_process.kill()
        except Exception as e:
            print(f"Error stopping JARVIS: {e}")
        
        jarvis_running = False
        jarvis_process = None
        emit('jarvis_status', {'status': 'stopped', 'message': 'JARVIS has been stopped.'})
    else:
        emit('jarvis_status', {'status': 'stopped', 'message': 'JARVIS is not running!'})

@socketio.on('wake_jarvis')
def handle_wake_jarvis():
    """Wake JARVIS with voice command"""
    if not jarvis_running:
        handle_start_jarvis()

@app.route('/status')
def get_status():
    """Get JARVIS status"""
    return jsonify({
        'running': jarvis_running,
        'status': 'running' if jarvis_running else 'stopped'
    })

if __name__ == '__main__':
    print("🌐 Starting JARVIS Web Interface...")
    print("🔗 Open your browser and go to: http://localhost:3000")
    print("📱 Beautiful JARVIS interface with all animations")
    print("📺 All JARVIS output will appear in this terminal")
    print("🎤 Say 'stop' to JARVIS to stop it")
    print("=" * 50)
    
    try:
        socketio.run(app, host='0.0.0.0', port=3000, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down web interface...")
        if jarvis_process:
            jarvis_process.terminate()