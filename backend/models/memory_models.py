from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


MessageRole = Literal["system", "user", "assistant"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    role: MessageRole
    content: str = Field(..., min_length=1, max_length=10000)
    created_at: datetime = Field(default_factory=utc_now)
    tokens_estimate: Optional[int] = Field(default=None, ge=0)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message content cannot be empty.")
        return value


class MemorySession(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=200)
    messages: List[MemoryMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    summary: Optional[str] = Field(default=None, max_length=4000)
    tags: List[str] = Field(default_factory=list)

    @field_validator("session_id")
    @classmethod
    def normalize_session_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("session_id cannot be empty.")
        return value

    def add_message(self, role: MessageRole, content: str) -> MemoryMessage:
        message = MemoryMessage(role=role, content=content)
        self.messages.append(message)
        self.updated_at = utc_now()
        return message

    def trim_messages(self, max_messages: int) -> None:
        if max_messages < 1:
            raise ValueError("max_messages must be greater than 0")
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]
            self.updated_at = utc_now()

    def to_llm_messages(self) -> List[dict]:
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]


class MemorySnapshot(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=200)
    summary: str = Field(..., min_length=1, max_length=4000)
    created_at: datetime = Field(default_factory=utc_now)