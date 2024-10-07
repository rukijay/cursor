import os
import json
from system_prompt import system_prompt as sp  # or use a different alias if needed

from openai import OpenAI

client = OpenAI()

# Load TOC from a separate file
json_file_path = 'toc.json'
if os.path.exists(json_file_path) and os.path.getsize(json_file_path) > 0:
    with open(json_file_path, 'r') as f:
        TOC = json.load(f)
else:
    print(f"Error: The file {json_file_path} is either missing or empty.")
    # Handle the error appropriately

import time
import openai
from openai import OpenAI


client = OpenAI()

from typing import List, Dict

class AIChatHistory:
    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        return self.messages

# Create an instance of AIChatHistory
chat_history = AIChatHistory()

def get_ai_response(prompt, conversation_history, max_retries=3, retry_delay=5):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": sp},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except openai.RateLimitError:
            if attempt < max_retries - 1:
                print(f"Rate limit reached. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                return "I'm sorry, but I'm currently experiencing high traffic. Please try again later."
        except openai.APIError as e:
            if attempt < max_retries - 1:
                print(f"API error occurred. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                return f"An API error occurred: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

def chatbot():
    # Clear the screen before starting the conversation
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("AI Chatbot: Hello! How can I assist you today? (Type 'quit' to exit)")
    
    conversation_history = []
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            break

        # Add user message to history
        chat_history.add_message("user", user_input)

        # Prepare the messages for the API call
        messages = [
            {"role": "system", "content": sp},
            *chat_history.get_history()
        ]

        # Make the API call with the updated messages
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        ai_response = response.choices[0].message.content

        # Add AI response to history
        chat_history.add_message("assistant", ai_response)

        print("AI:", ai_response)

if __name__ == "__main__":
    chatbot()
