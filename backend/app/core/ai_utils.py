import mimetypes
import pathlib
import hashlib
import json
import os
from google import genai
from google.genai import types
from backend.app.core.config import settings
from typing import Any
from tenacity import retry, wait_exponential, stop_after_attempt # <-- ADD THIS

# Initialize the global Gemini client
ai_client = genai.Client(api_key=settings.gemini_api_key)

CACHE_DIR = ".cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_document_part(file_path: str) -> types.Part:
    path = pathlib.Path(file_path)
    mime_type, _ = mimetypes.guess_type(path)
    if not mime_type:
        mime_type = "application/octet-stream"
    with open(path, "rb") as f:
        doc_bytes = f.read()
    return types.Part.from_bytes(data=doc_bytes, mime_type=mime_type)

# --- NEW: Robust Retry Wrapper ---
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=15), # Wait 2s, 4s, 8s, 15s...
    stop=stop_after_attempt(4), # Give up after 4 total tries
    reraise=True
)
def _execute_gemini_call(model_name, prompt, doc_part, config):
    """Executes the Gemini call with automatic retries for 503/429 errors."""
    return ai_client.models.generate_content(
        model=model_name,
        contents=[prompt, doc_part],
        config=config
    )
# ---------------------------------

async def cached_generate_content(
    file_path: str, 
    prompt: str, 
    agent_name: str, 
    model_name: str, 
    response_schema: Any = None
) -> Any:
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    signature = f"{agent_name}_{model_name}_{prompt}".encode('utf-8') + file_bytes
    cache_key = hashlib.md5(signature).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{cache_key}.json")

    if os.path.exists(cache_path):
        print(f"✅ CACHE HIT: {agent_name} (Key: {cache_key[:8]})")
        with open(cache_path, "r", encoding="utf-8") as f:
            cached_text = f.read()
            if response_schema:
                return response_schema.model_validate_json(cached_text)
            return cached_text

    print(f"⚠️ CACHE MISS: Calling Gemini for {agent_name}...")
    doc_part = get_document_part(file_path)
    
    config = types.GenerateContentConfig(
        temperature=0.1,
        response_mime_type="application/json" if response_schema else "text/plain",
        response_schema=response_schema if response_schema else None
    )

    # --- UPDATED: Use the retry wrapper instead of direct client call ---
    response = _execute_gemini_call(model_name, prompt, doc_part, config)

    result_text = response.text
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(result_text)

    if response_schema:
        return response_schema.model_validate_json(result_text)
    return result_text