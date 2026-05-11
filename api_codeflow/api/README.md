# CodeFlow API

API Flask para análise de arquitetura de código. Transforma o CodeFlow em um serviço REST.

## Endpoints

### `GET /api/health`
Health check da API.

### `POST /api/analyze`
Analisa um repositório GitHub.

```json
{ "repo": "owner/repo" }
```
ou
```json
{ "repo": "https://github.com/owner/repo" }
```

### `POST /api/analyze/local`
Analisa um diretório local.

```json
{ "path": "/caminho/absoluto/para/o/projeto" }
```

### `POST /api/analyze/upload`
Upload de arquivos para análise (multipart/form-data).

## Como usar

```bash
cd api
pip install -r requirements.txt
cp .env.example .env
python3 run.py
```

Acesse: `http://localhost:5000/api/health`
