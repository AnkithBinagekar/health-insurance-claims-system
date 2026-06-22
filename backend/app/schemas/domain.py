from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class MemberProfile(BaseModel):
    member_id: str
    name: str
    date_of_birth: date
    gender: str
    relationship: str
    join_date: date
    dependents: List[str] = Field(default_factory=list)

class PolicyTerms(BaseModel):
    """
    Strict representation of policy_terms.json.
    Configured to allow extra fields temporarily as we build out the full schema hierarchy.
    """
    policy_id: str
    policy_name: str
    
    class Config:
        extra = "allow" 

class ExtractedDocumentData(BaseModel):
    """Base class for all OCR outputs, ensuring all extractions share a common shape."""
    patient_name_on_doc: Optional[str] = None
    doctor_name: Optional[str] = None
    date: Optional[str] = None
    
    class Config:
        extra = "allow" # Allows specific agents to append diagnosis, medicines, etc.