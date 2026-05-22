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
from models import Usuario, Cliente, Funcionario, Projeto, Equipes, Habilidade, membros_equipe, equipes_projeto, Registro, Requisito, Documento, Diagrama, Galeria, Comentario
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
    if current_user.nivel != 1:
        abort(403)

# =============================================================================
# Utilitário - Registro de logs
# =============================================================================
def registrar_log(tipo, acao, descricao, projeto_id=None):
    try:
        novo_registro = Registro(
            tipo=tipo,
            acao=acao,
            descricao=descricao,
            projeto_id=projeto_id
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
    total_projetos   = Projeto.query.count()
    total_equipe     = Funcionario.query.count()
    total_clientes   = Cliente.query.count()
    projetos_recentes = Projeto.query.filter_by(situacao='Em andamento').all()
    for proj in projetos_recentes:
        ultimo_registro = Registro.query.filter_by(projeto_id=proj.id).order_by(Registro.data.desc()).first()
        proj.ultimo_registro = ultimo_registro.descricao if ultimo_registro else "Sem alterações recentes"

    orcamento_total = database.session.query(
        database.func.sum(Projeto.orcamento)
    ).scalar() or 0
    funcionarios_painel = (
        Funcionario.query
        .join(Usuario, Funcionario.usuario_id == Usuario.id)
        .add_entity(Usuario)
        .limit(4)
        .all()
    )

    # ── Gráfico de Status (donut) ──────────────────────────────────
    status_cores = {
        'Em andamento': '#f59e0b',
        'Concluído':    '#10b981',
        'Pausado':      '#FF5577',
        'Cancelado':    '#ec0000'
    }
    status_rows = database.session.query(
        Projeto.situacao, database.func.count(Projeto.id)
    ).group_by(Projeto.situacao).all()

    status_counts = {s: 0 for s in status_cores.keys()}
    for s, c in status_rows:
        if s == 'Pendente':
            status_counts['Pausado'] += c
        elif s == 'Cancelado':
            continue
        elif s in status_counts:
            status_counts[s] += c

    status_data = [
        {'label': s, 'val': c, 'color': status_cores.get(s, '#6b7280')}
        for s, c in status_counts.items()
    ]

    # ── Gráfico de Atividade Mensal (barras por status) ────────────────
    mes_expr = database.func.extract('month', Projeto.prazo)
    monthly_status_rows = database.session.query(
        mes_expr.label('mes'),
        Projeto.situacao,
        database.func.count(Projeto.id).label('total')
    ).filter(Projeto.prazo.isnot(None)).group_by(mes_expr, Projeto.situacao).all()

    monthly_map = {m: {'Em andamento': 0, 'Concluído': 0, 'Pausado': 0} for m in range(1, 13)}
    
    for r in monthly_status_rows:
        if r.mes is None:
            continue
        m_int = int(r.mes)
        status_str = r.situacao or 'Pausado'
        if status_str == 'Pendente':
            status_str = 'Pausado'
        if status_str == 'Cancelado':
            continue
        if status_str not in ['Em andamento', 'Concluído', 'Pausado']:
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
    logs_query = database.session.query(Registro, Projeto).outerjoin(Projeto, Registro.projeto_id == Projeto.id).order_by(Registro.data.desc()).limit(10).all()
    
    logs_data = []
    for log, projeto in logs_query:
        equipe_nome = projeto.nome if projeto else 'Geral'
        if projeto and projeto.lista_equipes:
            equipe_nome = ', '.join([eq.nome for eq in projeto.lista_equipes])
        logs_data.append({
            'acao': log.acao,
            'descricao': log.descricao,
            'data': log.data,
            'equipe_nome': equipe_nome
        })

    todos_logs_query = database.session.query(Registro, Projeto).outerjoin(Projeto, Registro.projeto_id == Projeto.id).order_by(Registro.data.desc()).all()
    todos_logs_data = []
    for log, projeto in todos_logs_query:
        equipe_nome = projeto.nome if projeto else 'Geral'
        if projeto and projeto.lista_equipes:
            equipe_nome = ', '.join([eq.nome for eq in projeto.lista_equipes])
        todos_logs_data.append({
            'acao': log.acao,
            'descricao': log.descricao,
            'data': log.data,
            'equipe_nome': equipe_nome
        })

    # ── Projetos criados no mês atual ──────────────────
    import datetime
    now = datetime.datetime.now()
    current_month_num = now.month
    current_year = now.year
    meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    current_month_name = meses_nomes[current_month_num]

    current_month_projects = {
        'em_andamento': [],
        'concluido': [],
        'pausado': []
    }

    logs_criacao = Registro.query.filter(
        Registro.acao == 'Projeto criado',
        extract('year', Registro.data) == current_year,
        extract('month', Registro.data) == current_month_num
    ).all()

    projeto_ids_mes = set()
    for log_entry in logs_criacao:
        if log_entry.projeto_id:
            projeto_ids_mes.add(log_entry.projeto_id)

    projetos_do_mes = Projeto.query.filter(Projeto.id.in_(projeto_ids_mes)).all() if projeto_ids_mes else []
    for proj in projetos_do_mes:
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

    return render_template(
        'admin/dashboard.html',
        total_projetos    = total_projetos,
        total_equipe      = total_equipe,
        total_clientes    = total_clientes,
        projetos_recentes = projetos_recentes,
        budget_total   = orcamento_total,
        funcionarios_painel = funcionarios_painel,
        status_data_json  = json.dumps(status_data),
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
    todos_projetos = Projeto.query.all()
    todos_clientes = Cliente.query.join(Usuario).all()
    todas_equipes = Equipes.query.all()
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
    orcamento = request.form.get('orcamento', 0)
    cliente_id = request.form.get('cliente_id')
    equipes_ids = [int(x) for x in request.form.getlist('check_equipes') if x.isdigit()]

    from datetime import date
    try:
        prazo_date = date.fromisoformat(prazo) if prazo else None
    except:
        prazo_date = None

    projeto = Projeto(
        nome=nome,
        descricao=descricao,
        situacao="Em andamento",
        prazo=prazo_date,
        orcamento=float(orcamento) if orcamento else 0.0,
        cliente_id=cliente_id if cliente_id else None
    )
    
    if equipes_ids:
        equipes = Equipes.query.filter(Equipes.id.in_(equipes_ids)).all()
        projeto.lista_equipes.extend(equipes)
    
    database.session.add(projeto)
    database.session.commit()
    
    registrar_log('projeto', 'Projeto criado', f"O projeto '{nome}' foi criado com sucesso.", projeto.id)
    
    return redirect(url_for('admin.projetos'))

# ---------------------------------------------------------------------------
# Detalhes de um projeto (com membros, documentos, diagramas, galeria, comentários)
# ---------------------------------------------------------------------------
@admin_bp.route('/projeto-detalhe')
def projeto_detalhe():
    projeto_id = request.args.get('id', type=int)
    if not projeto_id:
        return redirect(url_for('admin.projetos'))
    
    projeto = Projeto.query.get_or_404(projeto_id)
    cliente = projeto.cliente_rel
    equipes = projeto.lista_equipes
    
    membros = []
    equipes_ids = [eq.id for eq in equipes]
    if equipes_ids:
        membros = (
            database.session.query(Funcionario, Usuario)
            .join(membros_equipe, Funcionario.id == membros_equipe.c.funcionario_id)
            .filter(membros_equipe.c.equipe_id.in_(equipes_ids))
            .join(Usuario, Funcionario.usuario_id == Usuario.id)
            .distinct()
            .all()
        )
        
    documentos = Documento.query.filter_by(projeto_id=projeto_id).all()
    diagramas = Diagrama.query.filter_by(projeto_id=projeto_id).all()
    galeria = Galeria.query.filter_by(projeto_id=projeto_id).all()
    comentarios = Comentario.query.filter_by(projeto_id=projeto_id).order_by(Comentario.data.asc()).all()
    
    return render_template(
        'admin/projeto-detalhe.html',
        projeto=projeto,
        cliente=cliente,
        equipes=equipes,
        membros=membros,
        requisitos=projeto.requisitos,
        todas_equipes=Equipes.query.all(),
        todos_clientes=Cliente.query.all(),
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
        projeto = Projeto.query.get_or_404(projeto_id)
        equipes = Equipes.query.filter(Equipes.id.in_(equipes_ids)).all()
        projeto.lista_equipes = equipes
        database.session.commit()
        
        nomes = ', '.join([eq.nome for eq in equipes])
        registrar_log('projeto', 'Equipes vinculadas', f"As equipes '{nomes}' foram vinculadas ao projeto '{projeto.nome}'.", projeto.id)
    
    return redirect(url_for('admin.projeto_detalhe', id=projeto_id))

# ---------------------------------------------------------------------------
# Editar projeto
# ---------------------------------------------------------------------------
@admin_bp.route('/editar-projeto', methods=['POST'])
def editar_projeto():
    projeto_id = request.form.get('projeto_id', type=int)
    projeto = Projeto.query.get_or_404(projeto_id)
    
    nome = request.form.get('nome')
    if not nome:
        flash("O nome do projeto é obrigatório.", "erro")
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    
    projeto.nome = nome
    projeto.situacao = request.form.get('situacao')

    orcamento_raw = request.form.get('orcamento', type=float)
    projeto.orcamento = orcamento_raw if orcamento_raw else 0.0

    from datetime import date
    prazo_str = request.form.get('prazo')
    try:
        projeto.prazo = date.fromisoformat(prazo_str) if prazo_str else None
    except:
        projeto.prazo = None
    projeto.descricao = request.form.get('descricao')
    projeto.cliente_id = request.form.get('cliente_id', type=int)
    
    equipes_ids = [int(x) for x in request.form.getlist('check_equipes') if x.isdigit()]
    if equipes_ids:
        equipes = Equipes.query.filter(Equipes.id.in_(equipes_ids)).all()
        projeto.lista_equipes = equipes
    else:
        projeto.lista_equipes = []
    
    try:
        database.session.commit()
        registrar_log('projeto', 'Projeto atualizado', f"As informações do projeto '{projeto.nome}' foram atualizadas.", projeto.id)
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
    projeto = Projeto.query.get_or_404(id)
    nome_projeto = projeto.nome
    try:
        Registro.query.filter_by(projeto_id=id).delete()
        Requisito.query.filter_by(projeto_id=id).delete()
        
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
    
    projeto = Projeto.query.get_or_404(projeto_id)
    
    novo_req = Requisito(
        projeto_id=projeto_id,
        titulo=titulo,
        descricao=descricao,
        tipo=tipo,
        situacao='Pendente'
    )
    database.session.add(novo_req)
    database.session.commit()
    
    registrar_log('requisito', 'Requisito adicionado', f"Novo requisito '{titulo}' adicionado ao projeto '{projeto.nome}'.", projeto.id)
    
    return redirect(url_for('admin.projeto_detalhe', id=projeto_id))

# ---------------------------------------------------------------------------
# Excluir requisito
# ---------------------------------------------------------------------------
@admin_bp.route('/excluir-requisito/<int:id>', methods=['POST'])
def excluir_requisito(id):
    req = Requisito.query.get_or_404(id)
    projeto_id = req.projeto_id
    titulo = req.titulo
    
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
    todos_clientes = Cliente.query.join(Usuario).all()
    return render_template(
        'admin/clientes.html',
        clientes = todos_clientes
    )

def _gerar_email_cliente(nome):
    nome = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode('utf-8')
    nome = nome.lower()
    nome = nome.replace(' ', '.')
    nome = re.sub(r'[^a-z0-9.]', '', nome)
    return f'{nome}@cobyte_cliente.com'

# ---------------------------------------------------------------------------
# Criar novo cliente (cria Usuario + Cliente)
# ---------------------------------------------------------------------------
@admin_bp.route('/add-cliente', methods=['POST'])
def add_cliente():
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    empresa = request.form.get('empresa')
    email = _gerar_email_cliente(nome)

    if not Usuario.query.filter_by(email=email).first():
        usuario = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha),
            tipo='cliente',
            nivel=3
        )
        database.session.add(usuario)
        database.session.flush()

        cliente = Cliente(
            usuario_id=usuario.id,
            empresa=empresa
        )
        database.session.add(cliente)
        database.session.commit()

    return redirect(url_for('admin.clientes'))

# ---------------------------------------------------------------------------
# Excluir cliente (remove Cliente + Usuario associado)
# ---------------------------------------------------------------------------
@admin_bp.route('/cliente/excluir/<int:id>', methods=['POST'])
def excluir_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    usuario = Usuario.query.get(cliente.usuario_id)
    nome = usuario.nome if usuario else "Cliente"
    
    try:
        Projeto.query.filter_by(cliente_id=id).update({Projeto.cliente_id: None})
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
    cliente = Cliente.query.get_or_404(id)
    usuario = Usuario.query.get_or_404(cliente.usuario_id)
    
    nome = request.form.get('nome')
    email = request.form.get('email')
    empresa = request.form.get('empresa')
    
    if not nome or not email:
        flash("Nome e email são obrigatórios.", "erro")
        return redirect(url_for('admin.clientes'))
    
    email_existente = Usuario.query.filter(Usuario.email == email, Usuario.id != usuario.id).first()
    if email_existente:
        flash("Este email já está em uso por outro usuário.", "erro")
        return redirect(url_for('admin.clientes'))
    
    usuario.nome = nome
    usuario.email = email
    cliente.empresa = empresa
    
    senha = request.form.get('senha')
    if senha:
        usuario.senha = generate_password_hash(senha)
    
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
    todas_equipes = Equipes.query.all()
    todos_funcionarios = Funcionario.query.join(Usuario).all()
    todos_projetos = Projeto.query.all()
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
    
    equipe = Equipes(nome=nome, descricao=descricao, funcao=funcao, lider_equipe=lider_equipe)
    
    if funcionarios_ids:
        membros = Funcionario.query.filter(Funcionario.id.in_(funcionarios_ids)).all()
        equipe.membros_da_equipe.extend(membros)

    if projetos_ids:
        projs = Projeto.query.filter(Projeto.id.in_(projetos_ids)).all()
        equipe.projetos.extend(projs)

    database.session.add(equipe)
    database.session.commit()
    return redirect(url_for('admin.equipes'))

# ---------------------------------------------------------------------------
# Excluir equipe
# ---------------------------------------------------------------------------
@admin_bp.route('/equipes/excluir/<int:id>', methods=['POST'])
def excluir_equipe(id):
    equipe = Equipes.query.get_or_404(id)
    nome = equipe.nome
    try:
        database.session.execute(equipes_projeto.delete().where(equipes_projeto.c.equipe_id == id))
        equipe.membros_da_equipe = []
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
    equipe = Equipes.query.get_or_404(id)
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    funcao = request.form.get('funcao')
    lider_equipe = request.form.get('lider_equipe', type=int)
    funcionarios_ids = [int(x) for x in request.form.getlist('check_funcionarios') if x.isdigit()]
    projetos_ids = [int(x) for x in request.form.getlist('check_projetos') if x.isdigit()]
    
    if not nome:
        flash("O nome da equipe é obrigatório.", "erro")
        return redirect(url_for('admin.equipes'))
    
    equipe.nome = nome
    equipe.descricao = descricao
    equipe.funcao = funcao
    equipe.lider_equipe = lider_equipe
    
    if funcionarios_ids:
        membros = Funcionario.query.filter(Funcionario.id.in_(funcionarios_ids)).all()
        equipe.membros_da_equipe = membros
    else:
        equipe.membros_da_equipe = []
    
    if projetos_ids:
        projs = Projeto.query.filter(Projeto.id.in_(projetos_ids)).all()
        equipe.projetos = projs
    else:
        equipe.projetos = []
    
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
    equipe = Equipes.query.get_or_404(id)
    funcionarios = equipe.membros_da_equipe
    projetos = equipe.projetos
    
    lider = None
    if equipe.lider_equipe:
        lider = Funcionario.query.get(equipe.lider_equipe)
    
    projeto_ids = [p.id for p in projetos]
    logs = []
    if projeto_ids:
        logs = Registro.query.filter(Registro.projeto_id.in_(projeto_ids)).order_by(Registro.data.desc()).all()
    
    todos_funcionarios = (
        Funcionario.query
        .join(Usuario, Funcionario.usuario_id == Usuario.id)
        .add_entity(Usuario)
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
    equipe = Equipes.query.get_or_404(equipe_id)
    funcionario_id = request.form.get('funcionario_id')
    if funcionario_id:
        funcionario = Funcionario.query.get(int(funcionario_id))
        if funcionario and funcionario not in equipe.membros_da_equipe:
            equipe.membros_da_equipe.append(funcionario)
            
            registro = Registro(
                tipo="equipe",
                acao="Membro adicionado",
                descricao=f"Funcionário {funcionario.usuario_rel.nome} foi adicionado à equipe {equipe.nome}.",
                projeto_id=None
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
    equipe = Equipes.query.get_or_404(equipe_id)
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    if funcionario in equipe.membros_da_equipe:
        equipe.membros_da_equipe.remove(funcionario)
        
        registro = Registro(
            tipo="equipe",
            acao="Membro removido",
            descricao=f"Funcionário {funcionario.usuario_rel.nome} foi removido da equipe {equipe.nome}.",
            projeto_id=None
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
        Funcionario.query
        .join(Usuario, Funcionario.usuario_id == Usuario.id)
        .add_entity(Usuario)
        .all()
    )
    total = Funcionario.query.count()
    equipes = Equipes.query.all()
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
    funcionario = Funcionario.query.get_or_404(id)
    return render_template('admin/funcionario-perfil.html', funcionario=funcionario)

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

    while Usuario.query.filter_by(email=email).first():
        email = f'{nome_formatado}.{contador}@cobyte_funcionario.com'
        contador += 1

    usuario = Usuario(
        nome=nome,
        email=email,
        senha=generate_password_hash(senha),
        tipo='funcionario',
        nivel=2
    )
    database.session.add(usuario)
    database.session.flush()

    funcionario = Funcionario(
        usuario_id=usuario.id,
        cargo=cargo
    )

    if habilidades_str:
        for hab_nome in [s.strip() for s in habilidades_str.split(',')]:
            habilidade = Habilidade.query.filter_by(nome=hab_nome).first()
            if not habilidade:
                habilidade = Habilidade(nome=hab_nome)
                database.session.add(habilidade)
                database.session.flush()
            funcionario.lista_habilidades.append(habilidade)

    database.session.add(funcionario)
    database.session.commit()

    return redirect(url_for('admin.funcionarios'))

# ---------------------------------------------------------------------------
# Editar funcionário
# ---------------------------------------------------------------------------
@admin_bp.route('/funcionario/editar/<int:id>', methods=['POST'])
def editar_funcionario(id):
    funcionario = Funcionario.query.get_or_404(id)
    usuario = Usuario.query.get(funcionario.usuario_id)
    
    nome = request.form.get('nome')
    email = request.form.get('email')
    cargo = request.form.get('cargo')
    
    if not nome or not email or not cargo:
        flash("Nome, email e cargo são obrigatórios.", "erro")
        return redirect(url_for('admin.funcionario_perfil', id=id))
    
    email_existente = Usuario.query.filter(Usuario.email == email, Usuario.id != usuario.id).first()
    if email_existente:
        flash("Este email já está em uso por outro usuário.", "erro")
        return redirect(url_for('admin.funcionario_perfil', id=id)) 
    
    usuario.nome = nome
    usuario.email = email
    funcionario.cargo = cargo
    habilidades_str = request.form.get('habilidades', '')

    funcionario.lista_habilidades = []
    if habilidades_str:
        for hab_nome in [s.strip() for s in habilidades_str.split(',')]:
            habilidade = Habilidade.query.filter_by(nome=hab_nome).first()
            if not habilidade:
                habilidade = Habilidade(nome=hab_nome)
                database.session.add(habilidade)
                database.session.flush()
            if habilidade not in funcionario.lista_habilidades:
                funcionario.lista_habilidades.append(habilidade)

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
    membro = Funcionario.query.get_or_404(id)
    usuario = Usuario.query.get(membro.usuario_id)
    nome = usuario.nome if usuario else "Funcionário"
    try:
        membro.lista_equipes = []
        membro.lista_habilidades = []
        
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
        
    if not check_password_hash(current_user.senha, senha_atual):
        flash('Senha atual incorreta!', 'danger')
        return redirect(url_for('admin.configuracoes') + '#seguranca')
        
    current_user.senha = generate_password_hash(nova_senha)
    database.session.commit()
    flash('Senha atualizada com sucesso!', 'success')
    return redirect(url_for('admin.configuracoes') + '#seguranca')
