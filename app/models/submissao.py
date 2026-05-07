from app.extensions import Base
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, func, Integer
from sqlalchemy.orm import Mapped, mapped_column

class Submissao(Base):
    __tablename__ = "submissao"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_envio: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now(), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    id_aluno: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    id_curso: Mapped[int] = mapped_column(ForeignKey("curso.id"), nullable=False)
    id_atividade_complementar: Mapped[int] = mapped_column(ForeignKey("atividade_complementar.id"), nullable=False)
    id_certificado: Mapped[Optional[int]] = mapped_column(ForeignKey("certificado.id"))
    id_coordenador: Mapped[Optional[int]] = mapped_column(ForeignKey("usuario.id"))
    motivo_rejeicao: Mapped[Optional[str]] = mapped_column(String(300))
    carga_horaria_aprovada: Mapped[Optional[int]] = mapped_column(Integer)  # Nova coluna