# 🧪 PROMPT — Phase 14D SMTP (Playwright MCP Runner)

Copiar/colar no agente com MCP Playwright ativo. Executa o teste E2E de envio real via SMTP com o compositor do SendCraft.

---

Título: SendCraft Phase 14D — Real SMTP Send E2E (Playwright MCP)

Contexto:
- Validar envio real a partir de `geral@artnshine.pt` (ID 3) para `mmelo.deb@gmail.com` usando o composer UI do SendCraft.
- Servidor: http://localhost:5000 (dev), SMTP configurado conforme guia.

Pré‑requisitos:
- SMTP da conta configurado: mail.artnshine.pt:465 SSL, auth com `geral@artnshine.pt`
- DKIM/SPF no cPanel (recomendado)
- Composer UI ativo (Phase 14D)

Parâmetros:
- Base URL: http://localhost:5000
- Screenshots: ~/Downloads/SendCraft-Testing/phase14D/screenshots/
- Report: ~/Downloads/SendCraft-Testing/phase14D/SendCraft-Phase14D-SMTP-Report.md
- Viewport: 1440x900

Plano de execução:
1) Setup
- Abrir Chromium (headed), viewport 1440x900
- Criar diretórios de saída (se não existirem)

2) Navegar e compor
- Ir a /emails/inbox/3
- Screenshot: inbox-page.png
- Clicar botão "Escrever" (ou "Compor")
- Screenshot: composer-open.png

3) Preencher e enviar
- To: `mmelo.deb@gmail.com`
- Subject: `SendCraft Phase14D SMTP Real`
- Body HTML:
  ```html
  <h1>✅ SendCraft SMTP Real</h1>
  <p>Phase14D delivery test.</p>
  ```
- Screenshot: composer-filled.png
- Clicar "Enviar"
- Aguardar toast de sucesso (texto PT-PT)
- Screenshot: composer-success.png

4) Evidências e relatório
- Recolher mensagens de consola
- Resumir network (chamadas de /emails/send)
- Gerar relatório Markdown com:
  - Ambiente
  - Passos e resultados (PASS/FAIL)
  - Screenshots index
  - Console & network summary
  - Observações

Critérios de sucesso:
✅ Toast de sucesso após envio
✅ Sem erros críticos na consola
✅ Screenshots salvos e relatório gerado

Notas:
- Se envio falhar (ex.: 535 Authentication failed), capturar screenshot do erro e mensagem do toast e registar no relatório como FAIL com recomendação (ver guia SMTP).
