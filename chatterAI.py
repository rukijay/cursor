import os
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
from openai import OpenAI
from openai import RateLimitError, APIError
from tuneAI.system_prompt_recomend import recomend_prompt as rec_sp
from tuneAI.system_prompt_examprep import exam_prep_prompt as prep_sp
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

# Constants
GPT_MODEL = "gpt-4-0125-preview"
MAX_RETRIES = 3
RETRY_DELAY = 5
CHATLOG_DIR = "chatlog"

class ChatSession:
    def __init__(self, model: str = GPT_MODEL):
        self.history: List[Dict[str, str]] = []
        self.mode: Optional[str] = None
        self.initial_prompt_sent: bool = False
        self.log_file = os.path.join(CHATLOG_DIR, 'learning_log.json')
        self._ensure_chatlog_directory()
        self.is_exiting = False

    def _ensure_chatlog_directory(self):
        os.makedirs(CHATLOG_DIR, exist_ok=True)

    def _get_system_prompt(self) -> str:
        return prep_sp if self.mode == "exam_prep" else rec_sp

    def chat(self, user_input: str) -> str:
        if self.is_exiting:
            return "The session has already ended. Please start a new session if you wish to continue."

        # Check if user_input is a dictionary and extract the message
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
        mode = self._process_mode_selection(user_input)
        if mode:
            self.mode = mode
            response = (f"You selected {'Exam Preparation' if mode == 'exam_prep' else 'Learning Aids'}. "
                        f"How can I help you with your {'exam prep' if mode == 'exam_prep' else 'learning'}?")
        else:
            response = "Invalid selection. Please enter 1 for Exam Preparation or 2 for Learning Aids."
        self.history.append({"role": "assistant", "content": response})
        return response

    def _process_mode_selection(self, user_input: str) -> Optional[str]:
        return {"1": "exam_prep", "2": "learning_aids"}.get(user_input)

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
                ai_response = response.choices[0].message.content
                self._check_and_log_learnings(ai_response)
                return ai_response
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

    def _check_and_log_learnings(self, response: str):
        learnings_match = re.search(r'\[learn_start\](.*?)\[learn_end\]', response, re.DOTALL)
        if learnings_match:
            learnings = learnings_match.group(1).strip()
            self._log_learnings(learnings)

    def _log_learnings(self, learnings: str):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "learning": learnings
        }
        
        try:
            log_data = self._load_log_data()
            log_data.append(log_entry)
            self._save_log_data(log_data)
            print(f"Learning logged successfully to {self.log_file}")
        except Exception as e:
            print(f"Error logging learning: {str(e)}")

    def _load_log_data(self) -> List[Dict]:
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return []

    def _save_log_data(self, log_data: List[Dict]):
        with open(self.log_file, 'w') as f:
            json.dump(log_data, f, indent=2)

    def save_chat_history(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.json"
        filepath = os.path.join(CHATLOG_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
        
        print(f"Chat history saved to {filepath}")
        return filename

    def log_interaction(self, user_input: str, ai_response: str):
        with open(self.log_file, 'a') as f:
            f.write(f"User: {user_input}\n")
            f.write(f"AI: {ai_response}\n\n")

    def _handle_exit(self) -> str:
        self.is_exiting = True
        
        # Perform any necessary cleanup
        self._cleanup()

        # Generate a final response
        final_response = self._generate_final_response()

        # Log the exit
        self._log_exit()

        return final_response

    def _cleanup(self):
        # Perform any necessary cleanup tasks
        # For example, you might want to close any open resources or save any pending data
        print("Performing cleanup tasks...")
        # Add your cleanup logic here

    def _generate_final_response(self) -> str:
        # Generate a final response from the AI
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

    def _log_exit(self):
        # Log the exit event
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "Session ended"
        }
        
        try:
            log_data = self._load_log_data()
            log_data.append(log_entry)
            self._save_log_data(log_data)
            print(f"Exit logged successfully to {self.log_file}")
        except Exception as e:
            print(f"Error logging exit: {str(e)}")

if __name__ == "__main__":
    pass
