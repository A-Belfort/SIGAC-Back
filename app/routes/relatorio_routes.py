from flask import Blueprint
from app.middlewares import verificar_role
from app.controllers.relatorio_controller import dashboard_controller

bp = Blueprint("relatorio", __name__, url_prefix="/api/relatorios")

@bp.route("/dashboard", methods=["GET"])
@verificar_role(["admin", "coordenador"])
def dashboard():
    response, status = dashboard_controller()
    return response, status