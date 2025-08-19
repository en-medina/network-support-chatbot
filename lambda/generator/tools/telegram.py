
import requests
def send_message(token, chat_id, message):

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to send message: {response.text}")