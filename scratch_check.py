from app import app
from database import database
from models import User, Client, Project, Team

with app.app_context():
    print("--- USUARIOS ---")
    for u in User.query.all():
        print(f"ID: {u.pk_id_user}, Nome: {u.name_user}, Email: {u.email_user}, Tipo: {u.type_user}")
        
    print("\n--- CLIENTES ---")
    for c in Client.query.all():
        print(f"ID: {c.pk_id_client}, Usuario ID: {c.fk_user}, Empresa: {c.company_client}, Nome: {c.user.name_user}")
        
    print("\n--- PROJETOS ---")
    for p in Project.query.all():
        equipes_nomes = ', '.join([eq.name_team for eq in p.teams]) if p.teams else 'Nenhuma'
        print(f"ID: {p.pk_id_project}, Nome: {p.name_project}, Cliente ID: {p.fk_client}, Equipes: {equipes_nomes}")
