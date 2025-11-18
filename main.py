from fastapi import FastAPI, Depends, HTTPException, Form
from sqlalchemy.orm import Session
import models
import database
import schemas
from auth.jwt_handler import create_access_token
from routers.v1.books import router as v1_books_router
from routers.v1.users import router as v1_users_router
from routers.v1.borrows import router as v1_borrows_router
from routers.v2.books import router as v2_books_router
from utils.limiter import limiter
from passlib.context import CryptContext

app = FastAPI(
    title="Library REST API",
    description="Лабораторная работа — Библиотека",
    version="2.0.0"
)

app.state.limiter = limiter
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Создаём таблицы при старте
models.Base.metadata.create_all(bind=database.engine)

# Монтируем версии
api_v1 = FastAPI(title="v1")
api_v2 = FastAPI(title="v2")

api_v1.include_router(v1_books_router, prefix="/books")
api_v1.include_router(v1_users_router, prefix="/users")
api_v1.include_router(v1_borrows_router, prefix="/borrows")
api_v2.include_router(v2_books_router, prefix="/books")

app.mount("/api/v1", api_v1)
app.mount("/api/v2", api_v2)

# === РЕГИСТРАЦИЯ И ЛОГИН — РАБОЧИЕ! ===
@app.post("/register")
def register(
    user: schemas.UserCreate,
    db: Session = Depends(database.get_db)
):
    # Проверка на дубликат email
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(400, "Email already registered")

    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name,
        role="user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"msg": "User created successfully"}

@app.post("/token", response_model=schemas.Token)
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password")
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}