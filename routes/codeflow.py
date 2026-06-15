from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user

codeflow_bp = Blueprint('codeflow', __name__, url_prefix='/codeflow')


@codeflow_bp.route('/')
@codeflow_bp.route('/dashboard')
@login_required
def dashboard():
    from function.crypto import decrypt_token
    api_url = current_app.config.get('CODEFLOW_API_URL', 'http://localhost:5000')
    github_token = decrypt_token(current_app.config['SECRET_KEY'], current_user.github_key_user) if current_user.github_key_user else ''
    return render_template('admin/codeflow.html', api_url=api_url, github_token=github_token, active_page='codeflow')
