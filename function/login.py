from flask import request, render_template, redirect, url_for
from werkzeug.security import check_password_hash
from flask_login import login_user
from sqlalchemy import or_
from models import Usuario, Projeto, Cliente
import logging



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def logar():
    # Estatísticas dinâmicas para a tela de login
    total_projetos = Projeto.query.count()
    total_clientes = Cliente.query.count()
    projeto_destaque = Projeto.query.first()

    if request.method == 'POST':
        identificador = request.form['identificador']
        senha = request.form['senha']

        logging.info(f"Tentativa de login: {identificador}")

        # Busca por email OU nome de usuário
        usuario = Usuario.query.filter(
            or_(Usuario.email == identificador, Usuario.nome == identificador)
        ).first()

        if not usuario:
            logging.warning(f"Falha de login: Usuário não encontrado ({identificador})")
            return render_template('auth/login.html', error="Usuário não encontrado", 
                                 total_projetos=total_projetos, total_clientes=total_clientes,
                                 projeto_destaque=projeto_destaque)

        if not check_password_hash(usuario.senha, senha):
            logging.warning(f"Falha de login: Senha incorreta ({identificador})")
            return render_template('auth/login.html', error="Senha incorreta",
                                 total_projetos=total_projetos, total_clientes=total_clientes,
                                 projeto_destaque=projeto_destaque)
            

        login_user(usuario)
        logging.info(f"Login bem-sucedido: {identificador} (Tipo: {usuario.tipo})")
        
        
        

        if usuario.tipo == 'admin':
            logging.warning(f"entrou no admin ({identificador})")
            return redirect('/admin/')

        elif usuario.tipo == 'funcionario':
            logging.warning(f"entrou no funcionario ({identificador})")
            return redirect('/funcionario')

        else:
            logging.warning(f"entrou no cliente ({identificador})")
            return redirect('/cliente-dashboard')

    return render_template('auth/login.html', 
                         total_projetos=total_projetos, 
                         total_clientes=total_clientes,
                         projeto_destaque=projeto_destaque)