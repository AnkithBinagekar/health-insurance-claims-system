from backend.app.core.base_agent import BaseAgent
from backend.app.schemas.claim import ClaimContext
from backend.app.schemas.trace import AgentTrace
from backend.app.schemas.enums import DecisionType
from datetime import datetime

# Import our new deterministic math engine and its contracts
from backend.app.services.policy_service import (
    evaluate_claim,
    ClaimData,
    MemberData,
    PolicyData,
    LineItem
)

class DecisionAgent(BaseAgent):
    """
    Synthesizes the outputs of previous agents and executes strict 
    deterministic policy math to reach a final verdict.
    """
    async def _process(self, context: ClaimContext, trace: AgentTrace) -> ClaimContext:
        
        # 1. Check for manual review routing BEFORE doing math
        fraud_flagged = any("Fraud Signal" in note for note in context.result.notes)
        low_confidence = (context.trace.current_confidence_score or 0.0) < 0.80
        
        if fraud_flagged:
            context.result.decision = DecisionType.MANUAL_REVIEW
            context.result.approved_amount = 0.0
            trace.decision_impact = "Routed to MANUAL_REVIEW. Reason: Fraud flags detected."
            return context

        if low_confidence:
            context.result.notes.append("Manual review recommended due to degraded pipeline confidence.")
            trace.decision_impact = "Low confidence detected. Proceeding to math engine with warning."

        # 2. Extract the AI-parsed JSON safely, falling back to document-level test data
        extracted_data = getattr(context.state, "extracted_data", None)
        
        if not extracted_data:
            extracted_data = {"line_items": []}
            for doc in context.input.documents:
                if doc.extracted_data:
                    for key in ["hospital_name", "diagnosis", "procedure_name", "pre_auth_id"]:
                        if getattr(doc.extracted_data, key, None):
                            extracted_data[key] = getattr(doc.extracted_data, key)
                    for li in getattr(doc.extracted_data, "line_items", []):
                        extracted_data["line_items"].append(li if isinstance(li, dict) else {"description": li.description, "amount": li.amount})
        
        # 3. Map to our strict PolicyService Pydantic models
        try:
            # We use .model_dump() to convert your domain schemas into dicts 
            # so they perfectly load into the policy_service schemas
            policy_data = PolicyData(**context.hydrated.policy.model_dump())
            
            member_data = MemberData(
                member_id=context.hydrated.member.member_id,
                join_date=context.hydrated.member.join_date,
                ytd_claims_amount=context.hydrated.ytd_claims_amount
            )

            # Build line items safely
            line_items = [
                LineItem(description=item.get("description", "Unknown"), amount=float(item.get("amount", 0.0)))
                for item in extracted_data.get("line_items", [])
            ]

            claim_data = ClaimData(
                claim_id=context.input.claim_id,
                treatment_date=datetime.strptime(context.input.treatment_date, "%Y-%m-%d").date(),
                hospital_name=extracted_data.get("hospital_name", "Unknown Hospital"),
                diagnosis=extracted_data.get("diagnosis", "Unknown Diagnosis"),
                procedure_name=extracted_data.get("procedure_name"),
                pre_auth_id=extracted_data.get("pre_auth_id"),
                category_name=context.input.claim_category.value, # e.g., "CONSULTATION"
                line_items=line_items
            )
        except Exception as e:
            # If Pydantic fails to map the data (e.g., AI hallucinated bad numbers)
            context.result.decision = DecisionType.MANUAL_REVIEW
            trace.errors.append(f"Data mapping failed before math evaluation: {str(e)}")
            return context

        # 4. EXECUTE THE MATH ENGINE
        evaluation_result = evaluate_claim(claim_data, member_data, policy_data)

        # 5. Map the math results back into the overall ClaimContext
        # Convert string decisions back to Enums
        if evaluation_result.decision == "APPROVED":
            context.result.decision = DecisionType.APPROVED
        elif evaluation_result.decision == "PARTIAL":
            context.result.decision = DecisionType.PARTIAL
        else:
            context.result.decision = DecisionType.REJECTED

        context.result.approved_amount = evaluation_result.approved_amount
        context.result.rejection_reasons.extend(evaluation_result.rejection_reasons)
        
        # Save the detailed math steps to the notes for the UI
        for step in evaluation_result.trace:
            prefix = "✅" if step.passed else "❌"
            context.result.notes.append(f"{prefix} [{step.rule_name}] {step.notes}")

        trace.decision_impact = f"Math Engine executed. Final outcome: {context.result.decision.value} (₹{context.result.approved_amount})"
        
        return context