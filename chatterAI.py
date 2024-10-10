import os
import json
import time
from datetime import datetime
from typing import List, Dict
from openai import OpenAI
from tuneAI.system_prompt_recomend import recomend_prompt as rec_sp
from tuneAI.system_prompt_examprep import exam_prep_prompt as prep_sp

# Constants
GPT_MODEL = "gpt-4-0125-preview"
MAX_RETRIES = 3
RETRY_DELAY = 5

client = OpenAI()

class ChatSession:
    def __init__(self):
        self.history: List[Dict[str, str]] = []
        self.mode: str = None
        self.initial_prompt_sent: bool = False

    def _get_system_prompt(self) -> str:
        return prep_sp if self.mode == "exam_prep" else rec_sp

    def chat(self, user_input: str) -> str:
        if not self.initial_prompt_sent:
            initial_prompt = "Hi, I'm your AI assistant. Please enter:\n1 for Exam Preparation\n2 for Learning Aids"
            self.history.append({"role": "assistant", "content": initial_prompt})
            self.initial_prompt_sent = True
            return initial_prompt

        if self.mode is None:
            self.history.append({"role": "user", "content": user_input})
            mode = self._process_mode_selection(user_input)
            if mode:
                self.mode = mode
                response = (f"You selected {'Exam Preparation' if mode == 'exam_prep' else 'Learning Aids'}. "
                            f"How can I help you with your {'exam prep' if mode == 'exam_prep' else 'learning'}?")
                self.history.append({"role": "assistant", "content": response})
                return response
            else:
                response = "Invalid selection. Please enter 1 for Exam Preparation or 2 for Learning Aids."
                self.history.append({"role": "assistant", "content": response})
                return response

        ai_response = self._get_ai_response(user_input)
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": ai_response})
        return ai_response

    def _process_mode_selection(self, user_input: str) -> str:
        if user_input == "1":
            return "exam_prep"
        elif user_input == "2":
            return "learning_aids"
        else:
            return None

    def _get_ai_response(self, user_input: str) -> str:
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            *self.history,
            {"role": "user", "content": user_input}
        ]
        
        for attempt in range(MAX_RETRIES):
            try:
                response = client.chat.completions.create(
                    model=GPT_MODEL,
                    messages=messages,
                    max_tokens=200  # Limit the response to approximately 200 tokens
                )
                return response.choices[0].message.content
            except OpenAI.RateLimitError:
                if attempt < MAX_RETRIES - 1:
                    print(f"Rate limit reached. Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    return "I'm sorry, but I'm currently experiencing high traffic. Please try again later."
            except OpenAI.APIError as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"API error occurred. Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    return f"An API error occurred: {str(e)}"
            except Exception as e:
                return f"An unexpected error occurred: {str(e)}"

    def save_chat_history(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chatlog_dir = "chatlog"
        os.makedirs(chatlog_dir, exist_ok=True)
        filename = f"chat_history_{timestamp}.json"
        filepath = os.path.join(chatlog_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
        
        print(f"Chat history saved to {filepath}")
        return filename

if __name__ == "__main__":
    pass
