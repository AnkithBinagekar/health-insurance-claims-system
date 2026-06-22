from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas.enums import DecisionType, ClaimCategory, DocumentType
from backend.app.schemas.trace import SystemTrace
from backend.app.schemas.domain import MemberProfile, PolicyTerms, ExtractedDocumentData

class Document(BaseModel):
    file_id: str
    file_name: str
    storage_url: str
    detected_type: Optional[DocumentType] = None
    quality_score: Optional[float] = None
    is_readable: bool = True
    extracted_data: Optional[ExtractedDocumentData] = None

class LineItem(BaseModel):
    description: str
    amount: float
    is_covered: bool = True
    rejection_reason: Optional[str] = None

class ClaimInput(BaseModel):
    """Data explicitly provided by the user."""
    claim_id: str
    member_id: str
    claim_category: ClaimCategory
    treatment_date: str
    claimed_amount: float
    documents: List[Document]

class HydratedContext(BaseModel):
    """Data injected by the backend from databases/JSON."""
    policy: PolicyTerms
    member: MemberProfile
    ytd_claims_amount: float = 0.0
    claims_history: List[Dict[str, Any]] = Field(default_factory=list)
class ExecutionState(BaseModel):
    """Finite state machine variables mutated by agents."""
    is_halted: bool = False
    halt_reason: Optional[str] = None
    halt_message: Optional[str] = None
    # Flexible testing support: pass agent names here to force failures
    simulate_failures_for: List[str] = Field(default_factory=list) 

class DecisionResult(BaseModel):
    """The final deterministic output of the system."""
    decision: Optional[DecisionType] = None
    approved_amount: float = 0.0
    rejection_reasons: List[str] = Field(default_factory=list)
    line_items: List[LineItem] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)

class ClaimContext(BaseModel):
    """
    The master state object. Composed of segregated domain models.
    """
    input: ClaimInput
    hydrated: HydratedContext
    state: ExecutionState = Field(default_factory=ExecutionState)
    result: DecisionResult = Field(default_factory=DecisionResult)
    trace: SystemTrace