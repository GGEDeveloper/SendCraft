# 🎭 Playwright MCP — Phase 14 Functional UI Testing Runner

## 🎯 Objetivo
Executar testes funcionais end‑to‑end no browser (Chromium) usando o MCP Server do Playwright para validar as 3 áreas administrativas:
- 14A Domínios (CRUD)
- 14B Contas (CRUD + IMAP/SMTP tests)
- 14C API Access (enable/disable + key lifecycle)

Outputs:
- Screenshots: ~/Downloads/SendCraft-Testing/phase14/screenshots/
- Report Markdown: ~/Downloads/SendCraft-Testing/phase14/SendCraft-Phase14-Functional-Report.md
- Console & Network logs no relatório

## ✅ Pré‑requisitos
- Servidor dev ativo em http://localhost:5000
- Playwright MCP Server ligado
- MySQL remoto acessível
- Migração `add_api_fields.py` aplicada

## 🧾 Prompt (copiar/colar no agent com MCP Playwright)

```markdown
SendCraft Phase 14 Functional UI Testing — Playwright MCP Automation

## Context:
Validate Phase 14 admin areas (Domains, Accounts, API Access) with end-to-end functional testing in Chromium via Playwright MCP. Record screenshots, console logs, and network summaries. Produce a comprehensive Markdown report.

## Environment:
- Base URL: http://localhost:5000
- Output dir: ~/Downloads/SendCraft-Testing/phase14/
- Screenshots dir: ~/Downloads/SendCraft-Testing/phase14/screenshots/
- Viewport: 1440x900 desktop + 390x844 mobile

## Phase A — Domains (14A)
1) Navigate to /domains
   - Wait for page load
   - Screenshot: domains-list.png
   - Verify search box present and functional
   - Create domain: `playwright-test.com` (Active)
     - Navigate: /domains/new
     - Fill: name, description; set active
     - Submit; expect toast success
     - Screenshot: domain-created.png
   - Search for `playwright-test.com` and verify appears
     - Screenshot: domain-search.png
   - Toggle active/inactive state
     - Screenshot: domain-toggle.png
   - Edit description
     - Screenshot: domain-edit.png
   - Attempt delete (if protected by accounts, expect error toast)
     - Screenshot: domain-delete-attempt.png

Assertions:
- Search filters results
- Toggle changes visual state
- Edit persists changes
- Delete protection works (or delete succeeds if allowed)

## Phase B — Accounts (14B)
1) Navigate to /accounts
   - Screenshot: accounts-list.png
   - Create new account under `playwright-test.com`
     - /accounts/new
     - Select domain, local_part: `tester` (email: tester@playwright-test.com)
     - Fill SMTP + IMAP servers/ports (use same host: mail.artnshine.pt for test)
     - SSL/TLS ON for both; username tester@playwright-test.com; generate password (placeholder if no real auth)
     - Screenshot: account-form.png
     - Submit; expect toast success
     - Screenshot: account-created.png
   - Show/Hide password buttons work
   - Test IMAP button → expect JSON/status toast (OK or failure with message)
     - Screenshot: imap-test.png
   - Test SMTP button → expect JSON/status toast
     - Screenshot: smtp-test.png
   - Toggle active/inactive
     - Screenshot: account-toggle.png

Assertions:
- Account appears in list filtered by domain
- Password controls (show/hide/generate) respond
- IMAP/SMTP buttons return status without UI errors
- Toggle updates state

## Phase C — API Access (14C)
1) Navigate to /accounts/<new_account_id>/api
   - Screenshot: api-access-page.png
   - Enable API access → expect toggle state change
   - Generate API key → display key once, copy to clipboard
     - Screenshot: api-key-generated.png (mask key on image if needed)
   - Test endpoint with curl (health) using the generated key
     - Record response in report
   - Rotate key → expect previous invalid; new shown once
     - Screenshot: api-key-rotated.png
   - Revoke key → test endpoint again, expect 401
     - Screenshot: api-key-revoked.png

Assertions:
- API enable/disable reflects in UI
- Key shown once then masked
- Health endpoint accepts Bearer key; rejects after revoke

## Mobile Check
- Set viewport to 390x844
- Navigate to /domains and /accounts
- Capture: domains-mobile.png, accounts-mobile.png
- Validate responsive layout

## Evidence & Report
- Save ALL screenshots to screenshots dir
- Collect console errors/warnings
- Summarize network calls (counts, key endpoints)
- Generate report: SendCraft-Phase14-Functional-Report.md with:
  - Environment summary
  - Step-by-step results (PASS/FAIL)
  - Screenshots index
  - Console messages
  - Network summary
  - Issues & recommendations

## Success Criteria
✅ CRUD domains fully functional
✅ CRUD accounts + IMAP/SMTP tests operational (status shown)
✅ API access enable/generate/rotate/revoke functional
✅ Zero critical console errors
✅ Responsive design intact
✅ Report and screenshots generated
```

## 📝 Notas
- Se IMAP/SMTP falharem por credenciais não reais, validar que UI retorna estado amigável sem quebrar
- Não expor a chave gerada nos logs; no report registrar apenas “copiada” e passo bem-sucedido
- Se delete de domínio bloquear, validar a mensagem (é o esperado quando há contas)
