from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    year: int

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    available: bool
    genre: Optional[str] = None  # присутствует в v2

    class Config:
        from_attributes = True

# v2 — новое поле обязательно при создании
class BookCreateV2(BookBase):
    genre: str

class BookV2(Book):
    genre: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class User(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class BorrowBase(BaseModel):
    book_id: int

class BorrowCreate(BorrowBase):
    pass

class Borrow(BorrowBase):
    id: int
    user_id: int
    borrowed_at: datetime
    returned_at: Optional[datetime] = None

    class Config:
        from_attributes = True