# =============================================================================
# routes/admin.py - Blueprint de Administração
# =============================================================================
# Gerencia dashboards, CRUD de projetos, clientes, funcionários e equipes
# com nível de acesso restrito a administradores (nivel == 1).
# =============================================================================

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import database
from models import User, Client, Employee, Project, Team, Skill, team_members, project_teams, Log, Requirement, Document, Diagram, Gallery, Comment
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import extract
import functools
import json
import re
import unicodedata

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# =============================================================================
# Middleware - Proteção de nível de acesso
# =============================================================================
@admin_bp.before_request
@login_required
def verificar_nivel_admin():
    if not current_user.admin or current_user.admin.level_admin != 1:
        abort(403)

# =============================================================================
# Utilitário - Registro de logs
# =============================================================================
def registrar_log(tipo, acao, descricao, projeto_id=None):
    try:
        novo_registro = Log(
            type_log=tipo,
            description_log=descricao,
            fk_project=projeto_id
        )
        database.session.add(novo_registro)
        database.session.commit()
    except Exception as e:
        print(f"Erro ao registrar log: {e}")
        database.session.rollback()

# =============================================================================
# DASHBOARD
# =============================================================================
@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    # Métricas principais
    total_projetos   = Project.query.count()
    total_equipe     = Employee.query.count()
    total_clientes   = Client.query.count()
    projetos_recentes = Project.query.filter_by(status_project='Em andamento').all()
    for proj in projetos_recentes:
        ultimo_registro = Log.query.filter_by(fk_project=proj.pk_id_project).order_by(Log.date_log.desc()).first()
        proj.ultimo_registro = ultimo_registro.description_log if ultimo_registro else "Sem alterações recentes"

    orcamento_total = database.session.query(
        database.func.sum(Project.orcamento)
    ).scalar() or 0
    funcionarios_painel = (
        Employee.query
        .join(User, Employee.fk_user == User.pk_id_user)
        .add_entity(User)
        .limit(4)
        .all()
    )

    # ── Gráfico de Status (donut) ──────────────────────────────────
    status_cores = {
        'Em andamento': '#f59e0b',
        'Concluído':    '#10b981',
        'Pausado':      '#FF5577',
        'Cancelado':    '#6b7280'
    }
    status_rows = database.session.query(
        Project.status_project, database.func.count(Project.pk_id_project)
    ).group_by(Project.status_project).all()

    status_counts = {s: 0 for s in status_cores.keys()}
    for s, c in status_rows:
        if s == 'Pendente':
            status_counts['Pausado'] += c
        elif s in status_counts:
            status_counts[s] += c

    status_data = [
        {'label': s, 'val': c, 'color': status_cores.get(s, '#6b7280')}
        for s, c in status_counts.items()
    ]

    # ── Gráfico de Atividade Mensal (barras por status) ────────────────
    mes_expr = database.func.extract('month', Project.end_date_project)
    monthly_status_rows = database.session.query(
        mes_expr.label('mes'),
        Project.status_project,
        database.func.count(Project.pk_id_project).label('total')
    ).filter(Project.end_date_project.isnot(None)).group_by(mes_expr, Project.status_project).all()

    monthly_map = {m: {'Em andamento': 0, 'Concluído': 0, 'Pausado': 0, 'Cancelado': 0} for m in range(1, 13)}
    
    for r in monthly_status_rows:
        if r.mes is None:
            continue
        m_int = int(r.mes)
        status_str = r.status_project or 'Pausado'
        if status_str == 'Pendente':
            status_str = 'Pausado'
        if status_str not in ['Em andamento', 'Concluído', 'Pausado', 'Cancelado']:
            status_str = 'Pausado'
        if m_int in monthly_map:
            monthly_map[m_int][status_str] = r.total
            
    volumes = [
        {
            'em_andamento': monthly_map[m]['Em andamento'],
            'concluido': monthly_map[m]['Concluído'],
            'pendente': monthly_map[m]['Pausado']
        }
        for m in range(1, 13)
    ]

    # ── Logs recentes e completos ──────────────────────────────────
    logs_query = database.session.query(Log, Project).outerjoin(Project, Log.fk_project == Project.pk_id_project).order_by(Log.date_log.desc()).limit(10).all()
    
    logs_data = []
    for log, projeto in logs_query:
        equipe_nome = log.team.name_team if log.team else '—'
        logs_data.append({
            'acao': log.type_log,
            'descricao': log.description_log,
            'data': log.date_log,
            'equipe_nome': equipe_nome,
            'project_name': projeto.name_project if projeto else 'Geral',
            'type_log': log.type_log
        })

    todos_logs_query = database.session.query(Log, Project).outerjoin(Project, Log.fk_project == Project.pk_id_project).order_by(Log.date_log.desc()).all()
    todos_logs_data = []
    for log, projeto in todos_logs_query:
        equipe_nome = log.team.name_team if log.team else '—'
        todos_logs_data.append({
            'acao': log.type_log,
            'descricao': log.description_log,
            'data': log.date_log,
            'equipe_nome': equipe_nome
        })

    # ── Projetos agrupados por status para o mês atual ──────────────────
    import datetime
    now = datetime.datetime.now()
    current_month_num = now.month
    current_year = now.year
    meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    current_month_name = meses_nomes[current_month_num]

    current_month_projects = {
        'em_andamento': [],
        'concluido': [],
        'pausado': [],
        'cancelado': []
    }

    for proj in Project.query.all():
        status_str = proj.status_project or 'Pausado'
        if status_str == 'Pendente':
            status_str = 'Pausado'
        if status_str == 'Em andamento':
            current_month_projects['em_andamento'].append(proj)
        elif status_str == 'Concluído':
            current_month_projects['concluido'].append(proj)
        elif status_str == 'Cancelado':
            current_month_projects['cancelado'].append(proj)
        else:
            current_month_projects['pausado'].append(proj)

    # ── Todos os projetos agrupados por status para o Donut Chart tooltip ──
    projetos_por_status = {
        'em_andamento': [],
        'concluido': [],
        'pausado': [],
        'cancelado': []
    }
    for proj in Project.query.all():
        status_str = proj.status_project or 'Pausado'
        if status_str == 'Pendente':
            status_str = 'Pausado'
        
        proj_data = {
            'nome': proj.name_project,
            'prazo': proj.end_date_project.strftime('%d/%m/%Y') if proj.end_date_project else 'Sem prazo',
            'url': url_for('admin.projeto_detalhe', id=proj.pk_id_project)
        }
        
        if status_str == 'Em andamento':
            projetos_por_status['em_andamento'].append(proj_data)
        elif status_str == 'Concluído':
            projetos_por_status['concluido'].append(proj_data)
        elif status_str == 'Cancelado':
            projetos_por_status['cancelado'].append(proj_data)
        else:
            projetos_por_status['pausado'].append(proj_data)

    return render_template(
        'admin/dashboard.html',
        total_projetos    = total_projetos,
        total_equipe      = total_equipe,
        total_clientes    = total_clientes,
        projetos_recentes = projetos_recentes,
        budget_total   = orcamento_total,
        funcionarios_dash = funcionarios_painel,
        status_data_json  = json.dumps(status_data),
        projetos_status_json = json.dumps(projetos_por_status),
        volumes_json      = json.dumps(volumes),
        logs              = logs_data,
        todos_logs        = todos_logs_data,
        current_month_name = current_month_name,
        current_month_projects = current_month_projects
    )

# =============================================================================
# CRUD - PROJETOS
# =============================================================================

# ---------------------------------------------------------------------------
# Listagem de todos os projetos
# ---------------------------------------------------------------------------
@admin_bp.route('/projetos')
def projetos():
    todos_projetos = Project.query.all()
    todos_clientes = Client.query.join(User).all()
    todas_equipes = Team.query.all()
    return render_template(
        'admin/projetos.html',
        projetos = todos_projetos,
        clientes = todos_clientes,
        equipes = todas_equipes
    )

# ---------------------------------------------------------------------------
# Criar novo projeto
# ---------------------------------------------------------------------------
@admin_bp.route('/add-projeto', methods=['POST'])
def add_projeto():
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    prazo = request.form.get('prazo')
    orcamento = request.form.get('budget', 0)
    cliente_id = request.form.get('cliente_id')
    equipes_ids = [int(x) for x in request.form.getlist('check_equipes') if x.isdigit()]

    from datetime import date
    try:
        prazo_date = date.fromisoformat(prazo) if prazo else None
    except:
        prazo_date = None

    projeto = Project(
        name_project=nome,
        description_project=descricao,
        status_project="Em andamento",
        end_date_project=prazo_date,
        orcamento=float(orcamento) if orcamento else 0.0,
        fk_client=cliente_id if cliente_id else None
    )
    
    if equipes_ids:
        equipes = Team.query.filter(Team.pk_id_team.in_(equipes_ids)).all()
        projeto.teams.extend(equipes)
    
    database.session.add(projeto)
    database.session.commit()
    
    registrar_log('projeto', 'Projeto criado', f"O projeto '{nome}' foi criado com sucesso.", projeto.pk_id_project)
    
    return redirect(url_for('admin.projetos'))

# ---------------------------------------------------------------------------
# Detalhes de um projeto (com membros, documentos, diagramas, galeria, comentários)
# ---------------------------------------------------------------------------
@admin_bp.route('/projeto-detalhe')
def projeto_detalhe():
    projeto_id = request.args.get('id', type=int)
    if not projeto_id:
        return redirect(url_for('admin.projetos'))
    
    projeto = Project.query.get_or_404(projeto_id)
    cliente = projeto.client
    equipes = projeto.teams
    
    membros = []
    equipes_ids = [eq.pk_id_team for eq in equipes]
    if equipes_ids:
        membros = (
            database.session.query(Employee, User)
            .join(team_members, Employee.pk_id_employee == team_members.c.fk_employee)
            .filter(team_members.c.fk_team.in_(equipes_ids))
            .join(User, Employee.fk_user == User.pk_id_user)
            .distinct()
            .all()
        )
        
    documentos = Document.query.filter_by(fk_project=projeto_id).all()
    diagramas = Diagram.query.filter_by(fk_project=projeto_id).all()
    galeria = Gallery.query.filter_by(fk_project=projeto_id).all()
    comentarios = Comment.query.filter_by(fk_project=projeto_id).order_by(Comment.date_comment.asc()).all()
    
    return render_template(
        'admin/projeto-detalhe.html',
        projeto=projeto,
        cliente=cliente,
        equipes=equipes,
        membros=membros,
        requisitos=projeto.requirements,
        todas_equipes=Team.query.all(),
        todos_clientes=Client.query.all(),
        documentos=documentos,
        diagramas=diagramas,
        galeria=galeria,
        comentarios=comentarios
    )
    
# ---------------------------------------------------------------------------
# Vincular equipes a um projeto
# ---------------------------------------------------------------------------
@admin_bp.route('/vincular-equipes-projeto', methods=['POST'])
def vincular_equipes_projeto():
    projeto_id = request.form.get('projeto_id', type=int)
    equipes_ids = [int(x) for x in request.form.getlist('check_equipes') if x.isdigit()]
    
    if projeto_id and equipes_ids:
        projeto = Project.query.get_or_404(projeto_id)
        equipes = Team.query.filter(Team.pk_id_team.in_(equipes_ids)).all()
        projeto.teams = equipes
        database.session.commit()
        
        nomes = ', '.join([eq.name_team for eq in equipes])
        registrar_log('projeto', 'Equipes vinculadas', f"As equipes '{nomes}' foram vinculadas ao projeto '{projeto.name_project}'.", projeto.pk_id_project)
    
    return redirect(url_for('admin.projeto_detalhe', id=projeto_id))

# ---------------------------------------------------------------------------
# Editar projeto
# ---------------------------------------------------------------------------
@admin_bp.route('/editar-projeto', methods=['POST'])
def editar_projeto():
    projeto_id = request.form.get('projeto_id', type=int)
    projeto = Project.query.get_or_404(projeto_id)
    
    nome = request.form.get('nome')
    if not nome:
        flash("O nome do projeto é obrigatório.", "erro")
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    
    projeto.name_project = nome
    projeto.status_project = request.form.get('situacao')

    orcamento_raw = request.form.get('orcamento', type=float)
    projeto.orcamento = orcamento_raw if orcamento_raw else 0.0
    from datetime import date

    projeto.status_project = request.form.get('status')

    prazo_str = request.form.get('prazo_str')

    try:
        projeto.end_date_project = date.fromisoformat(prazo_str) if prazo_str else None
    except ValueError:
        projeto.end_date_project = None

    projeto.description_project = request.form.get('descricao')
    projeto.fk_client = request.form.get('cliente_id', type=int)
    
    equipes_ids = [int(x) for x in request.form.getlist('check_equipes') if x.isdigit()]
    if equipes_ids:
        equipes = Team.query.filter(Team.pk_id_team.in_(equipes_ids)).all()
        projeto.teams = equipes
    else:
        projeto.teams = []
    
    try:
        database.session.commit()
        registrar_log('projeto', 'Projeto atualizado', f"As informações do projeto '{projeto.name_project}' foram atualizadas.", projeto.pk_id_project)
        flash("Projeto atualizado com sucesso.", "sucesso")
    except Exception as e:
        database.session.rollback()
        flash(f"Erro ao atualizar projeto: {e}", "erro")
    
    return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
# ---------------------------------------------------------------------------
# Excluir projeto (remove logs e requisitos associados)
# ---------------------------------------------------------------------------
@admin_bp.route('/excluir-projeto/<int:id>', methods=['POST'])
def excluir_projeto(id):
    projeto = Project.query.get_or_404(id)
    nome_projeto = projeto.name_project
    try:
        Log.query.filter_by(fk_project=id).delete()
        Requirement.query.filter_by(fk_project=id).delete()
        
        database.session.delete(projeto)
        database.session.commit()
        registrar_log('projeto', 'Projeto excluído', f"O projeto '{nome_projeto}' foi removido do sistema.")
        flash("Projeto excluído com sucesso.", "sucesso")
    except Exception as e:
        database.session.rollback()
        flash(f"Erro ao excluir projeto: {e}", "erro")
    return redirect(url_for('admin.projetos'))

# =============================================================================
# CRUD - REQUISITOS
# =============================================================================

# ---------------------------------------------------------------------------
# Adicionar requisito a um projeto
# ---------------------------------------------------------------------------
@admin_bp.route('/add-requisito', methods=['POST'])
def add_requisito():
    projeto_id = request.form.get('projeto_id', type=int)
    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    tipo = request.form.get('tipo')
    
    projeto = Project.query.get_or_404(projeto_id)
    
    novo_req = Requirement(
        fk_project=projeto_id,
        name_requirement=titulo,
        description_requirement=descricao,
        type_requirement=tipo,
        status_requirement='Pendente'
    )
    database.session.add(novo_req)
    database.session.commit()
    
    registrar_log('requisito', 'Requisito adicionado', f"Novo requisito '{titulo}' adicionado ao projeto '{projeto.name_project}'.", projeto.pk_id_project)
    
    return redirect(url_for('admin.projeto_detalhe', id=projeto_id))

# ---------------------------------------------------------------------------
# Excluir requisito
# ---------------------------------------------------------------------------
@admin_bp.route('/excluir-requisito/<int:id>', methods=['POST'])
def excluir_requisito(id):
    req = Requirement.query.get_or_404(id)
    projeto_id = req.fk_project
    titulo = req.name_requirement
    
    try:
        database.session.delete(req)
        database.session.commit()
        registrar_log('requisito', 'Requisito excluído', f"O requisito '{titulo}' foi removido do projeto.", projeto_id)
        flash("Requisito excluído com sucesso.", "sucesso")
    except Exception as e:
        database.session.rollback()
        flash(f"Erro ao excluir requisito: {e}", "erro")
    
    return redirect(url_for('admin.projeto_detalhe', id=projeto_id))

# =============================================================================
# CRUD - CLIENTES
# =============================================================================

# ---------------------------------------------------------------------------
# Listagem de clientes
# ---------------------------------------------------------------------------
@admin_bp.route('/clientes')
def clientes():
    todos_clientes = Client.query.join(User).all()
    return render_template(
        'admin/clientes.html',
        clientes = todos_clientes
    )

def _gerar_email_cliente(nome):
    partes = nome.strip().split()
    if len(partes) > 1:
        nome_simplificado = f"{partes[0]} {partes[-1]}"
    elif len(partes) == 1:
        nome_simplificado = partes[0]
    else:
        nome_simplificado = ""
    nome_simplificado = unicodedata.normalize('NFKD', nome_simplificado).encode('ascii', 'ignore').decode('utf-8')
    nome_simplificado = nome_simplificado.lower()
    nome_simplificado = nome_simplificado.replace(' ', '.')
    nome_simplificado = re.sub(r'[^a-z0-9.]', '', nome_simplificado)
    return f'{nome_simplificado}@cobyte_cliente.com'

# ---------------------------------------------------------------------------
# Criar novo cliente (cria Usuario + Cliente)
# ---------------------------------------------------------------------------
@admin_bp.route('/add-cliente', methods=['POST'])

def add_cliente():
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    empresa = request.form.get('empresa')

    partes_nome = nome.strip().split()
    if len(partes_nome) > 1:
        nome_simplificado = f"{partes_nome[0]} {partes_nome[-1]}"
    elif len(partes_nome) == 1:
        nome_simplificado = partes_nome[0]
    else:
        nome_simplificado = ""

    base_nome = unicodedata.normalize('NFKD', nome_simplificado).encode(
        'ascii', 'ignore'
    ).decode('utf-8')

    base_nome = base_nome.lower()
    base_nome = base_nome.replace(' ', '.')
    base_nome = re.sub(r'[^a-z0-9.]', '', base_nome)

    email = f'{base_nome}@cobyte_cliente.com'

    contador = 1

    while User.query.filter_by(email_user=email).first():
        email = f'{base_nome}.{contador}@cobyte_cliente.com'
        contador += 1

    usuario = User(
        name_user=nome,
        email_user=email,
        password_user=generate_password_hash(senha),
        type_user='cliente'
    )

    database.session.add(usuario)
    database.session.flush()

    cliente = Client(
        fk_user=usuario.pk_id_user,
        company_client=empresa
    )

    database.session.add(cliente)
    database.session.commit()

    return redirect(url_for('admin.clientes'))
# ---------------------------------------------------------------------------
# Excluir cliente (remove Cliente + Usuario associado)
# ---------------------------------------------------------------------------
@admin_bp.route('/cliente/excluir/<int:id>', methods=['POST'])
def excluir_cliente(id):
    cliente = Client.query.get_or_404(id)
    usuario = User.query.get(cliente.fk_user)
    nome = usuario.name_user if usuario else "Cliente"
    
    try:
        Project.query.filter_by(fk_client=id).update({Project.fk_client: None})
        database.session.delete(cliente)
        if usuario:
            database.session.delete(usuario)
        database.session.commit()
        registrar_log('cliente', 'Cliente excluído', f"O cliente '{nome}' foi removido do sistema.")
        flash("Cliente excluído com sucesso.", "sucesso")
    except Exception as e:
        database.session.rollback()
        flash(f"Erro ao excluir cliente: {e}", "erro")
    return redirect(url_for('admin.clientes'))

# ---------------------------------------------------------------------------
# Editar cliente
# ---------------------------------------------------------------------------
@admin_bp.route('/cliente/editar/<int:id>', methods=['POST'])
def editar_cliente(id):
    cliente = Client.query.get_or_404(id)
    usuario = User.query.get_or_404(cliente.fk_user)
    
    nome = request.form.get('nome')
    email = request.form.get('email')
    empresa = request.form.get('empresa')
    
    if not nome or not email:
        flash("Nome e email são obrigatórios.", "erro")
        return redirect(url_for('admin.clientes'))
    
    email_existente = User.query.filter(User.email_user == email, User.pk_id_user != usuario.pk_id_user).first()
    if email_existente:
        flash("Este email já está em uso por outro usuário.", "erro")
        return redirect(url_for('admin.clientes'))
    
    usuario.name_user = nome
    usuario.email_user = email
    cliente.company_client = empresa
    
    senha = request.form.get('senha')
    if senha:
        usuario.password_user = generate_password_hash(senha)
    
    try:
        database.session.commit()
        flash("Cliente atualizado com sucesso.", "sucesso")
    except Exception as e:
        database.session.rollback()
        flash(f"Erro ao atualizar cliente: {e}", "erro")
    
    return redirect(url_for('admin.clientes'))

# ---------------------------------------------------------------------------
# Editar cliente
# ---------------------------------------------------------------------------
# Listagem de equipes
# ---------------------------------------------------------------------------
@admin_bp.route('/equipes')
def equipes():
    todas_equipes = Team.query.all()
    todos_funcionarios = Employee.query.join(User).all()
    todos_projetos = Project.query.all()
    return render_template(
        'admin/equipes.html',
        equipes = todas_equipes,
        funcionarios = todos_funcionarios,
        projetos = todos_projetos
    )

# ---------------------------------------------------------------------------
# Criar nova equipe (com membros e projetos)
# ---------------------------------------------------------------------------
@admin_bp.route('/add-equipe', methods=['POST'])
def add_equipe():
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    funcao = request.form.get('funcao')
    lider_equipe = request.form.get('lider_equipe', type=int)
    funcionarios_ids = [int(x) for x in request.form.getlist('check_funcionarios') if x.isdigit()]
    projetos_ids = [int(x) for x in request.form.getlist('check_projetos') if x.isdigit()]
    
    equipe = Team(name_team=nome, description_team=descricao, funcao=funcao, lider_equipe=lider_equipe)
    
    if funcionarios_ids:
        membros = Employee.query.filter(Employee.pk_id_employee.in_(funcionarios_ids)).all()
        equipe.employees.extend(membros)

    if projetos_ids:
        projs = Project.query.filter(Project.pk_id_project.in_(projetos_ids)).all()
        equipe.projects.extend(projs)

    database.session.add(equipe)
    database.session.commit()
    return redirect(url_for('admin.equipes'))

# ---------------------------------------------------------------------------
# Excluir equipe
# ---------------------------------------------------------------------------
@admin_bp.route('/equipes/excluir/<int:id>', methods=['POST'])
def excluir_equipe(id):
    equipe = Team.query.get_or_404(id)
    nome = equipe.name_team
    try:
        database.session.execute(project_teams.delete().where(project_teams.c.fk_team == id))
        equipe.employees = []
        database.session.delete(equipe)
        database.session.commit()
        registrar_log('equipe', 'Equipe excluída', f"A equipe '{nome}' foi removida do sistema.")
        flash("Equipe excluída com sucesso.", "sucesso")
    except Exception as e:
        database.session.rollback()
        flash(f"Erro ao excluir equipe: {e}", "erro")
    return redirect(url_for('admin.equipes'))

# ---------------------------------------------------------------------------
# Editar equipe
# ---------------------------------------------------------------------------
@admin_bp.route('/equipes/editar/<int:id>', methods=['POST'])
def editar_equipe(id):
    equipe = Team.query.get_or_404(id)
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    funcao = request.form.get('funcao')
    lider_equipe = request.form.get('lider_equipe', type=int)
    funcionarios_ids = [int(x) for x in request.form.getlist('check_funcionarios') if x.isdigit()]
    projetos_ids = [int(x) for x in request.form.getlist('check_projetos') if x.isdigit()]
    
    if not nome:
        flash("O nome da equipe é obrigatório.", "erro")
        return redirect(url_for('admin.equipes'))
    
    equipe.name_team = nome
    equipe.description_team = descricao
    equipe.funcao = funcao
    equipe.lider_equipe = lider_equipe
    
    if funcionarios_ids:
        membros = Employee.query.filter(Employee.pk_id_employee.in_(funcionarios_ids)).all()
        equipe.employees = membros
    else:
        equipe.employees = []
    
    if projetos_ids:
        projs = Project.query.filter(Project.pk_id_project.in_(projetos_ids)).all()
        equipe.projects = projs
    else:
        equipe.projects = []
    
    try:
        database.session.commit()
        flash("Equipe atualizada com sucesso.", "sucesso")
    except Exception as e:
        database.session.rollback()
        flash(f"Erro ao atualizar equipe: {e}", "erro")
    
    return redirect(url_for('admin.equipes'))

# ---------------------------------------------------------------------------
# Detalhes de uma equipe (membros, projetos, logs, líder)
# ---------------------------------------------------------------------------
@admin_bp.route('/equipes/<int:id>')
def equipe_detalhe(id):
    equipe = Team.query.get_or_404(id)
    funcionarios = equipe.employees
    projetos = equipe.projects
    
    lider = None
    if equipe.lider_equipe:
        lider = Employee.query.get(equipe.lider_equipe)
    
    projeto_ids = [p.pk_id_project for p in projetos]
    logs = []
    if projeto_ids:
        logs = Log.query.filter(Log.fk_project.in_(projeto_ids)).order_by(Log.date_log.desc()).all()
    
    todos_funcionarios = (
        Employee.query
        .join(User, Employee.fk_user == User.pk_id_user)
        .add_entity(User)
        .all()
    )
    
    return render_template('admin/equipe-detalhe.html', 
                           equipe=equipe, 
                           funcionarios=funcionarios, 
                           projetos=projetos,
                           logs=logs,
                           todos_funcionarios=todos_funcionarios,
                           lider=lider)

# ---------------------------------------------------------------------------
# Adicionar membro a uma equipe
# ---------------------------------------------------------------------------
@admin_bp.route('/equipes/<int:equipe_id>/add-membro', methods=['POST'])
def equipe_add_membro(equipe_id):
    equipe = Team.query.get_or_404(equipe_id)
    funcionario_id = request.form.get('funcionario_id')
    if funcionario_id:
        funcionario = Employee.query.get(int(funcionario_id))
        if funcionario and funcionario not in equipe.employees:
            equipe.employees.append(funcionario)
            
            nome_func = funcionario.user.name_user if funcionario.user else 'Desconhecido'
            registro = Log(
                type_log="Membro adicionado",
                description_log=f"Funcionário {nome_func} foi adicionado à equipe {equipe.name_team}.",
            )
            database.session.add(registro)
            database.session.commit()
            flash("Membro adicionado com sucesso!", "sucesso")
    return redirect(url_for('admin.equipe_detalhe', id=equipe_id))

# ---------------------------------------------------------------------------
# Remover membro de uma equipe
# ---------------------------------------------------------------------------
@admin_bp.route('/equipes/<int:equipe_id>/remover-membro/<int:funcionario_id>', methods=['POST'])
def equipe_remover_membro(equipe_id, funcionario_id):
    equipe = Team.query.get_or_404(equipe_id)
    funcionario = Employee.query.get_or_404(funcionario_id)
    if funcionario in equipe.employees:
        equipe.employees.remove(funcionario)
        
        nome_func = funcionario.user.name_user if funcionario.user else 'Desconhecido'
        registro = Log(
            type_log="Membro removido",
            description_log=f"Funcionário {nome_func} foi removido da equipe {equipe.name_team}.",
        )
        database.session.add(registro)
        database.session.commit()
        flash("Membro removido com sucesso!", "sucesso")
    return redirect(url_for('admin.equipe_detalhe', id=equipe_id))





# =============================================================================
# CRUD - FUNCIONÁRIOS
# =============================================================================

# ---------------------------------------------------------------------------
# Listagem de funcionários
# ---------------------------------------------------------------------------
@admin_bp.route('/funcionarios')
def funcionarios():
    funcionarios = (
        Employee.query
        .join(User, Employee.fk_user == User.pk_id_user)
        .add_entity(User)
        .all()
    )
    total = Employee.query.count()
    equipes = Team.query.all()
    return render_template(
        'admin/funcionarios.html',
        funcionarios = funcionarios,
        total        = total,
        equipes      = equipes
    )

# ---------------------------------------------------------------------------
# Perfil de um funcionário
# ---------------------------------------------------------------------------
@admin_bp.route('/funcionario/<int:id>')
def funcionario_perfil(id):
    funcionario = Employee.query.get_or_404(id)
    
    # Buscar equipes do funcionário
    equipes = funcionario.teams
    equipes_ids = [eq.pk_id_team for eq in equipes]
    
    # Buscar projetos associados às equipes do funcionário
    projetos = []
    if equipes_ids:
        projetos = (
            Project.query
            .join(project_teams, Project.pk_id_project == project_teams.c.fk_project)
            .filter(project_teams.c.fk_team.in_(equipes_ids))
            .distinct()
            .all()
        )
    
    projetos_ids = [proj.pk_id_project for proj in projetos]
    
    # Buscar documentos, diagramas e galeria dos projetos
    documentos = []
    diagramas = []
    galeria = []
    if projetos_ids:
        documentos = Document.query.filter(Document.fk_project.in_(projetos_ids)).all()
        diagramas = Diagram.query.filter(Diagram.fk_project.in_(projetos_ids)).all()
        galeria = Gallery.query.filter(Gallery.fk_project.in_(projetos_ids)).all()
    
    return render_template(
        'admin/funcionario-perfil.html', 
        funcionario=funcionario,
        projetos=projetos,
        documentos=documentos,
        diagramas=diagramas,
        galeria=galeria
    )

# ---------------------------------------------------------------------------
# Criar novo funcionário (cria Usuario + Funcionario + habilidades)
# ---------------------------------------------------------------------------
def _gerar_email_funcionario(nome):
    nome = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode('utf-8')
    nome = nome.lower().strip()
    nome = nome.replace(' ', '.')
    nome = re.sub(r'[^a-z0-9.]', '', nome)
    return nome

@admin_bp.route('/add-funcionario', methods=['POST'])
def add_funcionario():
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    cargo = request.form.get('cargo')
    habilidades_str = request.form.get('habilidades', '')

    nome_formatado = _gerar_email_funcionario(nome)
    email = f'{nome_formatado}@cobyte_funcionario.com'
    contador = 1

    while User.query.filter_by(email_user=email).first():
        email = f'{nome_formatado}.{contador}@cobyte_funcionario.com'
        contador += 1

    usuario = User(
        name_user=nome,
        email_user=email,
        password_user=generate_password_hash(senha),
        type_user='employee'
    )
    database.session.add(usuario)
    database.session.flush()

    funcionario = Employee(
        fk_user=usuario.pk_id_user,
        role_employee=cargo
    )

    if habilidades_str:
        for hab_nome in [s.strip() for s in habilidades_str.split(',')]:
            habilidade = Skill.query.filter_by(name_skill=hab_nome).first()
            if not habilidade:
                habilidade = Skill(name_skill=hab_nome)
                database.session.add(habilidade)
                database.session.flush()
            funcionario.skills.append(habilidade)

    database.session.add(funcionario)
    database.session.commit()

    return redirect(url_for('admin.funcionarios'))

# ---------------------------------------------------------------------------
# Editar funcionário
# ---------------------------------------------------------------------------
@admin_bp.route('/funcionario/editar/<int:id>', methods=['POST'])
def editar_funcionario(id):
    funcionario = Employee.query.get_or_404(id)
    usuario = User.query.get(funcionario.fk_user)
    if not usuario:
        flash("Usuário vinculado ao funcionário não encontrado.", "erro")
        return redirect(url_for('admin.funcionarios'))
    
    nome = request.form.get('nome')
    email = request.form.get('email')
    cargo = request.form.get('cargo')
    
    if not nome or not email or not cargo:
        flash("Nome, email e cargo são obrigatórios.", "erro")
        return redirect(url_for('admin.funcionario_perfil', id=id))
    
    email_existente = User.query.filter(User.email_user == email, User.pk_id_user != usuario.pk_id_user).first()
    if email_existente:
        flash("Este email já está em uso por outro usuário.", "erro")
        return redirect(url_for('admin.funcionario_perfil', id=id)) 
    
    usuario.name_user = nome
    usuario.email_user = email
    funcionario.role_employee = cargo
    habilidades_str = request.form.get('habilidades', '')

    funcionario.skills = []
    if habilidades_str:
        for hab_nome in [s.strip() for s in habilidades_str.split(',')]:
            habilidade = Skill.query.filter_by(name_skill=hab_nome).first()
            if not habilidade:
                habilidade = Skill(name_skill=hab_nome)
                database.session.add(habilidade)
                database.session.flush()
            if habilidade not in funcionario.skills:
                funcionario.skills.append(habilidade)

    try:
        database.session.commit()
        flash("Funcionário atualizado com sucesso.", "sucesso")
    except Exception as e:
        database.session.rollback()
        flash(f"Erro ao atualizar funcionário: {e}", "erro")
    
    return redirect(url_for('admin.funcionario_perfil', id=id))

# ---------------------------------------------------------------------------
# Excluir funcionário (remove associações + Usuario)
# ---------------------------------------------------------------------------
@admin_bp.route('/funcionario/excluir/<int:id>', methods=['POST'])
def excluir_funcionario(id):
    membro = Employee.query.get_or_404(id)
    usuario = User.query.get(membro.fk_user)
    nome = usuario.name_user if usuario else "Funcionário"
    try:
        membro.teams = []
        membro.skills = []
        
        database.session.delete(membro)
        if usuario:
            database.session.delete(usuario)
        database.session.commit()
        registrar_log('funcionario', 'Funcionário excluído', f"O funcionário '{nome}' foi removido do sistema.")
        flash("Funcionário excluído com sucesso.", "sucesso")
    except Exception as e:
        database.session.rollback()
        flash(f"Erro ao excluir funcionário: {e}", "erro")
    return redirect(url_for('admin.funcionarios'))

# =============================================================================
# CONFIGURAÇÕES DO ADMIN
# =============================================================================

# ---------------------------------------------------------------------------
# Página de configurações
# ---------------------------------------------------------------------------
@admin_bp.route('/configuracoes')
def configuracoes():
    from flask import get_flashed_messages
    get_flashed_messages()
    return render_template('admin/configuracoes.html')

# ---------------------------------------------------------------------------
# Alterar senha do administrador
# ---------------------------------------------------------------------------
@admin_bp.route('/configuracoes/senha', methods=['POST'])
def salvar_senha():
    senha_atual = request.form.get('senha_atual')
    nova_senha = request.form.get('nova_senha')
    confirmar_senha = request.form.get('confirmar_senha')
    
    if not senha_atual or not nova_senha or not confirmar_senha:
        flash('Preencha todos os campos!', 'danger')
        return redirect(url_for('admin.configuracoes') + '#seguranca')
        
    if nova_senha != confirmar_senha:
        flash('As senhas não coincidem!', 'danger')
        return redirect(url_for('admin.configuracoes') + '#seguranca')
        
    if not check_password_hash(current_user.password_user, senha_atual):
        flash('Senha atual incorreta!', 'danger')
        return redirect(url_for('admin.configuracoes') + '#seguranca')
        
    current_user.password_user = generate_password_hash(nova_senha)
    database.session.commit()
    flash('Senha atualizada com sucesso!', 'success')

# ---------------------------------------------------------------------------
# Salvar GitHub Key do administrador
# ---------------------------------------------------------------------------
@admin_bp.route('/configuracoes/github-key', methods=['POST'])
def salvar_github_key():
    from function.crypto import encrypt_token
    from flask import current_app

    github_key = request.form.get('github_key')
    if github_key and github_key != '********':
        current_user.github_key_user = encrypt_token(current_app.config['SECRET_KEY'], github_key)
        database.session.commit()
        flash('Token do GitHub salvo com sucesso!', 'success')
    else:
        flash('Nenhuma alteração realizada.', 'info')
    return redirect(url_for('admin.configuracoes') + '#integracoes')
    return redirect(url_for('admin.configuracoes') + '#seguranca')
