# -*- coding: utf-8 -*-
import logging
import os

logger = logging.getLogger("krishimitra.gemini")

AGRICULTURE_SYSTEM_PROMPT = (
    "You are KrishiMitra AI, an expert agriculture advisor for Indian farmers. "
    "Answer the farmer's latest question directly and only on that topic. "
    "Use clear, practical language. Reply ONLY in the requested language."
)


def _load_key(name: str) -> str:
    """Load API key: OS environ first, then pydantic settings, then manual .env parse."""
    # 1. OS environment (most reliable in uvicorn process)
    val = os.environ.get(name, "").strip()
    if val:
        return val

    # 2. pydantic settings
    try:
        from app.core.config import settings
        val = getattr(settings, name, "").strip()
        if val:
            return val
    except Exception:
        pass

    # 3. Manual .env parse (handles Windows .env folder quirk)
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for path in [os.path.join(base, ".env"), os.path.join(base, ".env", ".env")]:
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith(name + "="):
                            v = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if v:
                                return v
            except Exception:
                pass
    return ""


class GeminiService:
    """Chatbot service - uses Groq (primary) with Gemini fallback."""

    async def generate_response(
        self,
        user_prompt: str,
        category: str = "General",
        context: str = "",
        language: str = "en",
    ) -> str:
        question = user_prompt.strip()
        if not question:
            return "Please type your farming question."

        lang_map = {
            "en": "English", "hi": "Hindi", "mr": "Marathi",
            "ta": "Tamil", "te": "Telugu", "kn": "Kannada",
            "gu": "Gujarati", "pa": "Punjabi", "bn": "Bengali", "or": "Odia",
        }
        lang_name = lang_map.get(language.lower(), "English")

        prompt = (
            f"{AGRICULTURE_SYSTEM_PROMPT}\n\n"
            f"Category: {category}\n"
        )
        if context:
            prompt += f"Relevant knowledge:\n{context}\n\n"
        prompt += f"Farmer question: {question}\n\nIMPORTANT: Reply ONLY in {lang_name}."

        # 1. Try Groq (sync client run in thread executor to avoid event loop conflicts)
        groq_key = _load_key("GROQ_API_KEY")
        logger.info("GROQ_KEY present: %s", bool(groq_key))
        if groq_key:
            try:
                import asyncio
                from groq import Groq

                def _groq_call():
                    c = Groq(api_key=groq_key)
                    r = c.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                        max_tokens=1024,
                    )
                    return r.choices[0].message.content.strip()

                loop = asyncio.get_event_loop()
                answer = await loop.run_in_executor(None, _groq_call)
                if answer:
                    logger.info("Groq responded OK, len=%d", len(answer))
                    return answer
            except Exception as e:
                logger.error("Groq failed: %s", repr(e))

        # 2. Try Gemini
        gemini_key = _load_key("GEMINI_API_KEY")
        if gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)
                for model in ["gemini-3-flash-preview", "gemini-3.5-flash", "gemini-2.0-flash"]:
                    try:
                        resp = client.models.generate_content(model=model, contents=[prompt])
                        answer = (resp.text or "").strip()
                        if answer:
                            logger.info("Gemini model %s responded OK", model)
                            return answer
                    except Exception as me:
                        logger.warning("Gemini model %s failed: %s", model, me)
            except Exception as e:
                logger.warning("Gemini init failed: %s", e)

        # 3. Local fallback
        logger.error("Both Groq and Gemini failed - using local fallback")
        return self._fallback(question, category, language)

    def _fallback(self, question: str, category: str, language: str) -> str:
        topic = f"{question.lower()} {category.lower()}"

        if any(w in topic for w in ("fertilizer", "npk", "urea")):
            responses = {
                "en": "Please share crop name, area, growth stage and soil N-P-K values.",
                "hi": "Fasal ka naam, kshetra, avastha aur mitti N-P-K maan batayein.",
                "mr": "Pikache naav, kshetrafal, avastha aani mati N-P-K mulye sanga.",
            }
        elif any(w in topic for w in ("disease", "pest", "spot", "yellow", "blight")):
            responses = {
                "en": "Please share crop name, plant age, symptoms and a clear leaf photo.",
                "hi": "Fasal ka naam, aayu, lakshan aur patte ki photo bhejein.",
                "mr": "Pikache naav, vay, lakshane aani panache photo pathva.",
            }
        else:
            responses = {
                "en": f"AI service is temporarily unavailable. Your question: **{question}**",
                "hi": f"AI seva abhi uplabdh nahi hai. Prashna: **{question}**",
                "mr": f"AI seva sadhya uplabdh nahi. Prashna: **{question}**",
            }

        return responses.get(language.lower(), responses["en"])


gemini_service = GeminiService()
