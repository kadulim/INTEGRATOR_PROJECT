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
    projetos = database.relationship('Projeto', backref='equipe_rel', lazy=True)

class Projeto(database.Model):
    __tablename__ = 'projeto'
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(200), nullable=False)
    descricao = database.Column(database.Text)
    status = database.Column(database.String(20))
    prazo = database.Column(database.String(20))
    budget = database.Column(database.Float)

    
    # Chaves Estrangeiras Corretas
    cliente_id = database.Column(database.Integer, database.ForeignKey('cliente.id'))
    equipe_id = database.Column(database.Integer, database.ForeignKey('equipes.id'))