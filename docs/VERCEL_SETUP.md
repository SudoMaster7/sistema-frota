# Checklist de Deploy na Vercel — Frota Globo

Este guia resume o que precisa estar configurado para o deploy funcionar na Vercel com Flask (Serverless Functions).

## 1) Repositório
- Garanta que o projeto Vercel está conectado ao repositório correto: `SudoMaster7/sistema-frota`.
- Se necessário, ajuste o remoto local:

```bash
git remote set-url origin https://github.com/SudoMaster7/sistema-frota.git
```

## 2) Arquivos de configuração
- Adapter WSGI para Vercel: veja [api/index.py](../api/index.py)
- Config da Vercel (functions + rotas + env): veja [vercel.json](../vercel.json)

Estrutura usada:
- `api/index.py` expõe o `app` do Flask para o runtime Python da Vercel.
- `vercel.json` mapeia todas as rotas para `api/index.py` e define `runtime: python3.11`.

## 3) Variáveis de ambiente na Vercel
Configure no painel do projeto (Project Settings → Environment Variables):
- `FLASK_ENV=production`
- `SECRET_KEY=<sua_chave_segura>`
- `DATABASE_URL=postgresql://usuario:senha@host:5432/frota_globo`
- (Opcional) `REDIS_URL=redis://usuario:senha@host:6379/0`

Observação: Sem `DATABASE_URL`, a app sobe com SQLite em memória (sem persistência). Em produção, use Postgres gerenciado (Neon, Supabase, Render, Railway).

## 4) Banco de Dados
- Crie o banco e usuário (exemplo local):

```sql
CREATE DATABASE frota_globo;
CREATE USER frota_user WITH PASSWORD 'sua_senha_segura';
GRANT ALL PRIVILEGES ON DATABASE frota_globo TO frota_user;
```

- Ajuste `DATABASE_URL` para o seu provedor gerenciado.
- Inicialize tabelas e admin (execute localmente apontando para o DB remoto):

```bash
# Inicialização simples
python init_db_simple.py

# OU inicialização completa com dados exemplo
python init_db.py
```

## 5) Deploy
- O deploy é disparado por push na `main`.
- Alternativa via CLI:

```bash
# dentro da pasta do projeto
vercel
vercel --prod
```

## 6) Troubleshooting
- Erro 500 (FUNCTION_INVOCATION_FAILED):
  - Verifique se `DATABASE_URL` e `SECRET_KEY` estão setados na Vercel.
  - Sem `REDIS_URL`, o sistema usa `CACHE_TYPE='simple'` (ok para iniciar).
  - Cheque logs de funções no dashboard da Vercel.

- Conexão ao Postgres
  - Teste a string de conexão localmente com `psycopg2` ou um cliente.
  - Confirme que o host/porta do provedor estão acessíveis pela Vercel.

## 7) Referências do projeto
- App Flask principal: [app.py](../app.py)
- Configurações de ambiente: [config.py](../config.py)
- Modelos ORM: [models.py](../models.py)
- Estilos (tema Globo): [static/css/style.css](../static/css/style.css)
- Templates: [templates/](../templates)

## 8) Pós-deploy
- Validar login e dashboard.
- Conferir métricas: veículos disponíveis, viagens em rota e viagens do dia.
- Se necessário, ajustar permissões de usuário e dados iniciais.

---

Última atualização: Jan/2026
