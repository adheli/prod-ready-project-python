import hashlib
import hmac
import json
import os
import time
from typing import Optional

import redis
from sqlalchemy.orm import Session

from app.models import User


class NullPublisher:
    def publish(self, payload: dict) -> None:
        _ = payload


class UserService:
    def __init__(self, db: Session, publisher: Optional["UserCreatedPublisher"] = None):
        self.db = db
        self.publisher = publisher or UserCreatedPublisher()

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def create_user(self, name: str, email: str, password: str) -> User:
        existing = self.get_user_by_email(email)
        if existing:
            raise ValueError("Email already registered")
        user = User(name=name, email=email, hashed_password=self._hash_password(password))
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        self.publisher.publish({"user_id": user.id, "email": user.email})
        return user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if not user:
            return None
        if user.hashed_password != self._hash_password(password):
            return None
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def update_profile(self, user_id: int, name: str) -> User:
        user = self.get_user(user_id)
        if user is None:
            raise ValueError("User not found")
        user.name = name
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class JWTManager:
    def __init__(self, secret: Optional[str] = None):
        self.secret = (secret or os.getenv("JWT_SECRET", "dev-secret")).encode("utf-8")

    def create_token(self, user_id: int) -> str:
        payload = {"user_id": user_id, "iat": int(time.time())}
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        signature = hmac.new(self.secret, body, hashlib.sha256).hexdigest()
        return f"{body.hex()}.{signature}"


class UserCreatedPublisher:
    def __init__(self, client=None):
        self._channel = "user.created"
        self._client = client
        if self._client is None:
            redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
            self._client = redis.from_url(redis_url)

    def publish(self, payload: dict) -> None:
        try:
            self._client.publish(self._channel, json.dumps(payload))
        except Exception:
            # Keep skeleton resilient in local/dev test environments without Redis.
            pass
