from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import database
from models import Usuario, Cliente, Funcionario, Projeto, Equipes, Skill, membros_equipe, Log, Requisito
from werkzeug.security import generate_password_hash, check_password_hash
import functools
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Protege todas as rotas deste blueprint
@admin_bp.before_request
@login_required
def verificar_nivel_admin():
    if current_user.nivel != 1:
        abort(403)

def registrar_log(tipo, acao, descricao, projeto_id=None):
    try:
        novo_log = Log(
            tipo=tipo,
            acao=acao,
            descricao=descricao,
            projeto_id=projeto_id
        )
        database.session.add(novo_log)
        database.session.commit()
    except Exception as e:
        print(f"Erro ao registrar log: {e}")
        database.session.rollback()

@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    total_projetos   = Projeto.query.count()
    total_equipe     = Funcionario.query.count()
    total_clientes   = Cliente.query.count()
    projetos_recentes = Projeto.query.filter_by(status='Em andamento').all()
    for proj in projetos_recentes:
        latest_log = Log.query.filter_by(projeto_id=proj.id).order_by(Log.data.desc()).first()
        proj.ultimo_log = latest_log.descricao if latest_log else "Sem alterações recentes"

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
        'Pendente':     '#6b7280',
    }
    status_rows = database.session.query(
        Projeto.status, database.func.count(Projeto.id)
    ).group_by(Projeto.status).all()

    # Mapeia os resultados para as cores, garantindo que todos os status apareçam
    status_counts = {s: 0 for s in status_cores.keys()}
    for s, c in status_rows:
        if s in status_counts:
            status_counts[s] = c
        elif s: # caso haja um status fora do padrão
            status_counts[s] = c

    status_data = [
        {'label': s, 'val': c, 'color': status_cores.get(s, '#6b7280')}
        for s, c in status_counts.items()
    ]

    # ── Atividade Mensal (barras por status por mês) ─────────────────────
    mes_expr = database.func.substring(Projeto.prazo, 6, 2)
    monthly_status_rows = database.session.query(
        mes_expr.label('mes'),
        Projeto.status,
        database.func.count(Projeto.id).label('total')
    ).filter(Projeto.prazo.like('____-__-__')).group_by(mes_expr, Projeto.status).all()

    # Estrutura: monthly_map[mes] = {'Em andamento': X, 'Concluído': Y, 'Pendente': Z}
    monthly_map = {m: {'Em andamento': 0, 'Concluído': 0, 'Pendente': 0} for m in range(1, 13)}
    
    for r in monthly_status_rows:
        try:
            if r.mes and r.mes.isdigit():
                m_int = int(r.mes)
                status_str = r.status or 'Pendente'
                # Normaliza o status caso venha fora do padrão
                if status_str not in ['Em andamento', 'Concluído', 'Pendente']:
                    status_str = 'Pendente'
                if m_int in monthly_map:
                    monthly_map[m_int][status_str] = r.total
        except:
            continue
            
    volumes = [
        {
            'em_andamento': monthly_map[m]['Em andamento'],
            'concluido': monthly_map[m]['Concluído'],
            'pendente': monthly_map[m]['Pendente']
        }
        for m in range(1, 13)
    ]

    # ── Logs com Equipe ──────────────────────────────────────────
    logs_query = database.session.query(Log, Projeto, Equipes).outerjoin(Projeto, Log.projeto_id == Projeto.id).outerjoin(Equipes, Projeto.equipe_id == Equipes.id).order_by(Log.data.desc()).limit(10).all()
    
    logs_data = []
    for log, projeto, equipe in logs_query:
        logs_data.append({
            'acao': log.acao,
            'descricao': log.descricao,
            'data': log.data,
            'equipe_nome': equipe.nome if equipe else (projeto.nome if projeto else 'Geral')
        })

    todos_logs_query = database.session.query(Log, Projeto, Equipes).outerjoin(Projeto, Log.projeto_id == Projeto.id).outerjoin(Equipes, Projeto.equipe_id == Equipes.id).order_by(Log.data.desc()).all()
    todos_logs_data = []
    for log, projeto, equipe in todos_logs_query:
        todos_logs_data.append({
            'acao': log.acao,
            'descricao': log.descricao,
            'data': log.data,
            'equipe_nome': equipe.nome if equipe else (projeto.nome if projeto else 'Geral')
        })

    # ── Atividade Mensal do Mês Atual ──────────────────
    import datetime
    now = datetime.datetime.now()
    current_month_num = now.month
    meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    current_month_name = meses_nomes[current_month_num]

    current_month_projects = {
        'em_andamento': [],
        'concluido': [],
        'pendente': []
    }
    
    current_year = now.year
    prefix_current_month = f"{current_year}-{current_month_num:02d}"
    month_infix = f"-{current_month_num:02d}-"
    
    todos_projetos_lista = database.session.query(Projeto).all()
    for proj in todos_projetos_lista:
        if proj.prazo:
            # Match if matches current year-month OR matches the month infix (e.g. -05-)
            is_match = proj.prazo.startswith(prefix_current_month) or month_infix in proj.prazo
            
            # Additional fallback check for format parsing
            if not is_match and len(proj.prazo) >= 7:
                try:
                    parts = proj.prazo.split('-')
                    if len(parts) >= 2 and int(parts[1]) == current_month_num:
                        is_match = True
                except ValueError:
                    pass
            
            if is_match:
                status_str = proj.status or 'Pendente'
                if status_str == 'Em andamento':
                    current_month_projects['em_andamento'].append(proj)
                elif status_str == 'Concluído':
                    current_month_projects['concluido'].append(proj)
                else:
                    current_month_projects['pendente'].append(proj)

    return render_template(
        'admin/dashboard.html',
        total_projetos    = total_projetos,
        total_equipe      = total_equipe,
        total_clientes    = total_clientes,
        projetos_recentes = projetos_recentes,
        budget_total      = budget_total,
        funcionarios_dash = funcionarios_dash,
        status_data_json  = json.dumps(status_data),
        volumes_json      = json.dumps(volumes),
        logs              = logs_data,
        todos_logs        = todos_logs_data,
        current_month_name = current_month_name,
        current_month_projects = current_month_projects
    )

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
@admin_bp.route('/add-projeto', methods=['POST'])
def add_projeto():
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    prazo = request.form.get('prazo')
    budget = request.form.get('budget', 0)
    cliente_id = request.form.get('cliente_id')
    equipe_id = request.form.get('equipe_id')

    projeto = Projeto(
        nome=nome,
        descricao=descricao,
        status="Em andamento",
        prazo=prazo,
        budget=float(budget) if budget else 0.0,
        cliente_id=cliente_id if cliente_id else None,
        equipe_id=equipe_id if equipe_id else None
    )
    database.session.add(projeto)
    database.session.commit()
    
    registrar_log('projeto', 'Projeto criado', f"O projeto '{nome}' foi criado com sucesso.", projeto.id)
    
    return redirect(url_for('admin.projetos'))

@admin_bp.route('/projeto-detalhe')
def projeto_detalhe():
    projeto_id = request.args.get('id', type=int)
    if not projeto_id:
        return redirect(url_for('admin.projetos'))
    
    projeto = Projeto.query.get_or_404(projeto_id)
    cliente = projeto.cliente_rel
    equipe = projeto.equipe_rel
    membros = []
    if equipe:
        membros = (
            Funcionario.query
            .join(membros_equipe, Funcionario.id == membros_equipe.c.funcionario_id)
            .filter(membros_equipe.c.equipe_id == equipe.id)
            .join(Usuario, Funcionario.usuario_id == Usuario.id)
            .add_entity(Usuario)
            .all()
        )
    
    return render_template(
        'admin/projeto-detalhe.html',
        projeto=projeto,
        cliente=cliente,
        equipe=equipe,
        membros=membros,
        requisitos=projeto.requisitos,
        todas_equipes=Equipes.query.all(),
        todos_clientes=Cliente.query.all()
    )

@admin_bp.route('/vincular-equipe-projeto', methods=['POST'])
def vincular_equipe_projeto():
    projeto_id = request.form.get('projeto_id', type=int)
    equipe_id = request.form.get('equipe_id', type=int)
    
    if projeto_id and equipe_id:
        projeto = Projeto.query.get_or_404(projeto_id)
        projeto.equipe_id = equipe_id
        database.session.commit()
        
        equipe = Equipes.query.get(equipe_id)
        registrar_log('projeto', 'Equipe vinculada', f"A equipe '{equipe.nome}' foi vinculada ao projeto '{projeto.nome}'.", projeto.id)
    
    return redirect(url_for('admin.projeto_detalhe', id=projeto_id))

@admin_bp.route('/editar-projeto', methods=['POST'])
def editar_projeto():
    projeto_id = request.form.get('projeto_id', type=int)
    projeto = Projeto.query.get_or_404(projeto_id)
    
    projeto.nome = request.form.get('nome')
    projeto.status = request.form.get('status')
    projeto.budget = request.form.get('budget', type=float)
    projeto.prazo = request.form.get('prazo')
    projeto.descricao = request.form.get('descricao')
    projeto.cliente_id = request.form.get('cliente_id', type=int)
    projeto.equipe_id = request.form.get('equipe_id', type=int)
    
    database.session.commit()
    registrar_log('projeto', 'Projeto atualizado', f"As informações do projeto '{projeto.nome}' foram atualizadas.", projeto.id)
    return redirect(url_for('admin.projeto_detalhe', id=projeto_id))

@admin_bp.route('/excluir-projeto/<int:id>', methods=['POST'])
def excluir_projeto(id):
    projeto = Projeto.query.get_or_404(id)
    nome_projeto = projeto.nome
    try:
        # Primeiro exclui requisitos associados (cascade manual se não definido)
        Requisito.query.filter_by(projeto_id=id).delete()
        
        database.session.delete(projeto)
        database.session.commit()
        registrar_log('projeto', 'Projeto excluído', f"O projeto '{nome_projeto}' foi removido do sistema.")
        flash("Projeto excluído com sucesso.", "sucesso")
    except Exception as e:
        database.session.rollback()
        flash(f"Erro ao excluir projeto: {e}", "erro")
    return redirect(url_for('admin.projetos'))

@admin_bp.route('/add-requisito', methods=['POST'])
def add_requisito():
    projeto_id = request.form.get('projeto_id', type=int)
    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    tipo = request.form.get('tipo') # Funcional ou Não-Funcional
    
    projeto = Projeto.query.get_or_404(projeto_id)
    
    novo_req = Requisito(
        projeto_id=projeto_id,
        titulo=titulo,
        descricao=descricao,
        tipo=tipo,
        status='Pendente'
    )
    database.session.add(novo_req)
    database.session.commit()
    
    registrar_log('requisito', 'Requisito adicionado', f"Novo requisito '{titulo}' adicionado ao projeto '{projeto.nome}'.", projeto.id)
    
    return redirect(url_for('admin.projeto_detalhe', id=projeto_id))

@admin_bp.route('/excluir-requisito/<int:id>', methods=['POST'])
def excluir_requisito(id):
    req = Requisito.query.get_or_404(id)
    projeto_id = req.projeto_id
    titulo = req.titulo
    
    database.session.delete(req)
    database.session.commit()
    
    registrar_log('requisito', 'Requisito excluído', f"O requisito '{titulo}' foi removido do projeto.", projeto_id)
    return redirect(url_for('admin.projeto_detalhe', id=projeto_id))

@admin_bp.route('/clientes')
def clientes():
    todos_clientes = Cliente.query.join(Usuario).all()
    return render_template(
        'admin/clientes.html',
        clientes = todos_clientes
    )

@admin_bp.route('/add-cliente', methods=['POST'])
def add_cliente():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    empresa = request.form.get('empresa')
    
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

@admin_bp.route('/cliente/excluir/<int:id>', methods=['POST'])
def excluir_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    try:
        database.session.delete(cliente)
        database.session.commit()
        flash("Cliente excluído com sucesso.", "sucesso")
    except:
        database.session.rollback()
        flash("Ocorreu um erro ao excluir o cliente.", "erro")
    return redirect(url_for('admin.clientes'))

@admin_bp.route('/cliente/editar/<int:id>', methods=['POST'])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    usuario = Usuario.query.get_or_404(cliente.usuario_id)
    
    usuario.nome = request.form.get('nome')
    usuario.email = request.form.get('email')
    cliente.empresa = request.form.get('empresa')
    
    senha = request.form.get('senha')
    if senha:
        usuario.senha = generate_password_hash(senha)

    database.session.commit()
    
    return redirect(url_for('admin.clientes'))

@admin_bp.route('/equipes')
def equipes():
    todas_equipes = Equipes.query.all()
    todos_funcionarios = Funcionario.query.join(Usuario).all()
    return render_template(
        'admin/equipes.html',
        equipes = todas_equipes,
        funcionarios = todos_funcionarios
    )

@admin_bp.route('/add-equipe', methods=['POST'])
def add_equipe():
    nome = request.form.get('nome')
    funcionarios_ids = request.form.getlist('check_funcionarios')
    
    equipe = Equipes(nome=nome)
    
    if funcionarios_ids:
        membros = Funcionario.query.filter(Funcionario.id.in_(funcionarios_ids)).all()
        equipe.membros_da_equipe.extend(membros)

    database.session.add(equipe)
    database.session.commit()
    return redirect(url_for('admin.equipes'))

@admin_bp.route('/equipes/excluir/<int:id>', methods=['POST'])
def excluir_equipe(id):
    equipe = Equipes.query.get_or_404(id)
    try:
        database.session.delete(equipe)
        database.session.commit()
        flash("Equipe excluída com sucesso.", "sucesso")
    except:
        database.session.rollback()
        flash("Ocorreu um erro ao excluir a equipe.", "erro")
    return redirect(url_for('admin.equipes'))

@admin_bp.route('/equipes/editar/<int:id>', methods=['POST'])
def editar_equipe(id):
    equipe = Equipes.query.get_or_404(id)
    nome = request.form.get('nome')
    funcionarios_ids = request.form.getlist('check_funcionarios')
    
    equipe.nome = nome
    
    if funcionarios_ids:
        membros = Funcionario.query.filter(Funcionario.id.in_(funcionarios_ids)).all()
        equipe.membros_da_equipe = membros
    else:
        equipe.membros_da_equipe = []

    database.session.commit()
    return redirect(url_for('admin.equipes'))


@admin_bp.route('/equipes/<int:id>')
def equipe_detalhe(id):
    equipe = Equipes.query.get_or_404(id)
    funcionarios = equipe.membros_da_equipe
    projetos = Projeto.query.filter_by(equipe_id=equipe.id).all()
    
    # Busca os logs dos projetos dessa equipe
    projeto_ids = [p.id for p in projetos]
    logs = []
    if projeto_ids:
        logs = Log.query.filter(Log.projeto_id.in_(projeto_ids)).order_by(Log.data.desc()).all()
    
    return render_template('admin/equipe-detalhe.html', 
                           equipe=equipe, 
                           funcionarios=funcionarios, 
                           projetos=projetos,
                           logs=logs)





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

@admin_bp.route('/funcionario/<int:id>')
def funcionario_perfil(id):
    funcionario = Funcionario.query.get_or_404(id)
    return render_template('admin/funcionario-perfil.html', funcionario=funcionario)

@admin_bp.route('/funcionario/excluir/<int:id>', methods=['POST'])
def excluir_funcionario(id):
    membro = Funcionario.query.get_or_404(id)
    user = Usuario.query.get(membro.usuario_id)
    try:
        database.session.delete(membro)
        database.session.delete(user)
        database.session.commit()
        flash("Funcionário excluído com sucesso.", "sucesso")
    except:
        database.session.rollback()
        flash("Ocorreu um erro ao excluir o funcionário.", "erro")
    return redirect(url_for('admin.funcionarios'))

@admin_bp.route('/funcionario/editar/<int:id>', methods=['POST'])
def editar_funcionario(id):
    funcionario = Funcionario.query.get_or_404(id)
    usuario = Usuario.query.get(funcionario.usuario_id)
    
    usuario.nome = request.form.get('nome')
    usuario.email = request.form.get('email')
    funcionario.cargo = request.form.get('cargo')
    skills_str = request.form.get('skills', '')

    funcionario.lista_skills = []
    if skills_str:
        for sk_nome in [s.strip() for s in skills_str.split(',')]:
            skill = Skill.query.filter_by(nome=sk_nome).first()
            if not skill:
                skill = Skill(nome=sk_nome)
                database.session.add(skill)
                database.session.flush()
            if skill not in funcionario.lista_skills:
                funcionario.lista_skills.append(skill)

    database.session.commit()
    return redirect(url_for('admin.funcionario_perfil', id=id))

@admin_bp.route('/add-funcionario', methods=['POST'])
def add_funcionario():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    cargo = request.form.get('cargo')
    skills_str = request.form.get('skills', '')
    
    if not Usuario.query.filter_by(email=email).first():
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
        
        if skills_str:
            for sk_nome in [s.strip() for s in skills_str.split(',')]:
                skill = Skill.query.filter_by(nome=sk_nome).first()
                if not skill:
                    skill = Skill(nome=sk_nome)
                    database.session.add(skill)
                    database.session.flush()
                funcionario.lista_skills.append(skill)

        database.session.add(funcionario)
        database.session.commit()
    
    return redirect(url_for('admin.funcionarios'))

@admin_bp.route('/configuracoes')
def configuracoes():
    return render_template('admin/configuracoes.html')

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




    