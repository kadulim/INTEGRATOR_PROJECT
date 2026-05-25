# =============================================================================
# routes/funcionario.py - Blueprint do Funcionário
# =============================================================================
# Gerencia dashboard, visualização de projetos e equipes para funcionários
# com nível de acesso 2. Os funcionários só veem projetos de suas equipes.
# =============================================================================

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import database
import json
import datetime
from models import Usuario, Funcionario, Projeto, Equipes, Requisito, Registro, Cliente, equipes_projeto, Documento, Diagrama, Galeria, Comentario

funcionario_bp = Blueprint('funcionario', __name__, url_prefix='/funcionario')

# =============================================================================
# DASHBOARD DO FUNCIONÁRIO
# =============================================================================
@funcionario_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.tipo != 'funcionario':
        return redirect(url_for('page_login'))
    
    funcionario = Funcionario.query.filter_by(usuario_id=current_user.id).first()
    if not funcionario:
        return "Perfil de funcionário não encontrado", 404
    
    equipes = funcionario.lista_equipes
    
    # Projetos associados às equipes do funcionário
    projetos = []
    equipes_ids = [eq.id for eq in equipes]
    if equipes_ids:
        projetos = Projeto.query.join(equipes_projeto, Projeto.id == equipes_projeto.c.projeto_id).filter(equipes_projeto.c.equipe_id.in_(equipes_ids)).all()
    
    # Métricas
    total_projetos = len(projetos)
    
    membros_ids = set()
    for eq in equipes:
        for m in eq.membros_da_equipe:
            membros_ids.add(m.id)
    total_equipe = len(membros_ids)
    
    cliente_ids = set()
    for p in projetos:
        if p.cliente_id:
            cliente_ids.add(p.cliente_id)
    total_clientes = len(cliente_ids)
    
    orcamento_total = sum(p.orcamento for p in projetos if p.orcamento) or 0
    
    requisitos_pendentes = 0
    for proj in projetos:
        for req in proj.requisitos:
            if req.situacao == 'Pendente':
                requisitos_pendentes += 1
                
    stats = {
        'projetos_ativos': len([p for p in projetos if p.situacao == 'Em andamento']),
        'equipes_count': len(equipes),
        'requisitos_pendentes': requisitos_pendentes
    }
    
    # ── Gráfico de Status (Donut) ──────────────────
    status_cores = {
        'Em andamento': '#f59e0b',
        'Concluído':    '#10b981',
        'Pausado':      '#FF5577',
    }
    status_counts = {s: 0 for s in status_cores.keys()}
    for p in projetos:
        s = p.situacao or 'Pausado'
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
    
    # ── Gráfico de Atividade Mensal ──────────────────
    monthly_map = {m: {'Em andamento': 0, 'Concluído': 0, 'Pausado': 0} for m in range(1, 13)}
    for p in projetos:
        if p.prazo:
            try:
                # prazo é um objeto date
                m = p.prazo.month if hasattr(p.prazo, 'month') else int(str(p.prazo)[5:7])
                st = p.situacao or 'Pausado'
                if st == 'Pendente':
                    st = 'Pausado'
                if st == 'Cancelado':
                    continue
                if st not in monthly_map[m]:
                    st = 'Pausado'
                monthly_map[m][st] += 1
            except (ValueError, IndexError, AttributeError):
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
            database.session.query(Registro, Projeto)
            .outerjoin(Projeto, Registro.projeto_id == Projeto.id)
            .filter(Registro.projeto_id.in_(proj_ids))
            .order_by(Registro.data.desc())
            .limit(10)
            .all()
        )
        for log, proj_obj in logs_query:
            equipe_nome = proj_obj.nome if proj_obj else 'Geral'
            if proj_obj and proj_obj.lista_equipes:
                equipe_nome = ', '.join([eq.nome for eq in proj_obj.lista_equipes])
            logs_data.append({
                'acao': log.acao,
                'descricao': log.descricao,
                'data': log.data,
                'equipe_nome': equipe_nome
            })
            
        todos_logs_query = (
            database.session.query(Registro, Projeto)
            .outerjoin(Projeto, Registro.projeto_id == Projeto.id)
            .filter(Registro.projeto_id.in_(proj_ids))
            .order_by(Registro.data.desc())
            .all()
        )
        for log, proj_obj in todos_logs_query:
            equipe_nome = proj_obj.nome if proj_obj else 'Geral'
            if proj_obj and proj_obj.lista_equipes:
                equipe_nome = ', '.join([eq.nome for eq in proj_obj.lista_equipes])
            todos_logs_data.append({
                'acao': log.acao,
                'descricao': log.descricao,
                'data': log.data,
                'equipe_nome': equipe_nome
            })
            
    # Último registro de cada projeto para o painel de atividades
    for proj in projetos:
        ultimo_registro = Registro.query.filter_by(projeto_id=proj.id).order_by(Registro.data.desc()).first()
        proj.ultimo_registro = ultimo_registro.descricao if ultimo_registro else "Sem alterações recentes"
            
    # ── Projetos do mês atual ──────────────────
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
    
    for proj in projetos:
        if proj.prazo:
            try:
                # prazo é objeto date
                m = proj.prazo.month if hasattr(proj.prazo, 'month') else int(str(proj.prazo)[5:7])
                y = proj.prazo.year if hasattr(proj.prazo, 'year') else int(str(proj.prazo)[0:4])
                is_match = (m == current_month_num and y == current_year)
            except (ValueError, AttributeError):
                is_match = False
            if is_match:
                status_str = proj.situacao or 'Pausado'
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
                    
    # Widget de funcionários
    funcionarios_painel = (
        Funcionario.query
        .join(Usuario, Funcionario.usuario_id == Usuario.id)
        .add_entity(Usuario)
        .limit(4)
        .all()
    )

    # ── Todos os projetos do funcionário agrupados por status para o Donut Chart tooltip ──
    projetos_por_status = {
        'em_andamento': [],
        'concluido': [],
        'pausado': []
    }
    for proj in projetos:
        status_str = proj.situacao or 'Pausado'
        if status_str == 'Pendente':
            status_str = 'Pausado'
        if status_str == 'Cancelado':
            continue
        
        proj_data = {
            'nome': proj.nome,
            'prazo': proj.prazo.strftime('%d/%m/%Y') if proj.prazo else 'Sem prazo',
            'url': url_for('funcionario.projeto_detalhe', projeto_id=proj.id)
        }
        
        if status_str == 'Em andamento':
            projetos_por_status['em_andamento'].append(proj_data)
        elif status_str == 'Concluído':
            projetos_por_status['concluido'].append(proj_data)
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
        budget_total=orcamento_total,
        funcionarios_painel=funcionarios_painel,
        status_data_json=json.dumps(status_data),
        projetos_status_json=json.dumps(projetos_por_status),
        volumes_json=json.dumps(volumes),
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
    if current_user.tipo != 'funcionario':
        return redirect(url_for('page_login'))
    funcionario = Funcionario.query.filter_by(usuario_id=current_user.id).first()
    if not funcionario:
        return "Perfil de funcionário não encontrado", 404
    equipes = funcionario.lista_equipes
    equipes_ids = [eq.id for eq in equipes]
    
    projetos = []
    if equipes_ids:
        projetos = Projeto.query.join(equipes_projeto, Projeto.id == equipes_projeto.c.projeto_id).filter(equipes_projeto.c.equipe_id.in_(equipes_ids)).all()
        
    return render_template('funcionario/projetos.html', projetos=projetos)

# ---------------------------------------------------------------------------
# Detalhes de um projeto (com verificação de acesso por equipe)
# ---------------------------------------------------------------------------
@funcionario_bp.route('/projeto-detalhe/<int:projeto_id>')
@login_required
def projeto_detalhe(projeto_id):
    if current_user.tipo != 'funcionario':
        return redirect(url_for('page_login'))
    projeto = Projeto.query.get_or_404(projeto_id)
    
    funcionario = Funcionario.query.filter_by(usuario_id=current_user.id).first()
    if not funcionario:
        return "Perfil de funcionário não encontrado", 404
    equipes_ids = [eq.id for eq in funcionario.lista_equipes]
    projeto_equipes_ids = [eq.id for eq in projeto.lista_equipes]
    if not any(eq_id in projeto_equipes_ids for eq_id in equipes_ids):
        return "Acesso negado", 403
    
    membros = (
        Funcionario.query
        .join(Funcionario.lista_equipes)
        .filter(Equipes.id.in_(projeto_equipes_ids))
        .all()
    )
    
    documentos = Documento.query.filter_by(projeto_id=projeto_id).all()
    diagramas = Diagrama.query.filter_by(projeto_id=projeto_id).all()
    galeria = Galeria.query.filter_by(projeto_id=projeto_id).all()
    comentarios = Comentario.query.filter_by(projeto_id=projeto_id).order_by(Comentario.data.asc()).all()
    
    return render_template(
        'funcionario/projeto-detalhe.html',
        projeto=projeto,
        membros=membros,
        requisitos=projeto.requisitos,
        documentos=documentos,
        diagramas=diagramas,
        galeria=galeria,
        comentarios=comentarios
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
    
    novo_req = Requisito(
        projeto_id=projeto_id,
        titulo=titulo,
        descricao=descricao,
        tipo=tipo,
        situacao='Pendente'
    )
    database.session.add(novo_req)
    database.session.commit()
    
    return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))

# =============================================================================
# VISUALIZAÇÃO DE EQUIPES
# =============================================================================

# ---------------------------------------------------------------------------
# Página de equipes do funcionário (com membros)
# ---------------------------------------------------------------------------
@funcionario_bp.route('/equipe')
@login_required
def equipe():
    if current_user.tipo != 'funcionario':
        return redirect(url_for('page_login'))
    funcionario = Funcionario.query.filter_by(usuario_id=current_user.id).first()
    if not funcionario:
        return "Perfil de funcionário não encontrado", 404
    equipes = funcionario.lista_equipes
    
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
        
    if not check_password_hash(current_user.senha, senha_atual):
        flash('Senha atual incorreta!', 'danger')
        return redirect(url_for('funcionario.configuracoes') + '#seguranca')
        
    current_user.senha = generate_password_hash(nova_senha)
    database.session.commit()
    flash('Senha atualizada com sucesso!', 'success')
    return redirect(url_for('funcionario.configuracoes') + '#seguranca')
