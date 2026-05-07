from datetime import datetime
import os
from app.extensions import db
from app.models import Certificado, AtividadeComplementar, Submissao
from flask_jwt_extended import get_jwt_identity

PASTA_UPLOAD = 'certificados_uploaded'

def upload_certificado_controller(data, arquivo):
    id_aluno = int(get_jwt_identity())
    titulo = data.get("titulo")
    id_curso = data.get("id_curso")
    id_regra_atividade = data.get("id_regra_atividade")
    carga_horaria_solicitada = data.get("carga_horaria_solicitada")

    if not all([titulo, id_curso, id_regra_atividade, carga_horaria_solicitada, arquivo]):
        return {"success": False, "message": "Dados incompletos."}, 400

    # Salvar arquivo
    os.makedirs(PASTA_UPLOAD, exist_ok=True)
    nome_arquivo = f"{id_aluno}_{int(datetime.now().timestamp())}_{arquivo.filename}"
    filepath = os.path.join(PASTA_UPLOAD, nome_arquivo)
    arquivo.save(filepath)

    # Criar certificado
    certificado = Certificado(
        nome_arquivo=nome_arquivo,
        url_arquivo=filepath
    )
    db.session.add(certificado)
    db.session.flush()

    # Criar atividade complementar
    atividade = AtividadeComplementar(
        descricao=titulo,
        carga_horaria_solicitada=int(carga_horaria_solicitada),
        carga_horaria_aprovada=None,
        id_regra_atividade=int(id_regra_atividade)
    )
    db.session.add(atividade)
    db.session.flush()

    # Criar submissão
    submissao = Submissao(
        id_aluno=id_aluno,
        status="pendente",
        id_curso=int(id_curso),
        id_atividade_complementar=atividade.id,
        id_certificado=certificado.id,
        id_coordenador=None,
        motivo_rejeicao=None,
        carga_horaria_aprovada=None
    )
    db.session.add(submissao)
    db.session.commit()

    return {"success": True, "message": "Certificado enviado e submissão criada."}, 201