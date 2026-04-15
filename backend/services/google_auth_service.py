import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


def verify_google_token(credential: str) -> dict:
    if not GOOGLE_CLIENT_ID:
        raise ValueError("GOOGLE_CLIENT_ID is not configured")

    payload = id_token.verify_oauth2_token(
        credential,
        google_requests.Request(),
        GOOGLE_CLIENT_ID
    )

    if payload.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
        raise ValueError("Invalid Google token issuer")

    return payload