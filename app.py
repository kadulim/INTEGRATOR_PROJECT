from flask import Flask, render_template, abort, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user, logout_user
import functools

from database import database
from models import Usuario

import function.login as logar
import function.register as registrar

app = Flask(__name__)

app.config['SECRET_KEY'] = 'cobyte'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/database_cobyte'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

database.init_app(app)

lm = LoginManager(app)
lm.login_view = 'home'


# Decorator por nível
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


# User loader
@lm.user_loader
def user_loader(id):
    return database.session.get(Usuario, int(id))


# Rota Login (home)
@app.route('/', methods=['GET', 'POST'])
def page_login():
    return logar.logar()


# Rota Register
@app.route('/register', methods=['GET', 'POST'])
def page_register():
    return registrar.register()


# Rota Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# Rota Cliente
@app.route('/cliente')
@login_required
def cliente():
    return render_template('cliente/client.html')

# Rota Funcionario
@app.route('/funcionario')
@login_required
def funcionario():
    return render_template('cliente/client.html')

# Rota Admin
@app.route('/admin')
@login_required_nivel(3)
def admin():
    return render_template('admin/dashboard.html')

if __name__ == '__main__':
    with app.app_context():
        database.create_all()
    app.run(debug=True)