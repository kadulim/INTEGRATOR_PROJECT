from flask import Flask, render_template, abort, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user, logout_user
import functools
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Carrega variáveis do arquivo .env (local)
load_dotenv()

from database import database
from models import Usuario, Admin

import function.login as logar
import function.register as registrar

app = Flask(__name__)

# CONFIGURAÇÕES
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cobyte_default_key')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Lógica para alternar entre Postgres (Render) e MySQL (Local)
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'mysql+pymysql://root:@localhost/database_cobyte'

# Inicializa o banco
database.init_app(app)

# CONFIGURAÇÃO LOGIN
lm = LoginManager(app)
lm.login_view = '/'

# Criação das tabelas e Admin padrão (Roda no Render e Local)
with app.app_context():
    database.create_all()
    
    admin_email = os.getenv('ADMIN_EMAIL')
    if admin_email and not Usuario.query.filter_by(email=admin_email).first():
        nome = os.getenv('ADMIN_NOME', 'Admin')
        senha = os.getenv('ADMIN_SENHA', 'admin123')
        senha_hash = generate_password_hash(senha)
        
        usuario = Usuario(nome=nome, email=admin_email, senha=senha_hash, tipo='admin', nivel=1)
        database.session.add(usuario)
        database.session.flush()
        
        admin = Admin(usuario_id=usuario.id, nivel='1')
        database.session.add(admin)
        database.session.commit()
        print("Usuário Admin padrão verificado/criado com sucesso!")

# DECORATOR POR NÍVEL
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

# USER LOADER
@lm.user_loader
def user_loader(id):
    return database.session.get(Usuario, int(id))

# ROTAS
@app.route('/', methods=['GET', 'POST'])
def page_login():
    return logar.logar()

@app.route('/register', methods=['GET', 'POST'])
def page_register():
    return registrar.register()

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('page_login'))

@app.route('/cliente')
@login_required
def cliente():
    return render_template('cliente/client.html')

@app.route('/funcionario')
@login_required
def funcionario():
    return render_template('cliente/client.html')

# Blueprint Admin
from routes.admin import admin_bp
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(debug=True)
