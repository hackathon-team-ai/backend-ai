import logging
import json
try:
    import google.generativeai as genai
except ImportError:
    try:
        from google import genai
    except ImportError:
        genai = None

from app.core.config import settings

logger = logging.getLogger("krishimitra.gemini")

# System prompt tuned specifically for Indian & Global Agriculture
AGRICULTURE_SYSTEM_PROMPT = """
You are KrishiMitra AI, an expert Senior Agronomist and Multimodal Agriculture Advisor.
Your objective is to provide precise, scientific, practical, and highly empathetic farming advice to farmers.

Key Rules:
1. Cover topics accurately: Crop selection, Fertilizers (NPK dosage), Plant Pathology/Diseases, Pest management, Irrigation schedules, Harvesting techniques, and Organic/Regenerative farming.
2. Format responses with clear Markdown headings, bullet points, step-by-step instructions, bold highlights, and structured tables where applicable.
3. Offer actionable solutions considering soil types, weather conditions, organic alternatives, and safety instructions for agro-chemicals.
4. Keep explanations accessible to farmers of all experience levels while maintaining agronomic rigour.
"""

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if genai and hasattr(genai, 'configure') and self.api_key and self.api_key != "AIzaSy-placeholder-key-for-development":
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Initialized Google Gemini API client successfully.")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini API: {e}")
                self.model = None
        else:
            self.model = None
            logger.info("No valid GEMINI_API_KEY provided; operating with Agronomy AI Fallback Engine.")

    async def generate_response(self, user_prompt: str, category: str = "General", context: str = "") -> str:
        full_prompt = f"{AGRICULTURE_SYSTEM_PROMPT}\n\nCategory: {category}\n"
        if context:
            full_prompt += f"Retrieved Knowledge Context:\n{context}\n\n"
        full_prompt += f"Farmer Question:\n{user_prompt}"

        if self.model:
            try:
                response = self.model.generate_content(full_prompt)
                if response and response.text:
                    return response.text
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}. Falling back to domain engine.")

        # Agronomy Smart Fallback Engine
        return self._generate_smart_fallback(user_prompt, category)

    def _generate_smart_fallback(self, query: str, category: str) -> str:
        q_lower = query.lower()
        if "fertilizer" in q_lower or "npk" in q_lower or category == "Fertilizers":
            return """### 🌿 Recommended Fertilizer Management Plan

For optimal crop yield, follow balanced NPK management based on soil test results:

#### 1. Basal Application (At Sowing)
* **NPK Ratio**: Apply 50% Nitrogen, 100% Phosphorus (P2O5), and 50% Potash (K2O).
* **Organic Boost**: Apply 5-10 tonnes of well-decomposed Farm Yard Manure (FYM) or Vermicompost per acre 15 days before sowing.

#### 2. Top Dressing (Vegetative Stage)
* **Nitrogen Boost**: Apply the remaining 50% Urea in 2 split doses at 30 days and 50 days post-sowing.
* **Micro-nutrients**: Spray **Zinc Sulphate (0.5%)** and **Ferrous Sulphate (0.5%)** if leaf yellowing is observed.

> 💡 **Organic Tip**: Incorporate Bio-fertilizers like *Azotobacter* and *PSB (Phosphorus Solubilizing Bacteria)* @ 2 kg/acre to improve soil microbe activity.
"""

        elif "disease" in q_lower or "yellow" in q_lower or "spot" in q_lower or category == "Diseases":
            return """### 🔍 Plant Pathology Guidance

Leaf yellowing or fungal spots are common indicators of early-stage fungal or bacterial infection.

#### Recommended Action Steps:
1. **Immediate Inspection**: Check the undersides of lower leaves for white powder or brown concentric rings.
2. **Fungicide Spray**:
   - **Chemical**: Spray **Mancozeb 75% WP** @ 2g/liter of water or **Hexaconazole 5% EC** @ 1.5ml/liter.
   - **Organic**: Spray **Neem Oil (10,000 ppm)** @ 3ml/liter + 1ml liquid soap.
3. **Cultural Control**: Avoid overhead sprinkler irrigation during high atmospheric humidity to prevent fungal spore germination.
"""

        elif "irrigation" in q_lower or "water" in q_lower or category == "Irrigation":
            return """### 💧 Smart Irrigation & Water Advisory

Proper irrigation scheduling conserves water while preventing root rot and stress:

* **Drip Irrigation**: Maintain moisture at field capacity. Irrigate for 1.5 to 2 hours every alternate day depending on solar radiation.
* **Critical Moisture Stages**:
  - Flowering / Tasseling Stage
  - Grain Formation / Pod Filling Stage
* **Mulching**: Apply 3-inch straw or plastic mulch to reduce evaporation loss by up to 40%.
"""

        else:
            return f"""### 🌾 KrishiMitra Agronomy Advisory

Thank you for your question regarding **{category}**.

#### Comprehensive Recommendations:
1. **Soil Health**: Test soil pH (ideal range: 6.5–7.5) and electrical conductivity (EC) before seasonal planting.
2. **Crop Protection**: Inspect field early in the morning twice a week for early detection of pest egg masses or leaf feeding.
3. **Climate Resilience**: Monitor 7-day weather updates before applying foliar sprays or major irrigation runs.

*Feel free to ask a follow-up question or upload a leaf photo for automated disease identification!*
"""

gemini_service = GeminiService()
