# 🌐 SendCraft Phase 13 - Production Deployment Guide

## 🎯 Objectivo
Guia completo para deployment do SendCraft Enterprise em ambiente produção com email.artnshine.pt, incluindo configuração de segurança, API keys, e integração AliTools.pt.

## 📋 Pre-Requisites

### ✅ Code Validation
- **Phase 13A+B+C** implemented and tested
- **Main branch** up-to-date with all features
- **Testing protocol** executed successfully
- **Documentation** complete and validated

### 🌐 Infrastructure Requirements
- **Domain:** email.artnshine.pt configured
- **SSL Certificate:** Valid certificate installed
- **MySQL Database:** Production instance ready
- **Server:** cPanel hosting with Python support
- **DNS:** Proper A records configured

## 🚀 Deployment Steps

### Step 1: Server Preparation (10 min)

#### A. cPanel Configuration
```bash
# Domain setup:
1. Add subdomain: email.artnshine.pt
2. Point to public_html/sendcraft/
3. Enable Python app support
4. Configure WSGI application
5. Set Python version 3.9+
```

#### B. Database Setup
```sql
-- Production MySQL database
CREATE DATABASE sendcraft_prod;
CREATE USER 'sendcraft_prod'@'localhost' IDENTIFIED BY 'secure_prod_password_2024';
GRANT ALL PRIVILEGES ON sendcraft_prod.* TO 'sendcraft_prod'@'localhost';
FLUSH PRIVILEGES;
```

#### C. SSL Certificate
```bash
# Verify SSL certificate active for email.artnshine.pt
# Should show valid certificate in browser
# HTTPS redirect configured
```

### Step 2: Application Deployment (15 min)

#### A. Code Deployment
```bash
# Upload SendCraft code to server
cd /home/user/public_html/sendcraft/
git clone https://github.com/GGEDeveloper/SendCraft.git .
git checkout main  # Ensure main branch with Phase 13

# Set proper permissions
chmod -R 755 sendcraft/
chown -R user:user sendcraft/
```

#### B. Environment Configuration
```bash
# Create production environment file
cp .env.example .env.production

# Edit .env.production with production values:
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=ultra_secure_production_key_2024_change_immediately
DATABASE_URL=mysql://sendcraft_prod:secure_prod_password_2024@localhost/sendcraft_prod

# Email configuration
MAIL_SERVER=mail.artnshine.pt
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False

# API Keys
API_ADMIN_KEY=sendcraft-admin-prod-api-key-ultra-secure-2024
API_ALITOOLS_KEY=alitools-integration-prod-key-secure-2024
API_SERVICE_KEY=sendcraft-service-prod-key-secure-2024
```

#### C. Python Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db upgrade

# Create initial data if needed
python scripts/seed_production.py
```

### Step 3: Production Configuration (10 min)

#### A. Security Configuration
```python
# instance/config.py (production)
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_timeout': 30
    }
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # API Keys
    API_KEYS = {
        'admin': os.getenv('API_ADMIN_KEY'),
        'alitools': os.getenv('API_ALITOOLS_KEY'), 
        'service': os.getenv('API_SERVICE_KEY')
    }
    
    # Rate Limiting (Production)
    API_RATE_LIMIT = '10000/hour'  # Generous for business
    WEB_RATE_LIMIT = '2000/hour'   # Web protection
    
    # Email Settings
    MAIL_TIMEOUT = 30
    MAIL_MAX_EMAILS = 1000  # Per request limit
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/sendcraft/sendcraft.log'
```

#### B. WSGI Configuration
```python
# wsgi.py (production entry point)
import sys
import os

# Add application directory to path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

from sendcraft import create_app

# Create production app
application = create_app('production')

if __name__ == "__main__":
    application.run()
```

#### C. Web Server Configuration
```apache
# .htaccess (if using Apache)
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ wsgi.py/$1 [QSA,L]

# Security headers
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options SAMEORIGIN
Header always set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=31536000"
```

### Step 4: Email Account Configuration (5 min)

#### A. Production Email Accounts
```bash
# Configure production email accounts
python3 -c "
from sendcraft import create_app
from sendcraft.models import Domain, EmailAccount
from sendcraft.extensions import db

app = create_app('production')
with app.app_context():
    # Create domains
    alitools = Domain.create(
        name='alitools.pt',
        description='AliTools E-commerce Platform',
        is_active=True
    )
    
    artnshine = Domain.create(
        name='artnshine.pt', 
        description='ArtNShine Services',
        is_active=True
    )
    
    # Create email accounts with production credentials
    encomendas = EmailAccount.create(
        domain_id=alitools.id,
        local_part='encomendas',
        display_name='AliTools Encomendas',
        smtp_server='mail.alitools.pt',
        smtp_port=465,
        smtp_username='encomendas@alitools.pt',
        smtp_password='production_password_secure',
        use_ssl=True,
        imap_server='mail.alitools.pt',
        imap_port=993,
        imap_use_ssl=True,
        is_active=True
    )
    
    geral = EmailAccount.create(
        domain_id=artnshine.id,
        local_part='geral',
        display_name='ArtNShine Geral', 
        smtp_server='mail.artnshine.pt',
        smtp_port=465,
        smtp_username='geral@artnshine.pt',
        smtp_password='6+r&0io.ThlW2',
        use_ssl=True,
        imap_server='mail.artnshine.pt',
        imap_port=993, 
        imap_use_ssl=True,
        is_active=True
    )
    
    print('\u2705 Production email accounts configured')
"
```

### Step 5: API Integration Setup (5 min)

#### A. AliTools Integration
```javascript
// AliTools.pt integration example
// File: alitools-sendcraft-integration.js

class SendCraftIntegration {
    constructor() {
        this.apiUrl = 'https://email.artnshine.pt/api/v1';
        this.apiKey = 'alitools-integration-prod-key-secure-2024';
    }
    
    async sendOrderConfirmation(orderData) {
        const response = await fetch(`${this.apiUrl}/send/template`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                domain: 'alitools.pt',
                account: 'encomendas',
                template: 'order_confirmation',
                to: orderData.customer.email,
                variables: {
                    customer_name: orderData.customer.name,
                    order_number: orderData.order.id,
                    order_total: orderData.order.total,
                    order_items: orderData.order.items,
                    order_date: new Date().toLocaleDateString('pt-PT')
                }
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('Email sent successfully:', result.log_id);
            return { success: true, logId: result.log_id };
        } else {
            console.error('Email sending failed:', result.error);
            return { success: false, error: result.error };
        }
    }
}

// Usage in AliTools order processing:
const sendCraft = new SendCraftIntegration();
await sendCraft.sendOrderConfirmation(orderData);
```

### Step 6: Production Validation (10 min)

#### A. Health Checks
```bash
# Test production endpoints
curl https://email.artnshine.pt/api/v1/health
# Expected: {"status": "ok", "version": "1.0.0", ...}

curl https://email.artnshine.pt/api/docs  
# Should return HTML documentation page

# Test authentication
curl -H "Authorization: Bearer alitools-integration-prod-key-secure-2024" \
     https://email.artnshine.pt/api/v1/accounts/alitools.pt
# Should return account list
```

#### B. Email Sending Test
```bash
# Test production email sending
curl -X POST https://email.artnshine.pt/api/v1/send/direct \
     -H "Authorization: Bearer alitools-integration-prod-key-secure-2024" \
     -H "Content-Type: application/json" \
     -d '{
       "domain": "alitools.pt",
       "account": "encomendas",
       "to": "mmelo.deb@gmail.com",
       "subject": "SendCraft Production Test",
       "html": "<h1>\u2705 Production API Working!</h1>",
       "text": "Production API Working!"
     }'
# Expected: {"success": true, "log_id": X}
```

## 🔒 Production Security

### Environment Security
- **Environment variables** for all sensitive data
- **No hardcoded credentials** in code
- **Secure API keys** with rotation capability
- **Database credentials** encrypted
- **SSL/TLS** enforced for all connections

### API Security
- **Rate limiting** per API key
- **Request logging** comprehensive
- **Input validation** strict
- **CORS policies** restrictive
- **Error messages** sanitized

### Email Security
- **Password encryption** with production keys
- **IMAP/SMTP** over SSL/TLS only
- **HTML sanitization** active
- **Remote content** blocked by default

## 📊 Monitoring & Logging

### Production Logging
```python
# Structured logging configuration
LOGGING = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        },
        'json': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter'
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/sendcraft/sendcraft.log',
            'maxBytes': 50000000,  # 50MB
            'backupCount': 5,
            'formatter': 'json'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'file']
    }
}
```

### Health Monitoring
```python
# Health check endpoint enhancements
@api_bp.route('/health/detailed')
def health_detailed():
    return {
        'status': 'ok',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'database': check_database_connection(),
        'email_accounts': count_active_accounts(),
        'recent_emails': count_recent_emails(hours=24),
        'api_status': 'operational',
        'uptime': get_uptime_seconds()
    }
```

## 🌐 DNS & Domain Configuration

### DNS Records Required
```dns
# DNS configuration for email.artnshine.pt
A     email.artnshine.pt    [server_ip_address]
CNAME www.email.artnshine.pt email.artnshine.pt

# Email MX records (if hosting email)
MX    artnshine.pt    10 mail.artnshine.pt
TXT   artnshine.pt    "v=spf1 include:artnshine.pt ~all"
```

### SSL Certificate Validation
```bash
# Verify SSL certificate
openssl s_client -connect email.artnshine.pt:443 -servername email.artnshine.pt
# Should show valid certificate chain

# Test HTTPS redirect
curl -I http://email.artnshine.pt
# Should return 301 redirect to HTTPS
```

## 🔑 API Key Management

### Production API Keys
```python
# Generate secure API keys
import secrets
import string

def generate_api_key(length=64):
    alphabet = string.ascii_letters + string.digits + '-_'
    return 'sendcraft-' + ''.join(secrets.choice(alphabet) for i in range(length))

# Generated keys for production:
API_KEYS = {
    'admin': 'sendcraft-admin-[64-char-secure-key]',
    'alitools': 'sendcraft-alitools-[64-char-secure-key]',
    'service': 'sendcraft-service-[64-char-secure-key]'
}
```

### API Key Rotation
```python
# API key rotation procedure
1. Generate new API key
2. Update production environment
3. Notify integration partners (AliTools)
4. Grace period for transition
5. Deactivate old key
6. Monitor for usage of old key
```

## 📊 Performance Optimization

### Database Optimization
```sql
-- Production database indexes
CREATE INDEX idx_email_inbox_account_received ON email_inbox(account_id, received_at);
CREATE INDEX idx_email_inbox_account_read ON email_inbox(account_id, is_read);
CREATE INDEX idx_email_inbox_thread ON email_inbox(thread_id);
CREATE INDEX idx_email_accounts_active ON email_accounts(is_active);

-- Query optimization
ANALYZE TABLE email_inbox;
OPTIMIZE TABLE email_inbox;
```

### Caching Strategy
```python
# Redis caching for frequently accessed data
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Cache email counts and statistics
@cache.cached(timeout=300, key_prefix='email_stats')
def get_email_statistics(account_id):
    return EmailInbox.get_statistics(account_id)
```

### Static File Optimization
```bash
# Minify CSS and JavaScript for production
npm install -g clean-css-cli uglify-js

# Minify files
cleancss -o sendcraft/static/css/app.min.css sendcraft/static/css/app.css
uglifyjs sendcraft/static/js/app.js -o sendcraft/static/js/app.min.js

# Use minified versions in production templates
```

## 📊 Backup & Recovery

### Database Backup
```bash
#!/bin/bash
# Daily backup script
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u sendcraft_prod -p sendcraft_prod > /backups/sendcraft_$DATE.sql
gzip /backups/sendcraft_$DATE.sql

# Keep last 30 days of backups
find /backups -name "sendcraft_*.sql.gz" -mtime +30 -delete
```

### Application Backup
```bash
#!/bin/bash
# Code and configuration backup
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backups/sendcraft_app_$DATE.tar.gz \
    /home/user/public_html/sendcraft \
    --exclude=venv \
    --exclude=__pycache__ \
    --exclude=*.pyc
```

## 🔄 Maintenance Procedures

### Regular Maintenance
```bash
# Weekly maintenance script
#!/bin/bash

# Update application logs
sudo logrotate /etc/logrotate.d/sendcraft

# Clean old email data (optional - keep 1 year)
mysql -u sendcraft_prod -p sendcraft_prod -e "
    DELETE FROM email_inbox 
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 1 YEAR) 
    AND is_flagged = FALSE;
"

# Optimize database
mysql -u sendcraft_prod -p sendcraft_prod -e "OPTIMIZE TABLE email_inbox;"

# Check disk space
df -h /home/user/public_html/sendcraft

# Update dependencies (monthly)
source venv/bin/activate
pip list --outdated
```

### Monitoring Alerts
```python
# Basic monitoring integration
import requests

def send_alert(message, level='info'):
    # Integration with monitoring service
    webhook_url = os.getenv('MONITORING_WEBHOOK')
    if webhook_url:
        requests.post(webhook_url, json={
            'text': f'SendCraft Alert [{level.upper()}]: {message}',
            'timestamp': datetime.utcnow().isoformat()
        })

# Usage in error handlers
@app.errorhandler(500)
def internal_error(error):
    send_alert(f'500 Internal Server Error: {error}', 'error')
    return render_template('errors/500.html'), 500
```

## 📋 Production Checklist

### Pre-Deployment
☐ Code tested thoroughly in development
☐ Database migrations prepared
☐ Environment variables configured
☐ SSL certificate installed and valid
☐ DNS records pointing correctly
☐ Backup procedures tested

### Deployment
☐ Code uploaded to production server
☐ Virtual environment created and dependencies installed
☐ Database initialized with migrations
☐ Email accounts configured with production credentials
☐ WSGI application configured
☐ Web server configuration active

### Post-Deployment
☐ Health endpoints responding correctly
☐ API documentation accessible
☐ Email sending functionality tested
☐ IMAP synchronization working
☐ Multi-account interface functional
☐ All Phase 13 features operational
☐ Performance metrics within targets
☐ Monitoring and logging active

### Integration Testing
☐ AliTools API key configured
☐ Test email sent from AliTools integration
☐ Order confirmation template working
☐ Error handling and rate limiting functional
☐ Production monitoring alerts active

## 🎉 Success Metrics

### Performance Targets
- **API Response Time:** <500ms average
- **Email Sending:** <5 seconds per email
- **IMAP Sync:** <30 seconds for 50 emails
- **Database Queries:** <100ms average
- **Page Load Times:** <3 seconds

### Reliability Targets  
- **Uptime:** >99.5%
- **Email Delivery Rate:** >98%
- **API Success Rate:** >99%
- **Error Rate:** <1% of requests

**SendCraft Enterprise production deployment guide ensures reliable, secure, and performant email management system.**