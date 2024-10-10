from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from chatterAI import ChatSession

app = Flask(__name__)
CORS(app)

chat_session = ChatSession()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    ai_response = chat_session.chat(user_message)
    return jsonify({'response': ai_response})

@app.route('/save_chatlog', methods=['POST'])
def save_chatlog():
    filename = chat_session.save_chat_history()
    return jsonify({'filename': filename})

if __name__ == '__main__':
    app.run(debug=True)
