from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from chatterAI import get_ai_response, AIChatHistory
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # This allows CORS for all domains on all routes

chat_history = AIChatHistory()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data['message']
    
    # Add user message to history
    chat_history.add_message("user", user_message)
    
    # Get AI response
    ai_response = get_ai_response(user_message, chat_history.get_history())
    
    # Add AI response to history
    chat_history.add_message("assistant", ai_response)
    
    return jsonify({'response': ai_response})

@app.route('/save_chatlog', methods=['POST'])
def save_chatlog():
    data = request.json
    messages = data.get('messages', [])
    
    # Ensure the chatlog directory exists
    chatlog_dir = os.path.join(os.path.dirname(__file__), 'chatlog')
    os.makedirs(chatlog_dir, exist_ok=True)
    
    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chatlog_{timestamp}.json"
    
    # Full path for the file
    file_path = os.path.join(chatlog_dir, filename)
    
    # Save the chat log
    with open(file_path, 'w') as f:
        json.dump(messages, f, indent=2)
    
    return jsonify({'filename': filename})

if __name__ == '__main__':
    app.run(debug=True)
