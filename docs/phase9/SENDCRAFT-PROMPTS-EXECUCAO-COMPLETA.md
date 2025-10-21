# 🎯 SendCraft - Prompts Execução Completa

## 📋 **PROMPTS PARA FINALIZAR SISTEMA PERFEITO**

Lista completa de prompts para executar todas as correções e implementações necessárias para ter o SendCraft 100% funcional.

---

## 🔧 **PROMPT 1: CORRIGIR TEMPLATE FORM ERROR**

**Para:** Cursor Agent Local  
**Prioridade:** ALTA (Bloqueia funcionalidade crítica)

```
SendCraft - Fix Template Form 500 Error and Improve System

## Context:
Testing showed 93% success rate but template creation form returns HTTP 500 error.
System Status: Ready for API phase, but template creation is broken.

## Critical Issue:
- URL: http://localhost:5000/templates/new returns 500 error
- Impact: Users cannot create email templates via web interface
- All other CRUD operations working correctly

## Tasks:

### 1. INVESTIGATE AND FIX TEMPLATE FORM
- Check sendcraft/routes/web.py template creation route
- Verify sendcraft/templates/templates/editor.html renders properly  
- Fix any missing form fields or validation issues
- Ensure both GET (display) and POST (process) work
- Add proper error handling and flash messages

### 2. VERIFY TEMPLATE MODEL INTEGRATION
- Check sendcraft/models/email_template.py exists and works
- Ensure database table 'email_templates' exists and accessible
- Verify all required fields have proper validation
- Test database insertion and retrieval

### 3. ENHANCE SAMPLE DATA
Add realistic sample templates for testing:

#### Welcome Email Template:
```html
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h1 style="color: #2c3e50;">Welcome to {{company_name}}!</h1>
    <p>Dear {{user_name}},</p>
    <p>Thank you for joining SendCraft. We're excited to have you!</p>
    <p>Best regards,<br>{{sender_name}}</p>
</div>
```

#### Order Confirmation Template:
```html
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #27ae60;">Order Confirmation #{{order_number}}</h2>
    <p>Dear {{customer_name}},</p>
    <p>Your order has been confirmed.</p>
    <div style="background: #f8f9fa; padding: 15px; margin: 20px 0;">
        <strong>Order Total: {{order_total}}</strong><br>
        <strong>Delivery Date: {{delivery_date}}</strong>
    </div>
</div>
```

### 4. TEST COMPLETE TEMPLATE WORKFLOW
- Template creation form loads without 500 error
- Template creation saves to database successfully
- Template appears in templates list
- Template editing and deletion work properly

## Success Criteria:
✅ Template creation form accessible (no 500 error)
✅ Templates can be created and saved successfully  
✅ Database populated with 3-5 realistic sample templates
✅ All template CRUD operations functional
✅ Automated tests achieve 100% pass rate

Fix template creation functionality and enhance with realistic sample data.
```

---

## 🚀 **PROMPT 2: IMPLEMENTAR API CORE ENDPOINTS**

**Para:** Claude Opus  
**Prioridade:** ALTA (Fase API principal)

```
SendCraft - Implement Complete REST API v1.0

## Context:
- System Status: 93% functional, ready for API development
- Current: Basic web interface working, database populated
- Goal: Complete REST API implementation for enterprise integration

## Architecture:
Base URL: /api/v1/
Response Format: Consistent JSON with success/error structure
Authentication: API key based (future) | Open access (current)

## Core API Endpoints to Implement:

### 1. DOMAINS API (/api/v1/domains)
- GET /api/v1/domains - List domains with pagination
- GET /api/v1/domains/{id} - Get specific domain
- POST /api/v1/domains - Create new domain
- PUT /api/v1/domains/{id} - Update domain
- DELETE /api/v1/domains/{id} - Delete domain
- Query filters: active, search, pagination (page, per_page)

### 2. ACCOUNTS API (/api/v1/accounts)  
- GET /api/v1/accounts - List email accounts with relationships
- GET /api/v1/accounts/{id} - Get specific account
- POST /api/v1/accounts - Create account with SMTP validation
- PUT /api/v1/accounts/{id} - Update account
- DELETE /api/v1/accounts/{id} - Delete account
- POST /api/v1/accounts/{id}/test - Test SMTP connection

### 3. TEMPLATES API (/api/v1/templates)
- GET /api/v1/templates - List templates with metadata
- GET /api/v1/templates/{id} - Get specific template
- POST /api/v1/templates - Create template
- PUT /api/v1/templates/{id} - Update template  
- DELETE /api/v1/templates/{id} - Delete template
- POST /api/v1/templates/{id}/preview - Render with variables

### 4. LOGS API (/api/v1/logs)
- GET /api/v1/logs - List email logs with filters
- GET /api/v1/logs/{id} - Get specific log
- Query filters: status, date_range, domain_id, account_id

### 5. RESPONSE STANDARDIZATION
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "timestamp": "2025-10-21T21:30:00Z"
}
```

## Implementation Requirements:
- Consistent HTTP status codes (200, 201, 400, 404, 500)
- Input validation with detailed error messages
- Pagination metadata for list endpoints
- Proper error handling middleware
- CORS headers for cross-origin requests
- Request/response logging

## File Structure:
```
sendcraft/api/v1/
├── __init__.py (blueprint registration)
├── domains.py (domains CRUD endpoints)
├── accounts.py (accounts CRUD + SMTP test)
├── templates.py (templates CRUD + preview)  
├── logs.py (logs read endpoints)
└── utils.py (common functions)
```

## Success Criteria:
✅ All CRUD endpoints implemented and tested
✅ Consistent JSON response format
✅ Proper error handling and validation
✅ Pagination working for list endpoints  
✅ API documentation updated
✅ Integration tests passing

Implement complete REST API v1.0 with enterprise-grade standards.
```

---

## 📧 **PROMPT 3: SISTEMA EMAIL SENDING**

**Para:** Claude Opus  
**Prioridade:** MÉDIA (Funcionalidade avançada)

```
SendCraft - Implement Email Sending System

## Context:
Core API endpoints implemented, now need email sending functionality.
Current: Templates and accounts configured, need actual email sending.

## Email Sending API to Implement:

### 1. EMAIL SENDING ENDPOINTS
- POST /api/v1/emails/send - Send single email
- POST /api/v1/emails/bulk - Send bulk emails  
- GET /api/v1/emails/{id}/status - Get email status
- GET /api/v1/emails/{id}/analytics - Get email metrics

### 2. TEMPLATE PROCESSING ENGINE
```python
class TemplateProcessor:
    def render_template(self, template_id, variables):
        # Load template from database
        # Replace {{variable}} with actual values
        # Return rendered HTML and text content
        
    def validate_variables(self, template_id, variables):
        # Check all required variables provided
        # Validate variable formats
```

### 3. SMTP INTEGRATION
```python
class SMTPManager:
    def send_email(self, account_id, email_data):
        # Load account SMTP settings
        # Connect to SMTP server
        # Send email with proper headers
        # Return tracking information
        
    def test_smtp_connection(self, account_id):
        # Test SMTP settings
        # Return connection status
```

### 4. EMAIL QUEUE SYSTEM (Basic)
```python
class EmailQueue:
    def queue_email(self, email_data):
        # Add to database queue
        # Process immediately or defer
        
    def process_queue(self):
        # Process pending emails
        # Update status in database
```

### 5. TRACKING SYSTEM
- Generate unique tracking IDs
- Store email logs with full metadata
- Track delivery status updates
- Record open/click events (future)

## Request/Response Examples:

### Send Email:
```json
POST /api/v1/emails/send
{
  "from_account_id": 1,
  "to_address": "customer@example.com",
  "template_id": 1,
  "variables": {
    "customer_name": "John Doe",
    "order_number": "ORD-2025-001"
  },
  "subject_override": "Custom Subject",
  "schedule_at": "2025-10-22T09:00:00Z"
}
```

### Response:
```json
{
  "success": true,
  "data": {
    "email_id": "email_abc123",
    "tracking_id": "track_xyz789",
    "status": "queued",
    "scheduled_at": "2025-10-22T09:00:00Z"
  }
}
```

## Success Criteria:
✅ Single email sending functional
✅ Template variable processing works
✅ SMTP integration with accounts
✅ Email logging and tracking
✅ Basic queue system
✅ Error handling for failed sends

Implement email sending system with template processing and SMTP integration.
```

---

## 🔐 **PROMPT 4: AUTHENTICATION E SECURITY**

**Para:** Claude Opus  
**Prioridade:** MÉDIA (Segurança)

```
SendCraft - Implement Authentication and Security System

## Context:
API endpoints functional, need authentication and security layer.
Current: Open access, need API key system for production use.

## Authentication System:

### 1. API KEY MANAGEMENT
```sql
CREATE TABLE api_keys (
    id INT PRIMARY KEY AUTO_INCREMENT,
    key_id VARCHAR(50) UNIQUE NOT NULL,
    key_secret_hash VARCHAR(255) NOT NULL, 
    name VARCHAR(255) NOT NULL,
    permissions JSON,
    rate_limit_per_hour INT DEFAULT 1000,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP NULL,
    last_used_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. API KEY ENDPOINTS
- POST /api/v1/auth/keys - Generate new API key
- GET /api/v1/auth/keys - List user's API keys  
- PUT /api/v1/auth/keys/{id} - Update API key
- DELETE /api/v1/auth/keys/{id} - Revoke API key

### 3. AUTHENTICATION MIDDLEWARE
```python
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
            
        # Validate API key
        key_record = validate_api_key(api_key)
        if not key_record:
            return jsonify({'error': 'Invalid API key'}), 401
            
        # Check rate limit
        if is_rate_limited(key_record):
            return jsonify({'error': 'Rate limit exceeded'}), 429
            
        g.api_key = key_record
        return f(*args, **kwargs)
    return decorated_function
```

### 4. RATE LIMITING SYSTEM
- Per-API-key rate limits
- Global rate limits
- Rate limit headers in responses
- Redis or memory-based storage

### 5. PERMISSIONS SYSTEM
```json
{
  "permissions": [
    "domains:read",
    "domains:write", 
    "accounts:read",
    "templates:read",
    "templates:write",
    "emails:send",
    "logs:read"
  ]
}
```

### 6. SECURITY HEADERS
- CORS properly configured
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection
- Request size limits

## API Key Format:
- Production: sk_live_abc123xyz789
- Development: sk_test_abc123xyz789  
- Test: sk_test_sandbox_abc123xyz789

## Success Criteria:
✅ API key generation and management
✅ Authentication middleware working
✅ Rate limiting per API key
✅ Permission-based access control
✅ Security headers configured
✅ Production-ready security

Implement enterprise authentication and security system.
```

---

## 📊 **PROMPT 5: ADVANCED FEATURES E POLISH**

**Para:** Claude Opus  
**Prioridade:** BAIXA (Funcionalidades avançadas)

```
SendCraft - Implement Advanced Features and System Polish

## Context:
Core system functional with API and authentication.
Goal: Advanced features for enterprise use and system polish.

## Advanced Features:

### 1. WEBHOOK SYSTEM
- POST /api/v1/webhooks - Create webhook endpoint
- GET /api/v1/webhooks - List webhooks
- PUT /api/v1/webhooks/{id} - Update webhook
- DELETE /api/v1/webhooks/{id} - Delete webhook

Event Types:
- email.sent, email.delivered, email.opened, email.clicked
- email.failed, email.bounced, email.spam_complaint

### 2. ANALYTICS AND REPORTING  
- GET /api/v1/analytics/overview - System overview
- GET /api/v1/analytics/domains/{id} - Domain analytics
- GET /api/v1/analytics/templates/{id} - Template performance
- GET /api/v1/analytics/campaigns - Campaign analytics

### 3. BULK OPERATIONS
- POST /api/v1/domains/bulk - Bulk create domains
- POST /api/v1/templates/bulk - Bulk template operations
- GET /api/v1/exports/logs - Export email logs CSV

### 4. ADVANCED TEMPLATE FEATURES
- Template versioning system
- Template inheritance and fragments
- Dynamic content based on recipient data
- A/B testing framework

### 5. EMAIL AUTOMATION
```python
class EmailAutomation:
    def create_drip_campaign(self, campaign_data):
        # Multi-step email sequences
        # Time-based triggers
        # Conditional logic
        
    def setup_behavioral_triggers(self, triggers):
        # Event-based email sending
        # Customer journey mapping
```

### 6. PERFORMANCE OPTIMIZATIONS
- Database query optimization
- Connection pooling tuning  
- Caching layer (Redis)
- Background job processing (Celery)

### 7. MONITORING AND LOGGING
```python
# Structured logging
import structlog

logger = structlog.get_logger()

# Performance monitoring  
@monitor_performance
def slow_function():
    # Log slow operations
    pass

# Health checks
GET /api/v1/health/detailed
{
  "status": "healthy",
  "database": "connected", 
  "redis": "connected",
  "smtp_accounts": "3/3 active",
  "queue_size": 12,
  "response_time": "45ms"
}
```

### 8. DOCUMENTATION GENERATION
- OpenAPI/Swagger specification
- Auto-generated API documentation
- Code examples for integration
- Postman collection export

## Success Criteria:
✅ Webhook system functional
✅ Analytics endpoints implemented
✅ Bulk operations working
✅ Performance optimized
✅ Monitoring and logging complete
✅ Documentation comprehensive

Implement advanced enterprise features and system polish.
```

---

## 🔧 **PROMPT 6: DEPLOYMENT E PRODUCTION READY**

**Para:** Cursor Agent Local  
**Prioridade:** MÉDIA (Preparação produção)

```
SendCraft - Prepare for Production Deployment

## Context:
System feature-complete, need production deployment preparation.
Target: Robust production deployment on dominios.pt server.

## Production Preparation Tasks:

### 1. ENVIRONMENT CONFIGURATION
Create production-ready configurations:

#### .env.production (Complete):
```
# Flask Configuration
FLASK_ENV=production
DEBUG=False
SECRET_KEY=sendcraft-production-super-secure-key-2025

# Database (Local MySQL on server)
MYSQL_URL=mysql+pymysql://artnshin_sendcraft:secure_password@localhost:3306/artnshin_sendcraft
SQLALCHEMY_ENGINE_OPTIONS={
    "pool_size": 10,
    "pool_timeout": 30, 
    "pool_recycle": 7200,
    "pool_pre_ping": True
}

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
WTF_CSRF_ENABLED=True

# API Configuration
API_RATE_LIMIT=5000/hour
API_KEY_REQUIRED=True

# Email Configuration  
SMTP_TIMEOUT=30
MAX_EMAIL_SIZE=10485760

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/sendcraft/sendcraft.log
```

### 2. SYSTEMD SERVICE CONFIGURATION
Create /etc/systemd/system/sendcraft.service:
```ini
[Unit]
Description=SendCraft Email Manager
After=network.target mysql.service

[Service]
Type=simple
User=sendcraft
Group=sendcraft
WorkingDirectory=/opt/sendcraft
Environment=PATH=/opt/sendcraft/venv/bin
ExecStart=/opt/sendcraft/venv/bin/python run_production.py
Restart=always
RestartSec=3

# Security
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/var/log/sendcraft /var/lib/sendcraft

[Install]
WantedBy=multi-user.target
```

### 3. NGINX REVERSE PROXY
Create /etc/nginx/sites-available/sendcraft:
```nginx
server {
    listen 80;
    server_name email.artnshine.pt;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name email.artnshine.pt;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/artnshine.pt.crt;
    ssl_certificate_key /etc/ssl/private/artnshine.pt.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    location / {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    location /static {
        alias /opt/sendcraft/sendcraft/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
        gzip_static on;
    }
    
    location /api {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
    }
}
```

### 4. DATABASE BACKUP SYSTEM
Create backup scripts:
```bash
#!/bin/bash
# /opt/sendcraft/scripts/backup_database.sh

BACKUP_DIR="/var/backups/sendcraft"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="sendcraft_backup_${DATE}.sql"

mkdir -p $BACKUP_DIR

mysqldump -u backup_user -p'backup_password' \
    --single-transaction \
    --routines \
    --triggers \
    artnshin_sendcraft > $BACKUP_DIR/$BACKUP_FILE

gzip $BACKUP_DIR/$BACKUP_FILE

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

### 5. MONITORING AND ALERTING
```python
# health_monitor.py
import requests
import smtplib
from email.mime.text import MIMEText

def check_system_health():
    try:
        # Check API health
        response = requests.get('https://email.artnshine.pt/api/v1/health')
        if response.status_code != 200:
            send_alert('API health check failed')
            
        # Check database
        health_data = response.json()
        if health_data.get('database') != 'connected':
            send_alert('Database connection failed')
            
        # Check SMTP accounts
        accounts_response = requests.get('https://email.artnshine.pt/api/v1/accounts')
        active_accounts = sum(1 for acc in accounts_response.json()['data'] if acc['is_active'])
        if active_accounts == 0:
            send_alert('No active SMTP accounts')
            
    except Exception as e:
        send_alert(f'Health check script failed: {str(e)}')

def send_alert(message):
    # Send alert email to admin
    pass
```

### 6. LOG ROTATION
Create /etc/logrotate.d/sendcraft:
```
/var/log/sendcraft/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        systemctl reload sendcraft
    endscript
}
```

### 7. DEPLOYMENT SCRIPT
```bash
#!/bin/bash
# deploy.sh - Production deployment script

set -e

echo "🚀 Deploying SendCraft to Production"

# Pull latest code
git pull origin main

# Backup database
./scripts/backup_database.sh

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations
flask db upgrade

# Update static files
flask collect-static

# Restart services
sudo systemctl restart sendcraft
sudo systemctl reload nginx

# Health check
sleep 5
curl -f https://email.artnshine.pt/api/v1/health || (echo "❌ Health check failed" && exit 1)

echo "✅ Deployment successful"
```

## Success Criteria:
✅ Production environment configured
✅ Systemd service working
✅ Nginx reverse proxy configured  
✅ SSL certificates installed
✅ Database backups automated
✅ Monitoring and alerting setup
✅ Deployment script functional

Prepare robust production deployment with monitoring and security.
```

---

## 📚 **PROMPT 7: DOCUMENTAÇÃO FINAL**

**Para:** Claude Opus  
**Prioridade:** BAIXA (Documentação)

```
SendCraft - Generate Complete Documentation

## Context:
System fully implemented and production-ready.
Need comprehensive documentation for developers and users.

## Documentation to Generate:

### 1. API DOCUMENTATION (OpenAPI/Swagger)
Generate complete API specification:
- All endpoints documented
- Request/response schemas
- Error codes and messages
- Authentication examples
- Rate limiting information

### 2. INTEGRATION GUIDES
Create step-by-step integration guides:

#### Python Integration:
```python
# Quick start example
from sendcraft_client import SendCraftClient

client = SendCraftClient(
    api_key="sk_live_your_key_here",
    base_url="https://email.artnshine.pt/api/v1"
)

# Send email
result = client.send_email(
    template_id="welcome_template",
    to_address="user@example.com", 
    variables={"name": "John Doe"}
)
```

#### JavaScript Integration:
```javascript
// Node.js example
const SendCraft = require('sendcraft-js');

const client = new SendCraft({
    apiKey: 'sk_live_your_key_here',
    baseURL: 'https://email.artnshine.pt/api/v1'
});

await client.emails.send({
    templateId: 'welcome_template',
    toAddress: 'user@example.com',
    variables: { name: 'John Doe' }
});
```

### 3. ADMIN DOCUMENTATION
- System installation guide
- Configuration reference
- Maintenance procedures
- Troubleshooting guide
- Performance tuning
- Security best practices

### 4. USER GUIDE
- Web interface walkthrough
- Domain management
- Email account setup
- Template creation
- Analytics interpretation

### 5. DEVELOPER DOCUMENTATION
- Code architecture overview
- Database schema documentation
- Extension development guide
- Plugin system (future)
- Webhook integration
- Testing framework

### 6. DEPLOYMENT GUIDE
- Server requirements
- Installation steps
- SSL configuration
- Monitoring setup
- Backup procedures
- Scaling recommendations

### 7. CHANGELOG AND VERSIONING
- Version history
- Breaking changes
- Migration guides
- Deprecation notices

## Documentation Structure:
```
docs/
├── README.md (Overview)
├── installation/
├── api-reference/  
├── integration-guides/
├── user-guide/
├── admin-guide/
├── developer-guide/
└── examples/
```

## Success Criteria:
✅ Complete API documentation
✅ Integration examples working
✅ Admin procedures documented
✅ User guide comprehensive  
✅ Developer docs complete
✅ Deployment guide tested

Generate comprehensive documentation for all audiences.
```

---

## 📋 **ORDEM EXECUÇÃO PROMPTS**

### **🔥 Prioridade ALTA (Executar Primeiro):**
1. **PROMPT 1** - Corrigir Template Form Error
2. **PROMPT 2** - Implementar API Core Endpoints

### **⚡ Prioridade MÉDIA (Executar Segundo):**
3. **PROMPT 3** - Sistema Email Sending
4. **PROMPT 4** - Authentication e Security  
5. **PROMPT 6** - Deployment e Production Ready

### **💎 Prioridade BAIXA (Executar Terceiro):**
6. **PROMPT 5** - Advanced Features e Polish
7. **PROMPT 7** - Documentação Final

---

## ✅ **CHECKLIST EXECUÇÃO**

### **Sistema Básico Funcional:**
- [ ] Template form error corrigido
- [ ] API Core endpoints implementados
- [ ] Database operacional
- [ ] Interface web 100% funcional

### **Sistema Enterprise:**
- [ ] Email sending system
- [ ] Authentication API keys
- [ ] Rate limiting ativo
- [ ] Security hardening

### **Sistema Production:**
- [ ] Deployment configuration
- [ ] Monitoring e logging
- [ ] Backup system
- [ ] SSL e Nginx configurado

### **Sistema Completo:**
- [ ] Advanced features
- [ ] Webhooks system
- [ ] Analytics avançadas
- [ ] Documentação completa

**Executa os prompts na ordem de prioridade para ter SendCraft email manager enterprise completo e funcional!** 🚀