import mimetypes
import pathlib
import hashlib
import json
import os
from google import genai
from google.genai import types
from backend.app.core.config import settings
from typing import Any

# Initialize the global Gemini client
ai_client = genai.Client(api_key=settings.gemini_api_key)

# Ensure cache directory exists
CACHE_DIR = ".cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_document_part(file_path: str) -> types.Part:
    """Converts a local file into a Gemini-compatible Part object."""
    path = pathlib.Path(file_path)
    mime_type, _ = mimetypes.guess_type(path)
    if not mime_type:
        mime_type = "application/octet-stream"
        
    with open(path, "rb") as f:
        doc_bytes = f.read()
        
    return types.Part.from_bytes(data=doc_bytes, mime_type=mime_type)

async def cached_generate_content(
    file_path: str, 
    prompt: str, 
    agent_name: str, 
    model_name: str, 
    response_schema: Any = None
) -> Any:
    """
    Transparent caching proxy for Gemini. 
    Hashes the file bytes, prompt, and agent name to guarantee unique, deterministic responses.
    """
    # 1. Read bytes for hashing
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    # 2. Generate unique MD5 hash signature
    signature = f"{agent_name}_{model_name}_{prompt}".encode('utf-8') + file_bytes
    cache_key = hashlib.md5(signature).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{cache_key}.json")

    # 3. Check Cache
    if os.path.exists(cache_path):
        print(f"✅ CACHE HIT: {agent_name} (Key: {cache_key[:8]})")
        with open(cache_path, "r", encoding="utf-8") as f:
            cached_text = f.read()
            # If using Pydantic structured outputs, validate it back into the model
            if response_schema:
                return response_schema.model_validate_json(cached_text)
            return cached_text

    # 4. Cache Miss -> Call Gemini
    print(f"⚠️ CACHE MISS: Calling Gemini for {agent_name}...")
    doc_part = get_document_part(file_path)
    
    # Configure structured outputs if requested
    config = types.GenerateContentConfig(
        temperature=0.1,
        response_mime_type="application/json" if response_schema else "text/plain",
        response_schema=response_schema if response_schema else None
    )

    response = ai_client.models.generate_content(
        model=model_name,
        contents=[prompt, doc_part],
        config=config
    )

    # 5. Save to Cache
    result_text = response.text
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(result_text)

    # Return structured output or raw text
    if response_schema:
        return response_schema.model_validate_json(result_text)
    return result_text