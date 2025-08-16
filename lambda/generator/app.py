from agents.networksupportchatbot import NetworkSupportChatbot
from tools.telegram import send_message
from os import getenv
from dotenv import load_dotenv
import json

load_dotenv(override=False)

def local_handler():
    chatbot = NetworkSupportChatbot()
    debug_mode = getenv("DEBUG", "False").lower() == "true"
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = chatbot.process_question(user_input, debug=debug_mode)
        print(f"Bot: {response}")

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
def lambda_handler(event, context):
    for message in event['Records']:
        process_message(message)
    print("done")

def process_message(message):
    try:
        print(f"Processed message {message['body']}")
        income_message = json.loads(message['body'])
        if income_message.get("type") == "telegram":
            chat_id = income_message["message"]["message"]["chat"]["id"]
            msg_text = income_message["message"]["message"].get("text", " ")
            text = "The following message was received:\n" + msg_text
            print(f"Replying to chat_id {chat_id} with text: {text}")
            token = getenv("TELEGRAM_KEY")
            send_message(token, chat_id, text)

    except Exception as err:
        print("An error occurred")
        raise err


# if __name__ == "__main__":
#     local_handler()