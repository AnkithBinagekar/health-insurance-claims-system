import pytest
from backend.app.agents.policy_evaluation_agent import PolicyEvaluationAgent
from backend.app.schemas.claim import (
    ClaimContext, ClaimInput, HydratedContext, 
    ExecutionState, DecisionResult, Document, LineItem  # <-- Added LineItem import here!
)
from backend.app.schemas.domain import (
    MemberProfile, PolicyTerms, ExtractedDocumentData
)
from backend.app.schemas.trace import SystemTrace
from backend.app.schemas.enums import ClaimCategory, DocumentType

def build_mock_context(claimed_amount: float, category: ClaimCategory, member_tier: str = "Standard") -> ClaimContext:
    mock_doc = Document(
        file_id="fake_id",
        file_name="bill.png",
        storage_url="fake_url",
        detected_type=DocumentType.HOSPITAL_BILL,
        is_readable=True,
        extracted_data=ExtractedDocumentData(
            patient_name_on_doc="Test User",
            doctor_name="Dr. Smith",
            doctor_registration="KA/12345", 
            diagnosis="Viral Fever",        
            hospital_name="Plum Care",
            # <-- Wrapped the data in a LineItem object!
            line_items=[LineItem(description="Consultation Fee", amount=claimed_amount, is_covered=True)],
            total_amount=claimed_amount
        )
    )

    return ClaimContext(
        input=ClaimInput(
            claim_id="TEST_UNIT_001",
            member_id="EMP001",
            claim_category=category,
            treatment_date="2024-11-01",
            claimed_amount=claimed_amount,
            documents=[mock_doc] 
        ),
        hydrated=HydratedContext(
            policy=PolicyTerms(
                policy_id="POL123",
                policy_name="Plum Standard Corporate",
                coverage_categories=["CONSULTATION", "PHARMACY"],
                copay_percentage=10.0 if member_tier == "Standard" else 0.0,
                members=[] 
            ),
            member=MemberProfile(
                member_id="EMP001", name="Test User", date_of_birth="1990-01-01", 
                gender="M", relationship="SELF", join_date="2024-01-01"
            ),
            ytd_claims_amount=0.0,
            claims_history=[]
        ),
        state=ExecutionState(),
        result=DecisionResult(), 
        trace=SystemTrace(claim_id="TEST_UNIT_001")
    )

@pytest.mark.asyncio
async def test_standard_copay_calculation():
    """Test that a 10% co-pay is correctly deducted from the approved amount."""
    agent = PolicyEvaluationAgent()
    context = build_mock_context(claimed_amount=1000.0, category=ClaimCategory.CONSULTATION)
    
    updated_context = await agent.execute(context)
    
    assert updated_context.result.approved_amount == 900.0
    
    notes_str = " ".join(updated_context.result.notes)
    assert "Co-pay" in notes_str or "10" in notes_str

@pytest.mark.asyncio
async def test_uncovered_category_rejection():
    """Test that submitting a claim for an uncovered category flags a rejection."""
    agent = PolicyEvaluationAgent()
    context = build_mock_context(claimed_amount=5000.0, category=ClaimCategory.DENTAL)
    
    updated_context = await agent.execute(context)
    
    assert updated_context.result.approved_amount == 0.0
    
    reasons_str = " ".join(updated_context.result.rejection_reasons)
    assert "DENTAL" in reasons_str or "not covered" in reasons_str