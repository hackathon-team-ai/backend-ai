import logging

try:
    from google import genai
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
        self.api_key = getattr(settings, "GEMINI_API_KEY", "").strip()
        self.client = None
        self.model_name = "gemini-3-flash-preview"

        if not genai or not self.api_key:
            logger.warning("Gemini is not configured; chat will use the local question-aware fallback.")
            return

        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini chat client initialized: %s", self.model_name)
        except Exception as exc:
            logger.exception("Unable to initialise Gemini: %s", exc)

    async def generate_response(self, user_prompt: str, category: str = "General", context: str = "", language: str = "en") -> str:
        question = user_prompt.strip()
        if not question:
            return "Please type your farming question."

        LANGUAGE_NAMES = {
            "en": "English",
            "hi": "Hindi",
            "mr": "Marathi",
            "ta": "Tamil",
            "te": "Telugu",
            "kn": "Kannada",
            "gu": "Gujarati",
            "pa": "Punjabi",
            "bn": "Bengali",
            "or": "Odia",
        }
        language_name = LANGUAGE_NAMES.get(language.lower(), "English")
        prompt = f"{AGRICULTURE_SYSTEM_PROMPT}\n\nCategory: {category}\n"
        if context:
            prompt += f"Use this retrieved knowledge only when relevant:\n{context}\n\n"
        prompt += f"Farmer's latest question: {question}\n\nIMPORTANT: You MUST reply ONLY in {language_name}. Do not use English if the requested language is not English."

        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt],
                )
                answer = response.text.strip() if response.text else ""
                if answer:
                    return answer
                logger.warning("Gemini returned an empty response.")
            except Exception as exc:
                logger.warning("Gemini generation failed; using local fallback: %s", exc)

        return self._question_aware_fallback(question, category, language)

    def _question_aware_fallback(self, question: str, category: str, language: str) -> str:
        """Safe offline response that never substitutes an unrelated answer."""
        topic = f"{question.lower()} {category.lower()}"

        if any(term in topic for term in ("fertilizer", "npk", "urea", "manure", "खत", "खाद", "ಗೊಬ್ಬರ", "ఎరువు", "உரம்", "ખાતર", "ਖਾਦ", "সার", "ସାର")):
            return self._localized(language,
                en="Please share the crop name, area (acres), crop growth stage, and soil-test N-P-K values. Fertilizer dose varies by crop and soil — a single dose would be unsafe.",
                hi="कृपया फसल का नाम, क्षेत्रफल, अवस्था और मिट्टी परीक्षण N-P-K मान बताएँ। खाद की मात्रा फसल और मिट्टी के अनुसार बदलती है।",
                mr="कृपया पिकाचे नाव, क्षेत्रफळ, अवस्था आणि माती N-P-K मूल्ये सांगा. एकच खत मात्रा सुरक्षित नाही.",
                ta="பயிரின் பெயர், பரப்பு, வளர்ச்சி நிலை, மண் N-P-K மதிப்புகள் தெரிவிக்கவும். ஒரே உரத்தின் அளவு பாதுகாப்பானது அல்ல.",
                te="పంట పేరు, విస్తీర్ణం, దశ, మట్టి N-P-K విలువలు తెలపండి. ఒకే ఎరువు మోతాదు సురక్షితం కాదు.",
                kn="ಬೆಳೆ ಹೆಸರು, ವಿಸ್ತೀರ್ಣ, ಹಂತ, ಮಣ್ಣು N-P-K ಮೌಲ್ಯಗಳನ್ನು ತಿಳಿಸಿ. ಒಂದೇ ಗೊಬ್ಬರ ಪ್ರಮಾಣ ಸುರಕ್ಷಿತವಲ್ಲ.",
                gu="પાકનું નામ, વિસ્તાર, અવસ્થા, જમીન N-P-K મૂલ્ય જણાવો. એક જ ખાતરની માત્રા સુરક્ષિત નથી.",
                pa="ਫਸਲ ਦਾ ਨਾਮ, ਖੇਤਰਫਲ, ਅਵਸਥਾ, ਮਿੱਟੀ N-P-K ਮੁੱਲ ਦੱਸੋ। ਇੱਕੋ ਖਾਦ ਮਾਤਰਾ ਸੁਰੱਖਿਅਤ ਨਹੀਂ।",
                bn="ফসলের নাম, জমির পরিমাণ, পর্যায় এবং মাটির N-P-K মান জানান। একটি নির্দিষ্ট সার মাত্রা নিরাপদ নয়।", odia="ଫସଲର ନାମ, ଜମି, ଅବସ୍ଥା ଏବଂ ମାଟି N-P-K ମୂଲ୍ୟ ଜଣାନ୍ତୁ। ଗୋଟିଏ ସାର ମାତ୍ରା ସୁରକ୍ଷିତ ନୁହେଁ।",
            )

        if any(term in topic for term in ("disease", "spot", "yellow", "blight", "pest", "insect", "रोग", "कीड", "कीट", "ರೋಗ", "వ్యాధి", "நோய்", "રોગ", "ਬਿਮਾਰੀ", "রোগ", "ରୋଗ")):
            return self._localized(language,
                en="Please share the crop name, plant age, visible symptoms, and a clear leaf photo. Do not spray pesticide until the problem is identified.",
                hi="कृपया फसल का नाम, उम्र, लक्षण और पत्ते की साफ फोटो भेजें। समस्या पहचाने बिना कीटनाशक न डालें।",
                mr="पिकाचे नाव, वय, लक्षणे आणि पानाचा स्पष्ट फोटो पाठवा. समस्या ओळखल्याशिवाय फवारणी करू नका.",
                ta="பயிரின் பெயர், வயது, அறிகுறிகள், இலை தெளிவான படம் அனுப்பவும். பிரச்னை தெரியாமல் பூச்சிக்கொல்லி தெளிக்காதீர்கள்.",
                te="పంట పేరు, వయస్సు, లక్షణాలు, ఆకు స్పష్టమైన ఫోటో పంపండి. సమస్య గుర్తించకముందే పురుగుమందు వేయకండి.",
                kn="ಬೆಳೆ ಹೆಸರು, ವಯಸ್ಸು, ರೋಗಲಕ್ಷಣ, ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋ ಕಳುಹಿಸಿ. ಗುರುತಿಸದೆ ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸಬೇಡಿ.",
                gu="પાકનું નામ, ઉંમર, લક્ષણ, પાંદડાની સ્પષ્ટ ફોટો મોકલો. સમસ્યા ઓળખ્યા વગર જંતુનાશક ન છાંટો.",
                pa="ਫਸਲ ਦਾ ਨਾਮ, ਉਮਰ, ਲੱਛਣ ਅਤੇ ਪੱਤੇ ਦੀ ਸਾਫ਼ ਫੋਟੋ ਭੇਜੋ। ਸਮੱਸਿਆ ਪਛਾਣੇ ਬਿਨਾਂ ਕੀਟਨਾਸ਼ਕ ਨਾ ਪਾਓ।",
                bn="ফসলের নাম, বয়স, লক্ষণ এবং পাতার স্পষ্ট ছবি পাঠান। সমস্যা চেনার আগে কীটনাশক দেবেন না।", odia="ଫସଲ ନାମ, ବୟସ, ଲକ୍ଷଣ ଏବଂ ପତ୍ରର ସ୍ପଷ୍ଟ ଫୋଟୋ ପଠାନ୍ତୁ। ସମସ୍ୟା ଚିହ୍ନଟ ନ ହେଲା ପର୍ଯ୍ୟନ୍ତ କୀଟନାଶକ ଦିଅନ୍ତୁ ନାହିଁ।",
            )

        return self._localized(language,
            en=f"I received your question: **{question}**. The AI service is temporarily unavailable. Please try again later.",
            hi=f"आपका प्रश्न मिला: **{question}**। AI सेवा अभी अनुपलब्ध है। कृपया बाद में पुनः प्रयास करें।",
            mr=f"तुमचा प्रश्न मिळाला: **{question}**. AI सेवा सध्या उपलब्ध नाही. कृपया नंतर पुन्हा प्रयत्न करा.",
            ta=f"உங்கள் கேள்வி கிடைத்தது: **{question}**. AI சேவை தற்போது கிடைக்கவில்லை. தயவுசெய்து மீண்டும் முயற்சிக்கவும்.",
            te=f"మీ ప్రశ్న అందింది: **{question}**. AI సేవ ప్రస్తుతం అందుబాటులో లేదు. దయచేసి తర్వాత ప్రయత్నించండి.",
            kn=f"ನಿಮ್ಮ ಪ್ರಶ್ನೆ ಸಿಕ್ಕಿತು: **{question}**. AI ಸೇವೆ ಪ್ರಸ್ತುತ ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ನಂತರ ಪ್ರಯತ್ನಿಸಿ.",
            gu=f"તમારો પ્રશ્ન મળ્યો: **{question}**. AI સેવા હાલ ઉપલબ્ધ નથી. કૃપા કરીને પછી ફરી પ્રયત્ન કરો.",
            pa=f"ਤੁਹਾਡਾ ਸਵਾਲ ਮਿਲਿਆ: **{question}**. AI ਸੇਵਾ ਹੁਣ ਉਪਲਬਧ ਨਹੀਂ। ਕਿਰਪਾ ਕਰਕੇ ਬਾਅਦ ਵਿੱਚ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
            bn=f"আপনার প্রশ্ন পাওয়া গেছে: **{question}**. AI পরিষেবা এখন অনুপলব্ধ। পরে আবার চেষ্টা করুন।",
            odia=f"ଆପଣଙ୍କ ପ୍ରଶ୍ନ ମିଳିଲା: **{question}**. AI ସେବା ବର୍ତ୍ତମାନ ଉପଲବ୍ଧ ନୁହେଁ। ଦୟାକରି ପରେ ପୁଣି ଚେଷ୍ଟା କରନ୍ତୁ।",
        )

    @staticmethod
    def _localized(language: str, *, en: str, hi: str, mr: str,
                   ta: str = '', te: str = '', kn: str = '',
                   gu: str = '', pa: str = '', bn: str = '', odia: str = '') -> str:
        lang = language.lower()
        return {
            'hi': hi, 'mr': mr, 'ta': ta or en, 'te': te or en,
            'kn': kn or en, 'gu': gu or en, 'pa': pa or en,
            'bn': bn or en, 'or': odia or en,
        }.get(lang, en)


gemini_service = GeminiService()
