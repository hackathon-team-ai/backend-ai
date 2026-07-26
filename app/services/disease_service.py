import base64
import json
import logging
import re

try:
    from groq import Groq
except ImportError:
    Groq = None

from app.core.config import settings
from app.schemas.disease import DiseaseAnalysisResult, TreatmentPlan

logger = logging.getLogger("krishimitra.disease")


class DiseaseService:
    def __init__(self):
        self.api_key = getattr(settings, "GROQ_API_KEY", "").strip()
        self.client = None
        self.model_name = "qwen/qwen3.6-27b"

        if Groq and self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to configure Groq Vision API: {e}")
                self.client = None
        else:
            self.client = None

    async def analyze_leaf_image(self, image_path: str, filename: str) -> DiseaseAnalysisResult:
        """Analyze leaf photo using Groq Vision. No fake filename-based guessing."""
        if not self.client:
            logger.error("Groq Vision model not configured (missing/invalid API key).")
            return self._unavailable_result()

        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else "jpeg"
            mime = "image/png" if ext == "png" else "image/jpeg"

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

            res = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime};base64,{image_b64}"},
                            },
                        ],
                    }
                ],
                temperature=0.2,
                max_tokens=8000,
                reasoning_format="hidden",
            )

            raw_text = res.choices[0].message.content
            logger.info(f"Groq raw response: {raw_text!r}")

            if not raw_text or not raw_text.strip():
                logger.error("Groq returned an empty response.")
                return self._unavailable_result()

            clean_txt = raw_text.strip()
            if clean_txt.startswith("```json"):
                clean_txt = clean_txt[7:]
            if clean_txt.startswith("```"):
                clean_txt = clean_txt[3:]
            if clean_txt.endswith("```"):
                clean_txt = clean_txt[:-3]
            clean_txt = clean_txt.strip()

            # Extract the first {...} JSON object even if there's extra text around it
            match = re.search(r"\{.*\}", clean_txt, re.DOTALL)
            if match:
                clean_txt = match.group(0)

            data = json.loads(clean_txt)
            return DiseaseAnalysisResult(**data)

        except json.JSONDecodeError as e:
            logger.error(f"Groq response was not valid JSON: {e}")
            return self._unavailable_result()
        except Exception as e:
            logger.error(f"Groq Vision call failed: {e}")
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
