import os
import json
import time
import random
from datetime import datetime
from typing import List, Dict, Optional
from openai import OpenAI
from openai import RateLimitError, APIError
from tuneAI.system_prompt_recomend import recomend_prompt as rec_sp
from tuneAI.system_prompt_examprep import exam_prep_prompt as prep_sp
from dotenv import load_dotenv

# Load environment variables and initialize OpenAI client
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Constants
GPT_MODEL = "gpt-4o-mini"
CHATLOG_DIR = "chatlog"

class ChatSession:
    def __init__(self, model: str = GPT_MODEL):
        self.history: List[Dict[str, str]] = []
        self.mode: Optional[str] = None
        self.initial_prompt_sent: bool = False
        self._ensure_chatlog_directory()
        self.is_exiting = False

    def _ensure_chatlog_directory(self):
        os.makedirs(CHATLOG_DIR, exist_ok=True)

    def _get_system_prompt(self) -> str:
        return prep_sp if self.mode == "exam_prep" else rec_sp

    def chat(self, user_input: str) -> str:
        if self.is_exiting:
            return "The session has already ended. Please start a new session if you wish to continue."

        if isinstance(user_input, dict):
            user_input = user_input.get('message', '')

        if user_input.lower() == "exit":
            return self._handle_exit()

        if not self.initial_prompt_sent:
            return self._handle_initial_prompt()

        if self.mode is None:
            return self._handle_mode_selection(user_input)

        ai_response = self._get_ai_response(user_input)
        self._update_history(user_input, ai_response)
        return ai_response

    def _handle_initial_prompt(self) -> str:
        initial_prompt = "Hi, I'm your AI assistant. Please enter:\n1   for Exam Preparation\n2   for Learning Aids"
        self.history.append({"role": "assistant", "content": initial_prompt})
        self.initial_prompt_sent = True
        return initial_prompt

    def _handle_mode_selection(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})
        mode = {"1": "exam_prep", "2": "learning_aids"}.get(user_input)
        
        if mode:
            self.mode = mode
            response = (f"You selected {'Exam Preparation' if mode == 'exam_prep' else 'Learning Aids'}. "
                       f"How can I help you with your {'exam prep' if mode == 'exam_prep' else 'learning'}?")
        else:
            response = "Invalid selection. Please enter 1 for Exam Preparation or 2 for Learning Aids."
            
        self.history.append({"role": "assistant", "content": response})
        return response

    def _get_ai_response(self, user_input: str) -> str:
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            *self.history,
            {"role": "user", "content": user_input}
        ]
        
        max_retries = 5
        base_delay = 1

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=GPT_MODEL,
                    messages=messages,
                    max_tokens=400
                )
                return response.choices[0].message.content
            except RateLimitError:
                if attempt < max_retries - 1:
                    delay = (base_delay * 2 ** attempt) + (random.randint(0, 1000) / 1000.0)
                    print(f"Rate limit reached. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    return "I'm sorry, but I'm currently experiencing high traffic. Please try again later."
            except APIError as e:
                if attempt < max_retries - 1:
                    delay = (base_delay * 2 ** attempt) + (random.randint(0, 1000) / 1000.0)
                    print(f"API error occurred. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    return f"An API error occurred: {str(e)}"
            except Exception as e:
                return f"An unexpected error occurred: {str(e)}"

    def _update_history(self, user_input: str, ai_response: str):
        self.history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": ai_response}
        ])

    def save_chat_history(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.json"
        filepath = os.path.join(CHATLOG_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
        
        print(f"Chat history saved to {filepath}")
        return filename

    def _handle_exit(self) -> str:
        self.is_exiting = True
        messages = [
            {"role": "system", "content": "The user is ending the session. Please provide a brief, friendly closing message."},
            *self.history,
            {"role": "user", "content": "exit"}
        ]
        
        try:
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=messages,
                max_tokens=100
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Thank you for using the AI assistant. The session has ended. (Error: {str(e)})"

if __name__ == "__main__":
    pass
