from typing import Optional, List
from pydantic import BaseModel, Field


from backend.app.core.base_agent import BaseAgent
from backend.app.schemas.claim import ClaimContext
from backend.app.schemas.trace import AgentTrace
from backend.app.schemas.domain import ExtractedDocumentData
from backend.app.core.config import settings
from backend.app.core.ai_utils import cached_generate_content

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
       # model = settings.pro_model 
        model = settings.flash_model
        for doc in context.input.documents:
            # Add this safe fallback
            doc_type_str = doc.detected_type.value if doc.detected_type else "medical document"
            
            prompt = f"""
            Extract all available structured data from this {doc_type_str}.
            If a field is not present, omit it or return null.
            Pay strict attention to numbers, line item amounts, and totals.
            Ensure doctor registration numbers match standard Indian formats.
            
            CRITICAL INSTRUCTION FOR LINE ITEMS:
            For every line item extracted, you must provide its exact 2D bounding box 
            coordinates from the image. Return the coordinates as a list of 4 integers 
            in the format [ymin, xmin, ymax, xmax] scaled to 1000.
            """
            
            ocr_result = await cached_generate_content(
                 file_path=doc.storage_url,
                 prompt=prompt,
                 agent_name="OCRExtractionAgent",
                 model_name=model,
                 response_schema=OcrOutputSchema
             )
             
            extracted_dict = ocr_result.model_dump(exclude_none=True)
            
            # Map into the domain schema
            doc.extracted_data = ExtractedDocumentData(**extracted_dict)
            trace.extracted_keys.extend(extracted_dict.keys())
            
        return context