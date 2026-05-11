from flask import Blueprint, render_template, current_app
from flask_login import login_required

codeflow_bp = Blueprint('codeflow', __name__, url_prefix='/codeflow')


@codeflow_bp.route('/')
@codeflow_bp.route('/dashboard')
@login_required
def dashboard():
    api_url = current_app.config.get('CODEFLOW_API_URL', 'http://localhost:5000')
    return render_template('admin/codeflow.html', api_url=api_url, active_page='codeflow')
