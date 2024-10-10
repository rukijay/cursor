import os
from chatterAI import AIChatHistory, get_ai_response, log_chat_history

def chatbot():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("AI Chatbot: Hello! How can I assist you today? (Type 'quit' to exit)")
    
    chat_history = AIChatHistory()
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            break

        chat_history.add_message("user", user_input)
        ai_response = get_ai_response(user_input, chat_history.get_history())
        chat_history.add_message("assistant", ai_response)
        print("AI:", ai_response)

    log_chat_history(chat_history.get_history())

if __name__ == "__main__":
    chatbot()
