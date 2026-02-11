from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import JWTManager, UserService

router = APIRouter(prefix="/users", tags=["users"])


class RegisterUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UpdateProfileRequest(BaseModel):
    name: str


@router.post("/register")
def register(payload: RegisterUserRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        user = service.create_user(payload.name, payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"id": user.id, "name": user.name, "email": user.email}


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.authenticate(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = JWTManager().create_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.put("/{user_id}")
def update_profile(user_id: int, payload: UpdateProfileRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        user = service.update_profile(user_id, payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"id": user.id, "name": user.name, "email": user.email}


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.name, "email": user.email}
