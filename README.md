# 🚀 Configuração do Banco de Dados - CoByte

Este guia explica como configurar e inicializar o banco de dados do projeto em um novo ambiente (outro computador).

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

1.  **Python 3.x**
2.  **MySQL Server** (ou outro banco de dados compatível com SQLAlchemy)
3.  **Git** (para clonar o repositório)

---

## 🛠️ Passo a Passo

### 1. Clonar o Repositório
Abra o terminal no novo computador e clone o projeto:
```bash
git clone <url-do-repositorio>
cd INTEGRATOR_PROJECT
```

### 2. Criar um Ambiente Virtual (Opcional, mas Recomendado)
```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependências
Instale as bibliotecas necessárias listadas no `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Configurar o MySQL
Abra o seu cliente MySQL (MySQL Workbench, terminal, etc.) e crie o banco de dados:
```sql
CREATE DATABASE database_cobyte;
```

### 5. Configurar o Arquivo `.env`
O projeto utiliza um arquivo `.env` para gerenciar as configurações. 
1. Crie um arquivo chamado `.env` na raiz do projeto.
2. Adicione as configurações de conexão e os dados iniciais (Seed). 

**Exemplo de conteúdo para o `.env`:**
```env
# Configurações do Banco de Dados
# Formato: mysql+pymysql://usuario:senha@localhost/nome_do_banco
DATABASE_URL=mysql+pymysql://root:sua_senha@localhost/database_cobyte
SECRET_KEY=sua_chave_secreta_aqui

# Dados do Administrador Inicial
ADMIN_NOME=Admin
ADMIN_EMAIL=admin@cobyte.com
ADMIN_SENHA=admin123

# Exemplo de Cliente para Seed
CLIENTE_1_NOME=Empresa X
CLIENTE_1_EMAIL=contato@empresax.com
CLIENTE_1_SENHA=cliente123
CLIENTE_1_EMPRESA=Empresa X Tech

# Exemplo de Funcionário para Seed
FUNC_1_NOME=João Silva
FUNC_1_EMAIL=joao@cobyte.com
FUNC_1_SENHA=func123
FUNC_1_CARGO=Desenvolvedor Fullstack
FUNC_1_SKILLS=Python, Flask, MySQL
FUNC_1_EQUIPES=Desenvolvimento, Inovação
```

> [!IMPORTANT]
> Certifique-se de que o usuário e a senha no `DATABASE_URL` correspondem às suas credenciais do MySQL local.

### 6. Inicializar o Banco de Dados
O projeto está configurado para **criar as tabelas automaticamente** e inserir os dados iniciais (Seed) na primeira vez que o servidor for executado.

Basta rodar o comando:
```bash
python app.py
```

Ao iniciar, você verá mensagens no terminal confirmando a criação do Admin, Clientes e Funcionários.

---

## 🔍 Verificação
Após rodar o `app.py`, você pode acessar seu banco de dados MySQL e verificar se as tabelas (`usuario`, `funcionario`, `projeto`, etc.) foram criadas corretamente e se os dados do `.env` foram inseridos.

---

## 🚀 Próximos Passos
Agora o sistema está pronto para uso! Acesse `http://127.0.0.1:5000` no seu navegador.
