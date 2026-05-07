from app.extensions import db
from app.models import Curso
from sqlalchemy import select

def cadastrar_curso_controller(data):
    new_curso = Curso(
        nome=data["nome"],
        carga_horaria=data["carga_horaria"]
    )
    db.session.add(new_curso)
    db.session.commit()
    return {
        "success": True,
        "message": "Curso cadastrado com sucesso."
    }, 201

def listar_cursos_controller():
    query = select(Curso)
    cursos = db.session.execute(query).scalars().all()
    resultado = [
        {
            "id": curso.id,
            "nome": curso.nome,
            "carga_horaria": curso.carga_horaria
        }
        for curso in cursos
    ]
    return {
        "success": True,
        "cursos": resultado
    }, 200