from contextlib import asynccontextmanager

from app.db import engine
from app.models import Base
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ping")
def ping():
    return {"msg": "pong from order service"}
