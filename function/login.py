from flask import request, render_template, redirect, url_for
from werkzeug.security import check_password_hash
from flask_login import login_user
from models import Usuario

def logar():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario:
            return render_template('login.html', error="Usuário não encontrado")

        if not check_password_hash(usuario.senha, senha):
            return render_template('login.html', error="Senha incorreta")

        if usuario.tipo != tipo:
            return render_template('login.html', error="Tipo inválido")

        login_user(usuario)

        if usuario.tipo == 'admin':
            return redirect('/admin')

        elif usuario.tipo == 'funcionario':
            return redirect('/funcionario')

        else:
            return redirect('/cliente')

    return render_template('auth/login.html')