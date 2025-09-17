from langdetect import detect, DetectorFactory
from agents.state import model_selection
import settings

DetectorFactory.seed = 0  # For consistent results across runs


def detect_language(text: str) -> str:
    """Detects the language of the input text and returns a supported language.
    If the detected language is not supported, defaults to Spanish.
    """
    supported_languages = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "ja": "Japanese",
        "hi": "Hindi",
        "th": "Thai",
    }
    try:
        detected_lang = detect(text)
        return supported_languages.get(
            detected_lang, "Spanish"
        )  # Default to Spanish if not supported
    except Exception:
        return supported_languages.get("es", "Spanish")  # Default to Spanish on error

def llm_language_prompt(text: str) -> str:
    supported_languages = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "hi": "Hindi",
        "th": "Thai",
    }
    prompt = f"""
    You are a language detection agent.
    Your task is to detect the language of the MESSAGE and reply with the ISO 639-1 language code.
    Reply only with the language code.
    If you cannot detect a language of the MESSAGE reply with 'UNKNOWN' with uppercase

    Some examples:
    SAMPLE: "Hello, how are you?": "en"
    SAMPLE: "Hola, ¿cómo estás?": "es"
    SAMPLE: "Bonjour, comment ça va?": "fr"
    SAMPLE: "Hallo, wie geht's?": "de"

    below is the MESSAGE you need to detect the language for:
    MESSAGE: "{text}"
    """
    llm = model_selection(llm=settings.LLAMA32_MODEL_ARN)
    response = llm.invoke(prompt)
    return supported_languages.get(response.strip().lower(), "Spanish")  # Default to Spanish if not supported

def language_prompt(user_language: str) -> str:
    """Returns a prompt to ensure the response matches the user's language."""
    return f"""
    IMPORTANT: The user's original message was in {user_language}. 
    You MUST respond in {user_language} to match the user's language.
    If you don't speak {user_language} fluently, provide your technical response in Spanish 
    but add a note that you're responding in Spanish due to technical limitations.
    """
