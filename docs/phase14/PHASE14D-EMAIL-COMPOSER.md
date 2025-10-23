# ✉️ Phase 14D — Email Composer & Send (UI + SMTP)

## Objetivo
Adicionar um **compositor de email** na interface (por conta selecionada) e enviar emails via SMTP. Validar envio real a partir de `geral@artnshine.pt` para `mmelo.deb@gmail.com` com testes automatizados via Playwright MCP.

## Requisitos Funcionais
- Botão "Compor" acessível no cliente de email (/emails/inbox/<account_id>)
- Modal ou página dedicada com formulário:
  - From (conta atual, readonly)
  - To (um ou mais emails, com validação)
  - Subject (obrigatório)
  - Body (editor rich text – TinyMCE ou textarea HTML)
  - Attachments (upload múltiplo – opcional, inicial)
- Botões: Enviar, Guardar Rascunho (opcional), Cancelar
- Feedback: toasts de sucesso/erro

## Rotas Back-end
- GET /emails/compose/<account_id> — render UI (ou modal via partial)
- POST /emails/send — processa envio
  - Payload: account_id, to[], subject, body_html, body_text (fallback), attachments (opcional)
  - Validações: emails válidos, subject/body obrigatórios
  - Envio via SMTP configurado na conta
  - Logging de envio com status e erros

## UI/Frontend
- Botão "Compor" no header da inbox
- Formulário com validação client-side
- Editor rich text (TinyMCE recomendado; fallback para textarea)
- Previsão do From (ex.: geral@artnshine.pt)

## Segurança
- Sanitização do HTML no corpo antes de envio
- Limite de anexos/tamanho (opcional nesta fase)
- Não logar conteúdo completo do email; apenas metadados

## Testes (Playwright MCP)
- Abrir /emails/inbox/3 (geral@artnshine.pt)
- Clicar "Compor" → abrir UI
- Preencher To: mmelo.deb@gmail.com
- Subject: "SendCraft Test - Phase14D"
- Body: HTML simples com lista e bold
- Enviar → esperar toast SUCCESS
- Capturar screenshot do sucesso
- (Opcional) Verificar em /logs ou secção de envios

## Critérios de Aceitação
- UI de composição disponível e funcional
- Validações corretas de email e campos obrigatórios
- Envio via SMTP executado sem crash
- Toasts PT-PT com mensagens claras
- Teste automatizado via Playwright executa com sucesso

## Notas
- Se SMTP recusar por credenciais ou política, validar que a UI lida com o erro e apresenta mensagem clara.
- Para anexos, iniciar com 1 ficheiro opcional; expandir depois.
