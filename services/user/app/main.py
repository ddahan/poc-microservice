from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from services.order.app.db import SessionLocal
from services.user.app.publisher import publish_user_created

from .db import engine
from .models import Base, User


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
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
def create_user(name: str, email: str, db: Session = Depends(get_db)) -> JSONResponse:
    user = User(id=str(uuid4()), name=name, email=email)
    db.add(user)
    db.commit()
    publish_user_created(user.id, user.name, user.email)
    return JSONResponse(content={"id": user.id, "name": user.name, "email": user.email})
