from flask import request, redirect, url_for, render_template
from werkzeug.security import generate_password_hash
from models import Cliente, Usuario, database  

def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        empresa = request.form['empresa']
        senha = request.form['senha']
        confirmar = request.form['confirmar_senha']

        if senha != confirmar:
            return render_template('register.html', error="Senhas não conferem")

        if Usuario.query.filter_by(email=email).first():
            return render_template('register.html', error="E-mail já existe")

        senha_hash = generate_password_hash(senha)

        try:
            usuario = Usuario(
                nome=nome,
                email=email,
                senha=senha_hash,
                tipo="cliente",
                nivel=3
            )


            database.session.add(usuario)
            database.session.flush()  

            cliente = Cliente(
                usuario_id=usuario.id,
                empresa=empresa
            )


            database.session.add(cliente)

            database.session.commit()

            return redirect(url_for('login'))

        except Exception as e:
            database.session.rollback()
            return render_template('auth/register.html', error="Erro ao cadastrar usuário")

    return render_template('auth/register.html')