# 🧪 PROMPT — Phase 14D (Email Composer & Send)

Copiar/colar no agente (Playwright MCP) para implementar e testar a funcionalidade de composição e envio de emails.

---

Título: SendCraft Phase 14D — Email Composer & SMTP Send (UI + Tests)

Contexto:
- Adicionar um compositor de email (UI) e enviar via SMTP a partir de uma conta existente.
- Validar com Playwright MCP: compor e enviar de `geral@artnshine.pt` (ID 3) para `mmelo.deb@gmail.com`.

Tarefas de Implementação:
1) UI/Frontend
- Adicionar botão "Compor" no header do inbox (/emails/inbox/<account_id>)
- Implementar modal/página: From (readonly), To (multi), Subject, Body (TinyMCE/textarea), Attachments (opcional)
- Validação client-side de campos obrigatórios e emails

2) Backend/Rotas
- GET /emails/compose/<account_id> — render form
- POST /emails/send — processa envio
  - Campos: account_id, to[], subject, body_html, body_text, attachments (opcional)
  - Validar emails e obrigatórios
  - Enviar via SMTP conforme configuração da conta
  - Logging de sucesso/erro

3) Segurança
- Sanitização do HTML
- Limites básicos de tamanho/anexos (opcional nesta fase)
- Não logar conteúdo completo do email

Testes (Playwright MCP):
1) Abrir /emails/inbox/3
2) Clicar "Compor"
3) Preencher:
   - To: mmelo.deb@gmail.com
   - Subject: "SendCraft Test - Phase14D"
   - Body HTML: "<h1>✅ SendCraft</h1><p>Test Phase14D composer & send.</p>"
4) Clicar "Enviar" e aguardar toast de sucesso
5) Screenshot: composer-success.png
6) (Opcional) Abrir /logs ou /emails/sent (se existir) e validar registo

Success Criteria:
✅ Form abre e valida campos obrigatórios
✅ Envio via SMTP não causa crash e retorna feedback claro
✅ Toasts em PT-PT
✅ Screenshot de sucesso salva

Saídas:
- Screenshots em ~/Downloads/SendCraft-Testing/phase14D/screenshots/
- Report em ~/Downloads/SendCraft-Testing/phase14D/SendCraft-Phase14D-Composer-Report.md

Notas:
- Se SMTP rejeitar por credenciais/política, validar que a UI reporta o erro e continua utilizável.
- Anexos podem ser testados com 1 ficheiro pequeno (opcional), senão deixar para 14E.
