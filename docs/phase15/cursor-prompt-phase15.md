# 🔧 Prompt PERFEITO para Cursor - SendCraft Phase 15

Você é um desenvolvedor sénior Python/Flask responsável por implementar a **Phase 15** do SendCraft: **API de Envio de Emails**.

## 🎯 OBJETIVO ÚNICO
Criar **3 endpoints simples** para o e-commerce interno enviar emails com anexos. **FOCO EXCLUSIVO**: receber dados → processar → enviar → retornar status.

## 📂 CONTEXTO DO PROJETO
- **Repositório:** SendCraft (Flask + SQLAlchemy + Bootstrap)
- **Branch:** main  
- **API Atual:** `sendcraft/routes/external_api.py` (5 endpoints funcionais)
- **Serviços:** `smtp_service.py`, `auth_service.py` já implementados
- **Documentação:** `docs/phase15/sendcraft-phase15-spec.md` e `docs/phase15/api-examples.md`

## 🚀 ENTREGÁVEIS (3-5 DIAS)

### 1. NOVO BLUEPRINT: `sendcraft/routes/email_api.py`
```python
# Blueprint com URL prefix /api/v1
# 3 endpoints mínimos:
# - POST /api/v1/send
# - GET /api/v1/send/{message_id}/status  
# - POST /api/v1/attachments/upload (opcional)
```

### 2. SERVIÇOS NECESSÁRIOS
```python
# sendcraft/services/attachment_service.py
class AttachmentService:
    def save_base64(content, filename, content_type) -> str  # retorna attachment_id
    def get_attachment(attachment_id) -> dict
    def delete_attachment(attachment_id) -> bool
    def validate_attachment(content, filename, content_type) -> bool

# sendcraft/services/email_queue.py (simples, in-memory)
class EmailQueue:
    def enqueue(payload, priority='normal') -> str  # retorna job_id
    def process_queue() -> None  # worker simples
    def get_status(job_id) -> dict
```

### 3. ENDPOINTS IMPLEMENTAÇÃO

#### POST /api/v1/send
```json
// Payload de entrada
{
  "to": ["cliente@exemplo.com"],
  "subject": "Confirmação Encomenda #12345", 
  "html": "<h1>Obrigado!</h1>",
  "text": "Obrigado!",
  "attachments": [
    {
      "filename": "fatura.pdf",
      "content_type": "application/pdf",
      "content": "base64_content"
    }
  ],
  "domain": "alitools.pt",
  "account": "encomendas",
  "bulk": false,
  "idempotency_key": "order-12345-conf"
}

// Resposta sucesso
{
  "success": true,
  "message_id": "MSG-2025-001",
  "status": "sent",
  "recipients_processed": 1,
  "attachments_processed": 1
}
```

#### GET /api/v1/send/{message_id}/status
```json
{
  "message_id": "MSG-2025-001",
  "status": "sent",
  "created_at": "2025-10-24T00:15:30Z",
  "recipients": [
    {
      "email": "cliente@exemplo.com",
      "status": "sent",
      "smtp_response": "250 OK"
    }
  ]
}
```

## 🔧 IMPLEMENTAÇÃO TÉCNICA

### VALIDAÇÕES OBRIGATÓRIAS
- Anexos: máximo 10MB por ficheiro, 50MB total
- Tipos permitidos: PDF, JPG, PNG, DOCX, TXT
- Rate limiting: 100 requests/min por API key
- Idempotency: mesmo `idempotency_key` = sem envio duplicado

### REUTILIZAR CÓDIGO EXISTENTE
- **SMTPService.send_email()** para envio real (já suporta anexos)
- **@require_api_key** decorator para auth
- **EmailLog model** para logging
- **Domain/EmailAccount models** para validação

### FLUXO DE ENVIO
```python
# 1. Validar payload e autenticação
# 2. Processar anexos (base64 → arquivo temporário)
# 3. Se bulk=true → enqueue, se bulk=false → envio direto
# 4. Usar SMTPService.send_email() existente
# 5. Criar EmailLog record
# 6. Retornar resposta JSON
```

### QUEUE SIMPLES (Para Bulk)
```python
# In-memory queue com threading para desenvolvimento
# Interface preparada para migração futura para Redis
# Worker thread que processa jobs em background
```

## 📋 TAREFAS ESPECÍFICAS

### Fase 1: Blueprint e Rotas (1 dia)
1. Criar `sendcraft/routes/email_api.py`
2. Implementar 3 endpoints skeleton
3. Integrar autenticação existente
4. Testar rotas básicas

### Fase 2: Attachment Service (1 dia)  
1. Criar `AttachmentService` class
2. Validação de tipos/tamanhos
3. Storage temporário para anexos
4. Cleanup automático de ficheiros antigos

### Fase 3: Integração SMTP (1-2 dias)
1. Conectar endpoints ao `SMTPService` existente
2. Implementar bulk/queue simples
3. Logging em `EmailLog`
4. Idempotency check

### Fase 4: Documentação e Testes (1 dia)
1. Atualizar `sendcraft/routes/api_docs.py`
2. Gerar OpenAPI spec
3. Testes unitários básicos
4. Validação com exemplos cURL

## 🚫 NÃO IMPLEMENTAR
- ❌ Analytics/métricas avançadas
- ❌ Webhooks/notificações 
- ❌ Email management/IMAP
- ❌ Template management via API
- ❌ Complex queue systems (Redis/RabbitMQ)
- ❌ Scheduling/agendamento

## ✅ CRITÉRIOS DE ACEITAÇÃO
1. **Envio funcional:** Email com anexo PDF enviado via API
2. **Bulk processing:** Lista 10+ emails processada em background  
3. **Validação:** Anexo 15MB rejeitado com erro claro
4. **Status check:** Endpoint retorna info precisa
5. **Idempotency:** Mesmo key não duplica envio
6. **Compatibilidade:** Endpoints atuais continuam funcionais
7. **Docs:** OpenAPI em `/api/docs` atualizado

## 📝 ESTRUTURA DE ARQUIVOS FINAL
```
sendcraft/
├── routes/
│   ├── external_api.py      # Existente (manter)
│   ├── email_api.py         # NOVO - Phase 15
│   └── api_docs.py          # Atualizar
├── services/
│   ├── smtp_service.py      # Existente (reutilizar)
│   ├── attachment_service.py # NOVO
│   └── email_queue.py       # NOVO (simples)
└── docs/phase15/
    ├── sendcraft-phase15-spec.md     # Spec técnica
    └── api-examples.md               # Exemplos cURL
```

## 🔍 PONTOS DE ATENÇÃO
- Manter **backward compatibility** com API existente
- Usar **type hints** e **docstrings** consistentes  
- **Error handling** robusto com códigos HTTP adequados
- **Logging** detalhado para debug
- **Security** - validação rigorosa de inputs

## 🏁 ENTREGA
- **PR** com código funcional
- **Testes** com conta real `geral@artnshine.pt`
- **Documentação** OpenAPI atualizada
- **Zero breaking changes**

---

**COMEÇAR POR:** Criar o blueprint `email_api.py` com skeleton dos 3 endpoints e integrar autenticação existente.

**LEMBRETE:** Foco laser em **ENVIO DE EMAILS** apenas. Sem features complexas desnecessárias.