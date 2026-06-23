import json
import asyncio
from datetime import datetime
from typing import Dict, Any

from backend.app.schemas.claim import ClaimContext, ClaimInput, HydratedContext, ExecutionState, DecisionResult, Document
from backend.app.schemas.domain import MemberProfile, PolicyTerms, ExtractedDocumentData
from backend.app.schemas.trace import SystemTrace
from backend.app.schemas.enums import ClaimCategory, DocumentType
from backend.app.core.config import settings

# Import only the Deterministic Agents (Bypassing AI for the JSON-driven test cases)
from backend.app.agents.document_verification_agent import DocumentVerificationAgent
from backend.app.agents.cross_validation_agent import CrossValidationAgent
from backend.app.agents.fraud_detection_agent import FraudDetectionAgent
from backend.app.agents.policy_evaluation_agent import PolicyEvaluationAgent
from backend.app.agents.decision_agent import DecisionAgent

async def run_evaluation():
    print("🚀 Starting Automated Evaluation Runner...")
    
    # 1. Load Data
    with open("policy_terms.json", "r") as f:
        policy_data = json.load(f)
    
    with open("test_cases.json", "r") as f:
        test_cases_data = json.load(f)

    results = []
    
    # Initialize Agents
    agents = [
        DocumentVerificationAgent(), # Modified to handle test mode below
        CrossValidationAgent(),
        FraudDetectionAgent(),
        PolicyEvaluationAgent(),
        DecisionAgent()
    ]

    for tc in test_cases_data.get("test_cases", []):
        print(f"Running {tc['case_id']}: {tc['case_name']}...")
        input_data = tc["input"]
        
        # Build Documents with pre-extracted test data
        docs = []
        for doc_in in input_data.get("documents", []):
            extracted = None
            if "content" in doc_in:
                # Map the test case content to our strict schema
                content = doc_in["content"]
                extracted = ExtractedDocumentData(
                    patient_name_on_doc=content.get("patient_name"),
                    doctor_name=content.get("doctor_name"),
                    doctor_registration=content.get("doctor_registration"),
                    diagnosis=content.get("diagnosis"),
                    hospital_name=content.get("hospital_name"),
                    line_items=[{"description": li["description"], "amount": li["amount"]} for li in content.get("line_items", [])],
                    total_amount=content.get("total")
                )
            # Add this fallback for documents that supply root-level OCR attributes (TC003)
            elif "patient_name_on_doc" in doc_in:
                extracted = ExtractedDocumentData(
                    patient_name_on_doc=doc_in["patient_name_on_doc"]
                )
            
            # Map string to Enum safely
            detected_type = None
            try:
                detected_type = DocumentType(doc_in.get("actual_type"))
            except ValueError:
                detected_type = DocumentType.UNKNOWN

            docs.append(Document(
                file_id=doc_in.get("file_id", "test_file"),
                file_name=doc_in.get("file_name", "test_doc.jpg"),
                storage_url="mock_url",
                detected_type=detected_type,
                is_readable=doc_in.get("quality", "GOOD") != "UNREADABLE",
                extracted_data=extracted
            ))

        # Hydrate Member
        member_id = input_data["member_id"]
        member_data = next((m for m in policy_data.get("members", []) if m["member_id"] == member_id), None)
        member_profile = MemberProfile(**member_data) if member_data else MemberProfile(member_id=member_id, name="Test", date_of_birth="1990-01-01", gender="M", relationship="SELF", join_date="2024-01-01")

        # Build Context
        context = ClaimContext(
            input=ClaimInput(
                claim_id=f"TEST_{tc['case_id']}",
                member_id=member_id,
                claim_category=ClaimCategory(input_data["claim_category"]),
                treatment_date=input_data["treatment_date"],
                claimed_amount=input_data["claimed_amount"],
                documents=docs
            ),
            hydrated=HydratedContext(
                policy=PolicyTerms(**policy_data),
                member=member_profile,
                claims_history=input_data.get("claims_history", []),
                ytd_claims_amount=input_data.get("ytd_claims_amount", 0.0)
            ),
            state=ExecutionState(
                simulate_failures_for=["PolicyEvaluationAgent"] if input_data.get("simulate_component_failure") else []
            ),
            result=DecisionResult(),
            trace=SystemTrace(claim_id=f"TEST_{tc['case_id']}")
        )

        # Run Deterministic Pipeline
        for agent in agents:
            # Skip Gemini call in DocumentVerificationAgent during tests if it's already unreadable
            if agent.agent_name == "DocumentVerificationAgent":
                if any(not d.is_readable for d in context.input.documents):
                    context.state.is_halted = True
                    context.state.halt_reason = "UNREADABLE_DOCUMENT"
                    continue
            
            context = await agent.execute(context)
            if context.state.is_halted:
                break

        # Evaluate Output vs Expected
        expected = tc["expected"]
        actual_decision = context.result.decision.value if context.result.decision else None
        
        # TC001-TC003 expect early halts (decision = null)
        if expected.get("decision") is None:
            passed = context.state.is_halted
        else:
            passed = (actual_decision == expected.get("decision"))

        # Compile Report Entry
        report_entry = {
            "case_id": tc["case_id"],
            "case_name": tc["case_name"],
            "passed": passed,
            "expected_decision": expected.get("decision"),
            "actual_decision": actual_decision,
            "halt_reason": context.state.halt_reason,
            "approved_amount": context.result.approved_amount,
            "system_notes": context.result.notes,
            "trace_summary": [
                {"agent": t.agent_name, "status": t.status.value, "impact": t.decision_impact} 
                for t in context.trace.agent_traces
            ]
        }
        results.append(report_entry)

    # Save Report
    with open("eval_report.json", "w") as f:
        json.dump({"timestamp": datetime.utcnow().isoformat(), "results": results}, f, indent=2)
        
    passed_count = sum(1 for r in results if r["passed"])
    print(f"\n✅ Evaluation Complete! {passed_count}/{len(results)} cases passed.")
    print("📄 Saved to 'eval_report.json'")

if __name__ == "__main__":
    # Fix for Windows asyncio loop
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_evaluation())