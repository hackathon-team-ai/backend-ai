import json
import logging
import re

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    genai = None
    genai_types = None

from app.core.config import settings
from app.schemas.disease import DiseaseAnalysisResult, TreatmentPlan

logger = logging.getLogger("krishimitra.disease")

# Models to try in order — first one that works is used
_GEMINI_VISION_MODELS = [
    "gemini-3-flash-preview",   # Working — primary choice
    "gemini-3.5-flash",         # Fallback 1
    "gemini-3.1-flash-lite",    # Fallback 2
    "gemini-2.0-flash",         # Fallback 3 (may be rate-limited on free tier)
    "gemini-2.0-flash-lite",    # Fallback 4
]

_DISEASE_PROMPT = """
You are an expert Agricultural Plant Pathologist. Analyze the uploaded image carefully.

Step 1 — Check whether the image shows an agricultural crop plant, leaf, or plant part.

IF the image is NOT a crop or plant leaf (e.g. it shows a human, person, face, animal, vehicle,
building, furniture, text document, random object, etc.):
  Return this JSON exactly:
  {
    "disease_name": "No crop/plant leaf detected in image",
    "is_healthy": false,
    "crop_type": "Not a Plant/Crop",
    "confidence": 0.0,
    "symptoms": [
      "The uploaded image does not appear to be a crop or plant leaf.",
      "Please upload a clear photograph of an agricultural crop leaf for disease analysis."
    ],
    "treatment": {"chemical": [], "organic": [], "dosage": "N/A"},
    "prevention": [
      "Ensure the photo is taken in good natural light",
      "Focus closely on the affected crop leaf",
      "Avoid uploading non-plant photos"
    ],
    "urgency_level": "Low"
  }

Step 2 — IF the image IS a crop or plant leaf:
  - Identify the crop type from visual features (shape, venation, color, texture).
  - Identify the specific disease, or state "Healthy Leaf" if there are no disease symptoms.
  - If healthy: set "is_healthy" to true and "urgency_level" to "Low".
  - Provide symptoms, treatment (chemical + organic + dosage), prevention tips, and urgency level.

Return ONLY a valid JSON object — no preamble, no explanation, no markdown fences:
{
  "disease_name": "Exact Disease Name or Healthy Leaf or No crop/plant leaf detected in image",
  "is_healthy": true or false,
  "crop_type": "Crop name (e.g. Tomato, Rice, Wheat, Cotton) or Not a Plant/Crop",
  "confidence": number between 0.0 and 99.0,
  "symptoms": ["Symptom 1", "Symptom 2"],
  "treatment": {
    "chemical": ["Chemical treatment 1"],
    "organic": ["Organic treatment 1"],
    "dosage": "Dosage instructions"
  },
  "prevention": ["Prevention tip 1", "Prevention tip 2"],
  "urgency_level": "Low" or "Medium" or "High" or "Critical"
}
"""


def _load_gemini_key() -> str:
    """
    Load GEMINI_API_KEY with multiple fallbacks:
    1. From pydantic settings (reads .env or .env/.env automatically)
    2. From OS environment variable directly
    3. By manually parsing .env/.env file (Windows folder quirk workaround)
    """
    import os

    # 1. From settings (already handles .env/.env path via _find_env_file)
    key = getattr(settings, "GEMINI_API_KEY", "").strip()
    if key:
        return key

    # 2. OS env var (if server was started with env var set)
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key

    # 3. Manual parse — disease_service.py is at backend-ai/app/services/
    #    dirname x3 => backend-ai root
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates = [
        os.path.join(base, ".env"),           # correct: backend-ai/.env (plain file)
        os.path.join(base, ".env", ".env"),   # Windows quirk: backend-ai/.env/.env
    ]
    for env_path in candidates:
        if os.path.isfile(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY"):
                            _, _, val = line.partition("=")
                            val = val.strip().strip('"').strip("'")
                            if val:
                                logger.info(f"GEMINI_API_KEY loaded manually from: {env_path}")
                                return val
            except Exception as e:
                logger.warning(f"Could not parse {env_path}: {e}")
    return ""


class DiseaseService:
    def __init__(self):
        # Defer actual client creation to first use
        # so that env vars are fully loaded by the time we need them
        self._initialized = False
        self.api_key = ""
        self.client = None
        self.model_name = None

    def _ensure_initialized(self):
        """Lazy init — called on first actual use, not at import time."""
        if self._initialized:
            return
        self._initialized = True

        self.api_key = _load_gemini_key()

        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in any location. Disease detection will be unavailable.")
            return

        logger.info(f"GEMINI_API_KEY loaded (length={len(self.api_key)})")

        if genai:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Gemini Vision client initialised.")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini Vision client: {e}")
                self.client = None
        else:
            logger.error("google-genai package not installed. Run: pip install google-genai")

    def _find_working_model(self) -> str | None:
        """Try each candidate model with a trivial text call; return the first that works."""
        for model in _GEMINI_VISION_MODELS:
            try:
                self.client.models.generate_content(model=model, contents="hello")
                logger.info(f"Using Gemini vision model: {model}")
                return model
            except Exception as e:
                logger.warning(f"Model {model} not available: {e}")
        return None

    async def analyze_leaf_image(self, image_path: str, filename: str) -> DiseaseAnalysisResult:
        """Analyze a leaf/crop photo using Gemini Vision."""
        self._ensure_initialized()  # lazy init on first call

        if not self.client:
            logger.error("Gemini Vision client not configured (missing/invalid GEMINI_API_KEY).")
            return self._api_not_configured_result()

        # Resolve model on first real call (lazy, cached)
        if not self.model_name:
            self.model_name = self._find_working_model()
            if not self.model_name:
                logger.error("No working Gemini vision model found.")
                return self._api_not_configured_result()

        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else "jpeg"
            mime = "image/png" if ext == "png" else "image/jpeg"

            image_part = genai_types.Part.from_bytes(data=image_bytes, mime_type=mime)

            res = self.client.models.generate_content(
                model=self.model_name,
                contents=[image_part, _DISEASE_PROMPT],
            )

            raw_text = res.text
            logger.info(f"Gemini raw response: {raw_text!r}")

            if not raw_text or not raw_text.strip():
                logger.error("Gemini returned an empty response.")
                return self._unavailable_result()

            clean_txt = raw_text.strip()

            # Strip markdown fences if present
            if clean_txt.startswith("```json"):
                clean_txt = clean_txt[7:]
            elif clean_txt.startswith("```"):
                clean_txt = clean_txt[3:]
            if clean_txt.endswith("```"):
                clean_txt = clean_txt[:-3]
            clean_txt = clean_txt.strip()

            # Extract the first complete {...} JSON block
            match = re.search(r"\{.*\}", clean_txt, re.DOTALL)
            if match:
                clean_txt = match.group(0)

            data = json.loads(clean_txt)
            return DiseaseAnalysisResult(**data)

        except json.JSONDecodeError as e:
            logger.error(f"Gemini response was not valid JSON: {e}\nRaw: {raw_text!r}")
            return self._unavailable_result()
        except Exception as e:
            logger.error(f"Gemini Vision call failed: {e}")
            return self._unavailable_result()

    # ------------------------------------------------------------------
    # Fallback results
    # ------------------------------------------------------------------

    def _api_not_configured_result(self) -> DiseaseAnalysisResult:
        """Returned when the API key is missing, invalid, or no model is available."""
        return DiseaseAnalysisResult(
            disease_name="Service Unavailable",
            is_healthy=False,
            crop_type="Unknown",
            confidence=0.0,
            symptoms=[
                "The disease analysis service is currently unavailable.",
                "Please ensure GEMINI_API_KEY is set and has available quota.",
            ],
            treatment=TreatmentPlan(chemical=[], organic=[], dosage="N/A"),
            prevention=[],
            urgency_level="Low",
        )

    def _unavailable_result(self) -> DiseaseAnalysisResult:
        """Returned when the image could not be analyzed due to an API or parse error."""
        return DiseaseAnalysisResult(
            disease_name="Analysis Failed",
            is_healthy=False,
            crop_type="Unknown",
            confidence=0.0,
            symptoms=["The image could not be analyzed. Please try again."],
            treatment=TreatmentPlan(chemical=[], organic=[], dosage="N/A"),
            prevention=[
                "Retake the photo in good natural light",
                "Focus closely on the affected leaf",
                "Avoid blurry or dark images",
            ],
            urgency_level="Low",
        )


disease_service = DiseaseService()
