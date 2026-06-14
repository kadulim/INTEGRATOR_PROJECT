# =============================================================================
# app.py - Aplicação principal do sistema Cobyte/Integrator
# =============================================================================
# Responsável por inicializar o Flask, configurar banco de dados, segurança,
# login, blueprints e rotas principais (cliente, uploads, comentários).
# =============================================================================

# ---------------------------------------------------------------------------
# Imports padrão e de terceiros
# ---------------------------------------------------------------------------
from flask import Flask, render_template, abort, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user, logout_user
from flask_wtf.csrf import CSRFProtect
import functools
import json
import os
import sys

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Carrega variáveis do arquivo .env (apenas localmente)
load_dotenv()

# ---------------------------------------------------------------------------
# Path auxiliar para importar a API CodeFlow
# ---------------------------------------------------------------------------
_api_codeflow_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_codeflow', 'api')

# ---------------------------------------------------------------------------
# Imports internos do projeto
# ---------------------------------------------------------------------------
from database import database
from models import User, Client, Project, Log, Document, Diagram, Gallery, Comment

import function.login as logar
import function.adicionar_na_tabela as adicionar_na_tabela

# =============================================================================
# Inicialização da aplicação Flask
# =============================================================================
app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configurações de segurança
# ---------------------------------------------------------------------------
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    import warnings
    warnings.warn("SECRET_KEY não definida. Usando fallback inseguro. Defina SECRET_KEY no ambiente.")
    app.config['SECRET_KEY'] = 'cobyte_chave_padrao'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hora

csrf = CSRFProtect(app)

# ---------------------------------------------------------------------------
# Configuração do banco de dados (prioriza PostgreSQL do Render, fallback MySQL local)
# ---------------------------------------------------------------------------
uri = os.getenv("DATABASE_URL")

if uri:
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/database_cobyte'

database.init_app(app)

# ---------------------------------------------------------------------------
# Configuração do Flask-Login
# ---------------------------------------------------------------------------
lm = LoginManager(app)
lm.login_view = '/'

# ---------------------------------------------------------------------------
# Criação automática de tabelas + seed de dados iniciais
# ---------------------------------------------------------------------------
adicionar_na_tabela.adicionar(app)

# ---------------------------------------------------------------------------
# Decorator para controle de acesso por nível hierárquico
# ---------------------------------------------------------------------------
def login_required_nivel(nivel_minimo):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return lm.unauthorized()
            if current_user.type_user != 'admin':
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ---------------------------------------------------------------------------
# Carregador de usuário para Flask-Login
# ---------------------------------------------------------------------------
@lm.user_loader
def user_loader(id):
    return database.session.get(User, int(id))

# =============================================================================
# ROTAS PÚBLICAS
# =============================================================================

# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def page_login():
    return logar.logar()

# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('page_login'))

# =============================================================================
# ROTAS DO CLIENTE
# =============================================================================

# ---------------------------------------------------------------------------
# Dashboard do cliente
# ---------------------------------------------------------------------------
@app.route('/cliente-dashboard')
@login_required
def cliente_dashboard():
    cliente = Client.query.filter_by(fk_user=current_user.pk_id_user).first()
    projetos = cliente.projects if cliente else []

    total = len(projetos)
    ativos = sum(1 for p in projetos if p.status_project == 'Em andamento')
    concluidos = sum(1 for p in projetos if p.status_project == 'Concluído')
    pausados = total - ativos - concluidos

    status_data = [
        {'label': 'Em andamento', 'val': ativos,    'color': '#f59e0b'},
        {'label': 'Concluído',    'val': concluidos, 'color': '#10b981'},
        {'label': 'Pausado',      'val': pausados,   'color': '#FF5577'},
    ]

    # ── Todos os projetos do cliente agrupados por status para o Donut Chart tooltip ──
    projetos_por_status = {
        'em_andamento': [],
        'concluido': [],
        'pausado': []
    }
    for proj in projetos:
        status_str = proj.status_project or 'Pausado'
        if status_str == 'Pendente':
            status_str = 'Pausado'
        if status_str == 'Cancelado':
            continue
        
        proj_data = {
            'nome': proj.name_project,
            'prazo': proj.end_date_project.strftime('%d/%m/%Y') if proj.end_date_project else 'Sem prazo',
            'url': url_for('cliente_projeto_detalhe', projeto_id=proj.pk_id_project)
        }
        
        if status_str == 'Em andamento':
            projetos_por_status['em_andamento'].append(proj_data)
        elif status_str == 'Concluído':
            projetos_por_status['concluido'].append(proj_data)
        else:
            projetos_por_status['pausado'].append(proj_data)

    return render_template('cliente/cliente-dashboard.html',
                           projetos=projetos,
                           total=total,
                           ativos=ativos,
                           concluidos=concluidos,
                           status_data_json=json.dumps(status_data),
                           projetos_status_json=json.dumps(projetos_por_status))

# ---------------------------------------------------------------------------
# Listagem de projetos do cliente
# ---------------------------------------------------------------------------
@app.route('/cliente-dashboard/projetos')
@login_required
def cliente_projetos():
    cliente = Client.query.filter_by(fk_user=current_user.pk_id_user).first()
    projetos = cliente.projects if cliente else []
    if len(projetos) == 1:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projetos[0].pk_id_project))  
    else:
        return render_template('cliente/projetos.html', projetos=projetos)


# ---------------------------------------------------------------------------
# Detalhes de um projeto específico (cliente)
# ---------------------------------------------------------------------------
@app.route('/cliente-dashboard/projeto/<int:projeto_id>')
@login_required
def cliente_projeto_detalhe(projeto_id):
    cliente = Client.query.filter_by(fk_user=current_user.pk_id_user).first()
    if not cliente:
        abort(403)
    projeto = Project.query.get_or_404(projeto_id)
    if projeto.fk_client != cliente.pk_id_client:
        abort(403)
    
    logs = Log.query.filter_by(fk_project=projeto_id).order_by(Log.date_log.desc()).all()
    documentos = Document.query.filter_by(fk_project=projeto_id).all()
    diagramas = Diagram.query.filter_by(fk_project=projeto_id).all()
    galeria = Gallery.query.filter_by(fk_project=projeto_id).all()
    comentarios = Comment.query.filter_by(fk_project=projeto_id).order_by(Comment.date_comment.asc()).all()
    return render_template('cliente/projeto-detalhe.html', projeto=projeto, logs=logs,
                           documentos=documentos, diagramas=diagramas, galeria=galeria, comentarios=comentarios)

# ---------------------------------------------------------------------------
# Envio de feedback do cliente sobre um projeto
# ---------------------------------------------------------------------------
@app.route('/cliente-dashboard/projeto/<int:projeto_id>/feedback', methods=['POST'])
@login_required
def cliente_feedback(projeto_id):
    cliente = Client.query.filter_by(fk_user=current_user.pk_id_user).first()
    if not cliente:
        abort(403)
    projeto = Project.query.get_or_404(projeto_id)
    if projeto.fk_client != cliente.pk_id_client:
        abort(403)
    
    feedback_tipo = request.form.get('feedback_tipo', 'Geral')
    comentario = request.form.get('comentario', '').strip()
    
    if comentario:
        log_entry = Log(
            type_log='feedback',
            description_log=comentario,
            fk_project=projeto_id,
            fk_user=current_user.pk_id_user
        )
        database.session.add(log_entry)
        database.session.commit()
    
    return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

# =============================================================================
# REDIRECIONAMENTO PARA BLUEPRINT DE FUNCIONÁRIO
# =============================================================================
@app.route('/funcionario')
@login_required
def funcionario():
    return redirect(url_for('funcionario.dashboard'))

# =============================================================================
# MIDDLEWARE - Prevenir cache (impede voltar para página logada após logout)
# =============================================================================
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# =============================================================================
# Registro dos Blueprints
# =============================================================================

# Blueprint de Admin (CRUD de projetos, equipes, funcionários, clientes)
from routes.admin import admin_bp
app.register_blueprint(admin_bp)

# Blueprint de Funcionário (dashboard, projetos, equipes)
from routes.funcionario import funcionario_bp
app.register_blueprint(funcionario_bp)

# Blueprint CodeFlow (frontend de análise de código)
from routes.codeflow import codeflow_bp
app.register_blueprint(codeflow_bp)

# =============================================================================
# Registro da API CodeFlow (mesmo servidor, mesma porta)
# =============================================================================
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

# =============================================================================
# Configuração de upload de arquivos
# =============================================================================
from werkzeug.utils import secure_filename
import time

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Garante que as pastas de upload existam (importante no Render com filesystem efêmero)
for subdir in ('documentos', 'diagramas', 'galeria'):
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], subdir), exist_ok=True)

# =============================================================================
# ROTAS DE UPLOAD / CRUD DE ARQUIVOS (documentos, diagramas, galeria)
# =============================================================================

# ---------------------------------------------------------------------------
# Upload de documento (PDF/DOCX)
# ---------------------------------------------------------------------------
@app.route('/projeto/<int:projeto_id>/upload-documento', methods=['POST'])
@login_required
def upload_documento(projeto_id):
    projeto = Project.query.get_or_404(projeto_id)
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
    
    doc = Document(
        fk_project=projeto_id,
        name_document=filename,
        path_document=f"uploads/documentos/{unique_filename}",
        type_document=ext
    )
    database.session.add(doc)
    
    log_entry = Log(
        type_log='documento',
        description_log=f"Documento '{filename}' enviado por {current_user.name_user}.",
        fk_project=projeto_id,
        fk_user=current_user.pk_id_user
    )
    database.session.add(log_entry)
    database.session.commit()
    return "Upload concluído", 200

# ---------------------------------------------------------------------------
# Exclusão de documento
# ---------------------------------------------------------------------------
@app.route('/projeto/delete-documento/<int:doc_id>', methods=['POST'])
@login_required
def delete_documento(doc_id):
    doc = Document.query.get_or_404(doc_id)
    projeto_id = doc.fk_project
    
    try:
        physical_path = os.path.join(app.root_path, 'static', doc.path_document)
        if os.path.exists(physical_path):
            os.remove(physical_path)
    except Exception as e:
        print(f"Erro ao remover arquivo físico: {e}")
        
    log_entry = Log(
        type_log='documento',
        description_log=f"Documento '{doc.name_document}' excluído por {current_user.name_user}.",
        fk_project=projeto_id,
        fk_user=current_user.pk_id_user
    )
    database.session.add(log_entry)
    database.session.delete(doc)
    database.session.commit()
    
    if current_user.type_user == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.type_user == 'employee':
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
    else:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

# ---------------------------------------------------------------------------
# Upload de diagrama (imagens)
# ---------------------------------------------------------------------------
@app.route('/projeto/<int:projeto_id>/upload-diagrama', methods=['POST'])
@login_required
def upload_diagrama(projeto_id):
    projeto = Project.query.get_or_404(projeto_id)
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
    
    diag = Diagram(
        fk_project=projeto_id,
        name_diagram=filename,
        path_diagram=f"uploads/diagramas/{unique_filename}"
    )
    database.session.add(diag)
    
    log_entry = Log(
        type_log='diagrama',
        description_log=f"Diagrama '{filename}' enviado por {current_user.name_user}.",
        fk_project=projeto_id,
        fk_user=current_user.pk_id_user
    )
    database.session.add(log_entry)
    database.session.commit()
    return "Upload concluído", 200

# ---------------------------------------------------------------------------
# Exclusão de diagrama
# ---------------------------------------------------------------------------
@app.route('/projeto/delete-diagrama/<int:diag_id>', methods=['POST'])
@login_required
def delete_diagrama(diag_id):
    diag = Diagram.query.get_or_404(diag_id)
    projeto_id = diag.fk_project
    
    try:
        physical_path = os.path.join(app.root_path, 'static', diag.path_diagram)
        if os.path.exists(physical_path):
            os.remove(physical_path)
    except Exception as e:
        print(f"Erro ao remover arquivo físico: {e}")
        
    log_entry = Log(
        type_log='diagrama',
        description_log=f"Diagrama '{diag.name_diagram}' excluído por {current_user.name_user}.",
        fk_project=projeto_id,
        fk_user=current_user.pk_id_user
    )
    database.session.add(log_entry)
    database.session.delete(diag)
    database.session.commit()
    
    if current_user.type_user == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.type_user == 'employee':
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
    else:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

# ---------------------------------------------------------------------------
# Upload de imagem para galeria
# ---------------------------------------------------------------------------
@app.route('/projeto/<int:projeto_id>/upload-galeria', methods=['POST'])
@login_required
def upload_galeria(projeto_id):
    projeto = Project.query.get_or_404(projeto_id)
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
    
    gal = Gallery(
        fk_project=projeto_id,
        path_gallery=f"uploads/galeria/{unique_filename}"
    )
    database.session.add(gal)
    
    log_entry = Log(
        type_log='galeria',
        description_log=f"Imagem '{filename}' enviada para a galeria por {current_user.name_user}.",
        fk_project=projeto_id,
        fk_user=current_user.pk_id_user
    )
    database.session.add(log_entry)
    database.session.commit()
    return "Upload concluído", 200

# ---------------------------------------------------------------------------
# Exclusão de imagem da galeria
# ---------------------------------------------------------------------------
@app.route('/projeto/delete-galeria/<int:item_id>', methods=['POST'])
@login_required
def delete_galeria(item_id):
    gal = Gallery.query.get_or_404(item_id)
    projeto_id = gal.fk_project
    
    try:
        physical_path = os.path.join(app.root_path, 'static', gal.path_gallery)
        if os.path.exists(physical_path):
            os.remove(physical_path)
    except Exception as e:
        print(f"Erro ao remover arquivo físico: {e}")
        
    log_entry = Log(
        type_log='galeria',
        description_log=f"Imagem removida da galeria por {current_user.name_user}.",
        fk_project=projeto_id,
        fk_user=current_user.pk_id_user
    )
    database.session.add(log_entry)
    database.session.delete(gal)
    database.session.commit()
    
    if current_user.type_user == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.type_user == 'employee':
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
    else:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

# =============================================================================
# ROTAS DE COMENTÁRIOS
# =============================================================================

# ---------------------------------------------------------------------------
# Adicionar comentário a um projeto
# ---------------------------------------------------------------------------
@app.route('/projeto/<int:projeto_id>/add-comentario', methods=['POST'])
@login_required
def add_comentario(projeto_id):
    projeto = Project.query.get_or_404(projeto_id)
    conteudo = request.form.get('conteudo', '').strip()
    if not conteudo:
        flash("O conteúdo do comentário não pode estar vazio.", "erro")
        if current_user.type_user == 'admin':
            return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
        elif current_user.type_user == 'employee':
            return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
        else:
            return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))
            
    com = Comment(
        fk_project=projeto_id,
        fk_user=current_user.pk_id_user,
        content_comment=conteudo
    )
    database.session.add(com)
    
    log_entry = Log(
        type_log='comentario',
        description_log=f"{current_user.name_user} adicionou um comentário.",
        fk_project=projeto_id,
        fk_user=current_user.pk_id_user
    )
    database.session.add(log_entry)
    database.session.commit()
    
    if current_user.type_user == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.type_user == 'employee':
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
    else:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

# ---------------------------------------------------------------------------
# Excluir comentário
# ---------------------------------------------------------------------------
@app.route('/projeto/delete-comentario/<int:com_id>', methods=['POST'])
@login_required
def delete_comentario(com_id):
    com = Comment.query.get_or_404(com_id)
    projeto_id = com.fk_project
    
    if current_user.type_user != 'admin' and com.fk_user != current_user.pk_id_user:
        abort(403)
        
    database.session.delete(com)
    database.session.commit()
    
    if current_user.type_user == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.type_user == 'employee':
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
    else:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

def _redirect_to_projeto(projeto_id):
    if current_user.type_user == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.type_user == 'employee':
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
    else:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

def _next_version_name(current_name):
    match = re.search(r' \(versão (\d+)\)', current_name)
    if match:
        v = int(match.group(1)) + 1
        return re.sub(r' \(versão \d+\)', f' (versão {v})', current_name)
    name_parts = current_name.rsplit('.', 1)
    if len(name_parts) == 2:
        return f"{name_parts[0]} (versão 2).{name_parts[1]}"
    return f"{current_name} (versão 2)"

def _update_file(record, attr_name, file, upload_subdir, allowed_exts):
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed_exts:
        return "Tipo de arquivo inválido.", 400
    filename = secure_filename(file.filename)
    unique_filename = f"{int(time.time())}_{filename}"
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], upload_subdir)
    os.makedirs(upload_path, exist_ok=True)
    file.save(os.path.join(upload_path, unique_filename))
    try:
        old_path = os.path.join(app.root_path, 'static', getattr(record, attr_name))
        if os.path.exists(old_path):
            os.remove(old_path)
    except Exception as e:
        print(f"Erro ao remover arquivo físico: {e}")
    setattr(record, attr_name, f"uploads/{upload_subdir}/{unique_filename}")

# ---------------------------------------------------------------------------
# Atualizar documento
# ---------------------------------------------------------------------------
@app.route('/projeto/update-documento/<int:doc_id>', methods=['POST'])
@login_required
def update_documento(doc_id):
    doc = Document.query.get_or_404(doc_id)
    projeto_id = doc.fk_project
    if 'file' not in request.files:
        flash("Nenhum arquivo enviado.", "erro")
        return _redirect_to_projeto(projeto_id)
    file = request.files['file']
    if file.filename == '':
        flash("Nenhum arquivo selecionado.", "erro")
        return _redirect_to_projeto(projeto_id)
    result = _update_file(doc, 'path_document', file, 'documentos', ['pdf', 'docx'])
    if isinstance(result, tuple):
        return result
    database.session.commit()
    log_entry = Log(
        type_log='documento',
        description_log=f"Documento '{doc.name_document}' foi atualizado por {current_user.name_user}.",
        fk_project=projeto_id,
        fk_user=current_user.pk_id_user
    )
    database.session.add(log_entry)
    database.session.commit()
    flash("Documento atualizado com sucesso!", "sucesso")
    return _redirect_to_projeto(projeto_id)

# ---------------------------------------------------------------------------
# Atualizar diagrama
# ---------------------------------------------------------------------------
@app.route('/projeto/update-diagrama/<int:diag_id>', methods=['POST'])
@login_required
def update_diagrama(diag_id):
    diag = Diagram.query.get_or_404(diag_id)
    projeto_id = diag.fk_project
    if 'file' not in request.files:
        flash("Nenhum arquivo enviado.", "erro")
        return _redirect_to_projeto(projeto_id)
    file = request.files['file']
    if file.filename == '':
        flash("Nenhum arquivo selecionado.", "erro")
        return _redirect_to_projeto(projeto_id)
    result = _update_file(diag, 'path_diagram', file, 'diagramas', ['png', 'jpg', 'jpeg', 'gif', 'svg'])
    if isinstance(result, tuple):
        return result
    database.session.commit()
    log_entry = Log(
        type_log='diagrama',
        description_log=f"Diagrama '{diag.name_diagram}' foi atualizado por {current_user.name_user}.",
        fk_project=projeto_id,
        fk_user=current_user.pk_id_user
    )
    database.session.add(log_entry)
    database.session.commit()
    flash("Diagrama atualizado com sucesso!", "sucesso")
    return _redirect_to_projeto(projeto_id)

# ---------------------------------------------------------------------------
# Atualizar galeria
# ---------------------------------------------------------------------------
@app.route('/projeto/update-galeria/<int:item_id>', methods=['POST'])
@login_required
def update_galeria(item_id):
    gal = Gallery.query.get_or_404(item_id)
    projeto_id = gal.fk_project
    if 'file' not in request.files:
        flash("Nenhum arquivo enviado.", "erro")
        return _redirect_to_projeto(projeto_id)
    file = request.files['file']
    if file.filename == '':
        flash("Nenhum arquivo selecionado.", "erro")
        return _redirect_to_projeto(projeto_id)
    result = _update_file(gal, 'path_gallery', file, 'galeria', ['png', 'jpg', 'jpeg', 'gif', 'svg'])
    if isinstance(result, tuple):
        return result
    database.session.commit()
    log_entry = Log(
        type_log='galeria',
        description_log=f"Imagem na galeria foi atualizada por {current_user.name_user}.",
        fk_project=projeto_id,
        fk_user=current_user.pk_id_user
    )
    database.session.add(log_entry)
    database.session.commit()
    flash("Galeria atualizada com sucesso!", "sucesso")
    return _redirect_to_projeto(projeto_id)

# =============================================================================
# Ponto de entrada da aplicação
# =============================================================================
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)