from backend.app.schemas.claim import ClaimContext
from backend.app.schemas.enums import AgentStatus

from backend.app.agents.document_classifier_agent import DocumentClassifierAgent
from backend.app.agents.document_verification_agent import DocumentVerificationAgent
from backend.app.agents.ocr_extraction_agent import OCRExtractionAgent
from backend.app.agents.cross_validation_agent import CrossValidationAgent
from backend.app.agents.fraud_detection_agent import FraudDetectionAgent
from backend.app.agents.policy_evaluation_agent import PolicyEvaluationAgent
from backend.app.agents.decision_agent import DecisionAgent

class OrchestratorAgent:
    """
    The DAG (Directed Acyclic Graph) router for our pipeline.
    """
    def __init__(self):
        # We define the sequence explicitly here. 
        # In a fully autonomous system, an LLM might decide this routing, 
        # but insurance requires deterministic execution paths.
        self.pipeline = [
            DocumentClassifierAgent(),
            DocumentVerificationAgent(),
            OCRExtractionAgent(),
            CrossValidationAgent(),
            FraudDetectionAgent(),
            PolicyEvaluationAgent(),
            DecisionAgent()
        ]

    async def process_claim(self, context: ClaimContext) -> ClaimContext:
        for agent in self.pipeline:
            # The BaseAgent handles the try/except and skipped execution logic
            context = await agent.execute(context)
            
            # If a deterministic gatekeeper halts the pipeline, we break the loop.
            if context.state.is_halted:
                break
                
        # Finalize overall trace status
        if context.state.is_halted:
            context.trace.overall_status = "HALTED"
        else:
            context.trace.overall_status = "COMPLETED"
            
        return context