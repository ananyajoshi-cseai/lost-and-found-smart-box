from fastapi import APIRouter, HTTPException, Response
from ..schemas import ClaimIn, ClaimReceipt
from ..services import claims

router = APIRouter()


@router.post("/api/claims", status_code=201, response_model=ClaimReceipt)
def submit_claim(body: ClaimIn, response: Response):
    response.headers["Cache-Control"] = "no-store"
    try:
        return claims.submit_claim(body.item_id, body.contact, body.evidence)
    except claims.NotFound as error:
        raise HTTPException(404, str(error)) from None
    except claims.Conflict as error:
        raise HTTPException(409, str(error)) from None
