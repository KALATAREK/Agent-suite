from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import SessionLocal
from models.db_models import Message
from services.deps import get_current_user
from services.llm_service import LLMService

router = APIRouter(prefix="/sessions", tags=["sessions"])


# 🔧 DB DEP
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 LISTA SESJI
@router.get("/")
async def get_sessions(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    rows = (
        db.query(
            Message.session_id,
            func.count(Message.id).label("messages")
        )
        .filter(Message.user_id == user_id)
        .group_by(Message.session_id)
        .order_by(func.max(Message.created_at).desc())
        .all()
    )

    return [
        {
            "session_id": r.session_id,
            "messages": r.messages
        }
        for r in rows
    ]


# 🔹 KONKRETNA SESJA
@router.get("/{session_id}")
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    messages = (
        db.query(Message)
        .filter(
            Message.session_id == session_id,
            Message.user_id == user_id
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    return [
        {"role": m.role, "content": m.content}
        for m in messages
    ]


# 🔹 SUMMARY
@router.post("/{session_id}/summary")
async def generate_summary(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    llm = LLMService()

    messages = (
        db.query(Message)
        .filter(
            Message.session_id == session_id,
            Message.user_id == user_id
        )
        .order_by(Message.created_at.asc())
        .limit(30)
        .all()
    )

    if not messages:
        return {"summary": "No data"}

    history_text = "\n".join([
        f"{m.role}: {m.content[:200]}"
        for m in messages
    ])

    response = await llm.generate([
        {
            "role": "system",
            "content": (
                "Summarize this conversation:\n"
                "- main goal\n"
                "- key decisions\n"
                "- important context\n"
                "Max 120 words."
            )
        },
        {
            "role": "user",
            "content": history_text
        }
    ])

    return {
        "summary": response.get("content", "No summary")
    }


# 🔹 DELETE
@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    deleted = (
        db.query(Message)
        .filter(
            Message.session_id == session_id,
            Message.user_id == user_id
        )
        .delete()
    )

    db.commit()

    return {
        "status": "deleted",
        "deleted_count": deleted
    }