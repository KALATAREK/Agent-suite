from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, EmailStr


class BaseRequest(BaseModel):
    session_id: Optional[str] = Field(default="default", max_length=200)
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("session_id")
    @classmethod
    def normalize_session_id(cls, value: Optional[str]) -> str:
        if not value:
            return "default"
        return value.strip()


class ChatRequest(BaseRequest):
    message: str = Field(..., min_length=1, max_length=5000)

    @field_validator("message")
    @classmethod
    def clean_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be empty")
        return value


class AnalyzeRequest(BaseRequest):
    input: str = Field(..., min_length=1, max_length=10000)

    @field_validator("input")
    @classmethod
    def clean_input(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Input cannot be empty")
        return value


class AutomateRequest(BaseRequest):
    input: str = Field(..., min_length=1, max_length=10000)

    @field_validator("input")
    @classmethod
    def clean_input(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Input cannot be empty")
        return value


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 6:
            raise ValueError("Password too short")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("password")
    @classmethod
    def clean_password(cls, value: str) -> str:
        return value.strip()


class GoogleAuthRequest(BaseModel):
    credential: str = Field(..., min_length=1)