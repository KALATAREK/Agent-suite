from fastapi import APIRouter, Depends, HTTPException
import os

from database import SessionLocal
from models.db_models import User
from models.request_models import RegisterRequest, LoginRequest, GoogleAuthRequest
from services.auth_service import create_access_token, hash_password, verify_password
from services.deps import get_current_user
from services.google_auth_service import verify_google_token

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


@router.post("/auth/register")
async def register(req: RegisterRequest):
    print("REGISTER HIT")
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == req.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")

        user = User(
            email=req.email,
            password=hash_password(req.password),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        access_token = create_access_token({"sub": user.id, "email": user.email})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
            }
        }
    finally:
        db.close()


@router.post("/auth/login")
async def login(req: LoginRequest):
    print("LOGIN HIT")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == req.email).first()
        if not user or not user.password or not verify_password(req.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token({"sub": user.id, "email": user.email})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
            }
        }
    finally:
        db.close()


@router.get("/auth/me")
async def get_me(user_id: str = Depends(get_current_user)):
    print("ME HIT")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
        }
    finally:
        db.close()


@router.post("/auth/google")
async def google_login(req: GoogleAuthRequest):
    print("GOOGLE HIT")
    if not req.credential:
        raise HTTPException(status_code=400, detail="Missing credential")

    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google client ID not configured")

    try:
        payload = verify_google_token(req.credential)
        email = payload.get("email")
        google_id = payload.get("sub")
        name = payload.get("name")
        avatar_url = payload.get("picture")

        if not email or not google_id:
            raise HTTPException(status_code=400, detail="Invalid Google payload")
    except Exception as e:
        print("[GOOGLE AUTH ERROR]", e)
        raise HTTPException(status_code=401, detail="Invalid Google token")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            user = User(
                email=email,
                google_id=google_id,
                name=name,
                avatar_url=avatar_url,
                password=None,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            updated = False
            if not user.google_id:
                user.google_id = google_id
                updated = True
            if name and user.name != name:
                user.name = name
                updated = True
            if avatar_url and user.avatar_url != avatar_url:
                user.avatar_url = avatar_url
                updated = True
            if updated:
                db.commit()
                db.refresh(user)

        access_token = create_access_token({"sub": user.id, "email": user.email})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "avatar_url": user.avatar_url,
            }
        }
    finally:
        db.close()