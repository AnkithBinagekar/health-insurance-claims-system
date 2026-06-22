from typing import Optional, Dict, Any
from pydantic import BaseModel

class Document(BaseModel):
    """
    Represents an uploaded file.
    Does NOT store bytes directly to avoid memory bloat during agent execution.
    """
    file_id: str
    file_name: str
    storage_url: str  # URI to local temp or cloud storage
    
    # Filled by Classifier Agent
    detected_type: Optional[str] = None  # PRESCRIPTION, HOSPITAL_BILL, etc.
    
    # Filled by Verification Agent
    quality_score: Optional[float] = None
    is_readable: bool = True
    
    # Filled by OCR Extraction Agent
    extracted_data: Optional[Dict[str, Any]] = None
    patient_name_on_doc: Optional[str] = None