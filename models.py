from database import database
from flask_login import UserMixin

# --- TABELAS DE ASSOCIAÇÃO (Devem vir antes das classes que as utilizam) ---

membros_equipe = database.Table('membros_equipe',
    database.Column('funcionario_id', database.Integer, database.ForeignKey('funcionario.id'), primary_key=True),
    database.Column('equipe_id', database.Integer, database.ForeignKey('equipes.id'), primary_key=True)
)

skills_funcionario = database.Table('skills_funcionario',
    database.Column('funcionario_id', database.Integer, database.ForeignKey('funcionario.id'), primary_key=True),
    database.Column('skill_id', database.Integer, database.ForeignKey('skill.id'), primary_key=True)
)

equipes_projeto = database.Table('equipes_projeto',
    database.Column('equipe_id', database.Integer, database.ForeignKey('equipes.id'), primary_key=True),
    database.Column('projeto_id', database.Integer, database.ForeignKey('projeto.id'), primary_key=True)
)

# --- MODELOS ---

class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(100))
    email = database.Column(database.String(120), unique=True)
    senha = database.Column(database.String(200))
    tipo = database.Column(database.String(20))
    nivel = database.Column(database.Integer)

class Admin(database.Model):
    __tablename__ = 'admin'
    id = database.Column(database.Integer, primary_key=True)
    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    nivel = database.Column(database.String(50))
    usuario_rel = database.relationship('Usuario', backref='admin_perfil', uselist=False)

class Cliente(database.Model):
    __tablename__ = 'cliente'
    id = database.Column(database.Integer, primary_key=True)
    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    empresa = database.Column(database.String(200))
    usuario_rel = database.relationship('Usuario', backref='cliente_perfil', uselist=False)
    # Um cliente pode ter vários projetos
    projetos = database.relationship('Projeto', backref='cliente_rel', lazy=True)

class Skill(database.Model):
    __tablename__ = 'skill'
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(50), unique=True, nullable=False)

class Funcionario(database.Model):
    __tablename__ = 'funcionario'
    id = database.Column(database.Integer, primary_key=True)
    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    cargo = database.Column(database.String(50))
    usuario_rel = database.relationship('Usuario', backref='funcionario_perfil', uselist=False)
    
    # Relacionamentos Muitos-para-Muitos
    lista_equipes = database.relationship('Equipes', secondary=membros_equipe, backref='membros_da_equipe')
    lista_skills = database.relationship('Skill', secondary=skills_funcionario, backref='funcionarios_habilitados')

class Equipes(database.Model):
    __tablename__ = 'equipes'
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(250), nullable=False)
    descricao = database.Column(database.String(250), nullable=False)
    funcao = database.Column(database.String(250), nullable=False)
    lider_equipe = database.Column(database.Integer, database.ForeignKey('funcionario.id'))
    projetos = database.relationship('Projeto', secondary=equipes_projeto, back_populates='lista_equipes')

class Requisito(database.Model):
    __tablename__ = 'requisito'
    id = database.Column(database.Integer, primary_key=True)
    projeto_id = database.Column(database.Integer, database.ForeignKey('projeto.id'))
    titulo = database.Column(database.String(200), nullable=False)
    descricao = database.Column(database.Text)
    tipo = database.Column(database.String(50)) # Funcional, Não-Funcional
    status = database.Column(database.String(50), default='Pendente')

class Projeto(database.Model):
    __tablename__ = 'projeto'
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(200), nullable=False)
    descricao = database.Column(database.Text)
    status = database.Column(database.String(20))
    
    prazo = database.Column(database.String(20))
    budget = database.Column(database.Float)
    
    # Chaves Estrangeiras
    cliente_id = database.Column(database.Integer, database.ForeignKey('cliente.id'))

    # Relacionamentos
    requisitos = database.relationship('Requisito', backref='projeto_rel', lazy=True)
    lista_equipes = database.relationship('Equipes', secondary=equipes_projeto, back_populates='projetos')

class Log(database.Model):
    __tablename__ = 'log'
    id = database.Column(database.Integer, primary_key=True)
    tipo = database.Column(database.String(50)) # 'projeto', 'requisito', 'equipe', etc.
    acao = database.Column(database.String(100)) # Ex: 'Projeto criado'
    descricao = database.Column(database.String(255))
    data = database.Column(database.DateTime, default=database.func.now())
    projeto_id = database.Column(database.Integer, database.ForeignKey('projeto.id'), nullable=True)

class Documento(database.Model):
    __tablename__ = 'documento'
    id = database.Column(database.Integer, primary_key=True)
    projeto_id = database.Column(database.Integer, database.ForeignKey('projeto.id'), nullable=False)
    nome = database.Column(database.String(255), nullable=False)
    caminho = database.Column(database.String(255), nullable=False)
    data_upload = database.Column(database.DateTime, default=database.func.now())
    tipo_arquivo = database.Column(database.String(10), nullable=False) # 'pdf', 'docx'

class Diagrama(database.Model):
    __tablename__ = 'diagrama'
    id = database.Column(database.Integer, primary_key=True)
    projeto_id = database.Column(database.Integer, database.ForeignKey('projeto.id'), nullable=False)
    nome = database.Column(database.String(255), nullable=False)
    caminho = database.Column(database.String(255), nullable=False)
    data_upload = database.Column(database.DateTime, default=database.func.now())

class Galeria(database.Model):
    __tablename__ = 'galeria'
    id = database.Column(database.Integer, primary_key=True)
    projeto_id = database.Column(database.Integer, database.ForeignKey('projeto.id'), nullable=False)
    nome = database.Column(database.String(255), nullable=False)
    caminho = database.Column(database.String(255), nullable=False)
    data_upload = database.Column(database.DateTime, default=database.func.now())

class Comentario(database.Model):
    __tablename__ = 'comentario'
    id = database.Column(database.Integer, primary_key=True)
    projeto_id = database.Column(database.Integer, database.ForeignKey('projeto.id'), nullable=False)
    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)
    conteudo = database.Column(database.Text, nullable=False)
    data = database.Column(database.DateTime, default=database.func.now())
    
    usuario_rel = database.relationship('Usuario', backref=database.backref('comentarios_usuario', lazy=True))