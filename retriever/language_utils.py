"""
Language detection and processing utilities for multilingual support
"""
import logging
from typing import Dict, List, Optional, Tuple, Any
from langdetect import detect, LangDetectException
from googletrans import Translator

# Initialize the translator
translator = Translator()

# Map of language codes to human-readable names
LANGUAGE_NAMES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'nl': 'Dutch',
    'ru': 'Russian',
    'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'ur': 'Urdu',
    'te': 'Telugu',
    'ta': 'Tamil',
    'mr': 'Marathi',
    'gu': 'Gujarati'
}

# Map of language codes to appropriate embedding models
LANGUAGE_EMBEDDING_MODELS = {
    'en': 'sentence-transformers/all-MiniLM-L6-v2',  # English
    'es': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # Spanish
    'fr': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # French
    'de': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # German
    'it': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # Italian
    'pt': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # Portuguese
    'nl': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # Dutch
    'ru': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # Russian
    'zh-cn': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # Chinese (Simplified)
    'zh-tw': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # Chinese (Traditional)
    'ja': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # Japanese
    'ko': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # Korean
    'ar': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # Arabic
    'hi': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',  # Hindi
    'default': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'  # Default multilingual model
}

def detect_language(text: str) -> Tuple[str, str]:
    """
    Detect the language of the given text.
    
    Args:
        text (str): The text to detect language for
        
    Returns:
        Tuple[str, str]: A tuple containing (language_code, language_name)
    """
    try:
        if not text or len(text.strip()) < 10:
            return 'en', 'English (default, text too short)'
            
        lang_code = detect(text)
        lang_name = LANGUAGE_NAMES.get(lang_code, f'Unknown ({lang_code})')
        logging.info(f"Detected language: {lang_name} ({lang_code})")
        return lang_code, lang_name
    except LangDetectException as e:
        logging.warning(f"Language detection failed: {str(e)}. Defaulting to English.")
        return 'en', 'English (default)'

def get_embedding_model_for_language(lang_code: str) -> str:
    """
    Get the appropriate embedding model for the given language.
    
    Args:
        lang_code (str): The language code
        
    Returns:
        str: The name of the embedding model to use
    """
    return LANGUAGE_EMBEDDING_MODELS.get(lang_code, LANGUAGE_EMBEDDING_MODELS['default'])

def translate_text(text: str, target_lang: str = 'en', source_lang: Optional[str] = None) -> str:
    """
    Translate text to the target language.
    
    Args:
        text (str): The text to translate
        target_lang (str): The target language code (default: 'en')
        source_lang (Optional[str]): The source language code (if None, auto-detect)
        
    Returns:
        str: The translated text
    """
    try:
        if not text:
            return ""
            
        if source_lang == target_lang:
            return text
            
        result = translator.translate(text, dest=target_lang, src=source_lang if source_lang else 'auto')
        return result.text
    except Exception as e:
        logging.error(f"Translation error: {str(e)}")
        return text  # Return original text on error

def translate_chunks(chunks: List[Dict[str, Any]], target_lang: str = 'en') -> List[Dict[str, Any]]:
    """
    Translate a list of document chunks to the target language.
    
    Args:
        chunks (List[Dict[str, Any]]): List of document chunks
        target_lang (str): The target language code (default: 'en')
        
    Returns:
        List[Dict[str, Any]]: The translated chunks
    """
    translated_chunks = []
    
    for chunk in chunks:
        # Detect source language if not already in metadata
        source_lang = chunk.get('metadata', {}).get('language', None)
        if not source_lang:
            source_lang, _ = detect_language(chunk['text'])
            
        # Only translate if needed
        if source_lang != target_lang:
            translated_text = translate_text(chunk['text'], target_lang, source_lang)
            
            # Create a new chunk with translated text
            translated_chunk = chunk.copy()
            translated_chunk['text'] = translated_text
            translated_chunk['original_text'] = chunk['text']
            translated_chunk['original_language'] = source_lang
            translated_chunk['translated_to'] = target_lang
            
            translated_chunks.append(translated_chunk)
        else:
            # No translation needed
            translated_chunks.append(chunk)
            
    return translated_chunks
