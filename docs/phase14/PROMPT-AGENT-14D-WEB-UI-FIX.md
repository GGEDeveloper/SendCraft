# 🛠️ Prompt — Corrigir SMTP na UI + Suporte a Anexos (Phase 14D)

Copiar/colar no agente com Playwright MCP ativo. Este prompt aplica as correções na UI/Backend para:
- Decriptação de password consistente com CLI (resolver "Failed to decrypt password")
- Envio por SMTP via UI (resolver 550 AUTH na porta 465)
- Suporte a anexos no composer (upload + envio)
- Testes E2E no browser e relatório final

---

Título: SendCraft Phase 14D — Fix Web UI SMTP Auth + Attachments (Implement + Test)

Contexto:
- Enviar email via UI está a falhar com "SMTP AUTH is required..." e logs "Failed to decrypt password".
- Via CLI o envio funciona: a UI e o serviço de envio precisam de alinhar a decriptação e autenticação.
- Anexos não funcionam no composer; é necessário implementar multipart/form-data e processamento no backend.

Objetivos:
1) Usar exatamente o mesmo método de decriptação que o CLI (EmailAccount.get_password(SECRET_KEY)) na rota/serviço de envio
2) Garantir que a password é carregada/decriptada no momento do envio (não depender de variável global)
3) Ajustar o composer para multipart/form-data quando houver anexos, e usar FormData no JS
4) Implementar leitura de request.files no backend e anexar ao MIME
5) Mensagens PT-PT claras e toasts amigáveis
6) Testes E2E com Playwright MCP (sem e com anexos)

Tarefas técnicas:
1) Backend — Serviço de Envio (/emails/send)
- No ponto onde é feita a autenticação SMTP, obter a password via:
  - from flask import current_app as app
  - decrypted = account.get_password(app.config['SECRET_KEY'])
  - Validar: se decrypted estiver vazio → abortar com 400 e toast "Password SMTP não configurada".
- Garantir flags coerentes: porta 465 → smtp_use_ssl=True e smtp_use_tls=False
- Construção do email (MIME):
  - Usar EmailMessage (ou MIMEMultipart)
  - Incluir body_html e body_text (fallback)
  - Iterar request.files.getlist('attachments'):
    - Validar extensão/tamanho (ex.: <= 5MB; .txt,.pdf,.png,.jpg,.docx,.xlsx)
    - add_attachment(file.read(), maintype, subtype, filename=file.filename)
- Lidar com exceções específicas: smtplib.SMTPAuthenticationError → 401 com mensagem PT; smtplib.SMTPRecipientsRefused → 400; restante → 500

2) Frontend — Composer (templates + JS)
- Form do composer: adicionar enctype="multipart/form-data"; input type="file" name="attachments" multiple
- JS: quando houver anexos, enviar via FormData; manter JSON quando não houver anexos (ou sempre usar FormData para simplificar)
- Validar campos (To, Subject) e mostrar toasts PT-PT
- Estados de loading no botão "Enviar"

3) UI — Edição da Conta
- No POST de edição de conta: só atualizar password se o campo vier preenchido; não sobrescrever para vazio
- Botão "Testar Conexão SMTP": usar get_password(SECRET_KEY) internamente (mesmo método do envio)

4) Logs/Toasts PT-PT
- Password inválida/ausente: "Password SMTP não configurada ou inválida"
- Auth falhada: "Credenciais SMTP inválidas"
- Destinatário recusado: "Destinatário recusado pelo servidor SMTP"
- Anexo inválido: "Anexo inválido ou demasiado grande"
- Sucesso envio: "Email enviado com sucesso!"

5) Testes E2E (Playwright MCP)
- Abrir /accounts/3/edit → Testar Conexão SMTP → Esperado: sucesso
- Abrir /emails/inbox/3 → Escrever → enviar SEM anexos → sucesso (toast + 200)
- Repetir com anexo .txt (pequeno) → sucesso
- Capturar screenshots (smtp-test.png, composer-open.png, composer-success.png, send-with-attachment.png)
- Gerar relatório: ~/Downloads/SendCraft-Testing/phase14D-ui-fix/Phase14D-WebUI-Fix-Report.md

Critérios de aceitação:
✅ Decriptação de password sem erros na UI (mesmo método do CLI)
✅ Envio SMTP via UI com sucesso (porta 465 SSL)
✅ Anexos enviados com sucesso (até 5MB)
✅ Toasts PT-PT amigáveis e claros
✅ Relatório e screenshots gerados

Notas:
- Não logar password
- Sanitizar body_html antes de enviar
- Evitar sobrescrever password na edição se user não alterar
- Se usar 587, set smtp_use_tls=True e smtp_use_ssl=False (não misturar)

Executar estas correções e validar tudo via Playwright MCP.
