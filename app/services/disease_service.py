import os
import json
import logging
from PIL import Image
try:
    import google.generativeai as genai
except Exception:
    try:
        from google import genai
    except Exception:
        genai = None

from app.core.config import settings
from app.schemas.disease import DiseaseAnalysisResult, TreatmentPlan

logger = logging.getLogger("krishimitra.disease")


class DiseaseService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if genai and hasattr(genai, 'configure') and self.api_key and self.api_key != "AIzaSy-placeholder-key-for-development":
            try:
                genai.configure(api_key=self.api_key)
                self.vision_model = genai.GenerativeModel(settings.GEMINI_MODEL)
            except Exception as e:
                logger.warning(f"Failed to configure Gemini Vision API: {e}")
                self.vision_model = None
        else:
            self.vision_model = None

    async def analyze_leaf_image(self, image_path: str, filename: str) -> DiseaseAnalysisResult:
        """Analyze leaf photo using Gemini Vision. No fake filename-based guessing."""
        if not self.vision_model:
            logger.error("Gemini Vision model not configured (missing/invalid API key).")
            return self._unavailable_result()

        try:
            img = Image.open(image_path)
            prompt = """
            Analyze this agricultural plant leaf image carefully as a Plant Pathologist.

            First identify the crop type from the actual visual features of the leaf
            (shape, venation, color, texture) - do NOT guess based on anything except
            what is visible in the image itself.

            Then identify the disease (if any) specific to that crop.

            If the image is unclear, not a plant leaf, or you cannot confidently identify
            the crop/disease, set "confidence" below 50 and clearly say so in "disease_name".

            Return ONLY a JSON response in the following strict format, with no markdown
            fences, no preamble, and no extra text:
            {
              "disease_name": "Exact Disease Name or Healthy Leaf",
              "is_healthy": boolean,
              "crop_type": "Name of crop (e.g. Tomato, Rice, Wheat, Cotton)",
              "confidence": number between 0.0 and 99.0,
              "symptoms": ["Symptom 1", "Symptom 2", "Symptom 3"],
              "treatment": {
                 "chemical": ["Chemical Spray 1", "Chemical Spray 2"],
                 "organic": ["Organic Solution 1", "Organic Solution 2"],
                 "dosage": "Dosage instructions"
              },
              "prevention": ["Prevention tip 1", "Prevention tip 2"],
              "urgency_level": "Low" | "Medium" | "High" | "Critical"
            }
            """
            res = self.vision_model.generate_content([prompt, img])

            if not res or not res.text:
                logger.error("Gemini returned an empty response.")
                return self._unavailable_result()

            clean_txt = res.text.strip()
            if clean_txt.startswith("```json"):
                clean_txt = clean_txt[7:]
            if clean_txt.startswith("```"):
                clean_txt = clean_txt[3:]
            if clean_txt.endswith("```"):
                clean_txt = clean_txt[:-3]

            data = json.loads(clean_txt.strip())
            return DiseaseAnalysisResult(**data)

        except json.JSONDecodeError as e:
            logger.error(f"Gemini response was not valid JSON: {e}")
            return self._unavailable_result()
        except Exception as e:
            logger.error(f"Gemini Vision call failed: {e}")
            return self._unavailable_result()

    def _unavailable_result(self) -> DiseaseAnalysisResult:
        """Honest 'could not detect' response - never guesses a random disease."""
        return DiseaseAnalysisResult(
            disease_name="Unable to confidently detect crop/disease. Please upload a clearer, well-lit leaf photo.",
            is_healthy=False,
            crop_type="Unknown",
            confidence=0.0,
            symptoms=[],
            treatment=TreatmentPlan(chemical=[], organic=[], dosage="N/A"),
            prevention=["Retake photo in good natural light", "Focus closely on the affected leaf", "Avoid blurry or dark images"],
            urgency_level="Low"
        )


disease_service = DiseaseService()
