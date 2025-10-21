# 🚀 SendCraft Phase 9.1 - WORKFLOW COMPLETO DE EXECUÇÃO

## 📋 **FLOW COMPLETO DE TRABALHO - QUEM FAZ O QUÊ E QUANDO**

### **DISTRIBUIÇÃO DE TAREFAS POR AGENTE:**

```
┌─────────────────┬─────────────────┬──────────────┬─────────────────┐
│ FASE            │ QUEM EXECUTA    │ TEMPO        │ RESULTADO       │
├─────────────────┼─────────────────┼──────────────┼─────────────────┤
│ 1. Setup        │ LOCAL AGENT     │ 2-3 min      │ Environment     │
│ 2. Backend      │ CLAUDE 4.1 OPUS│ 15-20 min    │ IMAP Models     │
│ 3. Migration    │ USER MANUAL     │ 1-2 min      │ Database        │
│ 4. Frontend     │ CLAUDE 4.1 OPUS│ 20-25 min    │ Email Client    │
│ 5. Integration  │ LOCAL AGENT     │ 10-15 min    │ Routes & Config │
│ 6. Validation   │ USER MANUAL     │ 3-5 min      │ Testing         │
└─────────────────┴─────────────────┴──────────────┴─────────────────┘
```

---

## 🤖 **FASE 1: LOCAL AGENT - SETUP COMPLETO (2-3 minutos)**

### **✅ SIM - Local Agent pode fazer o setup inicial!**

**Cursor Agent Local pode executar:**

#### **Prompt para Cursor Agent:**
```markdown
SendCraft Phase 9.1 - Complete Setup and Environment Preparation

## Context:
Current SendCraft project on branch cursor/implement-modular-config-with-remote-mysql-access-42e8
Need to prepare environment for Phase 9.1 Email Inbox/Outbox Management
Real email account: encomendas@alitools.pt with mail.alitools.pt IMAP/SMTP

## Task 1: Environment Setup
1. Create backup of current state
2. Create new branch: phase-9.1-email-inbox-outbox-real  
3. Create directory structure for Phase 9.1
4. Install new dependencies: python-socketio, email-validator
5. Create placeholder files for implementation

## Task 2: Project Structure Setup
Create these directories and files:
```
sendcraft/
├── models/
│   └── email_inbox.py                # Placeholder
├── services/
│   └── imap_service.py              # Placeholder  
├── api/v1/
│   └── emails_inbox.py              # Placeholder
├── templates/emails/
│   ├── inbox.html                   # Placeholder
│   ├── outbox.html                  # Placeholder
│   └── compose.html                 # Placeholder
├── static/
│   ├── css/
│   │   └── email-client.css         # Placeholder
│   └── js/email-client/
│       └── EmailClientApp.js        # Placeholder
└── docs/phase9-1/
    └── implementation-notes.md      # Placeholder
```

## Task 3: Configuration Check
1. Verify MySQL connection to artnshine.pt works
2. Check current models import correctly
3. Verify Flask app starts without errors
4. Test existing API endpoints respond

## Task 4: Dependencies Management
Add to requirements.txt if not present:
- python-socketio>=5.9.0
- email-validator>=2.1.0

## Task 5: Create Implementation Config
Create docs/phase9-1/real-config.yaml with:
```yaml
email_account:
  address: "encomendas@alitools.pt"
  password: "6f2zniWMN6aUFaD"
  imap:
    server: "mail.alitools.pt"
    port: 993
    ssl: true
  smtp:
    server: "mail.alitools.pt"
    port: 465
    ssl: true
```

## Requirements:
- Use exact current project structure and patterns
- Don't modify existing models/services yet (just create placeholders)
- Ensure all paths are correct for SendCraft structure  
- Test that environment is ready for next implementation phases

Execute all setup tasks and report status of each step.
```

**Resultado esperado:** Environment 100% preparado para próximas fases

---

## 🧠 **FASE 2: CLAUDE 4.1 OPUS - BACKEND IMAP (15-20 minutos)**

### **Prompt para Claude 4.1 Opus:**
```markdown
SendCraft Phase 9.1 - Backend IMAP Implementation with REAL Configuration

## Real Email Configuration (from cPanel):
```yaml
Email: encomendas@alitools.pt
Password: 6f2zniWMN6aUFaD
IMAP: mail.alitools.pt:993 (SSL)
SMTP: mail.alitools.pt:465 (SSL)
```

## Context:
- SendCraft Flask app with existing models (Domain, EmailAccount, EmailLog, EmailTemplate)
- MySQL database: artnshine.pt:3306/artnshinsendcraft
- Current branch: phase-9.1-email-inbox-outbox-real (prepared by Local Agent)

## Task: Implement Complete IMAP Backend

### 1. EXTEND EmailAccount Model
Add IMAP fields to sendcraft/models/account.py:
```python
# Add to existing EmailAccount class:
imap_server = Column(String(200), default='mail.alitools.pt')
imap_port = Column(Integer, default=993)
imap_use_ssl = Column(Boolean, default=True)
last_sync = Column(DateTime)
auto_sync_enabled = Column(Boolean, default=True)
inbox_emails = relationship('EmailInbox', back_populates='account')
```

### 2. CREATE EmailInbox Model
Complete sendcraft/models/email_inbox.py with full model for received emails.

### 3. CREATE IMAPService  
Complete sendcraft/services/imap_service.py with SSL connection to mail.alitools.pt:993.

### 4. CREATE API Endpoints
Complete sendcraft/api/v1/emails_inbox.py with:
- GET /inbox/<account_id> - List emails
- POST /sync/<account_id> - IMAP sync  
- GET /inbox/<account_id>/<email_id> - Email details

### 5. CREATE Database Migration
Generate proper migration script for new tables and fields.

Use EXACT configurations: mail.alitools.pt SSL connections, integrate with existing patterns.
```

**Resultado esperado:** Backend IMAP completo e funcional

---

## 👤 **FASE 3: USER MANUAL - DATABASE MIGRATION (1-2 minutos)**

### **Comandos que o User executa:**
```bash
# 1. Aplicar migration gerada pelo Claude
flask db migrate -m "Add EmailInbox and IMAP support for Phase 9.1"

# 2. Executar migration
flask db upgrade

# 3. Verificar se tabelas foram criadas
mysql -h artnshine.pt -u artnshinsendcraft -p"gbxZmjJZt9Z,i" artnshinsendcraft -e "SHOW TABLES;" | grep email_inbox

# 4. Confirmar se campos IMAP foram adicionados
mysql -h artnshine.pt -u artnshinsendcraft -p"gbxZmjJZt9Z,i" artnshinsendcraft -e "DESCRIBE email_accounts;" | grep imap
```

**Resultado esperado:** Database atualizada com EmailInbox table e campos IMAP

---

## 🧠 **FASE 4: CLAUDE 4.1 OPUS - FRONTEND CLIENT (20-25 minutos)**

### **Prompt para Claude 4.1 Opus:**
```markdown
SendCraft Phase 9.1 - Modern Email Client Frontend

## Context:
- Backend IMAP implemented (EmailInbox model, IMAPService, API endpoints)
- SendCraft uses Bootstrap 5, jQuery, existing design system
- Need modern three-pane email client interface

## Task: Complete Frontend Email Client

### 1. CREATE templates/emails/inbox.html
Modern three-pane layout:
- Sidebar: Account selector + folders
- Email list: Virtual scrolling + search
- Content: Email preview + actions

### 2. CREATE templates/emails/outbox.html  
Sent emails management with filtering.

### 3. CREATE static/css/email-client.css
Complete responsive design:
- Three-pane layout
- Mobile responsive
- Dark/light theme ready

### 4. CREATE static/js/email-client/EmailClientApp.js
Full functionality:
- AJAX email loading
- Real-time sync integration
- Email selection and preview
- Search and filtering

### 5. UPDATE Navigation
Add email client links to main navigation.

Design Requirements:
- Follow existing SendCraft Bootstrap 5 patterns
- Professional, clean interface
- Performance optimized for large email lists
- Portuguese language interface
```

**Resultado esperado:** Interface email client completa e funcional

---

## 🤖 **FASE 5: LOCAL AGENT - INTEGRATION (10-15 minutos)**

### **Prompt para Cursor Agent:**
```markdown
SendCraft Phase 9.1 - Final Integration and Routes Setup

## Context:
- Backend IMAP implementation complete (models, services, API)
- Frontend email client complete (templates, CSS, JS)
- Database migration applied
- Need to integrate everything into existing SendCraft system

## Task: Complete System Integration

### 1. UPDATE sendcraft/routes/web.py
Add email client routes:
- /emails/inbox - Main email interface
- /emails/outbox - Sent emails
- /emails/<id> - Email detail view

### 2. UPDATE sendcraft/__init__.py
- Import new models (email_inbox)
- Register email API blueprint
- Ensure all routes are registered

### 3. UPDATE sendcraft/api/v1/__init__.py
Register emails_inbox blueprint properly.

### 4. CREATE Seed Data Function
Function to create encomendas@alitools.pt account with REAL config:
- Domain: alitools.pt
- IMAP: mail.alitools.pt:993 SSL
- SMTP: mail.alitools.pt:465 SSL
- Password: encrypted real password

### 5. UPDATE Navigation
Ensure email client is accessible from main navigation with unread count.

### 6. PERFORMANCE OPTIMIZATIONS
- Add proper database indexes
- Configure IMAP connection pooling
- Optimize email list loading

Requirements:
- Follow existing SendCraft patterns exactly
- Test all integrations work
- Ensure no conflicts with existing functionality
```

**Resultado esperado:** Sistema completamente integrado e funcional

---

## 👤 **FASE 6: USER MANUAL - VALIDATION & TESTING (3-5 minutos)**

### **Comandos de Validação:**
```bash
# 1. Criar conta real encomendas@alitools.pt
python -c "
from sendcraft import create_app
from sendcraft.models.domain import Domain
from sendcraft.models.account import EmailAccount

app = create_app('development')
with app.app_context():
    # Criar domínio
    domain = Domain.query.filter_by(name='alitools.pt').first()
    if not domain:
        domain = Domain(name='alitools.pt', is_active=True)
        domain.save()
    
    # Criar conta
    account = EmailAccount.query.filter_by(email_address='encomendas@alitools.pt').first()
    if not account:
        account = EmailAccount(
            domain_id=domain.id,
            email_address='encomendas@alitools.pt',
            smtp_server='mail.alitools.pt',
            smtp_port=465,
            use_ssl=True,
            imap_server='mail.alitools.pt',
            imap_port=993,
            imap_use_ssl=True,
            is_active=True
        )
        account.set_password('6f2zniWMN6aUFaD', app.config['ENCRYPTION_KEY'])
        account.save()
        print('✅ Conta encomendas@alitools.pt criada')
"

# 2. Executar validation script
./validate_phase_9_1_real.sh

# 3. Iniciar aplicação
python rundev.py

# 4. Testar interface
# Abrir: http://localhost:5000/emails/inbox

# 5. Testar sync IMAP
curl -X POST http://localhost:5000/api/v1/emails/sync/1
```

**Resultado esperado:** Sistema 100% funcional com emails reais

---

## ⏰ **CRONOGRAMA COMPLETO DE EXECUÇÃO:**

### **TIMELINE DETALHADO:**
```
🕐 00:00 - START
├── 🤖 LOCAL AGENT: Setup (2-3 min)
│   ├── Environment preparation
│   ├── Directory structure  
│   └── Dependencies installation
│
🕐 00:03 - Backend Phase
├── 🧠 CLAUDE 4.1: Backend IMAP (15-20 min)
│   ├── EmailInbox model
│   ├── IMAPService implementation
│   ├── API endpoints
│   └── Database migration script
│
🕐 00:23 - Database Phase  
├── 👤 USER: Migration (1-2 min)
│   ├── flask db migrate
│   └── flask db upgrade
│
🕐 00:25 - Frontend Phase
├── 🧠 CLAUDE 4.1: Frontend Client (20-25 min)
│   ├── Three-pane interface
│   ├── CSS responsive design
│   ├── JavaScript functionality
│   └── Navigation integration
│
🕐 00:50 - Integration Phase
├── 🤖 LOCAL AGENT: Integration (10-15 min)
│   ├── Routes integration
│   ├── Blueprint registration
│   ├── Seed data creation
│   └── Performance optimization
│
🕐 01:05 - Testing Phase
├── 👤 USER: Validation (3-5 min)
│   ├── Account creation
│   ├── Validation script
│   ├── Interface testing
│   └── IMAP sync testing
│
🕐 01:10 - COMPLETE ✅
```

**TOTAL TIME: ~70 minutos (1 hora e 10 minutos)**

---

## 🎯 **RESUMO DE DISTRIBUIÇÃO:**

### **LOCAL AGENT (Cursor)**: 2 fases - 12-18 minutos total
- ✅ **Pode fazer**: Setup completo, integração final
- ✅ **Vantagens**: Acesso direto ao código, modificações precisas
- ✅ **Resultado**: Environment + Integration perfeitos

### **CLAUDE 4.1 OPUS**: 2 fases - 35-45 minutos total  
- ✅ **Especialista**: Backend models/services + Frontend interfaces
- ✅ **Vantagens**: Código complexo, padrões architecture
- ✅ **Resultado**: Funcionalidades core completas

### **USER MANUAL**: 2 fases - 4-7 minutos total
- ✅ **Essencial**: Database operations, testing final
- ✅ **Vantagens**: Controlo direto, validação real
- ✅ **Resultado**: Sistema funcional validado

## ✅ **PRÓXIMA AÇÃO RECOMENDADA:**

**Começar AGORA com Cursor Agent Local:**
```bash
# Dar este prompt ao Cursor Agent:
"SendCraft Phase 9.1 - Complete Setup and Environment Preparation..."
```

**Fluxo otimizado = máxima eficiência + mínimo esforço manual + resultado profissional garantido!** 🚀
