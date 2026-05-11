from flask import Flask, render_template, abort, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user, logout_user
import functools
import os
import sys
import subprocess
import time
import socket
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Carrega variáveis do arquivo .env (apenas localmente)
load_dotenv()

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

# Registro do Blueprint CodeFlow
from routes.codeflow import codeflow_bp
app.register_blueprint(codeflow_bp)
api_url = os.getenv('CODEFLOW_API_URL')
if not api_url:
    base_port = int(os.getenv('PORT', '5000'))
    api_url = f'http://localhost:{base_port + 1}'
app.config['CODEFLOW_API_URL'] = api_url

def _port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def _install_requirements(req_file):
    try:
        import pkg_resources
        with open(req_file) as f:
            missing = []
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                try:
                    pkg_resources.require(line)
                except Exception:
                    missing.append(line)
        if missing:
            print(f'[CodeFlow] Instalando dependencias: {", ".join(missing)}')
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '-r', req_file, '-q'],
            )
    except Exception:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '-r', req_file, '-q'],
        )

def _start_codeflow_api():
    base_port = int(os.getenv('CODEFLOW_PORT', '5001'))
    cf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_codeflow')
    req_file = os.path.join(cf_dir, 'requirements.txt')
    if os.path.exists(req_file):
        _install_requirements(req_file)
    env = os.environ.copy()
    env['PYTHONPATH'] = cf_dir + os.pathsep + env.get('PYTHONPATH', '')
    for attempt in range(5):
        port = base_port + attempt
        if _port_in_use(port):
            print(f'[CodeFlow] Porta {port} ocupada, tentando proxima...')
            continue
        proc = subprocess.Popen(
            [sys.executable, 'run.py'],
            cwd=cf_dir,
            env={**env, 'FLASK_PORT': str(port)},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        time.sleep(1.5)
        if proc.poll() is not None:
            out, err = proc.communicate()
            err_text = err.decode().strip()
            if 'in use' in err_text.lower():
                print(f'[CodeFlow] Porta {port} conflitou, tentando proxima...')
                continue
            print(f'[CodeFlow] ERRO ao iniciar API: {err_text}')
            return None
        print(f'[CodeFlow] API iniciada (PID {proc.pid}) na porta {port}')
        app.config['CODEFLOW_API_URL'] = f'http://localhost:{port}'
        return proc
    print(f'[CodeFlow] Nao foi possivel encontrar uma porta livre')
    return None

if __name__ == '__main__':
    _start_codeflow_api()
    app.run(debug=True)