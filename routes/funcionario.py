# =============================================================================
# routes/funcionario.py - Blueprint do Funcionário
# =============================================================================
# Gerencia dashboard, visualização de projetos e equipes para funcionários
# com nível de acesso 2. Os funcionários só veem projetos de suas equipes.
# =============================================================================

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import database as db, database
import json
import datetime
from models import User, Employee, Project, Team, Requirement, Log, Client, project_teams, Document, Diagram, Gallery, Comment

funcionario_bp = Blueprint('funcionario', __name__, url_prefix='/funcionario')

# =============================================================================
# DASHBOARD DO FUNCIONÁRIO
# =============================================================================
@funcionario_bp.route('/')
@funcionario_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.type_user != 'employee':
        return redirect(url_for('page_login'))
    
    funcionario = Employee.query.filter_by(fk_user=current_user.pk_id_user).first()
    if not funcionario:
        return "Perfil de funcionário não encontrado", 404
    
    equipes = funcionario.teams
    
    # Projetos associados às equipes do funcionário
    projetos = []
    equipes_ids = [eq.pk_id_team for eq in equipes]
    projeto_equipes_map = {}
    if equipes_ids:
        projetos = Project.query.join(project_teams, Project.pk_id_project == project_teams.c.fk_project).filter(project_teams.c.fk_team.in_(equipes_ids)).all()
        for p in projetos:
            project_team_ids = [t.pk_id_team for t in p.teams]
            func_team_ids = [eid for eid in equipes_ids if eid in project_team_ids]
            func_teams = Team.query.filter(Team.pk_id_team.in_(func_team_ids)).all()
            projeto_equipes_map[p.pk_id_project] = func_teams
    
    # Métricas
    total_projetos = len(projetos)
    
    membros_ids = set()
    for eq in equipes:
        for m in eq.employees:
            membros_ids.add(m.pk_id_employee)
    total_equipe = len(membros_ids)
    
    cliente_ids = set()
    for p in projetos:
        if p.fk_client:
            cliente_ids.add(p.fk_client)
    total_clientes = len(cliente_ids)
    
    orcamento_total = sum(p.orcamento or 0 for p in projetos)
    
    requisitos_pendentes = 0
    for proj in projetos:
        for req in proj.requirements:
            if req.status_requirement == 'Pendente':
                requisitos_pendentes += 1
                
    stats = {
        'projetos_ativos': len([p for p in projetos if p.status_project == 'Em andamento']),
        'equipes_count': len(equipes),
        'requisitos_pendentes': requisitos_pendentes
    }
    
    # ── Gráfico de Status (Donut) ──────────────────
    status_cores = {
        'Em andamento': '#f59e0b',
        'Concluído':    '#10b981',
        'Pausado':      '#FF5577',
        'Cancelado':    '#6b7280',
    }
    status_counts = {s: 0 for s in status_cores.keys()}
    for p in projetos:
        s = p.status_project or 'Pausado'
        if s == 'Pendente':
            s = 'Pausado'
        if s in status_counts:
            status_counts[s] += 1
            
    status_data = [
        {'label': s, 'val': c, 'color': status_cores.get(s, '#6b7280')}
        for s, c in status_counts.items()
    ]
    
    # ── Logs dos projetos do funcionário (apenas do usuario logado) ──
    logs_data = []
    todos_logs_data = []
    if projetos:
        proj_ids = [p.pk_id_project for p in projetos]
        logs_query = (
            database.session.query(Log, Project, User)
            .outerjoin(Project, Log.fk_project == Project.pk_id_project)
            .outerjoin(User, Log.fk_user == User.pk_id_user)
            .filter(Log.fk_project.in_(proj_ids))
            .order_by(Log.date_log.desc())
            .limit(10)
            .all()
        )
        for log, proj_obj, usuario in logs_query:
            project_name = proj_obj.name_project if proj_obj else '—'
            equipe_nome = log.team.name_team if log.team else (', '.join([eq.name_team for eq in proj_obj.teams]) if proj_obj and proj_obj.teams else '—')
            user_name = usuario.name_user if usuario else 'Sistema'
            logs_data.append({
                'type_log': log.type_log,
                'description_log': log.description_log,
                'date_log': log.date_log,
                'project_name': project_name,
                'equipe_nome': equipe_nome,
                'user_name': user_name
            })
            
        todos_logs_query = (
            database.session.query(Log, Project, User)
            .outerjoin(Project, Log.fk_project == Project.pk_id_project)
            .outerjoin(User, Log.fk_user == User.pk_id_user)
            .filter(Log.fk_project.in_(proj_ids))
            .order_by(Log.date_log.desc())
            .all()
        )
        for log, proj_obj, usuario in todos_logs_query:
            project_name = proj_obj.name_project if proj_obj else '—'
            equipe_nome = log.team.name_team if log.team else (', '.join([eq.name_team for eq in proj_obj.teams]) if proj_obj and proj_obj.teams else '—')
            user_name = usuario.name_user if usuario else 'Sistema'
            todos_logs_data.append({
                'type_log': log.type_log,
                'description_log': log.description_log,
                'date_log': log.date_log,
                'project_name': project_name,
                'equipe_nome': equipe_nome,
                'user_name': user_name
            })
            
    # Último registro de cada projeto para o painel de atividades
    for proj in projetos:
        ultimo_registro = Log.query.filter_by(fk_project=proj.pk_id_project).order_by(Log.date_log.desc()).first()
        proj.ultimo_registro = ultimo_registro.description_log if ultimo_registro else "Sem alterações recentes"
            
    # ── Projetos do mês atual ──────────────────
    now = datetime.datetime.now()
    current_month_num = now.month
    meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    current_month_name = meses_nomes[current_month_num]
    
    current_month_projects = {
        'em_andamento': [],
        'concluido': [],
        'pausado': [],
        'cancelado': []
    }
    
    current_year = now.year
    
    for proj in projetos:
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
                    
    # Widget de funcionários
    funcionarios_painel = (
        Employee.query
        .join(User, Employee.fk_user == User.pk_id_user)
        .add_entity(User)
        .limit(4)
        .all()
    )

    # ── Todos os projetos do funcionário agrupados por status para o Donut Chart tooltip ──
    projetos_por_status = {
        'em_andamento': [],
        'concluido': [],
        'pausado': [],
        'cancelado': []
    }
    for proj in projetos:
        status_str = proj.status_project or 'Pausado'
        if status_str == 'Pendente':
            status_str = 'Pausado'
        
        proj_data = {
            'name_project': proj.name_project,
            'end_date_project': proj.end_date_project.strftime('%d/%m/%Y') if proj.end_date_project else 'Sem prazo',
            'url': url_for('funcionario.projeto_detalhe', projeto_id=proj.pk_id_project)
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
        'funcionario/dashboard.html',
        funcionario=funcionario,
        equipes=equipes,
        projetos=projetos,
        stats=stats,
        total_projetos=total_projetos,
        total_equipe=total_equipe,
        total_clientes=total_clientes,
        projetos_recentes=projetos,
        projeto_equipes_map=projeto_equipes_map,
        budget_total=orcamento_total,
        funcionarios_painel=funcionarios_painel,
        status_data_json=json.dumps(status_data),
        projetos_status_json=json.dumps(projetos_por_status),
        logs=logs_data,
        todos_logs=todos_logs_data,
        current_month_name=current_month_name,
        current_month_projects=current_month_projects
    )

# =============================================================================
# CRUD - PROJETOS (visão do funcionário)
# =============================================================================

# ---------------------------------------------------------------------------
# Listagem de projetos
# ---------------------------------------------------------------------------
@funcionario_bp.route('/projetos')
@login_required
def projetos():
    if current_user.type_user != 'employee':
        return redirect(url_for('page_login'))
    funcionario = Employee.query.filter_by(fk_user=current_user.pk_id_user).first()
    if not funcionario:
        return "Perfil de funcionário não encontrado", 404
    equipes = funcionario.teams
    equipes_ids = [eq.pk_id_team for eq in equipes]
    
    projetos = []
    projeto_equipes_map = {}
    if equipes_ids:
        projetos = Project.query.join(project_teams, Project.pk_id_project == project_teams.c.fk_project).filter(project_teams.c.fk_team.in_(equipes_ids)).all()
        for p in projetos:
            project_team_ids = [t.pk_id_team for t in p.teams]
            func_team_ids = [eid for eid in equipes_ids if eid in project_team_ids]
            func_teams = Team.query.filter(Team.pk_id_team.in_(func_team_ids)).all()
            projeto_equipes_map[p.pk_id_project] = func_teams
        
    return render_template('funcionario/projetos.html', projetos=projetos, projeto_equipes_map=projeto_equipes_map)

# ---------------------------------------------------------------------------
# Detalhes de um projeto (com verificação de acesso por equipe)
# ---------------------------------------------------------------------------
@funcionario_bp.route('/projeto-detalhe/<int:projeto_id>')
@login_required
def projeto_detalhe(projeto_id):
    if current_user.type_user != 'employee':
        return redirect(url_for('page_login'))
    projeto = Project.query.get_or_404(projeto_id)
    
    funcionario = Employee.query.filter_by(fk_user=current_user.pk_id_user).first()
    if not funcionario:
        return "Perfil de funcionário não encontrado", 404
    equipes_ids = [eq.pk_id_team for eq in funcionario.teams]
    projeto_equipes_ids = [eq.pk_id_team for eq in projeto.teams]
    if not any(eq_id in projeto_equipes_ids for eq_id in equipes_ids):
        return "Acesso negado", 403
    
    # teams do funcionario que estao no projeto
    func_projeto_teams = Team.query.filter(Team.pk_id_team.in_(projeto_equipes_ids)).filter(Team.pk_id_team.in_(equipes_ids)).all()
    
    # requisitos sao globais — todos veem todos os requisitos do projeto
    requisitos = Requirement.query.filter_by(fk_project=projeto_id).all()

    equipe_id = request.args.get('equipe', type=int)
    if equipe_id:
        if equipe_id not in [t.pk_id_team for t in func_projeto_teams]:
            return "Acesso negado a esta equipe", 403
    elif len(func_projeto_teams) == 1:
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id, equipe=func_projeto_teams[0].pk_id_team))
    
    membros = (
        Employee.query
        .join(Employee.teams)
        .filter(Team.pk_id_team.in_(projeto_equipes_ids))
        .all()
    )
    
    func_projeto_team_ids = [t.pk_id_team for t in func_projeto_teams]

    if equipe_id:
        documentos = Document.query.filter_by(fk_project=projeto_id, fk_team=equipe_id).all()
        diagramas = Diagram.query.filter_by(fk_project=projeto_id, fk_team=equipe_id).all()
        galeria = Gallery.query.filter_by(fk_project=projeto_id, fk_team=equipe_id).all()
    else:
        documentos = Document.query.filter(
            Document.fk_project == projeto_id,
            Document.fk_team.in_(func_projeto_team_ids)
        ).all()
        diagramas = Diagram.query.filter(
            Diagram.fk_project == projeto_id,
            Diagram.fk_team.in_(func_projeto_team_ids)
        ).all()
        galeria = Gallery.query.filter(
            Gallery.fk_project == projeto_id,
            Gallery.fk_team.in_(func_projeto_team_ids)
        ).all()
    logs_projeto = (
        Log.query
        .options(db.joinedload(Log.team), db.joinedload(Log.project), db.joinedload(Log.user))
        .filter(Log.fk_project == projeto_id)
        .order_by(Log.date_log.desc())
        .all()
    )
    comentarios = Comment.query.filter_by(fk_project=projeto_id).order_by(Comment.date_comment.asc()).all()
    
    return render_template(
        'funcionario/projeto-detalhe.html',
        projeto=projeto,
        membros=membros,
        requisitos=requisitos,
        equipe_atual=equipe_id,
        equipes_disponiveis=func_projeto_teams,
        equipes=func_projeto_teams,
        documentos=documentos,
        diagramas=diagramas,
        galeria=galeria,
        comentarios=comentarios,
        logs_projeto=logs_projeto
    )

# ---------------------------------------------------------------------------
# Adicionar requisito a um projeto
# ---------------------------------------------------------------------------
@funcionario_bp.route('/add-requisito', methods=['POST'])
@login_required
def add_requisito():
    projeto_id = request.form.get('projeto_id')
    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    tipo = request.form.get('tipo')
    equipe_id = request.form.get('equipe_id', type=int)
    
    novo_req = Requirement(
        fk_project=projeto_id,
        fk_team=equipe_id,
        name_requirement=titulo,
        description_requirement=descricao,
        type_requirement=tipo,
        status_requirement='Pendente'
    )
    database.session.add(novo_req)
    database.session.commit()
    
    return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id, equipe=equipe_id))

# ---------------------------------------------------------------------------
# Editar requisito
# ---------------------------------------------------------------------------
@funcionario_bp.route('/update-requisito/<int:req_id>', methods=['POST'])
@login_required
def update_requisito(req_id):
    req = Requirement.query.get_or_404(req_id)
    projeto_id = req.fk_project
    equipe_id = req.fk_team
    
    # Verifica acesso do funcionario a esta equipe
    funcionario = Employee.query.filter_by(fk_user=current_user.pk_id_user).first()
    if not funcionario:
        return "Perfil nao encontrado", 404
    equipes_ids = [eq.pk_id_team for eq in funcionario.teams]
    if equipe_id and equipe_id not in equipes_ids:
        abort(403)
    
    req.name_requirement = request.form.get('titulo', req.name_requirement)
    req.description_requirement = request.form.get('descricao', req.description_requirement)
    req.type_requirement = request.form.get('tipo', req.type_requirement)
    req.status_requirement = request.form.get('status', req.status_requirement)
    database.session.commit()
    
    flash("Requisito atualizado com sucesso!", "sucesso")
    return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id, equipe=equipe_id))

# =============================================================================
# CODEFLOW
# =============================================================================
@funcionario_bp.route('/codeflow')
@funcionario_bp.route('/codeflow/dashboard')
@login_required
def codeflow_dashboard():
    if current_user.type_user != 'employee':
        return redirect(url_for('page_login'))
    from function.crypto import decrypt_token
    api_url = current_app.config.get('CODEFLOW_API_URL', 'http://localhost:5000')
    github_token = decrypt_token(current_app.config['SECRET_KEY'], current_user.github_key_user) if current_user.github_key_user else ''
    return render_template('funcionario/codeflow.html', api_url=api_url, github_token=github_token, active_page='codeflow')

# =============================================================================
# CONFIGURAÇÕES DO FUNCIONÁRIO
# =============================================================================

# ---------------------------------------------------------------------------
# Página de configurações
# ---------------------------------------------------------------------------
@funcionario_bp.route('/configuracoes')
@login_required
def configuracoes():
    return render_template('funcionario/configuracoes.html')

# ---------------------------------------------------------------------------
# Alterar senha
# ---------------------------------------------------------------------------
@funcionario_bp.route('/configuracoes/senha', methods=['POST'])
@login_required
def salvar_senha():
    senha_atual = request.form.get('senha_atual')
    nova_senha = request.form.get('nova_senha')
    confirmar_senha = request.form.get('confirmar_senha')
    
    if not senha_atual or not nova_senha or not confirmar_senha:
        flash('Preencha todos os campos!', 'danger')
        return redirect(url_for('funcionario.configuracoes') + '#seguranca')
        
    if nova_senha != confirmar_senha:
        flash('As senhas não coincidem!', 'danger')
        return redirect(url_for('funcionario.configuracoes') + '#seguranca')
        
    if not check_password_hash(current_user.password_user, senha_atual):
        flash('Senha atual incorreta!', 'danger')
        return redirect(url_for('funcionario.configuracoes') + '#seguranca')
        
    current_user.password_user = generate_password_hash(nova_senha)
    database.session.commit()
    flash('Senha atualizada com sucesso!', 'success')
    return redirect(url_for('funcionario.configuracoes') + '#seguranca')

# ---------------------------------------------------------------------------
# Salvar chave GitHub
# ---------------------------------------------------------------------------
@funcionario_bp.route('/configuracoes/github-key', methods=['POST'])
@login_required
def salvar_github_key():
    from flask import current_app
    from function.crypto import encrypt_token
    github_key = request.form.get('github_key', '')
    current_user.github_key_user = encrypt_token(current_app.config['SECRET_KEY'], github_key)
    database.session.commit()
    flash('Chave do GitHub salva com sucesso!', 'success')
    return redirect(url_for('funcionario.configuracoes') + '#integracoes')
