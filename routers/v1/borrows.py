from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

import models
import crud
import schemas
import database
from auth.jwt_handler import get_current_user
from utils.limiter import limiter

router = APIRouter(prefix="/borrows", tags=["v1 - Borrows"])

@router.post("/", response_model=schemas.Borrow, status_code=201)
@limiter.limit("5/minute")
def borrow_book(
    request: Request,
    borrow: schemas.BorrowCreate,
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    book = crud.get_book(db, borrow.book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    if not book.available:
        raise HTTPException(400, "Book is already borrowed")

    db_borrow = models.Borrow(book_id=borrow.book_id, user_id=current_user.id)
    book.available = False
    db.add(db_borrow)
    db.commit()
    db.refresh(db_borrow)
    return db_borrow

@router.patch("/{borrow_id}/return", response_model=schemas.Borrow)
def return_book(
    borrow_id: int,
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    borrow = db.query(models.Borrow).filter(models.Borrow.id == borrow_id).first()
    if not borrow:
        raise HTTPException(404, "Borrow record not found")
    if borrow.user_id != current_user.id and current_user.role != "librarian" and current_user.role != "admin":
        raise HTTPException(403, "You can only return your own books")

    if borrow.returned_at:
        raise HTTPException(400, "Book already returned")

    borrow.returned_at = datetime.utcnow()
    book = crud.get_book(db, borrow.book_id)
    if book:
        book.available = True
    db.commit()
    db.refresh(borrow)
    return borrow

@router.get("/my", response_model=List[schemas.Borrow])
def my_borrows(
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    borrows = db.query(models.Borrow).filter(
        models.Borrow.user_id == current_user.id,
        models.Borrow.returned_at == None
    ).all()
    return borrows

@router.get("/", response_model=List[schemas.Borrow])
@limiter.limit("10/minute")
def all_borrows(
    request,
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role not in ["librarian", "admin"]:
        raise HTTPException(403, "Not enough permissions")
    return db.query(models.Borrow).all()