from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


# 🎯 BASE RESPONSE
class BaseResponse(BaseModel):
    type: str = Field(..., description="Response type (intent/module)")
    content: Any = Field(..., description="Main response payload")

    meta: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadata (confidence, quality, etc.)"
    )

    error: Optional[str] = Field(
        default=None,
        description="Error message if something failed"
    )


# 💬 ASSISTANT RESPONSE
class AssistantResponse(BaseModel):
    message: str = Field(..., description="AI reply")

    suggestions: Optional[List[str]] = Field(
        default=None,
        description="Optional suggestions for user actions"
    )


# 📊 ANALYZER RESPONSE
class AnalyzerData(BaseModel):
    seo: List[str] = Field(default_factory=list)
    ux: List[str] = Field(default_factory=list)
    conversion: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    score: int = Field(..., ge=1, le=10)


class AnalyzerResponse(BaseModel):
    data: AnalyzerData
    meta: Optional[Dict[str, Any]] = None


# ⚙️ AUTOMATOR RESPONSE
class AutomatorData(BaseModel):
    summary: str
    tasks: List[str]
    priority: Literal["low", "medium", "high"]
    reply: str
    client_type: Literal["vip", "normal", "low_value"]


class AutomatorResponse(BaseModel):
    data: AutomatorData
    meta: Optional[Dict[str, Any]] = None