import os
from chatterAI import ChatSession

def chatbot():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("AI Chatbot: Hello! How can I assist you today? (Type 'quit' to exit)")
    
    chat_session = ChatSession()
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            break

        ai_response = chat_session.chat(user_input)
        print("AI:", ai_response)

    chat_session.save_chat_history()

if __name__ == "__main__":
    chatbot()
