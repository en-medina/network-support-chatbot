import platform
import subprocess
from datetime import datetime
from typing import Annotated, List
import socket

from langchain_core.tools import tool
from pydantic import BaseModel, Field

import dns.resolver
from dns import rdatatype
from whois import whois

def get_escalation_tools() -> List[tool]:
    """
    Returns a list of escalation-related tools
    Each tool is defined with its name, description, and function.
    """
    return [escalate_request]

def get_escalation_tool_names() -> str:
    """
    Returns a comma-separated string of the names of all available escalation tools.
    """
    return ", ".join([tool.name for tool in get_escalation_tools()])

@tool
def escalate_request(
        title: Annotated[str, "A brief and descriptive name of the issue"],
        description: Annotated[str, "A detailed explanation of the network-related problem or issue"],
        question: Annotated[str,  "The user's question that prompted this ticket escalation"],
        ) -> str:
    """
    Escalates a user request by creating a new ticket in the ticketing system.
    Returns the ticket ID created in the ticketing system 
    """
    #TODO: API call to some ticketing system app
    #print(title, description, question)
    return "TASK-001"

