import os
import json
import time
import openai
from openai import OpenAI
from datetime import datetime  # Change this line
from typing import List, Dict
from system_prompt import system_prompt as sp

# Constants
GPT_MODEL = "gpt-4-0125-preview"
JSON_FILE_PATH = 'toc.json'
MAX_RETRIES = 3
RETRY_DELAY = 5

client = OpenAI()

class AIChatHistory:
    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        return self.messages

def load_toc():
    if os.path.exists(JSON_FILE_PATH) and os.path.getsize(JSON_FILE_PATH) > 0:
        with open(JSON_FILE_PATH, 'r') as f:
            return json.load(f)
    print(f"Error: The file {JSON_FILE_PATH} is either missing or empty.")
    return None

def get_ai_response(prompt, conversation_history):
    for attempt in range(MAX_RETRIES):
        try:
            messages = [
                {"role": "system", "content": sp},
                *conversation_history,
                {"role": "user", "content": prompt}
            ]
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=messages
            )
            return response.choices[0].message.content
        except openai.RateLimitError:
            if attempt < MAX_RETRIES - 1:
                print(f"Rate limit reached. Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                return "I'm sorry, but I'm currently experiencing high traffic. Please try again later."
        except openai.APIError as e:
            if attempt < MAX_RETRIES - 1:
                print(f"API error occurred. Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                return f"An API error occurred: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

def log_chat_history(chat_history):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create the chatlog directory if it doesn't exist
    chatlog_dir = "chatlog"
    os.makedirs(chatlog_dir, exist_ok=True)
    
    filename = f"chat_history_{timestamp}.json"
    filepath = os.path.join(chatlog_dir, filename)
    
    # Convert chat history to a list of dictionaries if it's not already
    chat_log = []
    for entry in chat_history:
        if isinstance(entry, dict):
            chat_log.append(entry)
        else:
            chat_log.append({
                "role": entry.role if hasattr(entry, 'role') else str(type(entry)),
                "content": entry.content if hasattr(entry, 'content') else str(entry)
            })
    
    # Write the chat log to a JSON file in the chatlog folder
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(chat_log, f, ensure_ascii=False, indent=2)
    
    print(f"Chat history saved to {filepath}")

if __name__ == "__main__":
    TOC = load_toc()
