from typing import Annotated, List
import requests
import settings
import json

def escalate_request(
        title: Annotated[str, "A brief and descriptive name of the issue"],
        description: Annotated[str, "A detailed explanation of the network-related problem or issue"],
        question: Annotated[str,  "The user's question that prompted this ticket escalation"],
        ) -> str:
    """
    Escalates a user request by creating a new ticket in the ticketing system.
    Returns the ticket ID created in the ticketing system 
    """

    # Replace with your actual values
    list_id = settings.CLICKUP_LIST_ID
    api_token = settings.CLICKUP_API_KEY

    url = f"https://api.clickup.com/api/v2/list/{list_id}/task"

    headers = {
        "Authorization": api_token,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "name": title,
        "description": f"User Question: {question}\n\n{description}",
        "tags": ["AI-generated"]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        return f"Error: Unable to create ticket. Status code {response.status_code}, Response: {response.text}"
    return response.json().get("id", "No ID returned")
