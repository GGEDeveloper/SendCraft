# 📬 Phase 14D — SMTP Configuration (cPanel Dominios.pt)

Guia prático para configurar e validar envio real via SMTP para as contas do domínio `artnshine.pt` (aplicável também às contas `@alitools.pt`).

## ✅ Recomendado (SSL/TLS)
- Username: `geral@artnshine.pt`
- Password: a password da caixa
- Incoming (IMAP): `mail.artnshine.pt` — Port 993 (SSL)
- Incoming (POP3): `mail.artnshine.pt` — Port 995 (SSL)
- Outgoing (SMTP): `mail.artnshine.pt` — Port 465 (SSL)
- Autenticação obrigatória para IMAP/POP3/SMTP

## ⚠️ Alternativo (não recomendado)
- IMAP: Port 143 (sem SSL)
- POP3: Port 110 (sem SSL)
- SMTP: Port 587 (STARTTLS)

> Nota: Usar sempre SSL/TLS quando possível (465/993/995).

---

## 🛠️ Configuração no SendCraft (Conta `geral@artnshine.pt`)

1) Aceder a: `http://localhost:5000/accounts`
2) Editar a conta `geral@artnshine.pt` (ID 3)
3) Definir:
   - SMTP server: `mail.artnshine.pt`
   - SMTP port: `465`
   - SSL: `ON` (TLS OFF se usar 465)
   - Username: `geral@artnshine.pt`
   - Password: inserir e guardar (fica encriptada)
4) Testar `SMTP handshake` no UI (esperado: OK)

### CLI (opcional) — aplicar via shell
```python
from sendcraft import create_app
from sendcraft.models import EmailAccount
from sendcraft.extensions import db
app = create_app()
with app.app_context():
    acc = EmailAccount.query.filter_by(email_address='geral@artnshine.pt').first()
    assert acc
    acc.smtp_server = 'mail.artnshine.pt'
    acc.smtp_port = 465
    acc.smtp_use_ssl = True
    acc.smtp_use_tls = False
    acc.smtp_username = 'geral@artnshine.pt'
    acc.set_password('SUA_PASSWORD_REAL_AQUI', app.config['SECRET_KEY'])
    db.session.commit()
    print('SMTP SSL configurado')
```

---

## 🔐 SPF/DKIM/DMARC (Entregabilidade)
- cPanel > Email Deliverability:
  - DKIM: ativar
  - SPF: incluir o servidor de envio (por ex. `a mx include:spf.antispamcloud.com` se usar SpamExperts)
  - DMARC (DNS): `_dmarc` → `v=DMARC1; p=none; rua=mailto:postmaster@artnshine.pt`

> Para SMTP direto no cPanel, SPF comum: `v=spf1 a mx ~all` ou `+ip4:` do teu host se aplicável.

---

## 🧪 Teste E2E (Playwright MCP) — Envio real

1) Garantir servidor ativo: `python run_dev.py`
2) Garantir Phase 14D implementada (composer UI)
3) Copiar o prompt em `docs/phase14/PROMPT-AGENT-14D-SMTP-PLAYWRIGHT.md` (ver abaixo)
4) O agente irá:
   - Abrir `/emails/inbox/3`
   - Clicar `Escrever`
   - Preencher To: `mmelo.deb@gmail.com`
   - Subject: `SendCraft Phase14D SMTP Real`
   - Body HTML: `<h1>✅ SendCraft SMTP Real</h1><p>Phase14D delivery test.</p>`
   - Enviar e aguardar toast de sucesso
   - Capturar screenshots e gerar relatório

Outputs:
- Screenshots: `~/Downloads/SendCraft-Testing/phase14D/screenshots/`
- Report: `~/Downloads/SendCraft-Testing/phase14D/SendCraft-Phase14D-SMTP-Report.md`

---

## 📎 Windows Live Mail (Anexo fornecido)
- "Secure Email Setup" (VBS) disponível e compatível com as definições acima.
- Usar as mesmas portas e hostname; autenticação sempre ativa.

---

## ✅ Checklist final
- [ ] Conta `geral@artnshine.pt` configurada em SendCraft com SSL 465
- [ ] DKIM/SPF configurados (cPanel)
- [ ] Teste SMTP handshake OK
- [ ] Envio Playwright: email enviado para `mmelo.deb@gmail.com`
- [ ] Receção confirmada na caixa destino
- [ ] Relatório Phase14D gerado com evidências
