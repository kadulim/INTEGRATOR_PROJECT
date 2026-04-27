from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from database import database
from models import Usuario, Cliente, Funcionario, Projeto
import functools

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Protege todas as rotas deste blueprint
@admin_bp.before_request
@login_required
def verificar_nivel_admin():
    if current_user.nivel != 1:
        abort(403)

@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    total_projetos   = Projeto.query.count()
    total_equipe     = Funcionario.query.count()
    total_clientes   = Cliente.query.count()
    projetos_ativos  = Projeto.query.filter_by(status='Em andamento').all()
    budget_total     = database.session.query(
        database.func.sum(Projeto.budget)
    ).scalar() or 0
    funcionarios_dash = (
        Funcionario.query
        .join(Usuario, Funcionario.usuario_id == Usuario.id)
        .add_entity(Usuario)
        .limit(4)
        .all()
    )

    # ── Status dos Projetos (donut) ──────────────────────────────────
    status_cores = {
        'Em andamento': '#3b82f6',
        'Concluído':    '#22c55e',
        'Planejamento': '#8b5cf6',
        'Pausado':      '#f59e0b',
    }
    status_rows = database.session.query(
        Projeto.status, database.func.count(Projeto.id)
    ).group_by(Projeto.status).all()

    status_data = [
        {'label': s or 'Sem status', 'val': c, 'color': status_cores.get(s, '#6b7280')}
        for s, c in status_rows
    ]

    # ── Volume por Mês (barras) — agrupa pelo mês do campo prazo ────
    # prazo está no formato 'YYYY-MM-DD' (string)
    monthly_rows = database.session.query(
        database.func.substring(Projeto.prazo, 6, 2).label('mes'),
        database.func.count(Projeto.id).label('total')
    ).filter(Projeto.prazo != None).group_by('mes').all()

    monthly_map = {int(r.mes): r.total for r in monthly_rows if r.mes and r.mes.isdigit()}
    volumes = [monthly_map.get(m, 0) for m in range(1, 13)]

    import json
    return render_template(
        'admin/dashboard.html',
        total_projetos    = total_projetos,
        total_equipe      = total_equipe,
        total_clientes    = total_clientes,
        projetos_ativos   = projetos_ativos,
        budget_total      = budget_total,
        funcionarios_dash = funcionarios_dash,
        status_data_json  = json.dumps(status_data),
        volumes_json      = json.dumps(volumes),
    )
@admin_bp.route('/equipes')
def equipes():
    funcionarios = (
        Funcionario.query
        .join(Usuario, Funcionario.usuario_id == Usuario.id)
        .add_entity(Usuario)
        .all()
    )
    total = Funcionario.query.count()
    return render_template(
        'admin/equipes.html',
        funcionarios = funcionarios,
        total        = total
    )

@admin_bp.route('/projetos')
def projetos():
    todos_projetos = Projeto.query.all()
    return render_template(
        'admin/projetos.html',
        projetos = todos_projetos
    )

@admin_bp.route('/projeto-detalhe')
def projeto_detalhe():
    return render_template('admin/projeto-detalhe.html')

@admin_bp.route('/configuracoes')
def configuracoes():
    return render_template('admin/configuracoes.html')