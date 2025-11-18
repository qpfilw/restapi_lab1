from fastapi import APIRouter, Depends, HTTPException, Header, Request, Response
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import uuid

import crud
import schemas
import database
import models
from auth.jwt_handler import get_current_user
from utils.limiter import limiter
from idempotency.store import IDEMPOTENCY_STORE

router = APIRouter(prefix="/books", tags=["v1 - Books"])

@router.get("/", response_model=list[schemas.Book])
@limiter.limit("10/minute")
def read_books(request: Request, db: Session = Depends(database.get_db)):
    books = crud.get_books(db)
    return books

@router.get("/{book_id}", response_model=schemas.Book)
def read_book(book_id: int, db: Session = Depends(database.get_db)):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(404, "Book not found")
    return book

@router.post("/", response_model=schemas.Book, status_code=201)
@limiter.limit("5/minute")
async def create_book(
    request: Request,
    response: Response,
    book: schemas.BookCreate,
    db: Session = Depends(database.get_db),
    current_user = Depends(get_current_user),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    # Идемпотентность
    if idempotency_key and idempotency_key in IDEMPOTENCY_STORE:
        stored = IDEMPOTENCY_STORE[idempotency_key]
        response.status_code = 200
        return stored

    db_book = crud.create_book(db, book)
    
    if idempotency_key:
        IDEMPOTENCY_STORE[idempotency_key] = db_book
    
    return db_book

@router.put("/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book_update: schemas.BookCreate, db: Session = Depends(database.get_db), current_user = Depends(get_current_user)):
    return crud.update_book(db, book_id, book_update)

@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(database.get_db), current_user = Depends(get_current_user)):
    crud.delete_book(db, book_id)
    return Response(status_code=204)