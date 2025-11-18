from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session

import crud
import schemas
import database
import models
from auth.jwt_handler import get_current_user
from utils.limiter import limiter
from idempotency.store import IDEMPOTENCY_STORE

router = APIRouter(prefix="/books", tags=["v2 - Books (with genre)"])

@router.post("/", response_model=schemas.BookV2, status_code=201)
@limiter.limit("5/minute")
def create_book_v2(
    request: Request,
    book: schemas.BookCreateV2,
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user)
):
    # Тот же crud, но с genre
    db_book = crud.create_book_v2(db, book)
    return db_book

@router.get("/", response_model=list[schemas.BookV2])
def read_books_v2(db: Session = Depends(database.get_db)):
    books = crud.get_books(db)
    return books