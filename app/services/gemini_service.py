import logging

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from app.core.config import settings

logger = logging.getLogger("krishimitra.gemini")

AGRICULTURE_SYSTEM_PROMPT = """
You are KrishiMitra AI, an expert agriculture advisor for Indian farmers.
Answer the farmer's latest question directly and only on that topic. Do not reuse
an answer from another question and do not give a generic NPK recommendation unless
the farmer asks about fertilizer. Use clear, practical language. If crop, growth
stage, location, or symptoms are required for a safe dosage or diagnosis, say what
information is missing instead of inventing it. Reply in the requested language.
"""


class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY.strip()
        self.model = None

        if not genai or not self.api_key or self.api_key.startswith("AIzaSy-placeholder"):
            logger.warning("Gemini is not configured; chat will use the local question-aware fallback.")
            return

        try:
            genai.configure(api_key=self.api_key)
            # gemini-3.5-flash is not a valid public Gemini model name.
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info("Gemini chat model initialized: %s", settings.GEMINI_MODEL)
        except Exception as exc:
            logger.exception("Unable to initialise Gemini: %s", exc)

    async def generate_response(self, user_prompt: str, category: str = "General", context: str = "", language: str = "en") -> str:
        question = user_prompt.strip()
        if not question:
            return "Please type your farming question."

        language_name = {"mr": "Marathi", "hi": "Hindi", "en": "English"}.get(language.lower(), "English")
        prompt = f"{AGRICULTURE_SYSTEM_PROMPT}\n\nCategory: {category}\n"
        if context:
            prompt += f"Use this retrieved knowledge only when relevant:\n{context}\n\n"
        prompt += f"Farmer's latest question: {question}\n\nReply only in {language_name}."

        if self.model:
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.2, "top_p": 0.9, "top_k": 32},
                )
                answer = getattr(response, "text", "").strip()
                if answer:
                    return answer
                logger.warning("Gemini returned an empty response.")
            except Exception as exc:
                logger.warning("Gemini generation failed; using local fallback: %s", exc)

        return self._question_aware_fallback(question, category, language)

    def _question_aware_fallback(self, question: str, category: str, language: str) -> str:
        """Safe offline response that never substitutes an unrelated NPK answer."""
        topic = f"{question.lower()} {category.lower()}"

        if any(term in topic for term in ("what is crop", "what are crops", "crop meaning", "what is a crop")):
            return self._localized(
                "### What is a crop?\n\nA crop is a plant grown and harvested by farmers for food, fodder, fibre, oil, medicine, or other useful products. Examples include rice, wheat, cotton, sugarcane, and vegetables.",
                "### पीक म्हणजे काय?\n\nशेतकरी अन्न, चारा, तंतू, तेल, औषध किंवा इतर उपयोगासाठी ज्या वनस्पती पिकवून काढतात त्याला पीक म्हणतात. उदा. तांदूळ, गहू, कापूस, ऊस आणि भाजीपाला.",
                "### फसल क्या है?\n\nकिसान भोजन, चारा, रेशा, तेल, दवा या अन्य उपयोग के लिए जिन पौधों को उगाकर काटते हैं, उन्हें फसल कहते हैं। उदाहरण: धान, गेहूँ, कपास, गन्ना और सब्जियाँ।",
                language,
            )
        if any(term in topic for term in ("fertilizer", "npk", "urea", "manure", "खत", "खाद")):
            return self._localized(
                "Please share the crop, area, crop stage, and soil-test values. Fertilizer dose changes by crop and soil, so a single NPK dose would be unsafe.",
                "कृपया पीक, क्षेत्रफळ, पिकाची अवस्था आणि माती परीक्षणातील N-P-K मूल्ये सांगा. खताची मात्रा पीक व मातीप्रमाणे बदलते; एकच NPK मात्रा सुरक्षित नाही.",
                "कृपया फसल, क्षेत्रफल, फसल की अवस्था और मिट्टी परीक्षण के N-P-K मान बताइए। उर्वरक की मात्रा फसल और मिट्टी के अनुसार बदलती है; एक ही NPK मात्रा सुरक्षित नहीं है।",
                language,
            )
        if any(term in topic for term in ("disease", "spot", "yellow", "blight", "pest", "insect", "रोग", "कीड", "कीट")):
            return self._localized(
                "Please share the crop name, plant age, visible symptoms, and a clear leaf photo. Do not spray a pesticide or fungicide until the problem is identified.",
                "कृपया पिकाचे नाव, पिकाचे वय, दिसणारी लक्षणे आणि पानाचा स्पष्ट फोटो पाठवा. समस्या ओळखल्याशिवाय कीटकनाशक किंवा बुरशीनाशक फवारू नका.",
                "कृपया फसल का नाम, फसल की उम्र, दिखने वाले लक्षण और पत्ते की साफ फोटो भेजें। समस्या पहचाने बिना कीटनाशक या फफूंदनाशक का छिड़काव न करें।",
                language,
            )
        return self._localized(
            f"I received your question: **{question}**. Gemini is currently unavailable, so please try again after configuring a valid Gemini API key. I will not replace it with an unrelated farming answer.",
            f"तुमचा प्रश्न मिळाला: **{question}**. Gemini सध्या उपलब्ध नाही. वैध Gemini API key सेट केल्यानंतर पुन्हा प्रयत्न करा; मी याऐवजी असंबंधित शेतीचा सल्ला देणार नाही.",
            f"आपका प्रश्न मिला: **{question}**। Gemini अभी उपलब्ध नहीं है। वैध Gemini API key सेट करने के बाद फिर प्रयास करें; मैं इसके बदले असंबंधित खेती की सलाह नहीं दूँगा।",
            language,
        )

    @staticmethod
    def _localized(english: str, marathi: str, hindi: str, language: str) -> str:
        return {"mr": marathi, "hi": hindi}.get(language.lower(), english)


gemini_service = GeminiService()
