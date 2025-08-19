from agents.networksupportchatbot import NetworkSupportChatbot
from tools.telegram import send_message
import json
import settings

def local_handler():
    chatbot = NetworkSupportChatbot()
    debug_mode = settings.DEBUG_MODE
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = chatbot.process_question(user_input, debug=debug_mode)
        print(f"Bot: {response}")

def lambda_handler(event, context):
    chatbot = NetworkSupportChatbot()
    debug_mode = settings.DEBUG_MODE
    token = settings.TELEGRAM_KEY
    for message in event['Records']:        
        try:
            print(f"Processed message {message['body']}")
            income_message = json.loads(message['body'])
            if income_message.get("type") == "telegram":
                chat_id = income_message["message"]["message"]["chat"]["id"]
                msg_text = income_message["message"]["message"].get("text", " ")
                try:
                    response = chatbot.process_question(msg_text, debug=debug_mode)
                    send_message(token, chat_id, response)
                except Exception as e:
                    print(f"Error processing message: {msg_text}")
                    print(e)
                    send_message(token, chat_id, "Un error a ocurrido al procesar tu mensaje. Por favor, inténtalo de nuevo más tarde.")
        except Exception as err:
            print("An error occurred")
            print(err)


if __name__ == "__main__":
    local_handler()