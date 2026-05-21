from flask import Flask, render_template, abort, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user, logout_user
from flask_wtf.csrf import CSRFProtect
import functools
import os
import sys
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Carrega variáveis do arquivo .env (apenas localmente)
load_dotenv()

_api_codeflow_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_codeflow', 'api')

from database import database
from models import Usuario, Cliente, Projeto, Log, Documento, Diagrama, Galeria, Comentario

import function.login as logar
import function.adicionar_na_tabela as adicionar_na_tabela

app = Flask(__name__)

# CONFIGURAÇÕES DE SEGURANÇA
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cobyte_chave_padrao')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hora

csrf = CSRFProtect(app)

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
    
    total = len(projetos)
    ativos = sum(1 for p in projetos if p.status == 'Em andamento')
    concluidos = sum(1 for p in projetos if p.status == 'Concluído')
    
    return render_template('cliente/cliente-dashboard.html', 
                           projetos=projetos, 
                           total=total, 
                           ativos=ativos, 
                           concluidos=concluidos)

@app.route('/cliente-dashboard/projetos')
@login_required
def cliente_projetos():
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    projetos = cliente.projetos if cliente else []
    return render_template('cliente/projetos.html', projetos=projetos)

@app.route('/cliente-dashboard/projeto/<int:projeto_id>')
@login_required
def cliente_projeto_detalhe(projeto_id):
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    if not cliente:
        abort(403)
    projeto = Projeto.query.get_or_404(projeto_id)
    if projeto.cliente_id != cliente.id:
        abort(403)
    
    # Buscar logs associados ao projeto
    logs = Log.query.filter_by(projeto_id=projeto_id).order_by(Log.data.desc()).all()
    documentos = Documento.query.filter_by(projeto_id=projeto_id).all()
    diagramas = Diagrama.query.filter_by(projeto_id=projeto_id).all()
    galeria = Galeria.query.filter_by(projeto_id=projeto_id).all()
    comentarios = Comentario.query.filter_by(projeto_id=projeto_id).order_by(Comentario.data.asc()).all()
    return render_template('cliente/projeto-detalhe.html', projeto=projeto, logs=logs,
                           documentos=documentos, diagramas=diagramas, galeria=galeria, comentarios=comentarios)

@app.route('/cliente-dashboard/projeto/<int:projeto_id>/feedback', methods=['POST'])
@login_required
def cliente_feedback(projeto_id):
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    if not cliente:
        abort(403)
    projeto = Projeto.query.get_or_404(projeto_id)
    if projeto.cliente_id != cliente.id:
        abort(403)
    
    feedback_tipo = request.form.get('feedback_tipo', 'Geral')
    comentario = request.form.get('comentario', '').strip()
    
    if comentario:
        log = Log(
            tipo='feedback',
            acao=f"Feedback - {feedback_tipo}",
            descricao=comentario,
            projeto_id=projeto_id
        )
        database.session.add(log)
        database.session.commit()
    
    return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

@app.route('/funcionario')
@login_required
def funcionario():
    return redirect(url_for('funcionario.dashboard'))

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

# Registro do Blueprint de Funcionário
from routes.funcionario import funcionario_bp
app.register_blueprint(funcionario_bp)

# Registro do Blueprint CodeFlow (frontend)
from routes.codeflow import codeflow_bp
app.register_blueprint(codeflow_bp)

# ── CodeFlow API (mesmo servidor, mesma porta) ──────────────────────
# Adiciona o path da API ao sys.path para importar os blueprints
if _api_codeflow_path not in sys.path:
    sys.path.insert(0, _api_codeflow_path)
from cfroutes.health import health_bp
from cfroutes.analyze import analyze_bp
csrf.exempt(health_bp)
csrf.exempt(analyze_bp)
app.register_blueprint(health_bp)
app.register_blueprint(analyze_bp)

if os.environ.get('RENDER') == 'true':
    app.config['CODEFLOW_API_URL'] = os.getenv('CODEFLOW_API_URL', 'https://api-codeflow.onrender.com')
else:
    app.config['CODEFLOW_API_URL'] = os.getenv('CODEFLOW_API_URL', '')

from werkzeug.utils import secure_filename
import time

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

@app.route('/projeto/<int:projeto_id>/upload-documento', methods=['POST'])
@login_required
def upload_documento(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)
    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400
    file = request.files['file']
    if file.filename == '':
        return "Nenhum arquivo selecionado", 400
    
    ext = file.filename.split('.')[-1].lower()
    if ext not in ['pdf', 'docx']:
        return "Tipo de arquivo inválido. Apenas PDF e DOCX são aceitos.", 400
        
    filename = secure_filename(file.filename)
    unique_filename = f"{int(time.time())}_{filename}"
    
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'documentos')
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, unique_filename)
    file.save(file_path)
    
    doc = Documento(
        projeto_id=projeto_id,
        nome=filename,
        caminho=f"uploads/documentos/{unique_filename}",
        tipo_arquivo=ext
    )
    database.session.add(doc)
    
    log = Log(
        tipo='documento',
        acao='Documento enviado',
        descricao=f"Documento '{filename}' enviado por {current_user.nome}.",
        projeto_id=projeto_id
    )
    database.session.add(log)
    database.session.commit()
    return "Upload concluído", 200

@app.route('/projeto/delete-documento/<int:doc_id>', methods=['POST'])
@login_required
def delete_documento(doc_id):
    doc = Documento.query.get_or_404(doc_id)
    projeto_id = doc.projeto_id
    
    try:
        physical_path = os.path.join(app.root_path, 'static', doc.caminho)
        if os.path.exists(physical_path):
            os.remove(physical_path)
    except Exception as e:
        print(f"Erro ao remover arquivo físico: {e}")
        
    log = Log(
        tipo='documento',
        acao='Documento excluído',
        descricao=f"Documento '{doc.nome}' excluído por {current_user.nome}.",
        projeto_id=projeto_id
    )
    database.session.add(log)
    database.session.delete(doc)
    database.session.commit()
    
    if current_user.tipo == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.tipo == 'funcionario':
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
    else:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

@app.route('/projeto/<int:projeto_id>/upload-diagrama', methods=['POST'])
@login_required
def upload_diagrama(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)
    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400
    file = request.files['file']
    if file.filename == '':
        return "Nenhum arquivo selecionado", 400
        
    ext = file.filename.split('.')[-1].lower()
    if ext not in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
        return "Tipo de arquivo inválido. Apenas imagens são aceitas.", 400
        
    filename = secure_filename(file.filename)
    unique_filename = f"{int(time.time())}_{filename}"
    
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'diagramas')
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, unique_filename)
    file.save(file_path)
    
    diag = Diagrama(
        projeto_id=projeto_id,
        nome=filename,
        caminho=f"uploads/diagramas/{unique_filename}"
    )
    database.session.add(diag)
    
    log = Log(
        tipo='diagrama',
        acao='Diagrama enviado',
        descricao=f"Diagrama '{filename}' enviado por {current_user.nome}.",
        projeto_id=projeto_id
    )
    database.session.add(log)
    database.session.commit()
    return "Upload concluído", 200

@app.route('/projeto/delete-diagrama/<int:diag_id>', methods=['POST'])
@login_required
def delete_diagrama(diag_id):
    diag = Diagrama.query.get_or_404(diag_id)
    projeto_id = diag.projeto_id
    
    try:
        physical_path = os.path.join(app.root_path, 'static', diag.caminho)
        if os.path.exists(physical_path):
            os.remove(physical_path)
    except Exception as e:
        print(f"Erro ao remover arquivo físico: {e}")
        
    log = Log(
        tipo='diagrama',
        acao='Diagrama excluído',
        descricao=f"Diagrama '{diag.nome}' excluído por {current_user.nome}.",
        projeto_id=projeto_id
    )
    database.session.add(log)
    database.session.delete(diag)
    database.session.commit()
    
    if current_user.tipo == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.tipo == 'funcionario':
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
    else:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

@app.route('/projeto/<int:projeto_id>/upload-galeria', methods=['POST'])
@login_required
def upload_galeria(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)
    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400
    file = request.files['file']
    if file.filename == '':
        return "Nenhum arquivo selecionado", 400
        
    ext = file.filename.split('.')[-1].lower()
    if ext not in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
        return "Tipo de arquivo inválido. Apenas imagens são aceitas.", 400
        
    filename = secure_filename(file.filename)
    unique_filename = f"{int(time.time())}_{filename}"
    
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'galeria')
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, unique_filename)
    file.save(file_path)
    
    gal = Galeria(
        projeto_id=projeto_id,
        nome=filename,
        caminho=f"uploads/galeria/{unique_filename}"
    )
    database.session.add(gal)
    
    log = Log(
        tipo='galeria',
        acao='Imagem da galeria enviada',
        descricao=f"Imagem '{filename}' enviada para a galeria por {current_user.nome}.",
        projeto_id=projeto_id
    )
    database.session.add(log)
    database.session.commit()
    return "Upload concluído", 200

@app.route('/projeto/delete-galeria/<int:item_id>', methods=['POST'])
@login_required
def delete_galeria(item_id):
    gal = Galeria.query.get_or_404(item_id)
    projeto_id = gal.projeto_id
    
    try:
        physical_path = os.path.join(app.root_path, 'static', gal.caminho)
        if os.path.exists(physical_path):
            os.remove(physical_path)
    except Exception as e:
        print(f"Erro ao remover arquivo físico: {e}")
        
    log = Log(
        tipo='galeria',
        acao='Imagem da galeria excluída',
        descricao=f"Imagem '{gal.nome}' removida da galeria por {current_user.nome}.",
        projeto_id=projeto_id
    )
    database.session.add(log)
    database.session.delete(gal)
    database.session.commit()
    
    if current_user.tipo == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.tipo == 'funcionario':
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
    else:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

@app.route('/projeto/<int:projeto_id>/add-comentario', methods=['POST'])
@login_required
def add_comentario(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)
    conteudo = request.form.get('conteudo', '').strip()
    if not conteudo:
        flash("O conteúdo do comentário não pode estar vazio.", "erro")
        if current_user.tipo == 'admin':
            return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
        elif current_user.tipo == 'funcionario':
            return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
        else:
            return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))
            
    com = Comentario(
        projeto_id=projeto_id,
        usuario_id=current_user.id,
        conteudo=conteudo
    )
    database.session.add(com)
    
    log = Log(
        tipo='comentario',
        acao='Comentário enviado',
        descricao=f"{current_user.nome} adicionou um comentário.",
        projeto_id=projeto_id
    )
    database.session.add(log)
    database.session.commit()
    
    if current_user.tipo == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.tipo == 'funcionario':
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
    else:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

@app.route('/projeto/delete-comentario/<int:com_id>', methods=['POST'])
@login_required
def delete_comentario(com_id):
    com = Comentario.query.get_or_404(com_id)
    projeto_id = com.projeto_id
    
    if current_user.nivel != 1 and com.usuario_id != current_user.id:
        abort(403)
        
    database.session.delete(com)
    database.session.commit()
    
    if current_user.tipo == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.tipo == 'funcionario':
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
    else:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

if __name__ == '__main__':
    app.run(debug=True)