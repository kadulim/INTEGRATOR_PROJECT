from flask import Flask, render_template, abort, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user, logout_user
import functools
import os
import sys
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Carrega variáveis do arquivo .env (apenas localmente)
load_dotenv()

_api_codeflow_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_codeflow', 'api')

from database import database
from models import Usuario,Cliente

import function.login as logar
import function.adicionar_na_tabela as adicionar_na_tabela

app = Flask(__name__)

# CONFIGURAÇÕES DE SEGURANÇA
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cobyte_chave_padrao')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Lógica de conexão para o Render
uri = os.getenv("DATABASE_URL")

if uri:
    # O SQLAlchemy exige 'postgresql://' (a sua já está assim, mas isso previne erros)
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
else:
    # Caso rode no seu Linux Mint local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/database_cobyte'

# Inicializa o banco de dados
database.init_app(app)

# CONFIGURAÇÃO DO LOGIN MANAGER
lm = LoginManager(app)
lm.login_view = '/'

# CRIAÇÃO AUTOMÁTICA DE TABELAS + SEED DE DADOS INICIAIS
adicionar_na_tabela.adicionar(app)

# DECORATOR PARA NÍVEL DE ACESSO
def login_required_nivel(nivel_minimo):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return lm.unauthorized()
            if current_user.nivel < nivel_minimo:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# CARREGADOR DE USUÁRIO PARA FLASK-LOGIN
@lm.user_loader
def user_loader(id):
    return database.session.get(Usuario, int(id))

# --- ROTAS ---

@app.route('/', methods=['GET', 'POST'])
def page_login():
    return logar.logar()
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('page_login'))

@app.route('/cliente-dashboard')
@login_required
def cliente_dashboard():
    # Busca o registro de Cliente associado ao Usuario logado
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    projetos = cliente.projetos if cliente else []
    return render_template('cliente/cliente-dashboard.html', projetos=projetos)

@app.route('/funcionario')
@login_required
def funcionario():
    return render_template('cliente/client.html')

# PREVENIR CACHE (Impede voltar para página logada após logout)
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Registro do Blueprint de Admin
from routes.admin import admin_bp
app.register_blueprint(admin_bp)

# Registro do Blueprint CodeFlow (frontend)
from routes.codeflow import codeflow_bp
app.register_blueprint(codeflow_bp)

# ── CodeFlow API (mesmo servidor, mesma porta) ──────────────────────
# Adiciona o path da API ao sys.path para importar os blueprints
if _api_codeflow_path not in sys.path:
    sys.path.insert(0, _api_codeflow_path)
from cfroutes.health import health_bp
from cfroutes.analyze import analyze_bp
app.register_blueprint(health_bp)
app.register_blueprint(analyze_bp)

app.config['CODEFLOW_API_URL'] = os.getenv('CODEFLOW_API_URL', '')

if __name__ == '__main__':
    app.run(debug=True)