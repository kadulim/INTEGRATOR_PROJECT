from database import database
from flask_login import UserMixin

#Tabela do Usuario
class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(100))
    email = database.Column(database.String(120), unique=True)
    senha = database.Column(database.String(200))
    tipo = database.Column(database.String(20))
    nivel = database.Column(database.Integer)

#Tabela do Admin
class Admin(database.Model, UserMixin):
    __tablename__ = 'admin'
    id = database.Column(database.Integer, primary_key=True)
    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    nivel = database.Column(database.String(50))

#Tabela do Cliente
class Cliente(database.Model, UserMixin):
    __tablename__ = 'cliente'
    id = database.Column(database.Integer, primary_key=True)
    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    empresa = database.Column(database.String(200))

#Tabela do Funcionario
class Funcionario(database.Model, UserMixin):
    __tablename__ = 'funcionario'
    id = database.Column(database.Integer, primary_key=True)
    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id'))
    projeto_id = database.Column(database.Integer, database.ForeignKey('projeto.id'))
    cargo = database.Column(database.String(50))
    salario = database.Column(database.Float)

#Tabel Projeto
class Projeto(database.Model, UserMixin):
    __tablename__ = 'projeto'
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(200))
    descricao = database.Column(database.String(200))
    status = database.Column(database.String(20))
    cliente = database.Column(database.String(200))
    funcionario = database.Column(database.String(200))
    prazo = database.Column(database.String(20))
    budget = database.Column(database.Float)
    prioridade = database.Column(database.String(20))
    cliente_id = database.Column(database.Integer, database.ForeignKey('cliente.id'))
    funcionario_id = database.Column(database.Integer, database.ForeignKey('funcionario.id'))