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
from models import Usuario, Cliente, Projeto, Registro, Documento, Diagrama, Galeria, Comentario

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
            if current_user.nivel < nivel_minimo:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ---------------------------------------------------------------------------
# Carregador de usuário para Flask-Login
# ---------------------------------------------------------------------------
@lm.user_loader
def user_loader(id):
    return database.session.get(Usuario, int(id))

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
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    projetos = cliente.projetos if cliente else []

    total = len(projetos)
    ativos = sum(1 for p in projetos if p.situacao == 'Em andamento')
    concluidos = sum(1 for p in projetos if p.situacao == 'Concluído')
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
        status_str = proj.situacao or 'Pausado'
        if status_str == 'Pendente':
            status_str = 'Pausado'
        if status_str == 'Cancelado':
            continue
        
        proj_data = {
            'nome': proj.nome,
            'prazo': proj.prazo.strftime('%d/%m/%Y') if proj.prazo else 'Sem prazo',
            'url': url_for('cliente_projeto_detalhe', projeto_id=proj.id)
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
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    projetos = cliente.projetos if cliente else []
    if len(projetos) == 1:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projetos[0].id))  
    else:
        return render_template('cliente/projetos.html', projetos=projetos)


# ---------------------------------------------------------------------------
# Detalhes de um projeto específico (cliente)
# ---------------------------------------------------------------------------
@app.route('/cliente-dashboard/projeto/<int:projeto_id>')
@login_required
def cliente_projeto_detalhe(projeto_id):
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    if not cliente:
        abort(403)
    projeto = Projeto.query.get_or_404(projeto_id)
    if projeto.cliente_id != cliente.id:
        abort(403)
    
    logs = Registro.query.filter_by(projeto_id=projeto_id).order_by(Registro.data.desc()).all()
    documentos = Documento.query.filter_by(projeto_id=projeto_id).all()
    diagramas = Diagrama.query.filter_by(projeto_id=projeto_id).all()
    galeria = Galeria.query.filter_by(projeto_id=projeto_id).all()
    comentarios = Comentario.query.filter_by(projeto_id=projeto_id).order_by(Comentario.data.asc()).all()
    return render_template('cliente/projeto-detalhe.html', projeto=projeto, logs=logs,
                           documentos=documentos, diagramas=diagramas, galeria=galeria, comentarios=comentarios)

# ---------------------------------------------------------------------------
# Envio de feedback do cliente sobre um projeto
# ---------------------------------------------------------------------------
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
        registro = Registro(
            tipo='feedback',
            acao=f"Feedback - {feedback_tipo}",
            descricao=comentario,
            projeto_id=projeto_id
        )
        database.session.add(registro)
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
    
    registro = Registro(
        tipo='documento',
        acao='Documento enviado',
        descricao=f"Documento '{filename}' enviado por {current_user.nome}.",
        projeto_id=projeto_id
    )
    database.session.add(registro)
    database.session.commit()
    return "Upload concluído", 200

# ---------------------------------------------------------------------------
# Exclusão de documento
# ---------------------------------------------------------------------------
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
        
    registro = Registro(
        tipo='documento',
        acao='Documento excluído',
        descricao=f"Documento '{doc.nome}' excluído por {current_user.nome}.",
        projeto_id=projeto_id
    )
    database.session.add(registro)
    database.session.delete(doc)
    database.session.commit()
    
    if current_user.tipo == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.tipo == 'funcionario':
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
    else:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

# ---------------------------------------------------------------------------
# Upload de diagrama (imagens)
# ---------------------------------------------------------------------------
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
    
    registro = Registro(
        tipo='diagrama',
        acao='Diagrama enviado',
        descricao=f"Diagrama '{filename}' enviado por {current_user.nome}.",
        projeto_id=projeto_id
    )
    database.session.add(registro)
    database.session.commit()
    return "Upload concluído", 200

# ---------------------------------------------------------------------------
# Exclusão de diagrama
# ---------------------------------------------------------------------------
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
        
    registro = Registro(
        tipo='diagrama',
        acao='Diagrama excluído',
        descricao=f"Diagrama '{diag.nome}' excluído por {current_user.nome}.",
        projeto_id=projeto_id
    )
    database.session.add(registro)
    database.session.delete(diag)
    database.session.commit()
    
    if current_user.tipo == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.tipo == 'funcionario':
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
    else:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

# ---------------------------------------------------------------------------
# Upload de imagem para galeria
# ---------------------------------------------------------------------------
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
    
    registro = Registro(
        tipo='galeria',
        acao='Imagem da galeria enviada',
        descricao=f"Imagem '{filename}' enviada para a galeria por {current_user.nome}.",
        projeto_id=projeto_id
    )
    database.session.add(registro)
    database.session.commit()
    return "Upload concluído", 200

# ---------------------------------------------------------------------------
# Exclusão de imagem da galeria
# ---------------------------------------------------------------------------
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
        
    registro = Registro(
        tipo='galeria',
        acao='Imagem da galeria excluída',
        descricao=f"Imagem '{gal.nome}' removida da galeria por {current_user.nome}.",
        projeto_id=projeto_id
    )
    database.session.add(registro)
    database.session.delete(gal)
    database.session.commit()
    
    if current_user.tipo == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.tipo == 'funcionario':
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
    
    registro = Registro(
        tipo='comentario',
        acao='Comentário enviado',
        descricao=f"{current_user.nome} adicionou um comentário.",
        projeto_id=projeto_id
    )
    database.session.add(registro)
    database.session.commit()
    
    if current_user.tipo == 'admin':
        return redirect(url_for('admin.projeto_detalhe', id=projeto_id))
    elif current_user.tipo == 'funcionario':
        return redirect(url_for('funcionario.projeto_detalhe', projeto_id=projeto_id))
    else:
        return redirect(url_for('cliente_projeto_detalhe', projeto_id=projeto_id))

# ---------------------------------------------------------------------------
# Excluir comentário
# ---------------------------------------------------------------------------
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

# =============================================================================
# Ponto de entrada da aplicação
# =============================================================================
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)