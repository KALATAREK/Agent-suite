from fastapi import APIRouter, Depends, HTTPException

from models.request_models import AnalyzeRequest
from models.response_models import BaseResponse
from services.analysis_service import analyze_business
from services.parsing_service import parse_input
from services.deps import get_current_user

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("/", response_model=BaseResponse)
async def analyze(
    req: AnalyzeRequest,
    user_id: str = Depends(get_current_user)
):
    try:
        parsed = parse_input(req.input)
        result = await analyze_business(parsed["cleaned"])

        return {
            "type": "analysis",
            "content": result.get("content"),
            "meta": result.get("meta", {})
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))