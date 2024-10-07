from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from chatterAI import get_ai_response, AIChatHistory
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

chat_history = AIChatHistory()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    chat_history.add_message("user", user_message)
    
    ai_response = get_ai_response(user_message, chat_history.get_history())
    chat_history.add_message("assistant", ai_response)
    
    return jsonify({'response': ai_response})

@app.route('/save_chatlog', methods=['POST'])
def save_chatlog():
    messages = request.json.get('messages', [])
    
    chatlog_dir = os.path.join(os.path.dirname(__file__), 'chatlog')
    os.makedirs(chatlog_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chatlog_{timestamp}.json"
    file_path = os.path.join(chatlog_dir, filename)
    
    with open(file_path, 'w') as f:
        json.dump(messages, f, indent=2)
    
    return jsonify({'filename': filename})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
