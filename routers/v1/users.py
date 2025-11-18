from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import crud
import schemas
import database
from auth.jwt_handler import get_current_user
from utils.limiter import limiter

router = APIRouter(prefix="/users", tags=["v1 - Users"])

@router.get("/", response_model=List[schemas.User])
@limiter.limit("10/minute")
def read_users(
    request,
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Not enough permissions")
    users = db.query(models.User).all()
    return users

@router.get("/me", response_model=schemas.User)
def read_current_user(current_user = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(403, "Not allowed")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user