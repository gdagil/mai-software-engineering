from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from api_gateway.config import settings
from api_gateway.models.auth import User

users_db = {
    "admin": User(
        id=1,
        username="admin",
        password="secret",
        is_admin=True
    )
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Optional[User]:
    user = users_db.get(username)
    if not user:
        return None
    if user.password != password:
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None


def get_current_user(token: str) -> Optional[User]:
    payload = verify_token(token)
    if payload is None:
        return None
    
    username = payload.get("sub")
    user = users_db.get(username)
    return user 