from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from chatterAI import ChatSession
import re
from html import escape

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
    
    # Check if the user clicked the [exit and done] button
    if user_message == "[exit and done]":
        # Impersonate the user to send "exit" to the LLM
        ai_response = chat_session.chat("exit")
    else:
        # Normal chat flow
        ai_response = chat_session.chat(user_message)
    
    processed_response = process_response(ai_response)
    return jsonify({'response': processed_response})

def process_response(response):
    # Escape HTML characters first
    response = escape(response)
    
    # Convert Markdown bold (double asterisks) to HTML bold
    response = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', response)
    
    # Convert Markdown links to HTML
    response = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', response)
    
    # Convert plain URLs to clickable links, but avoid already processed links
    response = re.sub(r'(?<!href=")(https?://[^\s<>]+)(?![^<>]*>)', r'<a href="\1" target="_blank">\1</a>', response)
    
    # Convert Markdown headers to HTML
    response = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', response, flags=re.MULTILINE)
    
    # Convert Markdown list items to HTML
    response = re.sub(r'^\s*-\s+(.+)$', r'<li>\1</li>', response, flags=re.MULTILINE)
    response = '<ul>' + response + '</ul>'
    
    return response

@app.route('/save_chatlog', methods=['POST'])
def save_chatlog():
    filename = chat_session.save_chat_history()
    return jsonify({'filename': filename})

if __name__ == '__main__':
    app.run(debug=True)
