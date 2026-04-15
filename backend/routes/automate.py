from fastapi import APIRouter, Depends, HTTPException

from models.request_models import AutomateRequest
from models.response_models import BaseResponse
from agents.automator_agent import handle_automator
from services.parsing_service import parse_input
from services.deps import get_current_user

router = APIRouter(prefix="/automate", tags=["automate"])


@router.post("/", response_model=BaseResponse)
async def automate(
    req: AutomateRequest,
    user_id: str = Depends(get_current_user)
):
    try:
        parsed = parse_input(req.input)
        result = await handle_automator(parsed["cleaned"])

        return {
            "type": "automate",
            "content": result,
            "meta": {}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))