from typing import Optional, List
from pydantic import BaseModel, Field
from google.genai import types

from backend.app.core.base_agent import BaseAgent
from backend.app.schemas.claim import ClaimContext
from backend.app.schemas.trace import AgentTrace
from backend.app.schemas.domain import ExtractedDocumentData
from backend.app.core.config import settings
from backend.app.core.ai_utils import ai_client, get_document_part

# Specific schemas for Gemini to adhere to
class ExtractedLineItem(BaseModel):
    description: str
    amount: float

class OcrOutputSchema(BaseModel):
    patient_name_on_doc: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_registration: Optional[str] = None
    date: Optional[str] = None
    hospital_name: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    medicines: List[str] = Field(default_factory=list)
    tests_ordered: List[str] = Field(default_factory=list)
    line_items: List[ExtractedLineItem] = Field(default_factory=list)
    total_amount: Optional[float] = None

class OCRExtractionAgent(BaseAgent):
    
    async def _process(self, context: ClaimContext, trace: AgentTrace) -> ClaimContext:
        # Use Pro model for deep OCR extraction as per assignment hint
        model = settings.pro_model 
        
        for doc in context.input.documents:
            prompt = f"""
            Extract all available structured data from this {doc.detected_type.value}.
            If a field is not present, omit it or return null.
            Pay strict attention to numbers, line item amounts, and totals.
            Ensure doctor registration numbers match standard Indian formats (e.g., KA/12345/2015).
            """
            
            doc_part = get_document_part(doc.storage_url)
            
            response = ai_client.models.generate_content(
                model=model,
                contents=[doc_part, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=OcrOutputSchema,
                    temperature=0.0 # Deterministic extraction
                )
            )
            
            extracted_dict = OcrOutputSchema.model_validate_json(response.text).model_dump(exclude_none=True)
            
            # Map into the domain schema
            doc.extracted_data = ExtractedDocumentData(**extracted_dict)
            trace.extracted_keys.extend(extracted_dict.keys())
            
        return context