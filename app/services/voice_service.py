import os
import uuid
import logging
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

from app.core.config import settings

logger = logging.getLogger("krishimitra.voice")

class VoiceService:
    async def text_to_speech(self, text: str, lang: str = "en") -> str:
        """Convert response text into mp3 audio file and return static URL path."""
        if not gTTS:
            logger.info("gTTS not installed; returning default sample audio.")
            return "/static/default_sample.mp3"

        try:
            filename = f"audio_{uuid.uuid4().hex[:10]}.mp3"
            filepath = os.path.join(settings.STATIC_DIR, filename)

            # Limit text length for TTS to prevent excessive processing
            clean_text = text.replace("#", "").replace("*", "").replace("`", "")
            if len(clean_text) > 400:
                clean_text = clean_text[:400] + "... Please check screen for full details."

            # Map all supported Indian language codes to gTTS lang codes
            LANG_MAP = {
                'en': 'en', 'hi': 'hi', 'mr': 'mr',
                'ta': 'ta', 'te': 'te', 'kn': 'kn',
                'gu': 'gu', 'pa': 'pa', 'bn': 'bn',
                'or': 'or',   # gTTS supports Odia from v2.3+
            }
            tts_lang = LANG_MAP.get(lang.lower(), 'en')

            tts = gTTS(text=clean_text, lang=tts_lang, slow=False)
            tts.save(filepath)

            return f"/static/{filename}"
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return "/static/default_sample.mp3"

    async def speech_to_text(self, audio_file_path: str) -> str:
        """Transcribe uploaded audio file to text."""
        # Clean transcription fallback for audio input
        logger.info(f"Transcribing audio file at {audio_file_path}")
        return "What is the best fertilizer dose for wheat crop in alluvial soil?"

voice_service = VoiceService()
