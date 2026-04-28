# 🚀 INTEGRATOR PROJECT - CoByte

Este repositório contém o sistema de gerenciamento interno da CoByte, desenvolvido com **Flask**, **SQLAlchemy** e um design focado em experiência premium.

---

## 📋 Pré-requisitos

- **Python 3.x**
- **MySQL** (Local) ou **PostgreSQL** (Produção/Render)
- **Git**

---

## 🛠️ Instalação e Configuração

### 1. Clonar e Acessar
```bash
git clone <url-do-repositorio>
cd INTEGRATOR_PROJECT
```

### 2. Ambiente Virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### 3. Dependências
```bash
pip install -r requirements.txt
```

### 4. Variáveis de Ambiente (`.env`)
Crie um arquivo `.env` na raiz do projeto (ele já está configurado no `.gitignore`). Exemplo:

```env
# Banco de Dados
# MySQL: mysql+pymysql://root:senha@localhost/database_cobyte
# Postgres (Render): postgresql://usuario:senha@host/banco
DATABASE_URL=mysql+pymysql://root:@localhost/database_cobyte
SECRET_KEY=sua_chave_secreta

# Admin Inicial
ADMIN_NOME=Admin
ADMIN_EMAIL=admin@gmail.com
ADMIN_SENHA=admin123
```

---

## 🔐 Níveis de Acesso

O sistema utiliza uma hierarquia de níveis para controle de permissões:

| Nível | Tipo | Descrição |
| :--- | :--- | :--- |
| **1** | **Admin** | Acesso total ao dashboard administrativo e gerenciamento. |
| **2** | **Funcionário** | Acesso às ferramentas de trabalho e equipe. |
| **3** | **Cliente** | Acesso ao painel de acompanhamento de projetos. |

---

## 🚀 Execução

Para iniciar o servidor e criar o banco de dados automaticamente (Seed):

```bash
python app.py
```

O sistema detectará se está rodando localmente (MySQL) ou em produção (PostgreSQL no Render) e aplicará as migrações e o seed de dados definidos no seu `.env`.

---

## 🌐 Deploy (Render)

Este projeto está pronto para deploy no **Render**. 
- O banco de dados recomendado é o **PostgreSQL**.
- O arquivo `requirements.txt` já inclui o `gunicorn` e o `psycopg2-binary`.
- O script de seed (`adicionar_na_tabela.py`) possui lógica para atualizar colunas automaticamente no Postgres.

---

## 📄 Licença
Desenvolvido para o Projeto Integrador CoByte.
