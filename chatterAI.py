import os
import json
import time
import openai
from openai import OpenAI
from datetime import datetime  # Change this line
from typing import List, Dict
# from tuneAI.system_prompt_examprep import exam_prep_prompt as sp
from tuneAI.system_prompt_recomend import recomend_prompt as sp

# Constants
GPT_MODEL = "gpt-4-0125-preview"
JSON_FILE_PATH = 'toc.json'
MAX_RETRIES = 3
RETRY_DELAY = 5

client = OpenAI()

class ChatSession:
    def __init__(self):
        self.history = []

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        return self.history

    def chat(self, user_input: str) -> str:
        self.add_message("user", user_input)
        ai_response = self._get_ai_response(user_input)
        self.add_message("assistant", ai_response)
        return ai_response

    def _get_ai_response(self, prompt: str) -> str:
        for attempt in range(MAX_RETRIES):
            try:
                messages = [
                    {"role": "system", "content": sp},
                    *self.history,
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

    def save_chat_history(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chatlog_dir = "chatlog"
        os.makedirs(chatlog_dir, exist_ok=True)
        filename = f"chat_history_{timestamp}.json"
        filepath = os.path.join(chatlog_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
        
        print(f"Chat history saved to {filepath}")
        return filename

def load_toc():
    if os.path.exists(JSON_FILE_PATH) and os.path.getsize(JSON_FILE_PATH) > 0:
        with open(JSON_FILE_PATH, 'r') as f:
            return json.load(f)
    print(f"Error: The file {JSON_FILE_PATH} is either missing or empty.")
    return None

if __name__ == "__main__":
    TOC = load_toc()
