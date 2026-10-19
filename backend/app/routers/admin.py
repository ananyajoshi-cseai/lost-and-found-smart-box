from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException, Path, Response
from ..auth import require_staff
from ..schemas import ApprovalOut, DecisionIn, RejectionOut, StaffClaimsOut
from ..services import claims

router = APIRouter()
ClaimId = Annotated[int, Path(gt=0)]


@router.get("/api/admin/claims", response_model=StaffClaimsOut, dependencies=[Depends(require_staff)])
def list_claims(response: Response, status: Literal["pending", "approved", "rejected"] | None = None):
    response.headers["Cache-Control"] = "no-store"
    return claims.list_claims(status)


def decide(claim_id, actor, reason, action):
    try:
        return claims.decide_claim(claim_id, actor, reason, action)
    except claims.NotFound as error:
        raise HTTPException(404, str(error)) from None
    except claims.Conflict as error:
        raise HTTPException(409, str(error)) from None


@router.post("/api/admin/claims/{claim_id}/approve", response_model=ApprovalOut)
def approve(claim_id: ClaimId, body: DecisionIn, response: Response, actor=Depends(require_staff)):
    response.headers["Cache-Control"] = "no-store"
    return decide(claim_id, actor, body.reason, "approved")


@router.post("/api/admin/claims/{claim_id}/reject", response_model=RejectionOut)
def reject(claim_id: ClaimId, body: DecisionIn, response: Response, actor=Depends(require_staff)):
    response.headers["Cache-Control"] = "no-store"
    return decide(claim_id, actor, body.reason, "rejected")
