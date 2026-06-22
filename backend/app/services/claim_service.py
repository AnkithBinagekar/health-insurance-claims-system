import json
import uuid
import os
from datetime import datetime, timezone
from typing import List, Dict
from fastapi import UploadFile

from backend.app.schemas.claim import (
    ClaimContext, ClaimInput, HydratedContext, 
    Document, ExecutionState, DecisionResult
)
from backend.app.schemas.domain import MemberProfile, PolicyTerms
from backend.app.schemas.trace import SystemTrace
from backend.app.schemas.enums import ClaimCategory
from backend.app.agents.orchestrator_agent import OrchestratorAgent

# In-memory store for prototype observability (Replaces Postgres/MongoDB for this assignment)
DB_CLAIMS_STORE: Dict[str, ClaimContext] = {}

class ClaimService:
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.upload_dir = "temp_uploads"
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # Load the assignment policy terms into memory
        with open("policy_terms.json", "r") as f:
            self.raw_policy_data = json.load(f)

    async def submit_claim(
        self, 
        member_id: str, 
        claim_category: ClaimCategory, 
        claimed_amount: float, 
        treatment_date: str, 
        files: List[UploadFile]
    ) -> str:
        """
        Accepts the raw HTTP request, builds the execution context, and fires the pipeline.
        Returns the generated claim_id.
        """
        claim_id = f"CLM-{uuid.uuid4().hex[:8].upper()}"
        
        # 1. Handle File Uploads (Moving bytes out of memory)
        documents = []
        for file in files:
            file_id = f"F-{uuid.uuid4().hex[:6].upper()}"
            safe_filename = file.filename.replace(" ", "_")
            storage_path = os.path.join(self.upload_dir, f"{file_id}_{safe_filename}")
            
            with open(storage_path, "wb") as buffer:
                buffer.write(await file.read())
                
            documents.append(Document(
                file_id=file_id,
                file_name=file.filename,
                storage_url=storage_path
            ))

        # 2. Hydrate Context (Mocking a DB query for member data)
        policy_terms = PolicyTerms(**self.raw_policy_data)
        member_data = next((m for m in self.raw_policy_data.get("members", []) if m["member_id"] == member_id), None)
        
        if not member_data:
            raise ValueError(f"Member ID {member_id} not found in policy roster.")
            
        member_profile = MemberProfile(**member_data)

        # 3. Initialize the Master Context
        context = ClaimContext(
            input=ClaimInput(
                claim_id=claim_id,
                member_id=member_id,
                claim_category=claim_category,
                treatment_date=treatment_date,
                claimed_amount=claimed_amount,
                documents=documents
            ),
            hydrated=HydratedContext(
                policy=policy_terms,
                member=member_profile,
                ytd_claims_amount=0.0 # Would query DB here
            ),
            state=ExecutionState(),
            result=DecisionResult(),
            trace=SystemTrace(claim_id=claim_id)
        )

        # 4. Execute the Agentic Pipeline
        completed_context = await self.orchestrator.process_claim(context)
        
        # 5. Persist the final state
        DB_CLAIMS_STORE[claim_id] = completed_context
        
        return claim_id

    def get_claim_result(self, claim_id: str) -> ClaimContext:
        """Retrieves the processed claim and its full observability trace."""
        if claim_id not in DB_CLAIMS_STORE:
            raise KeyError(f"Claim {claim_id} not found.")
        return DB_CLAIMS_STORE[claim_id]