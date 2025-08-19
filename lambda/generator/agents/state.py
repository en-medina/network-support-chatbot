from langchain_aws import ChatBedrock
from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel
from langchain_aws.embeddings import BedrockEmbeddings
from langchain_ollama.embeddings import OllamaEmbeddings
from botocore.config import Config
from typing import List, Any, TypedDict, Set
from enum import Enum

import settings

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

def model_selection(model_name: str = "") -> BaseChatModel:
    """Selects the appropriate model based on the environment."""
    if settings.ENVIRONMENT == "local":
        if model_name:
            return ChatOllama(model=model_name, temperature=0)
        return ChatOllama(model="llama3.2:3b", temperature=0)
    elif settings.ENVIRONMENT == "production":
        config=Config(connect_timeout=5, read_timeout=60, retries={'max_attempts': 20})
        max_token_limit = 4096
        if model_name:
            return ChatBedrock(
                model=model_name, 
                temperature=0, 
                config=config, 
                max_tokens=max_token_limit, 
                provider="meta")
        return ChatBedrock(
            model="arn:aws:bedrock:us-east-1:783111403365:inference-profile/us.meta.llama3-2-3b-instruct-v1:0", 
            temperature=0, 
            config=config, 
            max_tokens=max_token_limit, 
            provider="meta")


def select_embedding_model():
    """Selects the appropriate embedding model based on the environment."""
    if settings.ENVIRONMENT == "local":
        return OllamaEmbeddings(model="qllama/multilingual-e5-base:q4_k_m")
    elif settings.ENVIRONMENT == "production":
        config=Config(connect_timeout=5, read_timeout=60, retries={'max_attempts': 20})
        return BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", config=config)