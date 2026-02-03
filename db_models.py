from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, func, ForeignKey
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    
    # Связь: один пользователь может иметь много сниппетов
    snippets: Mapped[list["Snippet"]] = relationship(back_populates="author")

class Snippet(Base):
    __tablename__ = "snippets"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    runtime: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Внешний ключ (может быть NULL, если анонимный сниппет)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="snippets")