from google import genai
from google.genai import types
from backend.app.core.config import settings
import mimetypes
import pathlib

# Initialize the global Gemini client
ai_client = genai.Client(api_key=settings.gemini_api_key)

def get_document_part(file_path: str) -> types.Part:
    """
    Converts a local file into a Gemini-compatible Part object.
    In a fully scaled production environment, you would use the GenAI File API 
    for large PDFs, but inline data works well for standard multi-page claims.
    """
    path = pathlib.Path(file_path)
    mime_type, _ = mimetypes.guess_type(path)
    if not mime_type:
        mime_type = "application/octet-stream"
        
    with open(path, "rb") as f:
        doc_bytes = f.read()
        
    return types.Part.from_bytes(data=doc_bytes, mime_type=mime_type)