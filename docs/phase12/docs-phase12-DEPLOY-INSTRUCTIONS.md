# 🚀 **DEPLOY-INSTRUCTIONS.md**

## 📋 **Deploy Completo SendCraft Produção**

### **PRÉ-REQUISITOS:**
✅ Todos ficheiros `FILES-TO-CREATE.md` criados  
✅ Teste local funcionou
✅ GitHub main branch atualizado

---

## 🎯 **SEQUÊNCIA EXACTA DEPLOY:**

### **STEP 1: GIT COMMIT & PUSH (Local)**

```bash
# Verificar todos ficheiros criados
git status
git add .
git commit -m "feat: Phase 12 production deployment complete

- app.py: cPanel production entry point
- passenger_wsgi.py: WSGI entry point
- instance/config.py: production secrets template
- .cpanel.yml: complete deployment with pip install
- requirements.txt: added Flask-Migrate, chardet, Werkzeug
- Maintains run_dev.py compatibility for development

Enables email.artnshine.pt production deployment"

git push origin main
```

---

## 🔧 **STEP 2: cPanel DATABASE SETUP**

### **2.1 MySQL Database (se não existe):**
```
cPanel Login: https://dominios.pt:2083
Username: artnshin
Password: [senha_cpanel]

→ MySQL Database Wizard:
  Database Name: artnshin_sendcraft
  Username: artnshin_sendcraft  
  Password: g>bxZmj%=JZt9Z,i
  Privileges: ALL PRIVILEGES ✅

→ Remote MySQL:
  Add Access Host: % (wildcard) ✅
```

---

## 🔧 **STEP 3: cPanel GIT REPOSITORY**

### **3.1 Create Git Repository:**
```
cPanel → Git Version Control → Create Repository:

Repository URL: https://github.com/GGEDeveloper/SendCraft.git
Repository Path: public_html/sendcraft
Branch: main ✅
Clone Repository: ✅

Status: Wait for "Repository created successfully"
```

### **3.2 Configure Deploy Key (se necessário):**
```
GitHub → Settings → Deploy keys → Add deploy key:
Title: cPanel-SendCraft-Deploy
Key: [copiar de cPanel Git → Manage → Deploy Key]
Allow write access: ✅
```

---

## 🔧 **STEP 4: cPanel PYTHON APP**

### **4.1 Create Python Application:**
```
cPanel → Setup Python App → Create Application:

Python Version: 3.9 ✅
Application Root: public_html/sendcraft ✅  
Application URL: email.artnshine.pt ✅
Application Startup File: app.py ✅
Application Entry Point: application ✅

Create: ✅
```

### **4.2 Environment Variables:**
```
cPanel → Python App → sendcraft → Environment Variables:

Add Variables:
FLASK_ENV = production
SECRET_KEY = sendcraft-production-secret-key-32-characters-change-this!
ENCRYPTION_KEY = sendcraft-encrypt-key-32-chars-change-production!
MYSQL_URL = mysql+pymysql://artnshin_sendcraft:g>bxZmj%25=JZt9Z%2Ci@localhost:3306/artnshin_sendcraft
DEFAULT_FROM_EMAIL = noreply@artnshine.pt
ADMIN_EMAIL = admin@artnshine.pt

Save: ✅
```

---

## 🚀 **STEP 5: DEPLOY & INSTALL**

### **5.1 Deploy Code:**
```
cPanel → Git Version Control → Manage (sendcraft):
Last Deployment: Check timestamp
Pull or Deploy: ✅ Execute

Wait for: "Deployment completed successfully" ✅
```

### **5.2 Install Dependencies:**
```
cPanel → Python App → sendcraft:
Run Pip Install: ✅ Execute

Output should show:
✅ Flask==2.3.3
✅ Flask-SQLAlchemy==3.0.5  
✅ Flask-Migrate==4.0.5
✅ PyMySQL==1.0.2
✅ chardet==5.2.0
✅ ... (all dependencies)

Status: "Pip install completed successfully"
```

---

## 💾 **STEP 6: DATABASE INITIALIZATION**

### **6.1 SSH Terminal Access:**
```bash
# cPanel → Terminal, ou SSH:
ssh artnshin@artnshine.pt

# Navigate to app
cd public_html/sendcraft

# Activate virtual environment  
source /home/artnshin/virtualenv/public_html/sendcraft/3.9/bin/activate
```

### **6.2 Initialize Database:**
```python
# Run database setup
python3 -c "
import os
os.environ['FLASK_ENV'] = 'production'

from sendcraft import create_app
from sendcraft.extensions import db
from sendcraft.models import Domain, EmailAccount

print('🔧 Initializing SendCraft production database...')

app = create_app('production')
with app.app_context():
    print('📊 Creating database tables...')
    db.create_all()
    
    print('🌐 Creating alitools.pt domain...')
    domain = Domain.query.filter_by(name='alitools.pt').first()
    if not domain:
        domain = Domain(name='alitools.pt')
        db.session.add(domain)
        db.session.flush()  # Get domain.id
    
    print(f'✅ Domain: {domain.name} (ID: {domain.id})')
    
    print('📧 Creating geral@alitools.pt account...')
    account = EmailAccount.query.filter_by(email_address='geral@alitools.pt').first()
    if not account:
        account = EmailAccount(
            domain_id=domain.id,
            email_address='geral@alitools.pt',
            username='geral@alitools.pt',
            display_name='Geral AliTools',
            imap_server='mail.alitools.pt',
            imap_port=993,
            imap_use_ssl=True,
            smtp_server='mail.alitools.pt',
            smtp_port=465,
            smtp_use_ssl=True,
            is_active=True,
            auto_sync_enabled=True
        )
        # Set encrypted password
        account.set_encrypted_password('6+r&0io.ThlW', app.config['SECRET_KEY'])
        db.session.add(account)
    
    print(f'✅ Account: {account.email_address} (Active: {account.is_active})')
    
    db.session.commit()
    print('💾 Database initialized successfully!')
    
    # Test account encryption
    config = account.get_imap_config(app.config['SECRET_KEY'])
    print(f'🔐 IMAP config: {config[\"server\"]}:{config[\"port\"]} SSL:{config[\"use_ssl\"]}')
"
```

---

## ✅ **STEP 7: RESTART & VERIFY**

### **7.1 Restart Python App:**
```
cPanel → Python App → sendcraft → Restart: ✅ Execute

Status: "Application restarted successfully"
```

### **7.2 Health Check:**
```bash
# Test API health
curl -s https://email.artnshine.pt/api/v1/health

Expected output:
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "production",
  "database": "connected",
  "timestamp": "2025-10-22T17:45:00Z"
}
```

### **7.3 Web Interface:**
```bash
# Browser test:
https://email.artnshine.pt

Expected: SendCraft login/interface ✅

# Specific page:
https://email.artnshine.pt/emails/inbox

Expected: geral@alitools.pt inbox interface ✅
```

---

## 🧪 **STEP 8: IMAP SYNC TEST**

### **8.1 Manual IMAP Sync:**
```bash
# Test real IMAP sync (production - sem VPN issues)
curl -s -X POST "https://email.artnshine.pt/api/v1/emails/inbox/sync/1" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"folder":"INBOX","limit":15,"full_sync":false}'

Expected output:
{
  "status": "success",
  "synced_emails": 10,
  "total_emails": 85,
  "sync_time": "2.34s",
  "last_sync": "2025-10-22T17:45:30Z"
}
```

### **8.2 Verify Database:**
```python
# SSH terminal:
python3 -c "
import os
os.environ['FLASK_ENV'] = 'production'

from sendcraft import create_app
from sendcraft.models.email_inbox import EmailInbox
from sendcraft.models.account import EmailAccount

app = create_app('production')
with app.app_context():
    account = EmailAccount.query.filter_by(email_address='geral@alitools.pt').first()
    emails = EmailInbox.query.filter_by(account_id=account.id).limit(5).all()
    
    print(f'📊 Total emails stored: {EmailInbox.query.filter_by(account_id=account.id).count()}')
    print('📧 Latest emails:')
    for email in emails:
        print(f'  - {email.subject[:50]} | From: {email.from_address}')
"
```

---

## ✅ **SUCCESS CRITERIA:**

### **✅ DEPLOYMENT:**
- Git repository deployed ✅
- Python app running ✅  
- Dependencies installed ✅

### **✅ DATABASE:**
- MySQL connection working ✅
- Tables created ✅
- geral@alitools.pt account configured ✅

### **✅ FUNCTIONALITY:**
- Health check API responds ✅
- Web interface loads ✅
- IMAP sync works (real emails) ✅

### **✅ PRODUCTION READY:**
- https://email.artnshine.pt accessible ✅
- Real email management functional ✅
- No VPN/network issues ✅

---

## 🔧 **TROUBLESHOOTING:**

### **Error: "Application not responding"**
```bash
# Check Python app status
cPanel → Python App → sendcraft → View status

# Check error logs  
cPanel → Error Logs → Check latest entries

# Restart application
cPanel → Python App → sendcraft → Restart
```

### **Error: "Database connection failed"**
```bash
# Verify MySQL credentials
cPanel → MySQL Databases → Check user privileges

# Test connection in terminal:
mysql -u artnshin_sendcraft -p -h localhost artnshin_sendcraft
```

### **Error: "IMAP sync fails"**
```bash
# Check from production server (no VPN issues):
ssh artnshin@artnshine.pt
cd public_html/sendcraft
source /home/artnshin/virtualenv/public_html/sendcraft/3.9/bin/activate

# Test direct IMAP:
python3 -c "
import imaplib, ssl
conn = imaplib.IMAP4_SSL('mail.alitools.pt', 993)
result = conn.login('geral@alitools.pt', '6+r&0io.ThlW')
print('IMAP test:', result)
conn.logout()
"
```

---

## 🎉 **FINAL SUCCESS:**

### **✅ SendCraft Production Deploy Complete:**
- **Development:** `python3 run_dev.py` (local)
- **Production:** `https://email.artnshine.pt` (live)
- **IMAP:** Real sync geral@alitools.pt funcionando
- **Database:** MySQL produção com dados reais

**SendCraft está 100% production-ready!** 🚀