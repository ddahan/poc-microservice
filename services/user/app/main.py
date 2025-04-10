from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from services.order.app.db import SessionLocal

from .db import engine
from .models import Base, User
from .publisher import publish_user_created
from .schemas import CreateUserRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # will create User table
    yield


app = FastAPI(lifespan=lifespan)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Routes


@app.get("/ping")
def ping():
    return {"msg": "pong from user service"}


@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(
    payload: CreateUserRequest, db: Session = Depends(get_db)
) -> JSONResponse:
    user = User(id=str(uuid4()), name=payload.name, email=payload.email)
    db.add(user)
    db.commit()
    publish_user_created(user.id, user.name, user.email)
    return JSONResponse(content={"id": user.id, "name": user.name, "email": user.email})
