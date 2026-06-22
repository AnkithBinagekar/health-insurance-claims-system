from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from backend.app.schemas.enums import AgentStatus

class ConfidenceEvent(BaseModel):
    """An immutable ledger entry explaining a change in system confidence."""
    agent_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    penalty_applied: float
    reason: str

class AgentTrace(BaseModel):
    agent_name: str
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    execution_time_ms: Optional[float] = None
    status: AgentStatus = AgentStatus.PENDING
    
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    decision_impact: Optional[str] = None
    extracted_keys: List[str] = Field(default_factory=list)

class SystemTrace(BaseModel):
    claim_id: str
    overall_status: str = "PROCESSING"
    
    # Confidence is now a computed property based on the base score minus ledger penalties
    base_confidence: float = 1.0
    confidence_ledger: List[ConfidenceEvent] = Field(default_factory=list)
    agent_traces: List[AgentTrace] = Field(default_factory=list)

    @property
    def current_confidence_score(self) -> float:
        total_penalty = sum(event.penalty_applied for event in self.confidence_ledger)
        return max(0.0, round(self.base_confidence - total_penalty, 2))