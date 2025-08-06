import jwt
from src.config import get_settings
from datetime import datetime, timedelta, timezone
import uuid

settings = get_settings()
    
def create_jwt_token(user_id: uuid.UUID,
                    expires_delta: timedelta,
                    token_type: str = 'access'):
    
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    secret = settings.jwt.JWT_SECRET

    payload: dict = {
        "sub": str(user_id),
        "exp": expire,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "type": token_type
    }

    return jwt.encode(payload, secret, settings.jwt.JWT_ALGO)


def create_refresh_token(user_id: uuid.UUID):
    expires_delta = timedelta(days=30)

    return create_jwt_token(
        user_id,
        expires_delta,
        token_type='refresh'
    )


def create_access_token(user_id: uuid.UUID):
    expires_delta = timedelta(minutes=15)

    return create_jwt_token(
        user_id,
        expires_delta
    )

def create_verification_token(user_id: uuid.UUID):
    expires_delta = timedelta(minutes=15)

    return create_jwt_token(
            user_id,
            expires_delta,
            token_type='verification'
        )


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt.JWT_SECRET, algorithms=[settings.jwt.JWT_ALGO])
    
    