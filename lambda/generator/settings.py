from os import getenv
from dotenv import load_dotenv

load_dotenv(override=False)

ENVIRONMENT = getenv("ENVIRONMENT", "local")
PINECONE_API_KEY = getenv("PINECONE_API_KEY")
TELEGRAM_KEY = getenv("TELEGRAM_KEY")
PINECONE_INDEX_NAME = getenv("PINECONE_INDEX_NAME", "network-support-chatbot") + "-" + ENVIRONMENT
DEBUG_MODE = getenv("DEBUG", "False").lower() == "true"