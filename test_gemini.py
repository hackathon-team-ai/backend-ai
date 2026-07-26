"""
Backend च्या root folder (backend-ai) मध्ये ठेवून चालवा:
python test_gemini.py
"""
import os
import sys

try:
    from app.core.config import settings
    api_key = settings.GEMINI_API_KEY.strip()
    model_name = settings.GEMINI_MODEL or "gemini-2.0-flash"
    print(f"Loaded API key (masked): {api_key[:8]}...{api_key[-4:]}")
    print(f"Model: {model_name}")
except Exception as e:
    print("!! Could not load settings from app.core.config:", e)
    sys.exit(1)

try:
    from google import genai
    print("google-genai package: OK, imported successfully")
except Exception as e:
    print("!! google-genai import FAILED:", e)
    print(">> Run: pip install google-genai")
    sys.exit(1)

try:
    client = genai.Client(api_key=api_key)
    print("Client created successfully. Now calling generate_content...")
    response = client.models.generate_content(
        model=model_name,
        contents="Say hello in one short sentence.",
    )
    print("\n=== SUCCESS ===")
    print("Response:", response.text)
except Exception as e:
    print("\n=== FAILED ===")
    print("Error type:", type(e).__name__)
    print("Error message:", str(e))