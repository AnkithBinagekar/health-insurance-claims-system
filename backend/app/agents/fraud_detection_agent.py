from backend.app.core.base_agent import BaseAgent
from backend.app.schemas.claim import ClaimContext
from backend.app.schemas.trace import AgentTrace

class FraudDetectionAgent(BaseAgent):
    """
    Evaluates claims history and current claim thresholds to generate fraud signals.
    Does not halt the pipeline; it flags for MANUAL_REVIEW.
    """
    async def _process(self, context: ClaimContext, trace: AgentTrace) -> ClaimContext:
        policy_dict = context.hydrated.policy.model_extra or {}
        fraud_rules = policy_dict.get("fraud_thresholds", {})
        
        same_day_limit = fraud_rules.get("same_day_claims_limit", 2)
        treatment_date = context.input.treatment_date
        
        # 1. Velocity Check: Same-Day Claims
        same_day_claims = [
            c for c in context.hydrated.claims_history 
            if c.get("date") == treatment_date
        ]
        
        if len(same_day_claims) >= same_day_limit:
            msg = f"Fraud Signal: {len(same_day_claims)} prior claims detected for {treatment_date}."
            trace.warnings.append(msg)
            context.result.notes.append(msg)
            trace.decision_impact = "Flagged for MANUAL_REVIEW due to velocity limits."
            
        # 2. Threshold Check: High Value Claim
        high_value_threshold = fraud_rules.get("high_value_claim_threshold", 25000)
        if context.input.claimed_amount > high_value_threshold:
            msg = f"Fraud Signal: Claim amount (₹{context.input.claimed_amount}) exceeds high-value threshold."
            trace.warnings.append(msg)
            context.result.notes.append(msg)
            trace.decision_impact = "Flagged for MANUAL_REVIEW due to high claim amount."
            
        return context