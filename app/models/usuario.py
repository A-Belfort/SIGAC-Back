from app.extensions import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False,
                                       unique=True)
    senhaHash: Mapped[str] = mapped_column(String(300), nullable=False)
    tipo: Mapped[str] = mapped_column(String(100), nullable=False)
    matricula: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
