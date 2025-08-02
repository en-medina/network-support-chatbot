from agents.networksupportchatbot import NetworkSupportChatbot
from os import getenv

if __name__ == "__main__":
    chatbot = NetworkSupportChatbot()
    debug_mode = getenv("DEBUG", "False").lower() == "true"
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = chatbot.process_question(user_input, debug=debug_mode)
        print(f"Bot: {response}")
