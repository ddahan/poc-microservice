from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
