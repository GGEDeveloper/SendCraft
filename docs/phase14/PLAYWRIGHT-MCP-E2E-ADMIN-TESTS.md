# 🎭 Playwright MCP E2E — Phase 14 Admin Functional Testing

## Objetivo
Executar testes funcionais automáticos das áreas administrativas criadas na Phase 14 (Domínios, Contas, Acesso API) usando o Playwright MCP Server no agente local.

## Pré‑requisitos
- SendCraft a correr em http://localhost:5000
- Playwright MCP Server ativo e conectado ao agente
- Migração executada (migrations/add_api_fields.py)

## Plano de Testes (25–30 min)

### Configuração Inicial
- Browser: Chromium headed
- Viewport: 1440x900
- Diretório de evidências: ~/Downloads/SendCraft-Testing-Phase14/
- Subpasta screenshots: screenshots/
- Recolha de console errors e network logs

---

## PROMPT — Copy/Paste no agente (Playwright MCP)

```markdown
SendCraft Phase 14 Admin Functional Testing — Playwright MCP Automation

## Context:
Run automated functional tests for the new admin areas implemented in Phase 14:
- 14A: Domains CRUD
- 14B: Accounts CRUD + IMAP/SMTP tests
- 14C: API Access per Account (key lifecycle)

## Prerequisites:
- SendCraft running at http://localhost:5000
- Playwright MCP Server active
- Database migration executed (API fields added)

## Test Environment Setup (2 min)
- Launch Chromium in headed mode
- Set viewport to 1440x900
- Prepare folders:
  - ~/Downloads/SendCraft-Testing-Phase14/
  - ~/Downloads/SendCraft-Testing-Phase14/screenshots/

## Test Suite (20–25 min)

### A) Domains (14A) — CRUD + Search + Toggle (7–8 min)
1. Navigate to http://localhost:5000/domains
   - Wait for table to load
   - Screenshot: domains-list.png
2. Create domain:
   - Click "Novo Domínio" → fill:
     - Nome: test-domain.local
     - Descrição: Domínio de teste
     - Ativo: ON
   - Submit and wait for toast
   - Screenshot: domains-created.png
3. Search and filter:
   - Use search box to find "test-domain"
   - Toggle status to OFF, then ON
   - Screenshot: domains-search-toggle.png
4. Edit domain:
   - Open edit, change description
   - Save and wait for toast
   - Screenshot: domains-edited.png
5. Delete protection:
   - If domain has accounts, ensure delete is blocked with message
   - Screenshot: domains-delete-guard.png

### B) Accounts (14B) — CRUD + Encryption + Connectivity (9–10 min)
1. Navigate to http://localhost:5000/accounts
   - Screenshot: accounts-list.png
2. Create account for existing domain:
   - Click "Nova Conta" → fill:
     - Domínio: alitools.pt (or existing)
     - Local Part: testuser
     - Display Name: Test User
     - IMAP: server mail.domain.tld, port 993, SSL ON
     - SMTP: server mail.domain.tld, port 465, SSL ON
     - Username: testuser@domain.tld
     - Password: use "Gerar" then show/hide to verify UI
   - Submit and verify toast
   - Screenshot: accounts-created.png
3. Edit account:
   - Change display name
   - Save; screenshot: accounts-edited.png
4. Connectivity tests:
   - Click "Test IMAP" → wait for status (OK/Error)
   - Screenshot: accounts-imap-test.png
   - Click "Test SMTP" → wait for handshake status
   - Screenshot: accounts-smtp-test.png
5. Toggle & delete protection:
   - Toggle active state
   - Attempt delete; verify protection if inbox emails exist
   - Screenshot: accounts-delete-guard.png

### C) API Access (14C) — Enable + Generate + Test + Revoke (6–7 min)
1. Open API management:
   - http://localhost:5000/accounts/<id>/api
   - Screenshot: api-access-page.png
2. Enable API access and generate key:
   - Click "Ativar API" then "Gerar Chave"
   - Copy plaintext key shown once; store in memory for curl test
   - Screenshot: api-key-generated.png (mask part of key visually if needed)
3. Test endpoint with key:
   - Execute curl via agent:
     ```bash
     curl -s -X GET http://localhost:5000/api/v1/health \
          -H "Authorization: Bearer SC_copied_key" -i
     ```
   - Expect 200 OK with JSON
   - Save response summary in report
4. Revoke and re-test:
   - Click "Revogar Chave" → confirm
   - Repeat curl → expect 401 Unauthorized
   - Screenshot: api-key-revoked.png

## Mobile / Responsive Sanity (2 min)
- Set viewport 390x844
- Re-open each admin page quickly
- Screenshots:
  - domains-mobile.png
  - accounts-mobile.png
  - api-access-mobile.png

## Evidence & Report (2–3 min)
- Save all screenshots to ~/Downloads/SendCraft-Testing-Phase14/screenshots/
- Create report: ~/Downloads/SendCraft-Testing-Phase14/Phase14-Admin-E2E-Report.md
- Include:
  - Environment details (timestamp, browser)
  - PASS/FAIL checklist per section
  - Console errors summary (expected: none)
  - Network summary (key endpoints hit)
  - Screenshots index
  - Observations & recommendations

## Success Criteria
✅ Domains: CRUD, search, toggle, delete guard
✅ Accounts: CRUD, encryption UI, IMAP/SMTP tests, protections
✅ API Access: enable, key generate(test OK), revoke(test 401)
✅ Responsive checks OK
✅ No console errors, clean UX, PT-PT messages
✅ Email client unaffected by admin changes

Execute the full suite and provide the final Markdown report and all screenshots.
```

---

## Saídas Esperadas
- Pasta: `~/Downloads/SendCraft-Testing-Phase14/`
  - `Phase14-Admin-E2E-Report.md`
  - `screenshots/` com ~12–18 imagens
- Logs: resumo de console errors (ideal: 0)
- cURL results no relatório (200 OK e 401 após revoke)

## Dicas
- Se o IMAP/SMTP não puder autenticar, o teste deve reportar "Erro amigável" e não quebrar
- Chaves de API: não expor completo nos screenshots; mostrar masked
- Confirmar que o email client (/emails/inbox) continua estável após as mudanças
