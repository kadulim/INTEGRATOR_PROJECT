from flask import request, render_template, redirect, url_for
from werkzeug.security import check_password_hash
from flask_login import login_user
from sqlalchemy import or_
from models import User, Project, Client
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def logar():
    total_projetos = Project.query.count()
    total_clientes  = Client.query.count()
    projeto_destaque = Project.query.first()

    if request.method == 'POST':
        identificador = request.form['identificador']
        senha = request.form['senha']

        logging.info(f"Tentativa de login: {identificador}")

        user = User.query.filter(
            or_(User.email_user == identificador, User.name_user == identificador)
        ).first()

        if not user:
            logging.warning(f"Falha de login: Usuario nao encontrado ({identificador})")
            return render_template('auth/login.html', error="Usuário não encontrado",
                                 total_projetos=total_projetos, total_clientes=total_clientes,
                                 projeto_destaque=projeto_destaque)

        if not check_password_hash(user.password_user, senha):
            logging.warning(f"Falha de login: Senha incorreta ({identificador})")
            return render_template('auth/login.html', error="Senha incorreta",
                                 total_projetos=total_projetos, total_clientes=total_clientes,
                                 projeto_destaque=projeto_destaque)

        login_user(user)
        logging.info(f"Login bem-sucedido: {identificador} (Tipo: {user.type_user})")

        if user.type_user == 'admin':
            return redirect('/admin/')
        elif user.type_user == 'employee':
            return redirect(url_for('funcionario.dashboard'))
        else:
            return redirect(url_for('cliente_dashboard'))

    return render_template('auth/login.html',
                         total_projetos=total_projetos,
                         total_clientes=total_clientes,
                         projeto_destaque=projeto_destaque)
