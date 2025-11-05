from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sarvamai import SarvamAI
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/translation", tags=["translation"])

# --- Request Models ---
class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to translate to English")
    source_language: str = Field(..., description="Source language code (e.g., 'hi-IN', 'bn-IN', etc.)")

class AutoTranslateRequest(BaseModel):
    text: str = Field(..., description="Text to auto-detect language and translate to English")

# --- Constants ---
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

SUPPORTED_LANGUAGES = {
    "hi-IN": "हिंदी (Hindi)", "bn-IN": "বাংলা (Bengali)", "ta-IN": "தமிழ் (Tamil)",
    "te-IN": "తెలుగు (Telugu)", "gu-IN": "ગુજરાતી (Gujarati)", "kn-IN": "ಕನ್ನಡ (Kannada)",
    "ml-IN": "മലയാളം (Malayalam)", "mr-IN": "मराठी (Marathi)", "pa-IN": "ਪੰਜਾਬੀ (Punjabi)",
    "od-IN": "ଓଡ଼ିଆ (Odia)", "en-IN": "English",
    "as-IN": "অসমীয়া (Assamese)", "brx-IN": "बड़ो (Bodo)", "doi-IN": "डोगरी (Dogri)",
    "ks-IN": "कॉशुर (Kashmiri)", "kok-IN": "कोंकणी (Konkani)", "mai-IN": "मैथिली (Maithili)",
    "mni-IN": "মৈতৈলোন্ (Manipuri)", "ne-IN": "नेपाली (Nepali)", "sa-IN": "संस्कृतम् (Sanskrit)",
    "sat-IN": "ᱥᱟᱱᱛᱟᱲᱤ (Santali)", "sd-IN": "سنڌي (Sindhi)", "ur-IN": "اردو (Urdu)"
}

# --- Language Detection Function ---
async def detect_language(text: str) -> dict:
    """
    Detect the language of input text using Sarvam AI identify_language endpoint
    """
    try:
        client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
        
        # Use the correct method name: identify_language
        response = client.text.identify_language(input=text)
        
        return {
            "detected_language_code": response.language_code,
            "detected_language_name": SUPPORTED_LANGUAGES.get(response.language_code, "Unknown"),
            "confidence": getattr(response, 'confidence', None)
        }
        
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")

# --- Translation Function ---
async def translate_text_to_english(text: str, source_language: str) -> dict:
    """
    Translate text from supported Indian languages to English using Sarvam AI translate endpoint
    """
    try:
        client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
        
        # Use the translate endpoint
        response = client.text.translate(
            input=text,
            source_language_code=source_language,
            target_language_code="en-IN",
            speaker_gender="Male",
            mode="classic-colloquial",
            enable_preprocessing=False,
        )
        
        return {
            "original_text": text,
            "translated_text": response.translated_text,
            "source_language": source_language,
            "target_language": "en-IN",
            "source_language_name": SUPPORTED_LANGUAGES.get(source_language, "Unknown"),
            "target_language_name": "English"
        }
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

# --- Auto Translate Function ---
async def auto_translate_to_english(text: str) -> dict:
    """
    Automatically detect language using identify_language endpoint and then translate to English
    """
    try:
        # Step 1: Detect language using identify_language endpoint
        logger.info(f"Detecting language for text: {text[:50]}...")
        detection_result = await detect_language(text)
        detected_language = detection_result["detected_language_code"]
        
        logger.info(f"Detected language: {detected_language} ({detection_result['detected_language_name']})")
        
        # Step 2: If already English, return as is
        if detected_language == "en-IN":
            return {
                "original_text": text,
                "translated_text": text,
                "detected_language": detected_language,
                "detected_language_name": "English",
                "target_language": "en-IN",
                "target_language_name": "English",
                "confidence": detection_result.get("confidence"),
                "note": "Text is already in English"
            }
        
        # Step 3: Translate to English using translate endpoint
        logger.info(f"Translating from {detected_language} to English...")
        translation_result = await translate_text_to_english(text, detected_language)
        
        # Combine results
        return {
            **translation_result,
            "detected_language": detected_language,
            "detected_language_name": detection_result["detected_language_name"],
            "confidence": detection_result.get("confidence")
        }
        
    except Exception as e:
        logger.error(f"Auto translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Auto translation failed: {str(e)}")

# --- Endpoint: /translate ---
@router.post("/translate")
async def translate_text(req: TranslationRequest) -> dict:
    """
    Translate text from specified Indian language to English
    """
    try:
        # Validate source language
        if req.source_language not in SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported language code: {req.source_language}. Supported languages: {list(SUPPORTED_LANGUAGES.keys())}"
            )
        
        # Don't translate if already English
        if req.source_language == "en-IN":
            return {
                "original_text": req.text,
                "translated_text": req.text,
                "source_language": req.source_language,
                "target_language": "en-IN",
                "source_language_name": "English",
                "target_language_name": "English",
                "note": "Text is already in English"
            }
        
        logger.info(f"Translating from {req.source_language} to English: {req.text[:50]}...")
        return await translate_text_to_english(req.text, req.source_language)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoint: /auto-translate ---
@router.post("/auto-translate")
async def auto_translate_text(req: AutoTranslateRequest) -> dict:
    """
    Automatically detect language and translate text to English
    Uses detect-language endpoint first, then translate endpoint
    """
    try:
        logger.info(f"Auto-translating text: {req.text[:50]}...")
        return await auto_translate_to_english(req.text)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auto-translate endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoint: /detect-language ---
@router.post("/detect-language")
async def detect_text_language(req: AutoTranslateRequest) -> dict:
    """
    Detect the language of input text using Sarvam AI identify_language endpoint
    """
    try:
        logger.info(f"Detecting language for text: {req.text[:50]}...")
        return await detect_language(req.text)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Language detection endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoint: /supported-languages ---
@router.get("/supported-languages")
async def get_supported_languages() -> dict:
    """
    Get list of supported source languages for translation to English
    """
    return {
        "supported_languages": SUPPORTED_LANGUAGES,
        "target_language": "en-IN (English)",
        "total_languages": len(SUPPORTED_LANGUAGES)
    }
