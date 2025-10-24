# 📧 SendCraft API v1 - Referência Completa

## 🚀 Visão Geral

A SendCraft API v1 permite envio de emails transacionais e em bulk através de endpoints REST seguros. A API inclui suporte completo para anexos, validações rigorosas, rate limiting e idempotência.

### **Base URL**
```
http://localhost:5000/api/v1
```

### **Autenticação**
Todos os endpoints requerem autenticação via API Key no cabeçalho:
```
Authorization: Bearer YOUR_API_KEY
```

## 📋 **Endpoints Disponíveis**

### 1. **POST /send** - Envio de Email
Envia emails individuais ou em bulk com suporte a anexos.

#### **Request**
```http
POST /api/v1/send
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

#### **Payload**
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
      "content": "base64_encoded_content_here"
    }
  ],
  "from_name": "Loja Online",
  "reply_to": "suporte@loja.com",
  "domain": "artnshine.pt",
  "account": "geral",
  "bulk": false,
  "idempotency_key": "order-12345-confirmation"
}
```

#### **Campos Obrigatórios**
- `to` (array): Lista de destinatários
- `subject` (string): Assunto do email
- `html` (string): Conteúdo HTML **OU** `text`
- `domain` (string): Domínio configurado no SendCraft
- `account` (string): Conta local (parte antes do @)

#### **Campos Opcionais**
- `cc` (array): Destinatários em cópia
- `bcc` (array): Destinatários em cópia oculta
- `text` (string): Versão texto simples
- `attachments` (array): Anexos em base64
- `from_name` (string): Nome do remetente
- `reply_to` (string): Email para resposta
- `bulk` (boolean): Processamento em background se >1 destinatário
- `idempotency_key` (string): Chave única para evitar duplicação

#### **Limites**
- **Destinatários:** Máximo 100 para bulk
- **Anexos:** 10MB por arquivo, 50MB total
- **Rate Limit:** Conforme configuração da conta

#### **Responses**

**✅ 200 Success**
```json
{
  "success": true,
  "message_id": "MSG-123456",
  "status": "sent",
  "recipients_processed": 2,
  "recipients_success": ["cliente@exemplo.com", "outro@exemplo.com"],
  "recipients_failed": [],
  "attachments_processed": 1,
  "total_size_mb": 2.5,
  "processing_time_ms": 1250
}
```

**❌ 400 Validation Error**
```json
{
  "success": false,
  "error": "validation_failed",
  "message": "Missing required fields: subject",
  "details": {
    "missing_fields": ["subject"],
    "required_fields": ["to", "subject", "html", "domain", "account"]
  }
}
```

**🔒 401 Unauthorized**
```json
{
  "success": false,
  "error": "unauthorized",
  "message": "Include API key in Authorization header: Bearer <key>"
}
```

**📧 404 Account Not Found**
```json
{
  "success": false,
  "error": "account_not_found",
  "message": "Account 'geral@artnshine.pt' not found or inactive"
}
```

**⏰ 429 Rate Limit Exceeded**
```json
{
  "success": false,
  "error": "rate_limit_exceeded",
  "message": "Daily limit of 1000 emails exceeded"
}
```

---

### 2. **GET /send/{message_id}/status** - Status do Email

Consulta o status de um email enviado.

#### **Request**
```http
GET /api/v1/send/MSG-123456/status
Authorization: Bearer YOUR_API_KEY
```

#### **Response**
```json
{
  "message_id": "MSG-123456",
  "status": "sent",
  "created_at": "2025-10-24T01:30:00Z",
  "sent_at": "2025-10-24T01:30:15Z",
  "recipients": [
    {
      "email": "cliente@exemplo.com",
      "status": "sent",
      "smtp_response": "250 Message accepted"
    }
  ],
  "attachments_count": 1,
  "error_message": null
}
```

#### **Status Values**
- `pending`: Email na fila
- `sending`: Sendo enviado
- `sent`: Enviado com sucesso
- `delivered`: Confirmação de entrega
- `failed`: Falha no envio
- `bounced`: Email devolvido

---

### 3. **POST /attachments/upload** - Upload Prévio

Upload de anexos grandes antes do envio (opcional).

#### **Request**
```http
POST /api/v1/attachments/upload
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

#### **Payload**
```json
{
  "filename": "catalogo-produtos.pdf",
  "content_type": "application/pdf",
  "content": "base64_encoded_content"
}
```

#### **Response**
```json
{
  "attachment_id": "att_ABC123456789",
  "filename": "catalogo-produtos.pdf",
  "size_mb": 5.2,
  "expires_at": "2025-10-25T01:30:00Z"
}
```

---

## 🔧 **Exemplos Práticos**

### **cURL - Envio Simples**
```bash
curl -X POST http://localhost:5000/api/v1/send \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["geral@artnshine.pt"],
    "subject": "Teste SendCraft API",
    "html": "<h1>Hello from SendCraft!</h1>",
    "domain": "artnshine.pt",
    "account": "geral"
  }'
```

### **Node.js - Com Anexo**
```javascript
const axios = require('axios');
const fs = require('fs');

// Ler e converter arquivo para base64
const fileBuffer = fs.readFileSync('documento.pdf');
const base64Content = fileBuffer.toString('base64');

const emailData = {
  to: ['cliente@exemplo.com'],
  subject: 'Documento Importante',
  html: '<p>Segue documento em anexo.</p>',
  domain: 'artnshine.pt',
  account: 'geral',
  attachments: [
    {
      filename: 'documento.pdf',
      content_type: 'application/pdf',
      content: base64Content
    }
  ],
  idempotency_key: `doc-${Date.now()}`
};

try {
  const response = await axios.post('http://localhost:5000/api/v1/send', emailData, {
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY',
      'Content-Type': 'application/json'
    }
  });
  
  console.log('Email enviado:', response.data.message_id);
} catch (error) {
  console.error('Erro:', error.response?.data || error.message);
}
```

### **PHP - Bulk Marketing**
```php
<?php
$recipients = [
    'cliente1@exemplo.com',
    'cliente2@exemplo.com', 
    'cliente3@exemplo.com'
];

$emailData = [
    'to' => $recipients,
    'subject' => '🎯 Oferta Especial - 30% Desconto',
    'html' => '<h1>Oferta Limitada!</h1><p>Aproveite 30% de desconto.</p>',
    'domain' => 'artnshine.pt',
    'account' => 'geral',
    'bulk' => true,
    'from_name' => 'Loja Marketing',
    'idempotency_key' => 'campaign-' . date('Y-m-d-H')
];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, 'http://localhost:5000/api/v1/send');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($emailData));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer YOUR_API_KEY',
    'Content-Type: application/json'
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($httpCode === 200) {
    $data = json_decode($response, true);
    echo "Campanha enviada: " . $data['message_id'] . "\n";
} else {
    echo "Erro: " . $response . "\n";
}
?>
```

---

## 🛡️ **Validações e Limitações**

### **Anexos**
- **Formatos aceites:** PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, PNG, JPG, JPEG, GIF
- **Tamanho por arquivo:** 10MB máximo
- **Total por email:** 50MB máximo
- **Encoding:** Base64 obrigatório

### **Destinatários**
- **Email individual:** 1 destinatário
- **Bulk:** Até 100 destinatários
- **Formato:** RFC 5322 válido
- **CC/BCC:** Incluem no limite total

### **Conteúdo**
- **Subject:** Máximo 255 caracteres
- **HTML:** Sanitização automática (remove scripts)
- **Text:** Alternativa recomendada
- **Encoding:** UTF-8

### **Rate Limits**
- **Por conta:** Configurável (padrão: 1000/dia, 50/hora)
- **Bulk processing:** Background automático
- **Retry:** 3 tentativas com backoff exponencial

---

## 🔑 **Gestão de API Keys**

### **Como Obter**
1. Aceder à UI SendCraft: `http://localhost:5000`
2. Ir para **Contas** → Editar conta desejada
3. Clicar em **"API"** → **"Ativar API"**
4. Clicar em **"Gerar API Key"**
5. **Copiar imediatamente** - só é mostrada uma vez!

### **Segurança**
- **Armazenamento:** Nunca versionar em código
- **Transmissão:** Apenas HTTPS em produção
- **Rotação:** Regenerar periodicamente
- **Revogação:** Imediata via UI

### **Formatos**
```
# Desenvolvimento (HTTP)
Authorization: Bearer sendcraft_dev_abc123def456...

# Produção (HTTPS)
Authorization: Bearer sendcraft_prod_xyz789uvw123...
```

---

## 🚨 **Códigos de Erro Comuns**

| Código | Erro | Descrição | Solução |
|--------|------|-----------|---------|
| 400 | `validation_failed` | Campos obrigatórios em falta | Verificar payload |
| 401 | `unauthorized` | API Key inválida/em falta | Verificar cabeçalho Authorization |
| 404 | `account_not_found` | Conta não existe/inativa | Verificar domain/account |
| 404 | `domain_not_found` | Domínio não configurado | Configurar na UI |
| 429 | `rate_limit_exceeded` | Limite diário/horário excedido | Aguardar ou aumentar limite |
| 500 | `smtp_error` | Falha no servidor SMTP | Verificar configuração SMTP |
| 500 | `attachment_processing_failed` | Erro no processamento anexo | Verificar formato/tamanho |

---

## 📊 **Monitorização**

### **Logs na UI**
- **Localização:** `http://localhost:5000/logs`
- **Filtros:** Por domínio, status, data
- **Detalhes:** Payload, resposta SMTP, timing

### **Métricas de Status**
```bash
# Verificar status específico
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:5000/api/v1/send/MSG-123456/status

# Rate limit atual (via logs/dashboard)
# Acessar UI → Dashboard para estatísticas 24h
```

### **Health Check**
```bash
curl http://localhost:5000/api/v1/health
```

---

## 📝 **Notas da Implementação**

- **Idempotência:** Usar `idempotency_key` para evitar emails duplicados
- **Bulk Processing:** Emails >1 destinatário são processados em background
- **Anexos Grandes:** Usar `/attachments/upload` para arquivos >5MB
- **Templates:** Não suportados na API v1 - usar HTML direto
- **Webhooks:** Não implementados na v1
- **Tracking:** Apenas status via polling

**Versão:** API v1.0  
**Última atualização:** 24 Outubro 2025  
**Compatibilidade:** SendCraft Phase 15+