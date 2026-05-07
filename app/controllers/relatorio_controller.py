from app.extensions import db
from app.models import Usuario, Submissao, Curso, RegraAtividade
from sqlalchemy import select, func, extract
from flask_jwt_extended import get_jwt
from datetime import datetime, timedelta

def dashboard_controller():
    role = get_jwt().get("role")
    if role not in ("super_admin", "coordenador"):
        return {"success": False, "message": "Acesso negado."}, 403

    # 1. Métricas principais
    total_alunos = db.session.execute(select(func.count()).select_from(Usuario).where(Usuario.tipo == "aluno")).scalar()
    total_horas_aprovadas = db.session.execute(
        select(func.coalesce(func.sum(Submissao.carga_horaria_aprovada), 0))
        .where(Submissao.status == "aprovado")
    ).scalar()
    total_solicitacoes = db.session.execute(select(func.count()).select_from(Submissao)).scalar()
    total_aprovadas = db.session.execute(select(func.count()).select_from(Submissao).where(Submissao.status == "aprovado")).scalar()
    taxa_aprovacao = round((total_aprovadas / total_solicitacoes * 100), 1) if total_solicitacoes > 0 else 0

    metricas = {
        "total_alunos": total_alunos,
        "total_horas_aprovadas": int(total_horas_aprovadas or 0),
        "total_solicitacoes": total_solicitacoes,
        "taxa_aprovacao": taxa_aprovacao
    }

    # 2. Evolução mensal (últimos 6 meses)
    ultimos_6_meses = []
    for i in range(5, -1, -1):
        mes = datetime.now().replace(day=1) - timedelta(days=30*i)
        nome_mes = mes.strftime("%b")
        inicio_mes = mes.replace(day=1)
        fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        total_mes = db.session.execute(
            select(func.coalesce(func.sum(Submissao.carga_horaria_aprovada), 0))
            .where(Submissao.status == "aprovado")
            .where(Submissao.data_envio >= inicio_mes)
            .where(Submissao.data_envio <= fim_mes)
        ).scalar()
        ultimos_6_meses.append({"mes": nome_mes, "horas": int(total_mes or 0)})

    # 3. Distribuição por tipo de atividade (regras)
    distribuicao = db.session.execute(
        select(
            RegraAtividade.area,
            func.count(Submissao.id).label("quantidade")
        )
        .join(Submissao.atividade_complementar)
        .join(RegraAtividade, RegraAtividade.id == Submissao.atividade_complementar.id_regra_atividade)
        .group_by(RegraAtividade.area)
    ).all()

    distribuicao_atividades = [{"area": row.area, "quantidade": row.quantidade} for row in distribuicao]

    return {
        "success": True,
        "metricas": metricas,
        "evolucao_mensal": ultimos_6_meses,
        "distribuicao_atividades": distribuicao_atividades
    }, 200