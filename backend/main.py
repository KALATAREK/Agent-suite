from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from pydantic import BaseModel

from database import engine, SessionLocal
from models.db_models import Base, Message, Session
from models.request_models import (
    ChatRequest,
    AnalyzeRequest,
    AutomateRequest,
)
from models.response_models import BaseResponse

from agents.agent_brain import run_agent
from agents.automator_agent import handle_automator

from services.analysis_service import analyze_business
from services.parsing_service import parse_input
from services.deps import get_current_user
from services.llm_service import LLMService
from routes.auth import router as auth_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AgentSuite API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/debug/test")
async def debug_test():
    """Test endpoint to verify API is working"""
    return {"message": "API is working", "timestamp": str(__import__('datetime').datetime.now())}


def ensure_session(db: DBSession, session_id: str, user_id: str):
    session = db.query(Session).filter(
        Session.id == session_id,
        Session.user_id == user_id
    ).first()

    if not session:
        session = Session(
            id=session_id,
            user_id=user_id,
            name="New session"
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    return session


async def auto_name_session(db: DBSession, session: Session, first_message: str):
    if session.name != "New session":
        return

    llm = LLMService()

    try:
        response = await llm.generate([
            {
                "role": "system",
                "content": (
                    "Create a short (max 5 words) title for this conversation. "
                    "Be specific. No quotes."
                )
            },
            {
                "role": "user",
                "content": first_message[:200]
            }
        ])

        title = response.get("content", "").strip()

        if title:
            session.name = title[:60]
            db.commit()

    except Exception as e:
        print("[AUTO NAME ERROR]", e)


# =========================
# CHAT
# =========================

@app.post("/chat", response_model=BaseResponse)
async def chat(
    req: ChatRequest,
    db: DBSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    try:
        session = ensure_session(db, req.session_id, user_id)

        msg_count = db.query(Message).filter(
            Message.session_id == req.session_id,
            Message.user_id == user_id
        ).count()

        if msg_count == 0:
            await auto_name_session(db, session, req.message)

        result = await run_agent(
            session_id=req.session_id,
            message=req.message,
            user_id=user_id,
        )

        return result

    except Exception as e:
        print("[CHAT ERROR]", e)
        raise HTTPException(status_code=500, detail="Chat failed")


@app.post("/analyze", response_model=BaseResponse)
async def analyze(
    req: AnalyzeRequest,
    user_id: str = Depends(get_current_user)
):
    if not req.input.strip():
        raise HTTPException(status_code=400, detail="Empty input")

    try:
        parsed = parse_input(req.input)
        result = await analyze_business(parsed["cleaned"])

        return {
            "type": "analysis",
            "content": result.get("content"),
            "meta": result.get("meta", {})
        }

    except Exception as e:
        print("[ANALYZE ERROR]", e)
        raise HTTPException(status_code=500, detail="Analyze failed")


@app.post("/automate", response_model=BaseResponse)
async def automate(
    req: AutomateRequest,
    user_id: str = Depends(get_current_user)
):
    if not req.input.strip():
        raise HTTPException(status_code=400, detail="Empty input")

    try:
        print(f"[AUTOMATE] Processing for user {user_id}: {req.input[:50]}...")
        
        parsed = parse_input(req.input)
        print(f"[AUTOMATE] Parsed input: {parsed}")
        
        result = await handle_automator(parsed["cleaned"])
        print(f"[AUTOMATE] Handler returned: {result}")

        response = {
            "type": "automate",
            "content": result,
            "meta": {}
        }
        print(f"[AUTOMATE] Sending response: {response}")
        
        return response

    except Exception as e:
        print(f"[AUTOMATE ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# SESSIONS
# =========================

@app.get("/sessions")
async def get_sessions(
    db: DBSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    rows = (
        db.query(
            Session.id,
            Session.name,
            func.count(Message.id).label("messages")
        )
        .outerjoin(Message, Message.session_id == Session.id)
        .filter(Session.user_id == user_id)
        .group_by(Session.id)
        .order_by(func.max(Message.created_at).desc())
        .all()
    )

    return [
        {
            "session_id": r.id,
            "title": r.name,
            "messages": r.messages or 0,
        }
        for r in rows
    ]


@app.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    db: DBSession = Depends(get_db),
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


class RenameSessionRequest(BaseModel):
    title: str


@app.patch("/sessions/{session_id}")
async def rename_session(
    session_id: str,
    req: RenameSessionRequest,
    db: DBSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Empty title")

    session = db.query(Session).filter(
        Session.id == session_id,
        Session.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.name = req.title.strip()
    db.commit()

    return {"status": "renamed", "title": session.name}


@app.post("/sessions/{session_id}/summary")
async def generate_summary(
    session_id: str,
    db: DBSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    llm = LLMService()

    messages = (
        db.query(Message)
        .filter(
            Message.session_id == session_id,
            Message.user_id == user_id
        )
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
        {"role": "system", "content": "Summarize conversation in 3 bullet points."},
        {"role": "user", "content": history_text}
    ])

    return {"summary": response.get("content", "No summary")}


@app.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    deleted = db.query(Session).filter(
        Session.id == session_id,
        Session.user_id == user_id
    ).delete()

    db.commit()

    return {
        "status": "deleted",
        "deleted_count": deleted,
    }