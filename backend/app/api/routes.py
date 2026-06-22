from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from backend.app.services.claim_service import ClaimService
from backend.app.schemas.enums import ClaimCategory

router = APIRouter(prefix="/api/claims", tags=["Claims"])
service = ClaimService()

@router.post("/submit")
async def submit_claim(
    member_id: str = Form(...),
    claim_category: ClaimCategory = Form(...),
    claimed_amount: float = Form(...),
    treatment_date: str = Form(...),
    files: List[UploadFile] = File(...)
):
    try:
        claim_id = await service.submit_claim(
            member_id=member_id,
            claim_category=claim_category,
            claimed_amount=claimed_amount,
            treatment_date=treatment_date,
            files=files
        )
        return {"status": "success", "claim_id": claim_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{claim_id}")
async def get_claim_trace(claim_id: str):
    try:
        context = service.get_claim_result(claim_id)
        # We serialize the entire Context to power the TraceViewer UI
        return context.model_dump() 
    except KeyError:
        raise HTTPException(status_code=404, detail="Claim not found")