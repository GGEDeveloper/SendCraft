# Vercel deployment configuration for SendCraft (Flask)

## Overview
Este diretório contém os ficheiros necessários para fazer deploy do SendCraft no Vercel usando `@vercel/python`.

### Arquivos chave
- `vercel.json`: Configuração do Vercel (builds e routes) apontando para `wsgi.py`
- `runtime.txt`: Versão do Python (3.11.6)
- `build.sh`: Script de build (instala dependências)

## Passos de Deploy

1) Pré-requisitos
- Conta Vercel ativa
- Vercel CLI instalado (`npm i -g vercel`)
- Acesso ao repositório GitHub

2) Importar o projeto no Vercel
- Dashboard Vercel → New Project → Import Git Repository
- Selecionar `GGEDeveloper/SendCraft`

3) Definir Environment Variables
Na aba "Settings" → "Environment Variables", adicionar:

Obrigatórias (Produção):
- `FLASK_ENV=production`
- `SECRET_KEY=***`
- `SQLALCHEMY_DATABASE_URI=mysql+pymysql://USER:PASSWORD@HOST:3306/DBNAME`
- `MAIL_SERVER=smtp.alitools.pt`
- `MAIL_PORT=587`
- `MAIL_USE_TLS=true`
- `MAIL_USE_SSL=false`
- `MAIL_USERNAME=geral@artnshine.pt`
- `MAIL_PASSWORD=***`
- `DEFAULT_SENDER=SendCraft <geral@artnshine.pt>`

Opcional (CORS):
- `CORS_ORIGINS=*`

4) Build & Deploy
- O Vercel detetará `vercel.json` e usará `@vercel/python`
- Entrypoint: `wsgi.py`
- No primeiro deploy, ver logs para confirmar: `SendCraft iniciado em modo production`

5) Testes pós-deploy
- `GET /api/v1/health` → deve responder 200
- `POST /api/v1/send` com API Key válida
- Aceder UI: `/` (dashboard)

## Notas
- Vercel usa ambiente serverless; conexões persistentes a MySQL devem usar connection pooling (SQLAlchemy já gerido). Se ocorrer "MySQL server has gone away", ajustar `SQLALCHEMY_POOL_RECYCLE=280` e `SQLALCHEMY_POOL_PRE_PING=true` via ENV.
- Para logs persistentes, integrar com um serviço de logging externo.
