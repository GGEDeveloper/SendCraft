# SendCraft Phase 15: API de Envio de Emails

## Objetivo
Implementar 3 endpoints simples para e-commerce enviar emails com anexos:
- POST /api/v1/send (individual/bulk)
- GET /api/v1/send/{id}/status  
- POST /api/v1/attachments/upload

## Especificação Técnica

### 1. POST /api/v1/send
**Descrição**: Envia emails individuais ou em lote com anexos

**Headers**:
```
Content-Type: application/json
Authorization: Bearer {api_key}
```

**Body (Individual)**:
```json
{
  "to": "cliente@exemplo.com",
  "subject": "Confirmação de Pedido",
  "html_content": "<h1>Seu pedido foi confirmado!</h1>",
  "text_content": "Seu pedido foi confirmado!",
  "from_name": "ALITOOLS",
  "attachments": [
    {
      "filename": "invoice.pdf",
      "content_type": "application/pdf",
      "data": "base64_encoded_data"
    }
  ],
  "account": "geral@alitools.pt"
}
```

**Body (Bulk)**:
```json
{
  "emails": [
    {
      "to": "cliente1@exemplo.com",
      "subject": "Confirmação de Pedido",
      "html_content": "<h1>Seu pedido foi confirmado!</h1>",
      "text_content": "Seu pedido foi confirmado!",
      "attachments": [
        {
          "filename": "invoice1.pdf",
          "content_type": "application/pdf",
          "data": "base64_encoded_data"
        }
      ]
    }
  ],
  "from_name": "ALITOOLS",
  "account": "geral@alitools.pt"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Email(s) sent successfully",
  "data": {
    "job_id": "uuid-string",
    "emails_sent": 1,
    "emails_failed": 0,
    "status": "completed"
  }
}
```

### 2. GET /api/v1/send/{id}/status
**Descrição**: Consulta status de envio de email

**Headers**:
```
Authorization: Bearer {api_key}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "job_id": "uuid-string",
    "status": "completed",
    "emails_sent": 1,
    "emails_failed": 0,
    "created_at": "2024-01-01T10:00:00Z",
    "completed_at": "2024-01-01T10:00:05Z",
    "details": [
      {
        "to": "cliente@exemplo.com",
        "status": "sent",
        "message_id": "smtp-message-id",
        "error": null
      }
    ]
  }
}
```

### 3. POST /api/v1/attachments/upload
**Descrição**: Upload de anexos para uso posterior

**Headers**:
```
Content-Type: multipart/form-data
Authorization: Bearer {api_key}
```

**Body**:
```
file: (binary file data)
```

**Response**:
```json
{
  "success": true,
  "data": {
    "attachment_id": "uuid-string",
    "filename": "invoice.pdf",
    "content_type": "application/pdf",
    "size": 1024,
    "uploaded_at": "2024-01-01T10:00:00Z",
    "expires_at": "2024-01-08T10:00:00Z"
  }
}
```

## Componentes a Reutilizar
- SMTPService (existente)
- AuthService (existente) 
- EmailLog model (existente)

## Componentes a Criar
- attachment_service.py
- email_queue.py (simple)
- email_api.py (blueprint)

## Fluxo de Processamento
1. Receber dados → Validar → Processar → Enviar → Status
2. Suporte a anexos via base64 ou upload prévio
3. Queue simples para processamento assíncrono
4. Logging completo via EmailLog

## Validações
- API Key obrigatória
- Conta de envio válida e ativa
- Limites de envio respeitados
- Tamanho máximo de anexos: 10MB
- Tipos de arquivo permitidos: PDF, DOC, DOCX, XLS, XLSX, PNG, JPG, GIF
