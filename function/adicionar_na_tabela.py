import os
from database import database
from models import User, Admin, Client, Employee, Project, Team, Skill, Requirement, Log, project_teams
from werkzeug.security import generate_password_hash


def adicionar(app):
    """Popula o banco com os dados definidos no .env. Recebe o app Flask como argumento."""

    with app.app_context():
        database.create_all()

        # --- Migração de colunas (tenta nomes novos e antigos) ---
        from sqlalchemy import text

        def _try(sql):
            try:
                database.session.execute(text(sql))
                database.session.commit()
            except Exception:
                database.session.rollback()

        # Tabela project / projeto
        _try("ALTER TABLE project ADD COLUMN prioridade VARCHAR(20)")
        _try("ALTER TABLE projeto ADD COLUMN prioridade VARCHAR(20)")
        # Tabela requirement / requisito
        _try("ALTER TABLE requirement ADD COLUMN tipo VARCHAR(50)")
        _try("ALTER TABLE requisito ADD COLUMN tipo VARCHAR(50)")
        # Tabela employee / funcionario
        _try("ALTER TABLE employee ADD COLUMN skills VARCHAR(255)")
        _try("ALTER TABLE funcionario ADD COLUMN skills VARCHAR(255)")
        # Tabela team / equipes
        _try("ALTER TABLE team ADD COLUMN descricao VARCHAR(250) DEFAULT ''")
        _try("ALTER TABLE equipes ADD COLUMN descricao VARCHAR(250) DEFAULT ''")
        _try("ALTER TABLE team ADD COLUMN funcao VARCHAR(250) DEFAULT ''")
        _try("ALTER TABLE equipes ADD COLUMN funcao VARCHAR(250) DEFAULT ''")
        _try("ALTER TABLE team ADD COLUMN lider_equipe INTEGER")
        _try("ALTER TABLE equipes ADD COLUMN lider_equipe INTEGER")
        # Tabela admin
        _try("ALTER TABLE admin ADD COLUMN IF NOT EXISTS fk_user INTEGER")
        _try("ALTER TABLE admin ADD COLUMN fk_user INTEGER")
        _try("ALTER TABLE admin ADD COLUMN IF NOT EXISTS level_admin INTEGER DEFAULT 1")
        _try("ALTER TABLE admin ADD COLUMN level_admin INTEGER DEFAULT 1")
        # Tabela user / usuario
        _try("ALTER TABLE user ADD COLUMN nivel INTEGER")
        _try("ALTER TABLE usuario ADD COLUMN nivel INTEGER")

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
