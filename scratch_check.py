from app import app
from database import database
from models import Usuario, Cliente, Projeto, Equipes

with app.app_context():
    print("--- USUARIOS ---")
    for u in Usuario.query.all():
        print(f"ID: {u.id}, Nome: {u.nome}, Email: {u.email}, Tipo: {u.tipo}")
        
    print("\n--- CLIENTES ---")
    for c in Cliente.query.all():
        print(f"ID: {c.id}, Usuario ID: {c.usuario_id}, Empresa: {c.empresa}, Nome: {c.usuario_rel.nome}")
        
    print("\n--- PROJETOS ---")
    for p in Projeto.query.all():
        equipes_nomes = ', '.join([eq.nome for eq in p.lista_equipes]) if p.lista_equipes else 'Nenhuma'
        print(f"ID: {p.id}, Nome: {p.nome}, Cliente ID: {p.cliente_id}, Equipes: {equipes_nomes}")
