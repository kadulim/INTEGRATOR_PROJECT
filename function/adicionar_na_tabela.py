import os
from database import database
from models import Usuario, Admin, Cliente, Funcionario, Projeto, Equipes, Skill
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
                database.session.execute(text("ALTER TABLE projeto ADD COLUMN IF NOT EXISTS equipe_id INTEGER REFERENCES equipes(id)"))
                database.session.execute(text("ALTER TABLE projeto ADD COLUMN IF NOT EXISTS prioridade VARCHAR(20)"))
                database.session.execute(text("ALTER TABLE funcionario ADD COLUMN IF NOT EXISTS skills VARCHAR(255)"))
                database.session.execute(text("ALTER TABLE usuario ADD COLUMN IF NOT EXISTS nivel INTEGER"))
                database.session.commit()
            except:
                database.session.rollback()
                # Tentativa para MySQL (Local) - sem o IF NOT EXISTS
                # Projeto
                try: database.session.execute(text("ALTER TABLE projeto ADD COLUMN equipe_id INTEGER REFERENCES equipes(id)"))
                except: database.session.rollback()
                try: database.session.execute(text("ALTER TABLE projeto ADD COLUMN prioridade VARCHAR(20)"))
                except: database.session.rollback()
                # Funcionario
                try: database.session.execute(text("ALTER TABLE funcionario ADD COLUMN skills VARCHAR(255)"))
                except: database.session.rollback()
                # Usuario
                try: database.session.execute(text("ALTER TABLE usuario ADD COLUMN nivel INTEGER"))
                except: database.session.rollback()
                database.session.commit()
        except Exception as e:
            print(f"ℹ️  Nota: Colunas já existem ou erro ao atualizar: {e}")




        # ─── Seed: Admin ────────────────────────────────────────────────
        admin_email = os.getenv('ADMIN_EMAIL')
        if admin_email and not Usuario.query.filter_by(email=admin_email).first():
            usuario = Usuario(
                nome  = os.getenv('ADMIN_NOME'),
                email = admin_email,
                senha = generate_password_hash(os.getenv('ADMIN_SENHA')),
                tipo  = 'admin',
                nivel = 1
            )
            database.session.add(usuario)
            database.session.flush()

            admin = Admin(usuario_id=usuario.id, nivel='1')
            database.session.add(admin)
            database.session.commit()
            print("✅ Admin criado.")

        # ─── Seed: Clientes (CLIENTE_1_, CLIENTE_2_, …) ─────────────────
        i = 1
        while True:
            prefix = f'CLIENTE_{i}_'
            email  = os.getenv(f'{prefix}EMAIL')
            if not email:
                break

            if not Usuario.query.filter_by(email=email).first():
                u = Usuario(
                    nome  = os.getenv(f'{prefix}NOME'),
                    email = email,
                    senha = generate_password_hash(os.getenv(f'{prefix}SENHA')),
                    tipo  = 'cliente',
                    nivel = 3
                )
                database.session.add(u)
                database.session.flush()

                c = Cliente(
                    usuario_id = u.id,
                    empresa    = os.getenv(f'{prefix}EMPRESA')
                )
                database.session.add(c)
                database.session.commit()
                print(f"✅ Cliente {i} criado: {os.getenv(f'{prefix}NOME')}")
            else:
                print(f"ℹ️  Cliente {i} já existe: {email}")

            i += 1

        # ─── Seed: Funcionários (FUNC_1_, FUNC_2_, …) ───────────────────
        i = 1
        while True:
            prefix = f'FUNC_{i}_'
            email  = os.getenv(f'{prefix}EMAIL')
            if not email:
                break

            if not Usuario.query.filter_by(email=email).first():
                u = Usuario(
                    nome  = os.getenv(f'{prefix}NOME'),
                    email = email,
                    senha = generate_password_hash(os.getenv(f'{prefix}SENHA')),
                    tipo  = 'funcionario',
                    nivel = 2
                )
                database.session.add(u)
                database.session.flush()

                f = Funcionario(
                    usuario_id = u.id,
                    cargo      = os.getenv(f'{prefix}CARGO')
                )
                
                # Tratar Equipes
                equipes_str = os.getenv(f'{prefix}EQUIPES', '')
                if equipes_str:
                    for eq_nome in [e.strip() for e in equipes_str.split(',')]:
                        equipe = Equipes.query.filter_by(nome=eq_nome).first()
                        if not equipe:
                            equipe = Equipes(nome=eq_nome)
                            database.session.add(equipe)
                            database.session.flush()
                        f.lista_equipes.append(equipe)

                # Tratar Skills (M2M)
                skills_str = os.getenv(f'{prefix}SKILLS', '')
                if skills_str:
                    for sk_nome in [s.strip() for s in skills_str.split(',')]:
                        skill = Skill.query.filter_by(nome=sk_nome).first()
                        if not skill:
                            skill = Skill(nome=sk_nome)
                            database.session.add(skill)
                            database.session.flush()
                        f.lista_skills.append(skill)

                database.session.add(f)
                database.session.commit()
                print(f"✅ Funcionário {i} criado: {os.getenv(f'{prefix}NOME')}")
            else:
                print(f"ℹ️  Funcionário {i} já existe: {email}")

            i += 1

        # ─── Seed: Projetos (PROJETO_1_, PROJETO_2_, …) ─────────────────
        i = 1
        while True:
            prefix = f'PROJETO_{i}_'
            nome   = os.getenv(f'{prefix}NOME')
            if not nome:
                break

            if not Projeto.query.filter_by(nome=nome).first():
                cliente_email = os.getenv(f'{prefix}CLIENTE_EMAIL')
                equipe_nome   = os.getenv(f'{prefix}EQUIPE_NOME')

                _cliente = (Cliente.query.join(Usuario)
                            .filter(Usuario.email == cliente_email).first()
                            if cliente_email else None)
                
                _equipe = (Equipes.query.filter_by(nome=equipe_nome).first() 
                           if equipe_nome else None)

                p = Projeto(
                    nome           = nome,
                    descricao      = os.getenv(f'{prefix}DESCRICAO'),
                    status         = os.getenv(f'{prefix}STATUS'),
                    prazo          = os.getenv(f'{prefix}PRAZO'),
                    budget         = float(os.getenv(f'{prefix}BUDGET', 0)),
                    prioridade     = os.getenv(f'{prefix}PRIORIDADE'),
                    cliente_id     = _cliente.id if _cliente else None,
                    equipe_id      = _equipe.id  if _equipe  else None
                )
                database.session.add(p)
                database.session.commit()
                print(f"✅ Projeto {i} criado: {nome}")
            else:
                print(f"ℹ️  Projeto {i} já existe: {nome}")

            i += 1

        print("🚀 Seed concluído.")