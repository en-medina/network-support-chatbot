from os import getenv
from dotenv import load_dotenv

load_dotenv(override=False)

ENVIRONMENT = getenv("ENVIRONMENT", "local")
PINECONE_API_KEY = getenv("PINECONE_API_KEY")
TELEGRAM_KEY = getenv("TELEGRAM_KEY")
HUGGING_FACE_API_KEY = getenv("HUGGING_FACE_API_KEY")
PINECONE_INDEX_NAME = getenv("PINECONE_INDEX_NAME", "network-support-chatbot") + "-" + ENVIRONMENT
DEBUG_MODE = getenv("DEBUG", "False").lower() == "true"
LLAMA31_MODEL_ARN = getenv("LLAMA31_MODEL_ARN", "llama3.1:8b")
LLAMA32_MODEL_ARN = getenv("LLAMA32_MODEL_ARN", "llama3.2:3b")
TRIAGE_MODEL_ARN = getenv("TRIAGE_MODEL_ARN", "hf.co/sungun19961/Network-Route-Agent:Q4_K_M")
