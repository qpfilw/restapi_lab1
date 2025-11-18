from sqlalchemy.orm import Session
import schemas
import models

def get_books(db: Session):
    return db.query(models.Book).all()

def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.dict(), genre=None)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def create_book_v2(db: Session, book: schemas.BookCreateV2):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book(db: Session, book_id: int, book_update: schemas.BookCreate):
    db_book = get_book(db, book_id)
    if not db_book:
        raise HTTPException(404, "Book not found")
    for key, value in book_update.dict().items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int):
    db_book = get_book(db, book_id)
    if db_book:
        db.delete(db_book)
        db.commit()