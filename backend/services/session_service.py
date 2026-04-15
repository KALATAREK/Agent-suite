from services.llm_service import LLMService
from models.db_models import Session


async def auto_name_session(db, session_id: str, user_id: str, first_message: str):
    session = db.query(Session).filter(
        Session.id == session_id,
        Session.user_id == user_id
    ).first()

    if not session:
        return

    # 🔥 NIE nadpisuj jeśli user zmienił nazwę
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