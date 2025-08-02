from langdetect import detect


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
            detected_lang, "es"
        )  # Default to Spanish if not supported
    except Exception:
        return supported_languages.get("es", "Spanish")  # Default to Spanish on error


def language_prompt(user_language: str) -> str:
    """Returns a prompt to ensure the response matches the user's language."""
    return f"""
    IMPORTANT: The user's original message was in {user_language}. 
    You MUST respond in {user_language} to match the user's language.
    If you don't speak {user_language} fluently, provide your technical response in Spanish 
    but add a note that you're responding in Spanish due to technical limitations.
    """
