import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash


ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()


def validate_security_settings() -> None:
    if len(os.environ["SECRET_KEY"]) < 32:
        raise RuntimeError("SECRET_KEY must contain at least 32 characters")
    if len(os.environ["ADMIN_PASSWORD"]) < 12:
        raise RuntimeError("ADMIN_PASSWORD must contain at least 12 characters")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    return password_hash.verify(password, encoded)


def create_access_token(subject: str) -> str:
    minutes = int(os.environ.get("ACCESS_TOKEN_MINUTES", "30"))
    expires = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode(
        {"sub": subject, "exp": expires},
        os.environ["SECRET_KEY"],
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=[ALGORITHM])
    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise jwt.InvalidTokenError("Token subject is missing")
    return subject
