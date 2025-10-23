# SendCraft External API Documentation

## Overview
SendCraft External API provides REST endpoints for external applications to send emails programmatically. Designed for AliTools.pt e-commerce integration.

**Base URL:** `https://sendcraft.dominios.pt/api/v1`

## Authentication

All API requests require authentication using an API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

Or via X-API-Key header:
```
X-API-Key: YOUR_API_KEY
```

## Endpoints

### Health Check
```
GET /api/v1/health
```
No authentication required. Returns API status.

**Response:**
```json
{
  "status": "healthy",
  "service": "SendCraft External API",
  "version": "1.0.0"
}
```

---

### Send Direct Email
```
POST /api/v1/send/direct
```
Send email directly without using a template.

**Request Body:**
```json
{
  "domain": "alitools.pt",
  "account": "encomendas",
  "to": "customer@example.com",
  "subject": "Order Confirmation",
  "html": "<h1>Thank you!</h1>",
  "text": "Thank you for your order!"
}
```

**Response:**
```json
{
  "success": true,
  "log_id": 123,
  "message": "Email sent successfully",
  "message_id": "<message-id>",
  "from": "encomendas@alitools.pt",
  "to": "customer@example.com",
  "subject": "Order Confirmation"
}
```

---

### Send Template Email
```
POST /api/v1/send/template
```
Send email using a predefined template.

**Request Body:**
```json
{
  "domain": "alitools.pt",
  "account": "encomendas",
  "template": "order_confirmation",
  "to": "customer@example.com",
  "variables": {
    "customer_name": "João Silva",
    "order_number": "ALI-2025-001",
    "total": "149.99"
  }
}
```

**Response:**
```json
{
  "success": true,
  "log_id": 123,
  "message": "Email sent successfully",
  "message_id": "<message-id>",
  "template_used": "order_confirmation",
  "variables_count": 3,
  "from": "encomendas@alitools.pt",
  "to": "customer@example.com"
}
```

---

### List Domain Accounts
```
GET /api/v1/accounts/<domain>
```
List all email accounts for a domain.

**Example:** `GET /api/v1/accounts/alitools.pt`

**Response:**
```json
{
  "domain": "alitools.pt",
  "accounts": [
    {
      "email": "encomendas@alitools.pt",
      "display_name": "Encomendas",
      "is_active": true,
      "daily_limit": 1000,
      "monthly_limit": 20000,
      "emails_sent_today": 5,
      "emails_sent_this_month": 120
    }
  ],
  "count": 1
}
```

---

### List Domain Templates
```
GET /api/v1/templates/<domain>
```
List all email templates for a domain.

**Example:** `GET /api/v1/templates/alitools.pt`

**Response:**
```json
{
  "domain": "alitools.pt",
  "templates": [
    {
      "key": "order_confirmation",
      "name": "Order Confirmation",
      "subject": "Order #{{order_number}} Confirmed",
      "category": "orders",
      "is_active": true,
      "required_variables": ["order_number", "customer_name"],
      "optional_variables": ["total", "payment_method"]
    }
  ],
  "count": 1
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid data or missing required fields |
| 401 | Unauthorized - Missing or invalid API key |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Account limit exceeded |
| 500 | Internal Server Error |

---

## Rate Limiting

Each account has daily and monthly limits configured. Check account limits before sending emails to avoid 429 errors.

---

## Interactive Documentation

Visit https://sendcraft.dominios.pt/api/docs for interactive API documentation.

---

## AliTools Integration Example

### Sending Order Confirmation Email

```python
import requests

API_KEY = "your_api_key_here"
API_URL = "https://sendcraft.dominios.pt/api/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "domain": "alitools.pt",
    "account": "encomendas",
    "template": "order_confirmation",
    "to": "customer@example.com",
    "variables": {
        "customer_name": "João Silva",
        "order_number": "ALI-2025-001",
        "total": "149.99"
    }
}

response = requests.post(f"{API_URL}/send/template", json=data, headers=headers)
print(response.json())
```

---

## Support

For API keys and support, contact: geral@alitools.pt

