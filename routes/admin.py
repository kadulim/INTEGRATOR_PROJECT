from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import database
from models import Usuario, Cliente, Funcionario, Projeto, Equipes, Skill
from werkzeug.security import generate_password_hash
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

    # ── Volume por Mês (barras) ──────────────────────────────────
    # Extrai o mês do campo prazo ('YYYY-MM-DD'). 
    # Usamos substring para garantir compatibilidade se o campo for string.
    monthly_rows = database.session.query(
        database.func.substring(Projeto.prazo, 6, 2).label('mes'),
        database.func.count(Projeto.id).label('total')
    ).filter(Projeto.prazo.like('____-__-__')).group_by('mes').all()

    monthly_map = {}
    for r in monthly_rows:
        try:
            if r.mes and r.mes.isdigit():
                m_int = int(r.mes)
                monthly_map[m_int] = r.total
        except:
            continue
            
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

@admin_bp.route('/projeto-detalhe')
def projeto_detalhe():
    return render_template('admin/projeto-detalhe.html')

@admin_bp.route('/configuracoes')
def configuracoes():
    return render_template('admin/configuracoes.html')

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
            cargo=cargo,
            skills=skills_str
        )
        
        # Tratar Skills (M2M)
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
        status="Em Andamento",
        prazo=prazo,
        budget=float(budget) if budget else 0.0,
        cliente_id=cliente_id if cliente_id else None,
        equipe_id=equipe_id if equipe_id else None
    )
    database.session.add(projeto)
    database.session.commit()
    
    return redirect(url_for('admin.projetos'))

@admin_bp.route('/funcionario/<int:id>')
def funcionario_perfil(id):
    func = Funcionario.query.get_or_404(id)
    return render_template('admin/funcionario-perfil.html', funcionario=func)

@admin_bp.route('/funcionario/excluir/<int:id>', methods = ['GET' , 'POST'])
def excluir_funcionario(id):
    membro = Funcionario.query.get_or_404(id)
    user = Usuario.query.get(membro.usuario_id)
    try:
        database.session.delete(membro)
        database.session.delete(user)
        database.session.commit()
    except:
        flash("Ocorreu um erro ao excluir o funcionário.", "erro")
        return redirect(url_for('admin.funcionarios'))
    
    return redirect(url_for('admin.funcionarios'))

@admin_bp.route('/funcionario/editar/<int:id>', methods=['POST'])
def editar_funcionario(id):
    funcionario = Funcionario.query.get_or_404(id)
    usuario = Usuario.query.get(funcionario.usuario_id)
    
    usuario.nome = request.form.get('nome')
    usuario.email = request.form.get('email')
    funcionario.cargo = request.form.get('cargo')
    skills_str = request.form.get('skills', '')
    funcionario.skills = skills_str

    # Atualizar Skills (M2M)
    funcionario.lista_skills = [] # Limpa as skills atuais
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