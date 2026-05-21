from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import database
import json
import datetime
from models import Usuario, Funcionario, Projeto, Equipes, Requisito, Log, Cliente

funcionario_bp = Blueprint('funcionario', __name__, url_prefix='/funcionario')

@funcionario_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.tipo != 'funcionario':
        return redirect(url_for('page_login'))
    
    # Busca o registro de Funcionário
    funcionario = Funcionario.query.filter_by(usuario_id=current_user.id).first()
    if not funcionario:
        return "Perfil de funcionário não encontrado", 404
    
    # Busca as equipes do funcionário
    equipes = funcionario.lista_equipes
    
    # Busca os projetos associados a essas equipes
    projetos = []
    equipes_ids = [eq.id for eq in equipes]
    if equipes_ids:
        projetos = Projeto.query.filter(Projeto.equipe_id.in_(equipes_ids)).all()
    
    # Cálculo das métricas premium
    total_projetos = len(projetos)
    
    # Membros únicos de equipe
    membros_ids = set()
    for eq in equipes:
        for m in eq.membros_da_equipe:
            membros_ids.add(m.id)
    total_equipe = len(membros_ids)
    
    # Clientes únicos vinculados
    cliente_ids = set()
    for p in projetos:
        if p.cliente_id:
            cliente_ids.add(p.cliente_id)
    total_clientes = len(cliente_ids)
    
    # Total de Budget envolvido nos projetos do funcionário
    budget_total = sum(p.budget for p in projetos if p.budget) or 0
    
    # Requisitos pendentes associados aos projetos do funcionário
    requisitos_pendentes = 0
    for proj in projetos:
        for req in proj.requisitos:
            if req.status == 'Pendente':
                requisitos_pendentes += 1
                
    stats = {
        'projetos_ativos': len([p for p in projetos if p.status == 'Em andamento']),
        'equipes_count': len(equipes),
        'requisitos_pendentes': requisitos_pendentes
    }
    
    # ── Status dos Projetos (Donut) ──────────────────
    status_cores = {
        'Em andamento': '#f59e0b',
        'Concluído':    '#10b981',
        'Pausado':      '#FF5577',
    }
    status_counts = {s: 0 for s in status_cores.keys()}
    for p in projetos:
        s = p.status or 'Pausado'
        if s == 'Pendente':
            s = 'Pausado'
        if s == 'Cancelado':
            continue
        if s in status_counts:
            status_counts[s] += 1
            
    status_data = [
        {'label': s, 'val': c, 'color': status_cores.get(s, '#6b7280')}
        for s, c in status_counts.items()
    ]
    
    # ── Atividade Mensal (barras por status por mês dos projetos associados) ──────────────────
    monthly_map = {m: {'Em andamento': 0, 'Concluído': 0, 'Pausado': 0} for m in range(1, 13)}
    for p in projetos:
        if p.prazo and len(p.prazo) >= 7:
            try:
                parts = p.prazo.split('-')
                m = int(parts[1])
                st = p.status or 'Pausado'
                if st == 'Pendente':
                    st = 'Pausado'
                if st == 'Cancelado':
                    continue
                if st not in monthly_map[m]:
                    st = 'Pausado'
                monthly_map[m][st] += 1
            except (ValueError, IndexError):
                pass
                
    volumes = [
        {
            'em_andamento': monthly_map[m]['Em andamento'],
            'concluido': monthly_map[m]['Concluído'],
            'pendente': monthly_map[m]['Pausado']
        }
        for m in range(1, 13)
    ]
    
    # ── Logs dos projetos do funcionário ──────────────────
    logs_data = []
    todos_logs_data = []
    if projetos:
        proj_ids = [p.id for p in projetos]
        logs_query = (
            database.session.query(Log, Projeto, Equipes)
            .outerjoin(Projeto, Log.projeto_id == Projeto.id)
            .outerjoin(Equipes, Projeto.equipe_id == Equipes.id)
            .filter(Log.projeto_id.in_(proj_ids))
            .order_by(Log.data.desc())
            .limit(10)
            .all()
        )
        for log, proj_obj, eq_obj in logs_query:
            logs_data.append({
                'acao': log.acao,
                'descricao': log.descricao,
                'data': log.data,
                'equipe_nome': eq_obj.nome if eq_obj else (proj_obj.nome if proj_obj else 'Geral')
            })
            
        todos_logs_query = (
            database.session.query(Log, Projeto, Equipes)
            .outerjoin(Projeto, Log.projeto_id == Projeto.id)
            .outerjoin(Equipes, Projeto.equipe_id == Equipes.id)
            .filter(Log.projeto_id.in_(proj_ids))
            .order_by(Log.data.desc())
            .all()
        )
        for log, proj_obj, eq_obj in todos_logs_query:
            todos_logs_data.append({
                'acao': log.acao,
                'descricao': log.descricao,
                'data': log.data,
                'equipe_nome': eq_obj.nome if eq_obj else (proj_obj.nome if proj_obj else 'Geral')
            })
            
    # Para o painel de atividades recentes no rodapé do dashboard, vamos associar o último log a cada projeto
    for proj in projetos:
        latest_log = Log.query.filter_by(projeto_id=proj.id).order_by(Log.data.desc()).first()
        proj.ultimo_log = latest_log.descricao if latest_log else "Sem alterações recentes"
            
    # ── Atividade Mensal do Mês Atual ──────────────────
    now = datetime.datetime.now()
    current_month_num = now.month
    meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    current_month_name = meses_nomes[current_month_num]
    
    current_month_projects = {
        'em_andamento': [],
        'concluido': [],
        'pausado': []
    }
    
    current_year = now.year
    prefix_current_month = f"{current_year}-{current_month_num:02d}"
    month_infix = f"-{current_month_num:02d}-"
    
    for proj in projetos:
        if proj.prazo:
            is_match = proj.prazo.startswith(prefix_current_month) or month_infix in proj.prazo
            if not is_match and len(proj.prazo) >= 7:
                try:
                    parts = proj.prazo.split('-')
                    if len(parts) >= 2 and int(parts[1]) == current_month_num:
                        is_match = True
                except ValueError:
                    pass
            if is_match:
                status_str = proj.status or 'Pausado'
                if status_str == 'Pendente':
                    status_str = 'Pausado'
                if status_str == 'Cancelado':
                    continue
                if status_str == 'Em andamento':
                    current_month_projects['em_andamento'].append(proj)
                elif status_str == 'Concluído':
                    current_month_projects['concluido'].append(proj)
                else:
                    current_month_projects['pausado'].append(proj)
                    
    # Funcionários da equipe para o widget
    funcionarios_dash = (
        Funcionario.query
        .join(Usuario, Funcionario.usuario_id == Usuario.id)
        .add_entity(Usuario)
        .limit(4)
        .all()
    )

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
        budget_total=budget_total,
        funcionarios_dash=funcionarios_dash,
        status_data_json=json.dumps(status_data),
        volumes_json=json.dumps(volumes),
        logs=logs_data,
        todos_logs=todos_logs_data,
        current_month_name=current_month_name,
        current_month_projects=current_month_projects
    )

@funcionario_bp.route('/projetos')
@login_required
def projetos():
    funcionario = Funcionario.query.filter_by(usuario_id=current_user.id).first()
    equipes = funcionario.lista_equipes
    equipes_ids = [eq.id for eq in equipes]
    
    projetos = []
    if equipes_ids:
        projetos = Projeto.query.filter(Projeto.equipe_id.in_(equipes_ids)).all()
        
    return render_template('funcionario/projetos.html', projetos=projetos)

@funcionario_bp.route('/projeto-detalhe/<int:projeto_id>')
@login_required
def projeto_detalhe(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)
    
    # Verifica se o funcionário pertence à equipe do projeto
    funcionario = Funcionario.query.filter_by(usuario_id=current_user.id).first()
    if projeto.equipe_id not in [eq.id for eq in funcionario.lista_equipes]:
        return "Acesso negado", 403
    
    membros = (
        Funcionario.query
        .join(Funcionario.lista_equipes)
        .filter(Equipes.id == projeto.equipe_id)
        .all()
    )
    
    return render_template(
        'funcionario/projeto-detalhe.html',
        projeto=projeto,
        membros=membros,
        requisitos=projeto.requisitos
    )

@funcionario_bp.route('/add-requisito', methods=['POST'])
@login_required
def add_requisito():
    projeto_id = request.form.get('projeto_id')
    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    tipo = request.form.get('tipo')
    
    novo_req = Requisito(
        projeto_id=projeto_id,
        titulo=titulo,
        descricao=descricao,
        tipo=tipo,
        status='Pendente'
    )
    database.session.add(novo_req)
    database.session.commit()
    
    return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))

@funcionario_bp.route('/equipe')
@login_required
def equipe():
    funcionario = Funcionario.query.filter_by(usuario_id=current_user.id).first()
    equipes = funcionario.lista_equipes
    
    # Pega os membros de todas as equipes do funcionário
    membros_data = {}
    for eq in equipes:
        membros = (
            Funcionario.query
            .join(Funcionario.lista_equipes)
            .filter(Equipes.id == eq.id)
            .all()
        )
        membros_data[eq.id] = {
            'nome': eq.nome,
            'membros': membros
        }
        
    return render_template('funcionario/equipe.html', equipes_info=membros_data)

@funcionario_bp.route('/configuracoes')
@login_required
def configuracoes():
    return render_template('funcionario/configuracoes.html')


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
        
    if not check_password_hash(current_user.senha, senha_atual):
        flash('Senha atual incorreta!', 'danger')
        return redirect(url_for('funcionario.configuracoes') + '#seguranca')
        
    current_user.senha = generate_password_hash(nova_senha)
    database.session.commit()
    flash('Senha atualizada com sucesso!', 'success')
    return redirect(url_for('funcionario.configuracoes') + '#seguranca')
