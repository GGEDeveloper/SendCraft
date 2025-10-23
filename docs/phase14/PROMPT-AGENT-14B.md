# 🧪 PROMPT — Phase 14B (Contas)

Copiar/colar no agente para implementar contas por domínio e testes IMAP/SMTP.

---

Título: SendCraft Phase 14B — Email Accounts Management (CRUD + Tests)

Contexto:
- Implementar UI e rotas para gerir contas de email, com encriptação e testes de conectividade IMAP/SMTP via UI.
- UX consistente com projeto; não quebrar sync existente.

Tarefas:
1) Rotas Flask
- GET /accounts — lista com filtros por domínio
- GET/POST /accounts/new — criar
- GET/POST /accounts/<id>/edit — editar
- POST /accounts/<id>/toggle — ativar/desativar
- POST /accounts/<id>/delete — remover (bloquear se tiver emails vinculados; ou soft delete)
- POST /accounts/<id>/test-imap — tenta login com timeout (60s)
- POST /accounts/<id>/test-smtp — handshake SMTP (sem envio)

2) Templates
- templates/accounts/list.html — tabela, filtros, ações
- templates/accounts/form.html — formulário completo (domínio, local_part, display_name, servidores, portas, SSL/TLS, username, password)
- Password: botões Mostrar/Ocultar e Gerar

3) Segurança/Back-end
- Encriptação com SECRET_KEY
- Nunca logar plain password
- Mensagens PT-PT com toasts

4) Testes Manuais
- Criar conta válida
- Testar IMAP e SMTP (logs OK/erro)
- Toggle ativo e delete seguro
- Screenshots + mini relatório

Critérios de aceitação:
- CRUD de contas funcional
- Testes IMAP/SMTP retornam status amigável
- Inbox/sync permanece estável
