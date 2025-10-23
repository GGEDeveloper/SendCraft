# 📧 SendCraft Phase 15: Exemplos de Uso da API

## 🚀 Exemplos Práticos cURL

### 1. Envio Simples sem Anexos
```bash
curl -X POST https://sendcraft.dominios.pt/api/v1/send \
  -H "Authorization: Bearer sua_api_key_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["cliente@exemplo.com"],
    "subject": "Bem-vindo à nossa loja!",
    "html": "<h1>Obrigado por se registrar!</h1><p>Esperamos que tenha uma óptima experiência.</p>",
    "text": "Obrigado por se registrar! Esperamos que tenha uma óptima experiência.",
    "domain": "alitools.pt",
    "account": "marketing",
    "from_name": "Equipa AliTools"
  }'
```

### 2. Confirmação de Encomenda com Fatura PDF
```bash
curl -X POST https://sendcraft.dominios.pt/api/v1/send \
  -H "Authorization: Bearer sua_api_key_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["cliente@exemplo.com"],
    "cc": ["vendas@alitools.pt"],
    "subject": "Confirmação de Encomenda #ALI-2025-001",
    "html": "<h1>Encomenda Confirmada!</h1><p>Obrigado pela sua compra. A fatura encontra-se em anexo.</p><p><strong>Número:</strong> ALI-2025-001<br><strong>Total:</strong> €129.99</p>",
    "text": "Encomenda Confirmada! Obrigado pela sua compra. Número: ALI-2025-001. Total: €129.99",
    "attachments": [
      {
        "filename": "fatura-ALI-2025-001.pdf",
        "content_type": "application/pdf",
        "content": "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwo..."
      }
    ],
    "domain": "alitools.pt",
    "account": "encomendas",
    "from_name": "AliTools - Encomendas",
    "reply_to": "suporte@alitools.pt",
    "idempotency_key": "order-ALI-2025-001-confirmation"
  }'
```

### 3. Notificação de Envio com Tracking
```bash
curl -X POST https://sendcraft.dominios.pt/api/v1/send \
  -H "Authorization: Bearer sua_api_key_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["cliente@exemplo.com"],
    "subject": "Encomenda #ALI-2025-001 Enviada - Tracking Disponível",
    "html": "<h1>A sua encomenda foi enviada! 📦</h1><p>A encomenda <strong>ALI-2025-001</strong> foi despachada e está a caminho.</p><p><strong>Número de tracking:</strong> CTT1234567890</p><p><a href=\"https://track.ctt.pt/tracking?number=CTT1234567890\">Acompanhar encomenda</a></p>",
    "text": "A sua encomenda ALI-2025-001 foi enviada! Tracking: CTT1234567890. Acompanhe em: https://track.ctt.pt/tracking?number=CTT1234567890",
    "domain": "alitools.pt",
    "account": "envios",
    "from_name": "AliTools - Envios",
    "idempotency_key": "shipping-ALI-2025-001-notification"
  }'
```

### 4. Newsletter para Lista (Bulk)
```bash
curl -X POST https://sendcraft.dominios.pt/api/v1/send \
  -H "Authorization: Bearer sua_api_key_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "to": [
      "cliente1@exemplo.com",
      "cliente2@exemplo.com", 
      "cliente3@exemplo.com"
    ],
    "subject": "🎯 Newsletter AliTools - Outubro 2025",
    "html": "<h1>Novidades este mês!</h1><p>Descubra os nossos novos produtos com descontos especiais.</p><ul><li>Produto A - 20% desconto</li><li>Produto B - 15% desconto</li></ul><p><a href=\"https://alitools.pt/newsletter\">Ver todas as ofertas</a></p>",
    "text": "Novidades este mês! Produto A com 20% desconto, Produto B com 15% desconto. Ver todas as ofertas: https://alitools.pt/newsletter",
    "attachments": [
      {
        "filename": "catalogo-outubro-2025.pdf",
        "content_type": "application/pdf",
        "content": "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwo..."
      }
    ],
    "domain": "alitools.pt",
    "account": "newsletter",
    "from_name": "AliTools Newsletter",
    "bulk": true
  }'
```

### 5. Consultar Status de Envio
```bash
curl -X GET https://sendcraft.dominios.pt/api/v1/send/MSG-2025-001234/status \
  -H "Authorization: Bearer sua_api_key_aqui"
```

### 6. Upload de Anexo Grande (Opcional)
```bash
curl -X POST https://sendcraft.dominios.pt/api/v1/attachments/upload \
  -H "Authorization: Bearer sua_api_key_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "catalogo-completo-2025.pdf",
    "content_type": "application/pdf",
    "content": "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwo..."
  }'
```

**Depois usar no envio:**
```bash
curl -X POST https://sendcraft.dominios.pt/api/v1/send \
  -H "Authorization: Bearer sua_api_key_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["cliente@exemplo.com"],
    "subject": "Catálogo Completo 2025",
    "html": "<h1>Catálogo em anexo</h1>",
    "attachments": [
      {"attachment_id": "ATT-2025-789"}
    ],
    "domain": "alitools.pt",
    "account": "marketing"
  }'
```

## 🔧 Integração com E-commerce (JavaScript/PHP)

### JavaScript (Node.js)
```javascript
const axios = require('axios');

async function sendOrderConfirmation(orderData) {
  try {
    const response = await axios.post('https://sendcraft.dominios.pt/api/v1/send', {
      to: [orderData.customerEmail],
      subject: `Confirmação de Encomenda #${orderData.orderNumber}`,
      html: generateOrderHTML(orderData),
      text: generateOrderText(orderData),
      attachments: [
        {
          filename: `fatura-${orderData.orderNumber}.pdf`,
          content_type: 'application/pdf',
          content: orderData.invoicePdfBase64
        }
      ],
      domain: 'alitools.pt',
      account: 'encomendas',
      from_name: 'AliTools',
      idempotency_key: `order-${orderData.orderNumber}-confirmation`
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.SENDCRAFT_API_KEY}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('Email enviado:', response.data);
    return response.data;
  } catch (error) {
    console.error('Erro ao enviar email:', error.response?.data || error.message);
    throw error;
  }
}
```

### PHP
```php
<?php

function sendOrderConfirmation($orderData) {
    $apiKey = $_ENV['SENDCRAFT_API_KEY'];
    $url = 'https://sendcraft.dominios.pt/api/v1/send';
    
    $payload = [
        'to' => [$orderData['customer_email']],
        'subject' => "Confirmação de Encomenda #{$orderData['order_number']}",
        'html' => generateOrderHTML($orderData),
        'text' => generateOrderText($orderData),
        'attachments' => [
            [
                'filename' => "fatura-{$orderData['order_number']}.pdf",
                'content_type' => 'application/pdf',
                'content' => $orderData['invoice_pdf_base64']
            ]
        ],
        'domain' => 'alitools.pt',
        'account' => 'encomendas',
        'from_name' => 'AliTools',
        'idempotency_key' => "order-{$orderData['order_number']}-confirmation"
    ];
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        "Authorization: Bearer $apiKey",
        'Content-Type: application/json'
    ]);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode === 200) {
        return json_decode($response, true);
    } else {
        throw new Exception("Erro ao enviar email: $response");
    }
}
?>
```

## 🧪 Testes de Validação

### Teste 1: Validação de Anexos
```bash
# Deve falhar - anexo muito grande
curl -X POST https://sendcraft.dominios.pt/api/v1/send \
  -H "Authorization: Bearer sua_api_key_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["teste@exemplo.com"],
    "subject": "Teste anexo grande",
    "html": "<p>Teste</p>",
    "attachments": [
      {
        "filename": "arquivo-15mb.pdf",
        "content_type": "application/pdf",
        "content": "'$(base64 -i /dev/urandom | head -c 20971520)'"
      }
    ],
    "domain": "alitools.pt",
    "account": "teste"
  }'
```

### Teste 2: Idempotency
```bash
# Primeiro envio
curl -X POST https://sendcraft.dominios.pt/api/v1/send \
  -H "Authorization: Bearer sua_api_key_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["teste@exemplo.com"],
    "subject": "Teste idempotency",
    "html": "<p>Primeiro envio</p>",
    "domain": "alitools.pt",
    "account": "teste",
    "idempotency_key": "teste-idempotency-123"
  }'

# Segundo envio (deve ser ignorado)
curl -X POST https://sendcraft.dominios.pt/api/v1/send \
  -H "Authorization: Bearer sua_api_key_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["teste@exemplo.com"],
    "subject": "Teste idempotency DUPLICADO",
    "html": "<p>Segundo envio - NÃO DEVE SER ENVIADO</p>",
    "domain": "alitools.pt",
    "account": "teste",
    "idempotency_key": "teste-idempotency-123"
  }'
```

---

**Nota:** Substituir `sua_api_key_aqui` pela chave API real obtida na interface do SendCraft.