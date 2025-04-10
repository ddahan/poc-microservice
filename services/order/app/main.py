from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import engine
from .models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ping")
def ping():
    return {"msg": "pong from order service"}
