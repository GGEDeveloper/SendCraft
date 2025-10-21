# 🚀 SendCraft API - Documentação Completa v1.0

## 📋 **VISÃO GERAL**

SendCraft Email Manager API é um sistema RESTful para gestão empresarial de emails, domínios, contas SMTP e templates HTML.

**Base URL:** `http://localhost:5000` (Development) | `http://email.artnshine.pt:9000` (Production)  
**Version:** 1.0  
**Authentication:** API Key (futuro) | Open access (atual)  

---

## 🏗️ **ARQUITETURA API**

### **Estrutura Base:**
```
/api/v1/               # API Version 1
├── health             # Health check endpoint
├── stats              # System statistics
├── domains/           # Domain management
├── accounts/          # Email account management  
├── templates/         # Email template management
└── logs/              # Email log management
```

### **Response Format:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "timestamp": "2025-10-21T21:30:00Z"
}
```

### **Error Format:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { ... }
  },
  "timestamp": "2025-10-21T21:30:00Z"
}
```

---

## 📊 **ENDPOINTS DISPONÍVEIS**

### **🔍 1. HEALTH & STATS**

#### **GET /api/v1/health**
System health check
```bash
curl http://localhost:5000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0",
  "database": "connected",
  "timestamp": "2025-10-21T21:30:00Z"
}
```

#### **GET /api/stats**
System statistics dashboard
```bash
curl http://localhost:5000/api/stats
curl http://localhost:5000/api/stats?days=7
```

**Response:**
```json
{
  "daily_stats": [
    {
      "date": "2025-10-21",
      "domains": 3,
      "accounts": 2,
      "templates": 1,
      "logs": 5,
      "emails_sent": 12
    }
  ],
  "totals": {
    "domains": 3,
    "accounts": 2,
    "templates": 1,
    "logs": 15
  }
}
```

---

## 🌐 **2. DOMAINS API**

### **GET /api/v1/domains**
List all domains
```bash
curl http://localhost:5000/api/v1/domains
curl http://localhost:5000/api/v1/domains?active=true&page=1&per_page=10
```

**Query Parameters:**
- `active` (boolean): Filter by active status
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20, max: 100)
- `search` (string): Search in name/description

**Response:**
```json
{
  "success": true,
  "data": {
    "domains": [
      {
        "id": 1,
        "name": "alitools.pt",
        "description": "AliTools B2B Platform",
        "is_active": true,
        "created_at": "2025-10-21T10:00:00Z",
        "updated_at": "2025-10-21T10:00:00Z",
        "email_accounts_count": 2,
        "emails_sent_count": 25
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 3,
      "pages": 1
    }
  }
}
```

### **GET /api/v1/domains/{id}**
Get specific domain
```bash
curl http://localhost:5000/api/v1/domains/1
```

### **POST /api/v1/domains**
Create new domain
```bash
curl -X POST http://localhost:5000/api/v1/domains \
  -H "Content-Type: application/json" \
  -d '{
    "name": "newdomain.com",
    "description": "New domain for testing",
    "is_active": true
  }'
```

**Request Body:**
```json
{
  "name": "string (required, unique)",
  "description": "string (optional)",
  "is_active": "boolean (default: true)"
}
```

### **PUT /api/v1/domains/{id}**
Update domain
```bash
curl -X PUT http://localhost:5000/api/v1/domains/1 \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description",
    "is_active": false
  }'
```

### **DELETE /api/v1/domains/{id}**
Delete domain
```bash
curl -X DELETE http://localhost:5000/api/v1/domains/1
```

---

## 📧 **3. EMAIL ACCOUNTS API**

### **GET /api/v1/accounts**
List email accounts
```bash
curl http://localhost:5000/api/v1/accounts
curl http://localhost:5000/api/v1/accounts?domain_id=1&is_active=true
```

**Query Parameters:**
- `domain_id` (int): Filter by domain
- `is_active` (boolean): Filter by active status
- `page`, `per_page`, `search`: Standard pagination

**Response:**
```json
{
  "success": true,
  "data": {
    "accounts": [
      {
        "id": 1,
        "email_address": "info@alitools.pt",
        "display_name": "AliTools Support",
        "domain_id": 1,
        "domain_name": "alitools.pt",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_username": "info@alitools.pt",
        "use_tls": true,
        "is_active": true,
        "created_at": "2025-10-21T10:00:00Z",
        "last_used": "2025-10-21T15:30:00Z",
        "emails_sent": 15
      }
    ]
  }
}
```

### **POST /api/v1/accounts**
Create email account
```bash
curl -X POST http://localhost:5000/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "support@example.com",
    "display_name": "Support Team",
    "domain_id": 1,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "support@example.com",
    "smtp_password": "encrypted_password",
    "use_tls": true
  }'
```

### **POST /api/v1/accounts/{id}/test**
Test SMTP connection
```bash
curl -X POST http://localhost:5000/api/v1/accounts/1/test
```

**Response:**
```json
{
  "success": true,
  "data": {
    "test_result": "success",
    "connection_time": 0.5,
    "message": "SMTP connection successful"
  }
}
```

---

## 📝 **4. TEMPLATES API**

### **GET /api/v1/templates**
List email templates
```bash
curl http://localhost:5000/api/v1/templates
curl http://localhost:5000/api/v1/templates?type=welcome&search=order
```

**Query Parameters:**
- `type` (string): Filter by template type
- `search` (string): Search in name/subject/content

**Response:**
```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "id": 1,
        "name": "Welcome Email",
        "subject": "Welcome to {{company_name}}!",
        "template_type": "welcome",
        "html_content": "<div>...</div>",
        "variables": ["company_name", "user_name", "sender_name"],
        "created_at": "2025-10-21T10:00:00Z",
        "usage_count": 25
      }
    ]
  }
}
```

### **GET /api/v1/templates/{id}/preview**
Preview template with variables
```bash
curl -X POST http://localhost:5000/api/v1/templates/1/preview \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "company_name": "SendCraft",
      "user_name": "John Doe",
      "sender_name": "Support Team"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "subject": "Welcome to SendCraft!",
    "html_content": "<div><h1>Welcome to SendCraft!</h1><p>Dear John Doe,</p>...</div>",
    "text_content": "Welcome to SendCraft! Dear John Doe, ..."
  }
}
```

---

## 📊 **5. LOGS API**

### **GET /api/v1/logs**
List email logs
```bash
curl http://localhost:5000/api/v1/logs
curl "http://localhost:5000/api/v1/logs?status=sent&from_date=2025-10-20&to_date=2025-10-21"
```

**Query Parameters:**
- `status` (string): Filter by status (sent, delivered, failed, bounced)
- `from_date`, `to_date` (ISO date): Date range filter
- `domain_id`, `account_id`: Filter by domain/account
- `search`: Search in subject/recipient

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": 1,
        "from_address": "info@alitools.pt",
        "to_address": "customer@example.com",
        "subject": "Order Confirmation #12345",
        "status": "delivered",
        "template_id": 2,
        "template_name": "Order Confirmation",
        "account_id": 1,
        "domain_id": 1,
        "sent_at": "2025-10-21T15:30:00Z",
        "delivered_at": "2025-10-21T15:31:00Z",
        "error_message": null,
        "tracking_id": "msg_abc123",
        "opens": 1,
        "clicks": 0
      }
    ]
  }
}
```

---

## 🔐 **6. AUTHENTICATION (FUTURO)**

### **POST /api/v1/auth/keys**
Generate API key
```bash
curl -X POST http://localhost:5000/api/v1/auth/keys \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production App Key",
    "permissions": ["read:all", "write:logs"],
    "expires_in": 365
  }'
```

### **Headers Authentication:**
```bash
curl http://localhost:5000/api/v1/domains \
  -H "X-API-Key: sk_live_abc123xyz789"
```

---

## 📨 **7. EMAIL SENDING API (FUTURO)**

### **POST /api/v1/emails/send**
Send email using template
```bash
curl -X POST http://localhost:5000/api/v1/emails/send \
  -H "Content-Type: application/json" \
  -d '{
    "from_account_id": 1,
    "to_address": "customer@example.com",
    "template_id": 1,
    "variables": {
      "company_name": "AliTools",
      "user_name": "João Silva",
      "order_number": "ALI-2025-001"
    },
    "schedule_at": "2025-10-22T09:00:00Z"
  }'
```

### **POST /api/v1/emails/bulk**
Send bulk emails
```bash
curl -X POST http://localhost:5000/api/v1/emails/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "from_account_id": 1,
    "template_id": 1,
    "recipients": [
      {
        "email": "user1@example.com",
        "variables": {"name": "User 1", "code": "ABC123"}
      },
      {
        "email": "user2@example.com", 
        "variables": {"name": "User 2", "code": "XYZ789"}
      }
    ]
  }'
```

---

## 📈 **8. RATE LIMITS & QUOTAS**

### **Current Limits:**
- **API Calls:** 1000/hour (development), 5000/hour (production)
- **Bulk Email:** 100 recipients/request
- **File Upload:** 10MB max
- **Request Timeout:** 30 seconds

### **Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1698847200
```

---

## 🚨 **9. ERROR CODES**

### **HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Rate Limited
- `500` - Internal Server Error

### **Custom Error Codes:**
- `VALIDATION_ERROR` - Input validation failed
- `DUPLICATE_ENTRY` - Resource already exists
- `SMTP_CONNECTION_FAILED` - Email account SMTP test failed
- `TEMPLATE_RENDER_ERROR` - Template processing failed
- `RATE_LIMIT_EXCEEDED` - API rate limit exceeded

---

## 🛠️ **10. DESENVOLVIMENTO**

### **Testing Endpoints:**
```bash
# Base connectivity
curl http://localhost:5000/api/v1/health

# Get all resources
curl http://localhost:5000/api/v1/domains
curl http://localhost:5000/api/v1/accounts  
curl http://localhost:5000/api/v1/templates
curl http://localhost:5000/api/v1/logs

# Statistics
curl http://localhost:5000/api/stats?days=7
```

### **Database Schema:**
```sql
-- Domains
CREATE TABLE domains (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) UNIQUE NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Email Accounts  
CREATE TABLE email_accounts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  email_address VARCHAR(255) UNIQUE NOT NULL,
  display_name VARCHAR(255),
  domain_id INT,
  smtp_server VARCHAR(255) NOT NULL,
  smtp_port INT NOT NULL,
  smtp_username VARCHAR(255) NOT NULL,
  smtp_password_encrypted TEXT NOT NULL,
  use_tls BOOLEAN DEFAULT TRUE,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (domain_id) REFERENCES domains(id)
);

-- Email Templates
CREATE TABLE email_templates (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  subject VARCHAR(255) NOT NULL,
  html_content TEXT NOT NULL,
  template_type VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Email Logs
CREATE TABLE email_logs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  from_address VARCHAR(255) NOT NULL,
  to_address VARCHAR(255) NOT NULL,
  subject VARCHAR(255),
  status ENUM('sent', 'delivered', 'failed', 'bounced') NOT NULL,
  template_id INT,
  account_id INT,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (template_id) REFERENCES email_templates(id),
  FOREIGN KEY (account_id) REFERENCES email_accounts(id)
);
```

### **Environment Variables:**
```bash
# Development
FLASK_ENV=development
MYSQL_URL=mysql+pymysql://user:pass@artnshine.pt:3306/artnshin_sendcraft

# Production  
FLASK_ENV=production
MYSQL_URL=mysql+pymysql://user:pass@localhost:3306/artnshin_sendcraft
API_RATE_LIMIT=5000/hour
```

---

## 📚 **11. EXEMPLOS INTEGRAÇÃO**

### **Python Client:**
```python
import requests

# Base configuration
BASE_URL = "http://localhost:5000"
headers = {"Content-Type": "application/json"}

# Get domains
response = requests.get(f"{BASE_URL}/api/v1/domains", headers=headers)
domains = response.json()["data"]["domains"]

# Create email account
account_data = {
    "email_address": "support@mycompany.com",
    "display_name": "Support Team",
    "domain_id": 1,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "support@mycompany.com",
    "smtp_password": "app_password",
    "use_tls": True
}
response = requests.post(f"{BASE_URL}/api/v1/accounts", json=account_data, headers=headers)
```

### **JavaScript Client:**
```javascript
const sendCraftAPI = {
  baseURL: 'http://localhost:5000',
  
  async getDomains() {
    const response = await fetch(`${this.baseURL}/api/v1/domains`);
    return response.json();
  },
  
  async createTemplate(templateData) {
    const response = await fetch(`${this.baseURL}/api/v1/templates`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(templateData)
    });
    return response.json();
  },
  
  async getStats(days = 7) {
    const response = await fetch(`${this.baseURL}/api/stats?days=${days}`);
    return response.json();
  }
};
```

---

## 🎯 **NEXT STEPS - API DEVELOPMENT**

### **Priority 1: Core API Implementation**
1. Implement all CRUD endpoints for domains, accounts, templates, logs
2. Add proper validation and error handling
3. Implement pagination for all list endpoints
4. Add search and filtering capabilities

### **Priority 2: Email Sending**
1. Implement email sending API endpoints
2. Add template variable processing
3. Add email queue and background processing
4. Implement email tracking (opens, clicks)

### **Priority 3: Authentication & Security**
1. Implement API key authentication
2. Add role-based permissions
3. Add rate limiting per API key
4. Add request logging and monitoring

### **Priority 4: Advanced Features**
1. Webhook support for email events
2. Email scheduling system
3. A/B testing for templates
4. Analytics and reporting endpoints

**🚀 SendCraft API está pronto para implementação completa!**