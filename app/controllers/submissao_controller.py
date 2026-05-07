from app.extensions import db
from app.models import Submissao, AtividadeComplementar, Certificado, Usuario, Curso
from sqlalchemy import select, func
from flask_jwt_extended import get_jwt, get_jwt_identity

def criar_submissao_controller(data):
    id_aluno = int(get_jwt_identity())
    # data espera: titulo, id_curso, id_regra_atividade, carga_horaria_solicitada, nome_arquivo, url_arquivo
    # Primeiro cria o certificado
    certificado = Certificado(
        nome_arquivo=data["nome_arquivo"],
        url_arquivo=data["url_arquivo"]
    )
    db.session.add(certificado)
    db.session.flush()

    # Cria a atividade complementar
    atividade = AtividadeComplementar(
        descricao=data["titulo"],
        carga_horaria_solicitada=data["carga_horaria_solicitada"],
        carga_horaria_aprovada=None,
        id_regra_atividade=data["id_regra_atividade"]
    )
    db.session.add(atividade)
    db.session.flush()

    # Cria a submissão
    nova_submissao = Submissao(
        id_aluno=id_aluno,
        status="pendente",
        id_curso=data["id_curso"],
        id_atividade_complementar=atividade.id,
        id_certificado=certificado.id,
        id_coordenador=None,
        motivo_rejeicao=None,
        carga_horaria_aprovada=None
    )
    db.session.add(nova_submissao)
    db.session.commit()

    return {"success": True, "message": "Submissão criada com sucesso."}, 201

def listar_submissoes_controller(status=None):
    role = get_jwt().get("role")
    id_usuario = int(get_jwt_identity())

    query = select(
        Submissao.id,
        Submissao.status,
        Submissao.data_envio,
        Submissao.motivo_rejeicao,
        Submissao.carga_horaria_aprovada,
        Usuario.nome.label("aluno_nome"),
        Usuario.email.label("aluno_email"),
        Curso.nome.label("curso_nome"),
        AtividadeComplementar.descricao.label("atividade_descricao"),
        AtividadeComplementar.carga_horaria_solicitada,
        Certificado.url_arquivo.label("certificado_url")
    ).join(Usuario, Usuario.id == Submissao.id_aluno
    ).join(Curso, Curso.id == Submissao.id_curso
    ).join(AtividadeComplementar, AtividadeComplementar.id == Submissao.id_atividade_complementar
    ).outerjoin(Certificado, Certificado.id == Submissao.id_certificado)

    if role == "aluno":
        query = query.where(Submissao.id_aluno == id_usuario)
    elif role == "coordenador":
        query = query.where(Submissao.id_curso.in_(select(CoordenadorCurso.id_curso).where(CoordenadorCurso.id_coordenador == id_usuario)))
    # super_admin vê tudo

    if status:
        query = query.where(Submissao.status == status)

    submissoes = db.session.execute(query).all()
    resultado = [
        {
            "id": s.id,
            "status": s.status,
            "data_envio": s.data_envio.isoformat(),
            "aluno_nome": s.aluno_nome,
            "aluno_email": s.aluno_email,
            "curso_nome": s.curso_nome,
            "atividade_descricao": s.atividade_descricao,
            "carga_horaria_solicitada": s.carga_horaria_solicitada,
            "certificado_url": s.certificado_url,
            "motivo_rejeicao": s.motivo_rejeicao,
            "carga_horaria_aprovada": s.carga_horaria_aprovada
        }
        for s in submissoes
    ]

    return {"success": True, "submissoes": resultado}, 200

def validar_submissao_controller(id_submissao, data):
    id_coordenador = int(get_jwt_identity())
    submissao = db.session.get(Submissao, id_submissao)
    if not submissao:
        return {"success": False, "message": "Submissão não encontrada."}, 404

    novo_status = data.get("status")
    if novo_status not in ("aprovado", "recusado"):
        return {"success": False, "message": "Status inválido."}, 400

    submissao.status = novo_status
    submissao.id_coordenador = id_coordenador
    if novo_status == "recusado":
        submissao.motivo_rejeicao = data.get("motivo_rejeicao")
    elif novo_status == "aprovado":
        # Aprova com a carga horária solicitada (ou pode vir no payload)
        carga_aprovada = data.get("carga_horaria_aprovada", submissao.atividade_complementar.carga_horaria_solicitada)
        submissao.carga_horaria_aprovada = carga_aprovada
        # Atualiza também na atividade complementar (opcional)
        submissao.atividade_complementar.carga_horaria_aprovada = carga_aprovada

    db.session.commit()
    return {"success": True, "message": f"Submissão {novo_status} com sucesso."}, 200