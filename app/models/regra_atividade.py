from app.extensions import Base
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

class RegraAtividade(Base):
    __tablename__ = "regra_atividade"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str] = mapped_column(String(300), nullable=False)
    limite_horas: Mapped[int] = mapped_column(Integer, nullable=False)
    requisito: Mapped[str] = mapped_column(String(100), nullable=False)
    exige_certificado: Mapped[int] = mapped_column(Boolean, nullable=False)
    id_curso: Mapped[Optional[int]] = mapped_column(ForeignKey("curso.id"), nullable=True)