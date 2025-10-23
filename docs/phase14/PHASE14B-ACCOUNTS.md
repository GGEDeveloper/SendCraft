# 📧 Phase 14B — Gestão de Contas (CRUD + IMAP/SMTP Test)

## Objetivo
Gerir contas por domínio, com encriptação de credenciais e testes IMAP/SMTP via UI.

## Requisitos Funcionais
- Listar contas com filtro por domínio e estado
- Criar/editar conta: domínio, local_part, display_name, servidores/portas, SSL/TLS, username/password
- Toggle ativo/inativo, delete seguro
- Teste IMAP/SMTP (handshake) a partir da UI (sem envio externo)

## Rotas
- GET /accounts — lista (filtros)
- GET/POST /accounts/new — criar
- GET/POST /accounts/{id}/edit — editar
- POST /accounts/{id}/toggle — alternar ativo
- POST /accounts/{id}/delete — remover (seguro)
- POST /accounts/{id}/test-imap — testar acesso IMAP
- POST /accounts/{id}/test-smtp — testar handshake SMTP

## Segurança
- Encriptar password com SECRET_KEY
- Nunca logar valores puros
- Botão "Mostrar/Ocultar" password no UI; "Gerar" senha forte

## Templates
- templates/accounts/list.html — tabela, filtros, ações
- templates/accounts/form.html — formulário completo

## Testes Manuais
- Criar conta válida
- Testar IMAP com logs (OK/erro amigável)
- Testar SMTP handshake
- Toggle ativo e delete seguro
