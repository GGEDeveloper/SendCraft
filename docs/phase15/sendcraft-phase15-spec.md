# 📧 SendCraft Phase 15: API de Envio de Emails

## 🎯 Objetivo Único
Criar uma API simples e robusta para permitir que o projeto de e-commerce interno envie emails com anexos através do SendCraft.

**FOCO EXCLUSIVO:** Receber dados → Processar anexos → Enviar email → Retornar status

## 📋 Especificação Técnica

### Endpoints Mínimos (3 endpoints)

#### 1. POST /api/v1/send
**Envio de email individual ou em lote**

**Headers:**
```
Authorization: Bearer {api_key}
Content-Type: application/json
```

**Payload:**
```json
{
  "to": ["cliente@exemplo.com", "outro@exemplo.com"],
  "cc": ["copia@exemplo.com"],
  "bcc": ["oculta@exemplo.com"],
  "subject": "Confirmação de Encomenda #12345",
  "html": "<h1>Obrigado pela sua compra!</h1><p>Detalhes em anexo.</p>",
  "text": "Obrigado pela sua compra! Detalhes em anexo.",
  "attachments": [
    {
      "filename": "fatura-12345.pdf",
      "content_type": "application/pdf",
      "content": "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwo..."
    },
    {
      "filename": "guia-produto.jpg",
      "content_type": "image/jpeg", 
      "content": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ..."
    }
  ],
  "from_name": "Loja Online",
  "reply_to": "suporte@loja.com",
  "domain": "alitools.pt",
  "account": "encomendas",
  "bulk": false,
  "idempotency_key": "order-12345-confirmation"
}
```

**Resposta Sucesso (200):**
```json
{
  "success": true,
  "message_id": "MSG-2025-001234",
  "status": "sent",
  "recipients_processed": 2,
  "recipients_success": ["cliente@exemplo.com", "outro@exemplo.com"],
  "recipients_failed": [],
  "attachments_processed": 2,
  "total_size_mb": 1.2,
  "processing_time_ms": 850
}
```

**Resposta Erro (400/500):**
```json
{
  "success": false,
  "error": "validation_failed",
  "message": "Anexo excede tamanho máximo de 10MB",
  "details": {
    "attachment_index": 0,
    "filename": "arquivo-grande.pdf",
    "size_mb": 15.2,
    "max_allowed_mb": 10
  }
}
```

#### 2. GET /api/v1/send/{message_id}/status
**Consultar status de envio**

**Headers:**
```
Authorization: Bearer {api_key}
```

**Resposta (200):**
```json
{
  "message_id": "MSG-2025-001234", 
  "status": "sent",
  "created_at": "2025-10-24T00:15:30Z",
  "sent_at": "2025-10-24T00:15:32Z",
  "recipients": [
    {
      "email": "cliente@exemplo.com",
      "status": "sent",
      "smtp_response": "250 2.0.0 OK"
    },
    {
      "email": "outro@exemplo.com", 
      "status": "failed",
      "smtp_response": "550 5.1.1 User unknown"
    }
  ],
  "attachments_count": 2,
  "error_message": null
}
```

#### 3. POST /api/v1/attachments/upload (Opcional)
**Upload prévio de anexos grandes**

**Headers:**
```
Authorization: Bearer {api_key}
Content-Type: application/json
```

**Payload:**
```json
{
  "filename": "catalogo-produtos.pdf",
  "content_type": "application/pdf",
  "content": "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwo..."
}
```

**Resposta (200):**
```json
{
  "attachment_id": "ATT-2025-789",
  "filename": "catalogo-produtos.pdf",
  "size_mb": 5.8,
  "expires_at": "2025-10-25T00:15:30Z"
}
```

**Uso no /send:**
```json
{
  "attachments": [
    {"attachment_id": "ATT-2025-789"}
  ]
}
```

## 🔧 Implementação Técnica

### Estrutura de Arquivos
```
sendcraft/
├── routes/
│   └── email_api.py          # Novo blueprint para Phase 15
├── services/
│   ├── attachment_service.py  # Gestão de anexos
│   └── email_queue.py        # Queue simples para bulk
└── docs/phase15/
    ├── sendcraft-phase15-spec.md
    └── api-examples.md
```

### Validações Obrigatórias
- **Anexos:** Máximo 10MB por ficheiro, 50MB total por request
- **Destinatários:** Máximo 100 emails por request bulk
- **Tipos permitidos:** PDF, JPG, PNG, DOCX, XLSX, TXT
- **Rate limiting:** 100 requests/minuto por API key
- **Idempotency:** Evitar envios duplicados com mesmo idempotency_key

### Queue Para Bulk (Simples)
- **Bulk = false:** Envio imediato síncrono
- **Bulk = true:** Enfileirar para processamento assíncrono
- **Worker simples:** Thread em background que processa queue
- **Status:** pending → processing → sent/failed

## 📝 Casos de Uso E-commerce

### 1. Confirmação de Encomenda
```bash
curl -X POST https://sendcraft.dominios.pt/api/v1/send \
  -H "Authorization: Bearer {api_key}" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["cliente@exemplo.com"],
    "subject": "Confirmação Encomenda #12345",
    "html": "<h1>Encomenda confirmada!</h1>",
    "attachments": [{
      "filename": "fatura.pdf",
      "content_type": "application/pdf", 
      "content": "base64_content"
    }],
    "domain": "alitools.pt",
    "account": "encomendas"
  }'
```

### 2. Notificação de Envio
```bash
curl -X POST https://sendcraft.dominios.pt/api/v1/send \
  -H "Authorization: Bearer {api_key}" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["cliente@exemplo.com"],
    "subject": "Encomenda #12345 Enviada",
    "html": "<h1>A sua encomenda foi enviada!</h1><p>Tracking: XYZ123</p>",
    "domain": "alitools.pt",
    "account": "envios",
    "idempotency_key": "shipping-12345-notification"
  }'
```

### 3. Newsletter (Bulk)
```bash
curl -X POST https://sendcraft.dominios.pt/api/v1/send \
  -H "Authorization: Bearer {api_key}" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["cliente1@exemplo.com", "cliente2@exemplo.com"],
    "subject": "Newsletter Outubro 2025",
    "html": "<h1>Novidades da loja!</h1>",
    "bulk": true,
    "domain": "alitools.pt",
    "account": "marketing"
  }'
```

## ✅ Critérios de Aceitação

1. **Envio Individual:** Email com 1-2 anexos PDF enviado com sucesso
2. **Envio Bulk:** Lista de 10+ emails processada em background
3. **Validação:** Anexos inválidos rejeitados com erro claro
4. **Status:** Endpoint de status retorna informação precisa
5. **Idempotency:** Mesmo idempotency_key não gera envio duplicado
6. **Logging:** EmailLog criado para cada envio
7. **Compatibilidade:** Endpoints existentes continuam funcionais
8. **Documentação:** OpenAPI spec acessível em /api/docs

## 🚀 Entrega Final

- **Tempo estimado:** 3-5 dias
- **Endpoints:** 3 funcionais 
- **Testes:** Unitários para serviços
- **Docs:** OpenAPI + exemplos cURL
- **Zero breaking changes** nos endpoints atuais

---

**Versão:** Phase 15 - Simplified Email Sending API  
**Data:** 24 Outubro 2025  
**Foco:** Envio de emails apenas - sem analytics, webhooks ou management