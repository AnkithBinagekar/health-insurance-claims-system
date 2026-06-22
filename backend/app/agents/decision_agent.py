from backend.app.core.base_agent import BaseAgent
from backend.app.schemas.claim import ClaimContext
from backend.app.schemas.trace import AgentTrace
from backend.app.schemas.enums import DecisionType

class DecisionAgent(BaseAgent):
    """
    Synthesizes the outputs of previous agents to reach a final deterministic verdict.
    """
    async def _process(self, context: ClaimContext, trace: AgentTrace) -> ClaimContext:
        
        # 1. Check for Hard Rejections
        if context.result.rejection_reasons:
            context.result.decision = DecisionType.REJECTED
            context.result.approved_amount = 0.0
            trace.decision_impact = "Final Decision: REJECTED due to policy rules."
            return context

        # 2. Check for Manual Review Routing (Fraud flags or degraded AI confidence)
        fraud_flagged = any("Fraud Signal" in note for note in context.result.notes)
        low_confidence = context.trace.current_confidence_score < 0.80
        
        if fraud_flagged or low_confidence:
            context.result.decision = DecisionType.MANUAL_REVIEW
            reason = "Fraud flags detected." if fraud_flagged else "Pipeline confidence degraded."
            trace.decision_impact = f"Routed to MANUAL_REVIEW. Reason: {reason}"
            return context

        # 3. Check for Approval vs Partial Approval
        claimed = context.input.claimed_amount
        approved = context.result.approved_amount
        
        if approved == 0:
            context.result.decision = DecisionType.REJECTED
        elif approved < claimed:
            context.result.decision = DecisionType.PARTIAL
        else:
            context.result.decision = DecisionType.APPROVED
            
        trace.decision_impact = f"Final Decision: {context.result.decision.value} (₹{approved})"
        
        return context