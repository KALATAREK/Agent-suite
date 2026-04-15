from typing import List
from uuid import uuid4
from threading import Lock

from database import SessionLocal
from models.db_models import Message

# 🔒 THREAD SAFETY
_lock = Lock()

# 🔧 CONFIG
MAX_HISTORY = 20
CONTEXT_WINDOW = 8


# =========================
# 🎯 GET FULL MEMORY
# =========================
def get_memory(session_id: str, user_id: str) -> List[dict]:
    db = SessionLocal()
    try:
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
    finally:
        db.close()


# =========================
# 🎯 GET CONTEXT
# =========================
def get_context(session_id: str, user_id: str) -> List[dict]:
    memory = get_memory(session_id, user_id)
    return memory[-CONTEXT_WINDOW:]


# =========================
# 💾 SAVE SINGLE MESSAGE
# =========================
def save_memory(session_id: str, user_id: str, role: str, content: str):
    with _lock:
        db = SessionLocal()
        try:
            msg = Message(
                id=str(uuid4()),
                session_id=session_id,
                user_id=user_id,
                role=role,
                content=_sanitize_content(content),
            )

            db.add(msg)
            db.commit()

            _trim_history(db, session_id, user_id)

        finally:
            db.close()


# =========================
# 🧠 SAVE CONVERSATION (PAIR)
# =========================
def save_conversation(session_id: str, user_id: str, user_message: str, ai_response: str):
    with _lock:
        db = SessionLocal()
        try:
            # USER
            db.add(Message(
                id=str(uuid4()),
                session_id=session_id,
                user_id=user_id,
                role="user",
                content=_sanitize_content(user_message)
            ))

            # 🔥 skracamy AI (lepszy kontekst)
            shortened = _sanitize_content(ai_response)[:500]

            db.add(Message(
                id=str(uuid4()),
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=shortened
            ))

            db.commit()

            _trim_history(db, session_id, user_id)

        finally:
            db.close()


# =========================
# 🧹 CLEAR MEMORY
# =========================
def clear_memory(session_id: str, user_id: str):
    with _lock:
        db = SessionLocal()
        try:
            db.query(Message).filter(
                Message.session_id == session_id,
                Message.user_id == user_id
            ).delete()

            db.commit()
        finally:
            db.close()


# =========================
# 🧠 INTERNALS
# =========================
def _trim_history(db, session_id: str, user_id: str):
    messages = (
        db.query(Message)
        .filter(
            Message.session_id == session_id,
            Message.user_id == user_id
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    if len(messages) > MAX_HISTORY:
        to_delete = messages[: len(messages) - MAX_HISTORY]

        for msg in to_delete:
            db.delete(msg)

        db.commit()


def _sanitize_content(content: str) -> str:
    if not content:
        return ""

    content = str(content).strip()
    content = " ".join(content.split())

    return content


# =========================
# 📊 DEBUG
# =========================
def debug_session(session_id: str, user_id: str):
    db = SessionLocal()
    try:
        messages = (
            db.query(Message)
            .filter(
                Message.session_id == session_id,
                Message.user_id == user_id
            )
            .order_by(Message.created_at.desc())
            .limit(5)
            .all()
        )

        print(f"[MEMORY] session={session_id} user={user_id} messages={len(messages)}")

        for msg in messages:
            print(f"{msg.role}: {msg.content[:60]}...")
    finally:
        db.close()