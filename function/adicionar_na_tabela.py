import os
from database import database
from models import User, Admin, Client, Employee, Project, Team, Skill, Requirement, Log, project_teams
from werkzeug.security import generate_password_hash


def adicionar(app):
    """Popula o banco com os dados definidos no .env. Recebe o app Flask como argumento."""

    with app.app_context():
        database.create_all()

        # --- Verificação de colunas (Postgres e MySQL) ---
        try:
            from sqlalchemy import text
            # Tentativa para Postgres (Render)
            try:
                database.session.execute(text("ALTER TABLE projeto ADD COLUMN IF NOT EXISTS prioridade VARCHAR(20)"))
                database.session.execute(text("ALTER TABLE requisito ADD COLUMN IF NOT EXISTS tipo VARCHAR(50)"))
                database.session.execute(text("ALTER TABLE funcionario ADD COLUMN IF NOT EXISTS skills VARCHAR(255)"))
                database.session.execute(text("ALTER TABLE usuario ADD COLUMN IF NOT EXISTS nivel INTEGER"))
                database.session.execute(text("ALTER TABLE equipes ADD COLUMN IF NOT EXISTS descricao VARCHAR(250) DEFAULT ''"))
                database.session.execute(text("ALTER TABLE equipes ADD COLUMN IF NOT EXISTS funcao VARCHAR(250) DEFAULT ''"))
                database.session.execute(text("ALTER TABLE equipes ADD COLUMN IF NOT EXISTS lider_equipe INTEGER"))
                database.session.commit()
            except:
                database.session.rollback()
                # Tentativa para MySQL (Local) - sem o IF NOT EXISTS
                try: database.session.execute(text("ALTER TABLE projeto ADD COLUMN prioridade VARCHAR(20)"))
                except: database.session.rollback()
                try: database.session.execute(text("ALTER TABLE requisito ADD COLUMN tipo VARCHAR(50)"))
                except: database.session.rollback()
                try: database.session.execute(text("ALTER TABLE funcionario ADD COLUMN skills VARCHAR(255)"))
                except: database.session.rollback()
                try: database.session.execute(text("ALTER TABLE usuario ADD COLUMN nivel INTEGER"))
                except: database.session.rollback()
                try: database.session.execute(text("ALTER TABLE equipes ADD COLUMN descricao VARCHAR(250) DEFAULT ''"))
                except: database.session.rollback()
                try: database.session.execute(text("ALTER TABLE equipes ADD COLUMN funcao VARCHAR(250) DEFAULT ''"))
                except: database.session.rollback()
                try: database.session.execute(text("ALTER TABLE equipes ADD COLUMN lider_equipe INTEGER"))
                except: database.session.rollback()
                database.session.commit()
        except Exception as e:
            print(f"[INFO] Nota: Colunas ja existem ou erro ao atualizar: {e}")

        # ─── Seed: Admin ────────────────────────────────────────────────
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_nome = os.getenv('ADMIN_NOME')
        if admin_email and not User.query.filter_by(email_user=admin_email).first() and admin_nome and not User.query.filter_by(name_user=admin_nome).first():
            user = User(
                name_user     = admin_nome,
                email_user    = admin_email,
                password_user = generate_password_hash(os.getenv('ADMIN_SENHA')),
                type_user     = 'admin',
            )
            database.session.add(user)
            database.session.flush()

            admin = Admin(fk_user=user.pk_id_user, level_admin=1)
            database.session.add(admin)
            database.session.commit()
            print("[OK] Admin criado.")

        print("[OK] Seed concluido (apenas admin via .env).")
