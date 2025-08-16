from typing import List, Any, TypedDict, Set
from enum import Enum


class AgentState(TypedDict):
    messages: List[Any]
    tool_messages: List[Any]
    user_question: str
    final_answer: str
    user_language: str
    knowledge_score: int
    knowledge_action: str
    triage_message: str

class AgentNames(Enum):
    CONNECTIVITY = "CONNECTIVITY"
    DEVICE = "DEVICE"
    KNOWLEDGE = "KNOWLEDGE"
    TRIAGE = "TRIAGE"
    ESCALATION = "ESCALATION"

    @classmethod
    def list(cls) -> List[str]:
        """Return all status values as a list of strings."""
        return [status.value for status in cls]

    @classmethod
    def set(cls) -> Set[str]:
        """Return all status values as a set of strings."""
        return {status.value for status in cls}

    @classmethod
    def has_value(cls, value: str) -> bool:
        """Check if a string is a valid status."""
        return value in cls._value2member_map_
