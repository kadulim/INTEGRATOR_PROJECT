from flask import request, render_template, redirect, url_for
from werkzeug.security import check_password_hash
from flask_login import login_user
from models import Usuario
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def logar():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        logging.info(f"Tentativa de login: {email}")

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario:
            logging.warning(f"Falha de login: Usuário não encontrado ({email})")
            return render_template('auth/login.html', error="Usuário não encontrado")

        if not check_password_hash(usuario.senha, senha):
            logging.warning(f"Falha de login: Senha incorreta ({email})")
            return render_template('auth/login.html', error="Senha incorreta")

        login_user(usuario)
        logging.info(f"Login bem-sucedido: {email} (Tipo: {usuario.tipo})")

        if usuario.tipo == 'admin':
            logging.warning(f"entrou no admin ({email})")
            return redirect('/admin/')

        elif usuario.tipo == 'funcionario':
            logging.warning(f"entrou no funcionario ({email})")
            return redirect('/funcionario')

        else:
            logging.warning(f"entrou no cliente ({email})")
            return redirect('/cliente-dashboard')

    return render_template('auth/login.html')