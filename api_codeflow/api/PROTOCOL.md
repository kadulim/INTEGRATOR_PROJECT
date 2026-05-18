# Protocolo da API CodeFlow

## Base URL
```
http://localhost:5000/api
```

## Autenticação
Para analisar repositórios privados, configure o token no `.env`:
```
GITHUB_TOKEN=seu_token_aqui
```

## Resposta Padrão (sucesso)
Todas as respostas são JSON. Estrutura:
```json
{
  "stats": {
    "files": 63,
    "functions": 470,
    "loc": 11352,
    "languages": { "javascript": { "files": 10, "loc": 200 } },
    "layers": { "utils": { "files": 5, "functions": 10, "loc": 50 } }
  },
  "health": { "score": 85, "grade": "B", "level": "good" },
  "security_issues": [],
  "patterns": [],
  "circular_dependencies": [],
  "dead_functions": [],
  "dependency_map": {},
  "files": [],
  "repository": "owner/repo"
}
```

## Códigos de Erro
| Status | Significado |
|--------|------------|
| 200 | Sucesso |
| 400 | Requisição inválida (parâmetros faltando) |
| 500 | Erro interno do servidor |
