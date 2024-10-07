from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from chatterAI import get_ai_response, AIChatHistory

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

if __name__ == '__main__':
    app.run(debug=True)
