import os
from database import database
from models import Usuario, Admin, Cliente, Funcionario, Projeto
from werkzeug.security import generate_password_hash


def adicionar(app):
    """Popula o banco com os dados definidos no .env. Recebe o app Flask como argumento."""

    with app.app_context():
        database.create_all()

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
                    nivel = 0
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
                    nivel = 0
                )
                database.session.add(u)
                database.session.flush()

                f = Funcionario(
                    usuario_id = u.id,
                    cargo      = os.getenv(f'{prefix}CARGO'),
                    salario    = float(os.getenv(f'{prefix}SALARIO', 0))
                )
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
                func_email    = os.getenv(f'{prefix}FUNC_EMAIL')

                _cliente     = (Cliente.query.join(Usuario)
                                .filter(Usuario.email == cliente_email).first()
                                if cliente_email else None)
                _funcionario = (Funcionario.query.join(Usuario)
                                .filter(Usuario.email == func_email).first()
                                if func_email else None)

                p = Projeto(
                    nome           = nome,
                    descricao      = os.getenv(f'{prefix}DESCRICAO'),
                    status         = os.getenv(f'{prefix}STATUS'),
                    prazo          = os.getenv(f'{prefix}PRAZO'),
                    budget         = float(os.getenv(f'{prefix}BUDGET', 0)),
                    prioridade     = os.getenv(f'{prefix}PRIORIDADE'),
                    cliente        = Usuario.query.get(_cliente.usuario_id).nome if _cliente else '',
                    funcionario    = Usuario.query.get(_funcionario.usuario_id).nome if _funcionario else '',
                    cliente_id     = _cliente.id    if _cliente    else None,
                    funcionario_id = _funcionario.id if _funcionario else None
                )
                database.session.add(p)
                database.session.commit()
                print(f"✅ Projeto {i} criado: {nome}")
            else:
                print(f"ℹ️  Projeto {i} já existe: {nome}")

            i += 1

        print("🚀 Seed concluído.")