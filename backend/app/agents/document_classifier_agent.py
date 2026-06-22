import json
from pydantic import BaseModel, Field
from google.genai import types

from backend.app.core.base_agent import BaseAgent
from backend.app.schemas.claim import ClaimContext
from backend.app.schemas.trace import AgentTrace
from backend.app.schemas.enums import DocumentType
from backend.app.core.config import settings
from backend.app.core.ai_utils import ai_client, get_document_part

class ClassificationOutput(BaseModel):
    detected_type: DocumentType = Field(description="The primary classification of the document.")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0.")

class DocumentClassifierAgent(BaseAgent):
    
    async def _process(self, context: ClaimContext, trace: AgentTrace) -> ClaimContext:
        model = settings.flash_model
        
        for doc in context.input.documents:
            if doc.detected_type:
                continue # Skip if already classified
                
            prompt = """
            Analyze this medical document and classify it. 
            Select the most accurate document type from the allowed enum values.
            If it is completely unrelated to medical claims, select UNKNOWN.
            """
            
            doc_part = get_document_part(doc.storage_url)
            
            response = ai_client.models.generate_content(
                model=model,
                contents=[doc_part, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ClassificationOutput,
                    temperature=0.1
                )
            )
            
            result = ClassificationOutput.model_validate_json(response.text)
            doc.detected_type = result.detected_type
            trace.extracted_keys.append(f"{doc.file_name} -> {result.detected_type.value}")
            
        return context