from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
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
    return render_template('admin/dashboard.html')

@admin_bp.route('/cliente-dashboard')
def cliente_dashboard():
    return render_template('admin/cliente-dashboard.html')

@admin_bp.route('/equipes')
def equipes():
    return render_template('admin/equipes.html')

@admin_bp.route('/projetos')
def projetos():
    return render_template('admin/projetos.html')

@admin_bp.route('/projeto-detalhe')
def projeto_detalhe():
    return render_template('admin/projeto-detalhe.html')

@admin_bp.route('/configuracoes')
def configuracoes():
    return render_template('admin/configuracoes.html')