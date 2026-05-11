from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from database import database
from models import Usuario, Funcionario, Projeto, Equipes, Requisito

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
    
    # Estatísticas simples
    stats = {
        'projetos_ativos': len([p for p in projetos if p.status == 'Em andamento']),
        'equipes_count': len(equipes),
        'requisitos_pendentes': 0 # Placeholder para futura lógica de tarefas
    }
    
    return render_template(
        'funcionario/dashboard.html',
        funcionario=funcionario,
        equipes=equipes,
        projetos=projetos,
        stats=stats
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
