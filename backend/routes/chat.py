from fastapi import APIRouter, Depends, HTTPException

from models.request_models import ChatRequest
from models.response_models import BaseResponse
from agents.agent_brain import run_agent
from services.deps import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=BaseResponse)
async def chat(
    req: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    try:
        result = await run_agent(
            session_id=req.session_id,
            message=req.message
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))