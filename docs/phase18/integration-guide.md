# 🔗 SendCraft Integration Guide - Para Projetos Externos

## 🎯 Visão Geral

Este guia fornece instruções completas para integrar o SendCraft com qualquer projeto externo. O SendCraft oferece uma API REST v1 robusta para envio de emails transacionais e marketing bulk.

### **Pré-requisitos**
- SendCraft rodando e configurado
- API Key ativa obtida via UI de gestão
- Conta SMTP configurada no sistema

---

## 🚀 Integração Rápida (5 min)

### **1. Obter API Key**
1. Aceder UI SendCraft: `http://seu-sendcraft.com`
2. Ir para **Contas** → Selecionar conta → **API**
3. Ativar API e gerar chave
4. **Copiar imediatamente** - só é mostrada uma vez!

### **2. Teste Básico**
```bash
curl -X POST http://seu-sendcraft.com/api/v1/send \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["destinatario@exemplo.com"],
    "subject": "Teste SendCraft",
    "html": "<h1>Hello World!</h1>",
    "domain": "seu-dominio.com",
    "account": "sua-conta"
  }'
```

### **3. Verificar Resposta**
```json
{
  "success": true,
  "message_id": "MSG-123456",
  "status": "sent"
}
```

**✅ Integração funcionando!**

---

## 📚 Implementações por Tecnologia

### **Node.js / Express**

#### Instalação
```bash
npm install axios
```

#### Implementação Básica
```javascript
const axios = require('axios');

class SendCraftClient {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
        this.client = axios.create({
            baseURL: baseUrl,
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            }
        });
    }

    async sendEmail(emailData) {
        try {
            const response = await this.client.post('/api/v1/send', emailData);
            return {
                success: true,
                messageId: response.data.message_id,
                data: response.data
            };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || error.message,
                details: error.response?.data
            };
        }
    }

    async getEmailStatus(messageId) {
        try {
            const response = await this.client.get(`/api/v1/send/${messageId}/status`);
            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.message || error.message);
        }
    }
}

// Uso
const sendcraft = new SendCraftClient(
    'http://seu-sendcraft.com',
    'your_api_key_here'
);

// Email simples
const result = await sendcraft.sendEmail({
    to: ['cliente@exemplo.com'],
    subject: 'Confirmação de Pedido #12345',
    html: '<h1>Obrigado pela sua compra!</h1><p>Seu pedido foi confirmado.</p>',
    domain: 'loja.exemplo.com',
    account: 'vendas'
});

if (result.success) {
    console.log('Email enviado:', result.messageId);
} else {
    console.error('Erro:', result.error);
}
```

#### E-commerce Integration (Express)
```javascript
// routes/checkout.js
app.post('/checkout/complete', async (req, res) => {
    const { orderId, customerEmail, customerName, orderTotal, items } = req.body;
    
    // Processar pedido...
    const order = await processOrder(orderData);
    
    // Enviar email de confirmação
    const emailResult = await sendcraft.sendEmail({
        to: [customerEmail],
        subject: `Confirmação de Pedido #${orderId}`,
        html: `
            <h1>Obrigado pela sua compra, ${customerName}!</h1>
            <p>Seu pedido #${orderId} foi confirmado.</p>
            <p><strong>Total:</strong> €${orderTotal}</p>
            <h3>Itens:</h3>
            <ul>${items.map(item => `<li>${item.name} - €${item.price}</li>`).join('')}</ul>
        `,
        domain: 'loja.exemplo.com',
        account: 'vendas',
        idempotency_key: `order-confirmation-${orderId}`
    });
    
    if (emailResult.success) {
        res.json({ 
            success: true, 
            orderId, 
            emailSent: true,
            messageId: emailResult.messageId 
        });
    } else {
        // Log erro mas não falhar checkout
        console.error('Email failed:', emailResult.error);
        res.json({ 
            success: true, 
            orderId, 
            emailSent: false 
        });
    }
});
```

### **PHP / Laravel**

#### Implementação Básica
```php
<?php

class SendCraftClient {
    private $baseUrl;
    private $apiKey;
    
    public function __construct($baseUrl, $apiKey) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->apiKey = $apiKey;
    }
    
    public function sendEmail($emailData) {
        $ch = curl_init();
        
        curl_setopt_array($ch, [
            CURLOPT_URL => $this->baseUrl . '/api/v1/send',
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($emailData),
            CURLOPT_HTTPHEADER => [
                'Authorization: Bearer ' . $this->apiKey,
                'Content-Type: application/json'
            ],
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 30
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($error) {
            throw new Exception("Curl error: " . $error);
        }
        
        $data = json_decode($response, true);
        
        if ($httpCode !== 200) {
            throw new Exception($data['message'] ?? 'Unknown error');
        }
        
        return $data;
    }
    
    public function getEmailStatus($messageId) {
        $ch = curl_init();
        
        curl_setopt_array($ch, [
            CURLOPT_URL => $this->baseUrl . '/api/v1/send/' . $messageId . '/status',
            CURLOPT_HTTPHEADER => [
                'Authorization: Bearer ' . $this->apiKey
            ],
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 10
        ]);
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }
}

// Uso
$sendcraft = new SendCraftClient(
    'http://seu-sendcraft.com',
    'your_api_key_here'
);

try {
    $result = $sendcraft->sendEmail([
        'to' => ['cliente@exemplo.com'],
        'subject' => 'Bem-vindo!',
        'html' => '<h1>Bem-vindo ao nosso serviço!</h1>',
        'domain' => 'exemplo.com',
        'account' => 'welcome'
    ]);
    
    echo "Email enviado: " . $result['message_id'];
} catch (Exception $e) {
    echo "Erro: " . $e->getMessage();
}
?>
```

#### WooCommerce Integration
```php
// functions.php
add_action('woocommerce_order_status_completed', 'send_order_completion_email');

function send_order_completion_email($order_id) {
    $order = wc_get_order($order_id);
    $sendcraft = new SendCraftClient(
        get_option('sendcraft_url'),
        get_option('sendcraft_api_key')
    );
    
    $emailData = [
        'to' => [$order->get_billing_email()],
        'subject' => 'Seu pedido foi enviado! #' . $order->get_order_number(),
        'html' => generate_order_shipped_email_html($order),
        'domain' => 'loja.exemplo.com',
        'account' => 'vendas',
        'idempotency_key' => 'woo-shipped-' . $order_id
    ];
    
    try {
        $result = $sendcraft->sendEmail($emailData);
        $order->add_order_note('Email de envio enviado via SendCraft: ' . $result['message_id']);
    } catch (Exception $e) {
        error_log('SendCraft error: ' . $e->getMessage());
        $order->add_order_note('Falha ao enviar email de envio: ' . $e->getMessage());
    }
}
```

### **Python / Django**

#### Implementação Básica
```python
import requests
import json
from typing import Dict, List, Optional

class SendCraftClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def send_email(self, email_data: Dict) -> Dict:
        try:
            response = self.session.post(
                f'{self.base_url}/api/v1/send',
                json=email_data,
                timeout=30
            )
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'details': getattr(e, 'response', {}).get('json', lambda: {})()
            }
    
    def get_email_status(self, message_id: str) -> Dict:
        response = self.session.get(
            f'{self.base_url}/api/v1/send/{message_id}/status',
            timeout=10
        )
        response.raise_for_status()
        return response.json()

# Django integration
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

class SendCraftBackend(BaseEmailBackend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = SendCraftClient(
            settings.SENDCRAFT_URL,
            settings.SENDCRAFT_API_KEY
        )
    
    def send_messages(self, email_messages):
        sent_count = 0
        
        for message in email_messages:
            email_data = {
                'to': message.to,
                'cc': getattr(message, 'cc', []),
                'bcc': getattr(message, 'bcc', []),
                'subject': message.subject,
                'html': message.body if message.content_subtype == 'html' else None,
                'text': message.body if message.content_subtype == 'plain' else None,
                'domain': settings.SENDCRAFT_DOMAIN,
                'account': settings.SENDCRAFT_ACCOUNT,
                'from_name': getattr(message, 'from_name', None),
                'reply_to': getattr(message, 'reply_to', None)
            }
            
            result = self.client.send_email(email_data)
            if result['success']:
                sent_count += 1
        
        return sent_count

# settings.py
EMAIL_BACKEND = 'myapp.backends.SendCraftBackend'
SENDCRAFT_URL = 'http://seu-sendcraft.com'
SENDCRAFT_API_KEY = 'your_api_key_here'
SENDCRAFT_DOMAIN = 'exemplo.com'
SENDCRAFT_ACCOUNT = 'noreply'
```

---

## 🔧 Casos de Uso Comuns

### **1. Email de Confirmação de Registo**
```javascript
const sendWelcomeEmail = async (user) => {
    return await sendcraft.sendEmail({
        to: [user.email],
        subject: `Bem-vindo, ${user.name}!`,
        html: `
            <h1>Bem-vindo, ${user.name}!</h1>
            <p>A sua conta foi criada com sucesso.</p>
            <p><a href="${process.env.APP_URL}/verify/${user.verificationToken}">Confirmar Email</a></p>
        `,
        domain: 'app.exemplo.com',
        account: 'welcome',
        idempotency_key: `welcome-${user.id}`
    });
};
```

### **2. Recuperação de Password**
```javascript
const sendPasswordReset = async (user, resetToken) => {
    return await sendcraft.sendEmail({
        to: [user.email],
        subject: 'Recuperação de Password',
        html: `
            <h1>Recuperação de Password</h1>
            <p>Clique no link abaixo para redefinir a sua password:</p>
            <p><a href="${process.env.APP_URL}/reset/${resetToken}">Redefinir Password</a></p>
            <p><small>Este link expira em 1 hora.</small></p>
        `,
        domain: 'app.exemplo.com',
        account: 'security',
        idempotency_key: `reset-${user.id}-${Date.now()}`
    });
};
```

### **3. Campanha de Marketing Bulk**
```javascript
const sendMarketingCampaign = async (subscribers, campaign) => {
    const emailData = {
        to: subscribers.map(s => s.email),
        subject: campaign.subject,
        html: campaign.html_content,
        domain: 'marketing.exemplo.com',
        account: 'campaigns',
        bulk: true,
        from_name: 'Equipa Marketing',
        reply_to: 'marketing@exemplo.com',
        idempotency_key: `campaign-${campaign.id}`
    };
    
    return await sendcraft.sendEmail(emailData);
};
```

### **4. Notificação com Anexo**
```javascript
const fs = require('fs');

const sendInvoice = async (customer, invoiceData) => {
    // Ler e converter PDF para base64
    const pdfBuffer = fs.readFileSync(`invoices/invoice-${invoiceData.id}.pdf`);
    const pdfBase64 = pdfBuffer.toString('base64');
    
    return await sendcraft.sendEmail({
        to: [customer.email],
        subject: `Fatura #${invoiceData.number}`,
        html: `
            <h1>Nova Fatura</h1>
            <p>Olá ${customer.name},</p>
            <p>Segue em anexo a sua fatura #${invoiceData.number}.</p>
            <p><strong>Valor:</strong> €${invoiceData.total}</p>
        `,
        attachments: [{
            filename: `fatura-${invoiceData.number}.pdf`,
            content_type: 'application/pdf',
            content: pdfBase64
        }],
        domain: 'billing.exemplo.com',
        account: 'invoices',
        idempotency_key: `invoice-${invoiceData.id}`
    });
};
```

---

## 🛡️ Boas Práticas de Segurança

### **1. Gestão de API Keys**
```bash
# .env (NUNCA versionar)
SENDCRAFT_API_KEY=sendcraft_prod_xyz789...
SENDCRAFT_URL=https://sendcraft.empresa.com
```

```javascript
// config.js
const config = {
    sendcraft: {
        apiKey: process.env.SENDCRAFT_API_KEY,
        baseUrl: process.env.SENDCRAFT_URL
    }
};

// Validar configuração na inicialização
if (!config.sendcraft.apiKey) {
    throw new Error('SENDCRAFT_API_KEY não configurada');
}
```

### **2. Rate Limiting Client-side**
```javascript
const rateLimiter = require('bottleneck');

const limiter = new rateLimiter({
    maxConcurrent: 5,
    minTime: 200 // 200ms entre requests
});

const sendEmailWithRateLimit = limiter.wrap(sendcraft.sendEmail.bind(sendcraft));
```

### **3. Error Handling Robusto**
```javascript
const sendEmailWithRetry = async (emailData, maxRetries = 3) => {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            const result = await sendcraft.sendEmail(emailData);
            if (result.success) return result;
            
            if (attempt === maxRetries) {
                throw new Error(`Max retries reached: ${result.error}`);
            }
            
            // Exponential backoff
            await new Promise(resolve => 
                setTimeout(resolve, Math.pow(2, attempt) * 1000)
            );
        } catch (error) {
            if (attempt === maxRetries) throw error;
            await new Promise(resolve => 
                setTimeout(resolve, Math.pow(2, attempt) * 1000)
            );
        }
    }
};
```

### **4. Logging e Monitorização**
```javascript
const winston = require('winston');

const logger = winston.createLogger({
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
    ),
    transports: [
        new winston.transports.File({ filename: 'sendcraft.log' })
    ]
});

const sendEmailWithLogging = async (emailData) => {
    const startTime = Date.now();
    
    try {
        const result = await sendcraft.sendEmail(emailData);
        
        logger.info('Email sent successfully', {
            messageId: result.data.message_id,
            recipients: emailData.to.length,
            duration: Date.now() - startTime,
            subject: emailData.subject
        });
        
        return result;
    } catch (error) {
        logger.error('Email send failed', {
            error: error.message,
            recipients: emailData.to.length,
            duration: Date.now() - startTime,
            subject: emailData.subject
        });
        
        throw error;
    }
};
```

---

## 📊 Monitorização e Health Checks

### **1. Health Check Endpoint**
```javascript
// routes/health.js
app.get('/health/sendcraft', async (req, res) => {
    try {
        // Teste simples de conectividade
        const response = await axios.get(
            `${process.env.SENDCRAFT_URL}/api/v1/health`,
            { timeout: 5000 }
        );
        
        res.json({
            status: 'healthy',
            sendcraft: {
                reachable: true,
                responseTime: response.duration,
                version: response.data.version
            }
        });
    } catch (error) {
        res.status(503).json({
            status: 'unhealthy',
            sendcraft: {
                reachable: false,
                error: error.message
            }
        });
    }
});
```

### **2. Métricas de Email**
```javascript
const metrics = {
    sent: 0,
    failed: 0,
    totalDuration: 0
};

const sendEmailWithMetrics = async (emailData) => {
    const start = Date.now();
    
    try {
        const result = await sendcraft.sendEmail(emailData);
        metrics.sent++;
        metrics.totalDuration += (Date.now() - start);
        return result;
    } catch (error) {
        metrics.failed++;
        throw error;
    }
};

app.get('/metrics/email', (req, res) => {
    res.json({
        ...metrics,
        averageDuration: metrics.totalDuration / (metrics.sent + metrics.failed),
        successRate: metrics.sent / (metrics.sent + metrics.failed)
    });
});
```

---

## 🚀 Deploy e Configuração

### **Variáveis de Ambiente**
```bash
# Produção
SENDCRAFT_URL=https://sendcraft.empresa.com
SENDCRAFT_API_KEY=sendcraft_prod_xyz789...
SENDCRAFT_DOMAIN=empresa.com
SENDCRAFT_ACCOUNT=noreply

# Desenvolvimento
SENDCRAFT_URL=http://localhost:5000
SENDCRAFT_API_KEY=sendcraft_dev_abc123...
SENDCRAFT_DOMAIN=dev.empresa.com
SENDCRAFT_ACCOUNT=dev
```

### **Docker Configuration**
```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3000/health/sendcraft || exit 1

EXPOSE 3000
CMD ["npm", "start"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    environment:
      - SENDCRAFT_URL=${SENDCRAFT_URL}
      - SENDCRAFT_API_KEY=${SENDCRAFT_API_KEY}
      - SENDCRAFT_DOMAIN=${SENDCRAFT_DOMAIN}
    depends_on:
      - sendcraft
  
  sendcraft:
    image: sendcraft:latest
    environment:
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - sendcraft_data:/app/data
```

---

## 🆘 Troubleshooting

### **Problemas Comuns**

| Erro | Causa | Solução |
|------|-------|----------|
| 401 Unauthorized | API key inválida | Regenerar chave na UI |
| 404 Account Not Found | Conta/domínio não existem | Verificar configuração |
| 429 Rate Limit | Muitos requests | Implementar rate limiting |
| 500 SMTP Error | Problema SMTP | Testar SMTP na UI |
| Connection Timeout | SendCraft down | Verificar health check |

### **Debug Mode**
```javascript
const sendcraft = new SendCraftClient(
    process.env.SENDCRAFT_URL,
    process.env.SENDCRAFT_API_KEY,
    { debug: process.env.NODE_ENV === 'development' }
);
```

---

**Versão:** Integration Guide v1.0  
**Atualização:** 24 Outubro 2025  
**Compatibilidade:** SendCraft API v1+

**🔗 Links Úteis:**
- [API Reference](./api-reference.md)
- [UI Guide](./ui-guide.md)
- [Security Checklist](./security-checklist.md)