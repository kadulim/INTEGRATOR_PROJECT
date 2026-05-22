from database import database
from flask_login import UserMixin

# =============================================================================
# TABELAS DE ASSOCIAÇÃO
# =============================================================================

membros_equipe = database.Table('membros_equipe',
    database.Column('funcionario_id', database.Integer, database.ForeignKey('funcionario.id', ondelete='CASCADE'), primary_key=True),
    database.Column('equipe_id', database.Integer, database.ForeignKey('equipes.id', ondelete='CASCADE'), primary_key=True)
)

habilidades_funcionario = database.Table('habilidades_funcionario',
    database.Column('funcionario_id', database.Integer, database.ForeignKey('funcionario.id', ondelete='CASCADE'), primary_key=True),
    database.Column('habilidade_id', database.Integer, database.ForeignKey('habilidade.id', ondelete='CASCADE'), primary_key=True)
)

equipes_projeto = database.Table('equipes_projeto',
    database.Column('equipe_id', database.Integer, database.ForeignKey('equipes.id', ondelete='CASCADE'), primary_key=True),
    database.Column('projeto_id', database.Integer, database.ForeignKey('projeto.id', ondelete='CASCADE'), primary_key=True)
)

# =============================================================================
# MODELOS
# =============================================================================

class Usuario(database.Model, UserMixin):
    __tablename__ = 'usuario'
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(100), nullable=False)
    email = database.Column(database.String(120), unique=True, nullable=False)
    senha = database.Column(database.Text, nullable=False)
    tipo = database.Column(database.String(20))
    nivel = database.Column(database.Integer)

    data_criacao = database.Column(database.DateTime, default=database.func.now())
    data_atualizacao = database.Column(database.DateTime, onupdate=database.func.now())

    ultimo_login = database.Column(database.DateTime, nullable=True)

class Admin(database.Model):
    __tablename__ = 'admin'
    id = database.Column(database.Integer, primary_key=True)
    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id', ondelete='CASCADE'))
    nivel = database.Column(database.String(50))
    usuario_rel = database.relationship('Usuario', backref='admin_perfil', uselist=False)


class Cliente(database.Model):
    __tablename__ = 'cliente'
    id = database.Column(database.Integer, primary_key=True)
    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id', ondelete='CASCADE'))
    empresa = database.Column(database.String(200))
    usuario_rel = database.relationship('Usuario', backref='cliente_perfil', uselist=False)
    projetos = database.relationship('Projeto', backref='cliente_rel', lazy=True)


class Habilidade(database.Model):
    __tablename__ = 'habilidade'
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(50), unique=True, nullable=False)


class Funcionario(database.Model):
    __tablename__ = 'funcionario'
    id = database.Column(database.Integer, primary_key=True)
    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id', ondelete='CASCADE'))
    cargo = database.Column(database.String(50))
    usuario_rel = database.relationship('Usuario', backref='funcionario_perfil', uselist=False)

    lista_equipes = database.relationship('Equipes', secondary=membros_equipe, backref='membros_da_equipe')
    lista_habilidades = database.relationship('Habilidade', secondary=habilidades_funcionario, backref='funcionarios_habilitados')


class Equipes(database.Model):
    __tablename__ = 'equipes'
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(250), nullable=False)
    descricao = database.Column(database.String(250), nullable=False)
    funcao = database.Column(database.String(250), nullable=False)
    lider_equipe = database.Column(database.Integer, database.ForeignKey('funcionario.id', ondelete='SET NULL'))
    projetos = database.relationship('Projeto', secondary=equipes_projeto, back_populates='lista_equipes')

class Requisito(database.Model):
    __tablename__ = 'requisito'
    id = database.Column(database.Integer, primary_key=True)
    projeto_id = database.Column(database.Integer, database.ForeignKey('projeto.id', ondelete='CASCADE'))
    titulo = database.Column(database.String(200), nullable=False)
    descricao = database.Column(database.Text)
    tipo = database.Column(database.String(50))
    situacao = database.Column(database.String(50), default='Pendente')

class Projeto(database.Model):
    __tablename__ = 'projeto'
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(200), nullable=False)
    descricao = database.Column(database.Text)
    situacao = database.Column(database.String(20))
    prazo = database.Column(database.Date, nullable=True)
    orcamento = database.Column(database.Float)
    cliente_id = database.Column(database.Integer, database.ForeignKey('cliente.id', ondelete='SET NULL'))

    requisitos = database.relationship('Requisito', backref='projeto_rel', lazy=True, cascade='all, delete-orphan')
    lista_equipes = database.relationship('Equipes', secondary=equipes_projeto, back_populates='projetos')

class Registro(database.Model):
    __tablename__ = 'registro'
    id = database.Column(database.Integer, primary_key=True)
    tipo = database.Column(database.String(50))
    acao = database.Column(database.String(100))
    descricao = database.Column(database.Text)
    data = database.Column(database.DateTime(timezone=True), default=database.func.now())
    projeto_id = database.Column(database.Integer, database.ForeignKey('projeto.id', ondelete='SET NULL'), nullable=True)
    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id', ondelete='SET NULL'), nullable=True)

    __table_args__ = (
        database.Index('ix_registro_data', 'data'),
        database.Index('ix_registro_usuario', 'usuario_id'),
        database.Index('ix_registro_projeto', 'projeto_id'),
    )

class Documento(database.Model):
    __tablename__ = 'documento'
    id = database.Column(database.Integer, primary_key=True)
    projeto_id = database.Column(database.Integer, database.ForeignKey('projeto.id', ondelete='CASCADE'), nullable=False)
    nome = database.Column(database.String(255), nullable=False)
    caminho = database.Column(database.String(255), nullable=False)
    data_envio = database.Column(database.DateTime, default=database.func.now())
    tipo_arquivo = database.Column(database.String(10), nullable=False)

class Diagrama(database.Model):
    __tablename__ = 'diagrama'
    id = database.Column(database.Integer, primary_key=True)
    projeto_id = database.Column(database.Integer, database.ForeignKey('projeto.id', ondelete='CASCADE'), nullable=False)
    nome = database.Column(database.String(255), nullable=False)
    caminho = database.Column(database.String(255), nullable=False)
    data_envio = database.Column(database.DateTime, default=database.func.now())

class Galeria(database.Model):
    __tablename__ = 'galeria'
    id = database.Column(database.Integer, primary_key=True)
    projeto_id = database.Column(database.Integer, database.ForeignKey('projeto.id', ondelete='CASCADE'), nullable=False)
    nome = database.Column(database.String(255), nullable=False)
    caminho = database.Column(database.String(255), nullable=False)
    data_envio = database.Column(database.DateTime, default=database.func.now())

class Comentario(database.Model):
    __tablename__ = 'comentario'
    id = database.Column(database.Integer, primary_key=True)
    projeto_id = database.Column(database.Integer, database.ForeignKey('projeto.id', ondelete='CASCADE'), nullable=False)
    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    conteudo = database.Column(database.Text, nullable=False)
    data = database.Column(database.DateTime, default=database.func.now())
    usuario_rel = database.relationship('Usuario', backref=database.backref('comentarios_usuario', lazy=True))