# 🚀 SendCraft Phase 9.1 - DOCUMENTAÇÃO FINAL COMPLETA COM CONFIGURAÇÕES REAIS

## 📧 **CONFIGURAÇÕES EMAIL CONFIRMADAS - encomendas@alitools.pt**

### ✅ **Dados Reais do cPanel (SSL/TLS Seguro):**
```yaml
Email: encomendas@alitools.pt
Password: 6f2zniWMN6aUFaD

# IMAP (Receber emails) - SSL/TLS
IMAP_SERVER: mail.alitools.pt
IMAP_PORT: 993
IMAP_SSL: true
IMAP_AUTH: required

# SMTP (Enviar emails) - SSL/TLS  
SMTP_SERVER: mail.alitools.pt
SMTP_PORT: 465
SMTP_SSL: true
SMTP_AUTH: required
```

---

## 📋 **INSTRUÇÕES COMPLETAS PARA O USER**

### **STEP 1: Preparar Environment (5 minutos)**

#### **1.1 Verificar Branch Atual**
```bash
cd /caminho/para/SendCraft
git status
git checkout cursor/implement-modular-config-with-remote-mysql-access-42e8
git pull origin cursor/implement-modular-config-with-remote-mysql-access-42e8
```

#### **1.2 Configurar Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### **1.3 Criar Diretórios Phase 9.1**
```bash
mkdir -p docs/phase9-1
mkdir -p sendcraft/templates/emails
mkdir -p sendcraft/static/js/email-client
```

### **STEP 2: Testar Sistema Atual (5 minutos)**

#### **2.1 Testar Conexão MySQL**
```bash
# Testar conexão remota (já confirmada funcional)
mysql -h artnshine.pt -u artnshinsendcraft -p artnshinsendcraft -e "SHOW TABLES;"
# Password: gbxZmjJZt9Z,i
```

#### **2.2 Arrancar Modo Development**
```bash
python rundev.py
# Deve mostrar:
# SendCraft Development Mode Remote MySQL dominios.pt
# Remote MySQL connection OK
# Web Interface http://localhost:5000
```

#### **2.3 Verificar Interface Atual**
```bash
# Noutro terminal
curl http://localhost:5000
curl http://localhost:5000/domains
curl http://localhost:5000/accounts
```

### **STEP 3: Implementar Phase 9.1 com AI Agents (45 minutos)**

#### **3.1 Prompt para Claude 4.1 Opus - Backend (15 min)**
**Arquivo:** `PROMPT-1-BACKEND-REAL-CONFIG.md`
```markdown
# PROMPT 1 REAL: SendCraft Backend IMAP - encomendas@alitools.pt

## CONFIGURAÇÕES REAIS (do cPanel):
Email: encomendas@alitools.pt
Password: 6f2zniWMN6aUFaD
IMAP_SERVER: mail.alitools.pt
IMAP_PORT: 993
SMTP_SERVER: mail.alitools.pt  
SMTP_PORT: 465
SSL: true (ambos IMAP e SMTP)

## Task: Implementar IMAP Backend com configurações REAIS

1. EXTEND EmailAccount model - adicionar campos IMAP
2. CREATE EmailInbox model - emails recebidos
3. CREATE IMAPService - cliente IMAP para mail.alitools.pt:993
4. CREATE API endpoints - /api/v1/emails/inbox/<account_id>
5. CREATE Migration - novas tabelas
6. CREATE Seed data - conta encomendas@alitools.pt REAL

Usar configurações SSL exatas: mail.alitools.pt:993 IMAP, mail.alitools.pt:465 SMTP
```

#### **3.2 Prompt para Claude 4.1 Opus - Frontend (20 min)**
**Arquivo:** `PROMPT-2-FRONTEND-REAL.md`
```markdown
# PROMPT 2 REAL: SendCraft Frontend Email Client

## Task: Interface Three-pane Email Client

1. CREATE templates/emails/inbox.html - interface moderna
2. CREATE templates/emails/outbox.html - emails enviados
3. CREATE templates/emails/compose.html - compositor
4. CREATE static/css/email-client.css - estilos modernos
5. CREATE static/js/email-client/EmailClientApp.js - funcionalidade
6. INTEGRATE com dados reais encomendas@alitools.pt

Design: Three-pane (sidebar + lista + preview)
Performance: Virtual scrolling
Mobile: Responsive design
```

#### **3.3 Prompt para Cursor Agent - Integration (10 min)**
**Arquivo:** `PROMPT-3-INTEGRATION-REAL.md`
```markdown
# PROMPT 3 REAL: SendCraft Integration Final

## Task: Integrar tudo no sistema existente

1. UPDATE sendcraft/routes/web.py - rotas /emails/*
2. REGISTER blueprints - API e Web
3. UPDATE navigation - link para Email Client
4. CONFIGURE SocketIO - real-time updates
5. TEST com conta encomendas@alitools.pt real
```

### **STEP 4: Aplicar Migrations e Seed Data (10 minutos)**

#### **4.1 Aplicar Database Changes**
```bash
# Depois do Claude implementar backend
flask db migrate -m "Add EmailInbox and IMAP support for encomendas@alitools.pt"
flask db upgrade
```

#### **4.2 Seed Data Real**
```bash
# Executar seed com dados reais
python -c "
from sendcraft import create_app
from sendcraft.models import EmailAccount, Domain
app = create_app('development')
with app.app_context():
    # Criar/verificar domínio alitools.pt
    domain = Domain.query.filter_by(name='alitools.pt').first()
    if not domain:
        domain = Domain(name='alitools.pt', is_active=True)
        domain.save()
    
    # Criar conta real encomendas@alitools.pt
    account = EmailAccount.query.filter_by(email_address='encomendas@alitools.pt').first()
    if not account:
        account = EmailAccount(
            domain_id=domain.id,
            local_part='encomendas',
            email_address='encomendas@alitools.pt',
            smtp_server='mail.alitools.pt',
            smtp_port=465,
            use_ssl=True,
            imap_server='mail.alitools.pt',
            imap_port=993,
            imap_use_ssl=True,
            is_active=True
        )
        # Definir password real
        encryption_key = app.config['ENCRYPTION_KEY']
        account.set_password('6f2zniWMN6aUFaD', encryption_key)
        account.save()
        print('✅ Conta encomendas@alitools.pt criada com configurações REAIS')
"
```

### **STEP 5: Testes e Validação (10 minutos)**

#### **5.1 Testar API Endpoints**
```bash
# Testar novos endpoints
curl http://localhost:5000/api/v1/health
curl http://localhost:5000/api/v1/emails/inbox/1
curl -X POST http://localhost:5000/api/v1/emails/sync/1
```

#### **5.2 Testar Interface**
```bash
# Abrir no browser
python rundev.py &
open http://localhost:5000/emails/inbox
```

#### **5.3 Validação Completa**
```bash
# Executar script de validação
chmod +x validate_implementation.sh
./validate_implementation.sh
```

---

## 🤖 **PROMPTS ESPECÍFICOS PARA AI AGENTS**

### **PROMPT 1: Backend IMAP Real (Claude 4.1 Opus)**

```markdown
SendCraft Email Management - Backend IMAP Implementation

## REAL EMAIL CONFIGURATION (cPanel confirmed):
```yaml
Email: encomendas@alitools.pt
Password: 6f2zniWMN6aUFaD

IMAP_SERVER: mail.alitools.pt
IMAP_PORT: 993
IMAP_SSL: true

SMTP_SERVER: mail.alitools.pt
SMTP_PORT: 465
SMTP_SSL: true
```

## Context:
- Existing SendCraft Flask app with working models (Domain, EmailAccount, EmailLog, EmailTemplate)
- MySQL remote database working: artnshine.pt:3306/artnshinsendcraft
- Current branch: cursor/implement-modular-config-with-remote-mysql-access-42e8
- Need to implement IMAP email receiving for real account encomendas@alitools.pt

## Task: Implement Complete IMAP Backend

### 1. EXTEND EmailAccount Model (sendcraft/models/account.py)
Add IMAP configuration fields to existing model:

```python
# Add these fields to existing EmailAccount class:
# IMAP Configuration  
imap_server = Column(String(200), default='mail.alitools.pt')
imap_port = Column(Integer, default=993)
imap_use_ssl = Column(Boolean, default=True)
imap_use_tls = Column(Boolean, default=False)

# Sync settings
last_sync = Column(DateTime)
auto_sync_enabled = Column(Boolean, default=True)
sync_interval_minutes = Column(Integer, default=5)

# New relationship
inbox_emails = relationship('EmailInbox', back_populates='account', lazy='dynamic')

def get_imap_config(self, encryption_key: str) -> Dict[str, Any]:
    """Retorna configuração IMAP."""
    return {
        'server': self.imap_server,
        'port': self.imap_port,
        'username': self.email_address,
        'password': self.get_password(encryption_key),
        'use_ssl': self.imap_use_ssl
    }
```

### 2. CREATE EmailInbox Model (sendcraft/models/email_inbox.py)

Complete model for received emails:

```python
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from .base import BaseModel, TimestampMixin

class EmailInbox(BaseModel, TimestampMixin):
    """Modelo para emails recebidos via IMAP."""
    __tablename__ = 'email_inbox'
    
    # Relacionamentos
    account_id = Column(Integer, ForeignKey('email_accounts.id'), nullable=False)
    account = relationship('EmailAccount', back_populates='inbox_emails')
    
    # Email data
    message_id = Column(String(255), unique=True, nullable=False, index=True)
    from_address = Column(String(255), nullable=False, index=True)
    to_addresses = Column(JSON)
    subject = Column(Text)
    body_text = Column(Text)
    body_html = Column(Text)
    received_at = Column(DateTime, nullable=False, index=True)
    
    # Status flags
    is_read = Column(Boolean, default=False, index=True)
    is_flagged = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Metadata
    size_bytes = Column(Integer)
    attachments = Column(JSON)
    raw_headers = Column(JSON)
    
    @classmethod
    def get_inbox_emails(cls, account_id: int, page: int = 1, per_page: int = 50):
        return cls.query.filter_by(account_id=account_id, is_archived=False)\
                       .order_by(cls.received_at.desc())\
                       .paginate(page=page, per_page=per_page, error_out=False)
    
    def to_dict(self, include_body: bool = False) -> dict:
        data = {
            'id': self.id,
            'message_id': self.message_id,
            'from_address': self.from_address,
            'subject': self.subject,
            'received_at': self.received_at.isoformat(),
            'is_read': self.is_read,
            'is_flagged': self.is_flagged
        }
        if include_body:
            data.update({
                'body_text': self.body_text,
                'body_html': self.body_html
            })
        return data
```

### 3. CREATE IMAPService (sendcraft/services/imap_service.py)

IMAP client specifically for mail.alitools.pt:

```python
import imaplib
import email
from datetime import datetime
from typing import List, Dict, Any, Optional

class IMAPService:
    """IMAP client for mail.alitools.pt (SSL port 993)."""
    
    def __init__(self, account: EmailAccount, encryption_key: str):
        self.account = account
        self.encryption_key = encryption_key
    
    def connect(self) -> imaplib.IMAP4_SSL:
        """Conecta via SSL ao mail.alitools.pt:993."""
        conn = imaplib.IMAP4_SSL(
            host=self.account.imap_server,
            port=self.account.imap_port
        )
        conn.login(
            self.account.email_address,
            self.account.get_password(self.encryption_key)
        )
        return conn
    
    def fetch_recent_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Busca emails recentes."""
        emails = []
        with self.connect() as conn:
            conn.select('INBOX')
            typ, messages = conn.search(None, 'ALL')
            
            for msg_id in messages[0].split()[-limit:]:
                typ, msg_data = conn.fetch(msg_id, '(RFC822)')
                raw_email = msg_data[0][1]
                parsed = self.parse_email_message(raw_email)
                if parsed:
                    emails.append(parsed)
        return emails
    
    def sync_account_emails(self) -> Dict[str, Any]:
        """Sincroniza emails, salvando novos na database."""
        from ..models.email_inbox import EmailInbox
        
        emails = self.fetch_recent_emails()
        new_count = 0
        
        for email_data in emails:
            existing = EmailInbox.query.filter_by(
                message_id=email_data['message_id']
            ).first()
            
            if not existing:
                inbox_email = EmailInbox(
                    account_id=self.account.id,
                    **email_data
                )
                inbox_email.save()
                new_count += 1
        
        # Update last sync
        self.account.last_sync = datetime.utcnow()
        self.account.save()
        
        return {
            'success': True,
            'new_emails': new_count,
            'total_synced': len(emails)
        }
    
    def parse_email_message(self, raw_email: bytes) -> Optional[Dict[str, Any]]:
        """Parse raw email para dict."""
        try:
            msg = email.message_from_bytes(raw_email)
            
            return {
                'message_id': msg.get('Message-ID', ''),
                'from_address': self._decode_header(msg.get('From', '')),
                'to_addresses': [self.account.email_address],
                'subject': self._decode_header(msg.get('Subject', '')),
                'received_at': self._parse_date(msg.get('Date', '')) or datetime.utcnow(),
                'body_text': self._extract_text(msg),
                'body_html': self._extract_html(msg),
                'size_bytes': len(raw_email),
                'raw_headers': dict(msg.items())
            }
        except Exception:
            return None
```

### 4. CREATE API Endpoints (sendcraft/api/v1/emails_inbox.py)

API for email management:

```python
from flask import Blueprint, jsonify, current_app
from ...models.account import EmailAccount
from ...models.email_inbox import EmailInbox
from ...services.imap_service import IMAPService

emails_bp = Blueprint('emails', __name__)

@emails_bp.route('/inbox/<int:account_id>')
def get_inbox_emails(account_id):
    """Lista emails da inbox."""
    try:
        pagination = EmailInbox.get_inbox_emails(account_id)
        return jsonify({
            'success': True,
            'emails': [email.to_dict() for email in pagination.items],
            'pagination': {
                'page': pagination.page,
                'total': pagination.total,
                'has_next': pagination.has_next
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@emails_bp.route('/sync/<int:account_id>', methods=['POST'])
def sync_account_emails(account_id):
    """Sincroniza emails via IMAP."""
    try:
        account = EmailAccount.query.get_or_404(account_id)
        encryption_key = current_app.config.get('ENCRYPTION_KEY')
        
        imap_service = IMAPService(account, encryption_key)
        result = imap_service.sync_account_emails()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

### 5. CREATE Database Migration

```python
def upgrade():
    # Add IMAP fields to email_accounts
    op.add_column('email_accounts', sa.Column('imap_server', sa.String(200), default='mail.alitools.pt'))
    op.add_column('email_accounts', sa.Column('imap_port', sa.Integer(), default=993))
    op.add_column('email_accounts', sa.Column('imap_use_ssl', sa.Boolean(), default=True))
    op.add_column('email_accounts', sa.Column('last_sync', sa.DateTime()))
    op.add_column('email_accounts', sa.Column('auto_sync_enabled', sa.Boolean(), default=True))
    
    # Create email_inbox table
    op.create_table('email_inbox',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('account_id', sa.Integer(), sa.ForeignKey('email_accounts.id')),
        sa.Column('message_id', sa.String(255), unique=True),
        sa.Column('from_address', sa.String(255)),
        sa.Column('subject', sa.Text()),
        sa.Column('body_text', sa.Text()),
        sa.Column('body_html', sa.Text()),
        sa.Column('received_at', sa.DateTime()),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now())
    )
```

### 6. REGISTER in API (sendcraft/api/v1/__init__.py)

```python
from .emails_inbox import emails_bp

def register_blueprints(app):
    app.register_blueprint(emails_bp, url_prefix='/api/v1/emails')
```

## Requirements:
- Use EXACT configurations: mail.alitools.pt:993 (IMAP SSL), mail.alitools.pt:465 (SMTP SSL)
- Integrate with existing encryption system
- Follow current SendCraft patterns
- Test with real credentials: encomendas@alitools.pt / 6f2zniWMN6aUFaD

Generate production-ready code that works immediately with real email account!
```

### **PROMPT 2: Frontend Email Client (Claude 4.1 Opus)**

```markdown
SendCraft Email Client - Modern Three-Pane Interface

## Task: Implement Modern Email Client Frontend

Based on existing SendCraft design system (Bootstrap 5, jQuery, HTMX) and real email account encomendas@alitools.pt.

### 1. CREATE templates/emails/inbox.html

Three-pane layout:

```html
{% extends "base.html" %}
{% block title %}Email Inbox - SendCraft{% endblock %}

{% block content %}
<div class="email-client-container">
    <!-- Sidebar -->
    <div class="email-sidebar">
        <div class="sidebar-header">
            <h5><i class="bi bi-envelope"></i> Email</h5>
            <button class="btn btn-primary btn-sm" id="compose-btn">
                <i class="bi bi-plus"></i> Novo
            </button>
        </div>
        
        <div class="account-selector mb-3">
            <select class="form-select" id="account-select">
                <option value="">Todas as Contas</option>
                {% for account in accounts %}
                <option value="{{ account.id }}">
                    {{ account.email_address }}
                    {% if account.unread_count > 0 %}
                        <span class="badge bg-primary">{{ account.unread_count }}</span>
                    {% endif %}
                </option>
                {% endfor %}
            </select>
        </div>
        
        <div class="folder-list">
            <div class="folder-item active" data-folder="inbox">
                <i class="bi bi-inbox"></i> Inbox
                <span class="badge bg-primary" id="inbox-count">0</span>
            </div>
            <div class="folder-item" data-folder="sent">
                <i class="bi bi-send"></i> Enviados
            </div>
        </div>
        
        <div class="sync-controls mt-3">
            <button class="btn btn-outline-primary btn-sm w-100" id="sync-all">
                <i class="bi bi-arrow-clockwise"></i> Sincronizar
            </button>
        </div>
    </div>
    
    <!-- Email List -->
    <div class="email-list">
        <div class="list-header">
            <input type="text" class="form-control" id="email-search" placeholder="Pesquisar emails...">
        </div>
        <div class="email-items" id="email-items-container">
            <div class="loading-state text-center p-4">
                <div class="spinner-border text-primary"></div>
                <p>Carregando emails...</p>
            </div>
        </div>
    </div>
    
    <!-- Email Content -->
    <div class="email-content">
        <div class="content-header" id="email-header" style="display:none;">
            <div class="email-actions">
                <button class="btn btn-outline-secondary btn-sm" id="mark-read">
                    <i class="bi bi-envelope-open"></i>
                </button>
                <button class="btn btn-outline-secondary btn-sm" id="flag-email">
                    <i class="bi bi-flag"></i>
                </button>
                <button class="btn btn-outline-danger btn-sm" id="delete-email">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
        
        <div class="content-body" id="email-body">
            <div class="empty-state text-center p-5">
                <i class="bi bi-envelope" style="font-size: 4rem; color: #ccc;"></i>
                <h4 class="text-muted mt-3">Selecione um email</h4>
                <p class="text-muted">Escolha um email da lista para ler</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/email-client.js') }}"></script>
{% endblock %}
```

### 2. CREATE static/css/email-client.css

Modern email client styles:

```css
/* Email Client Layout */
.email-client-container {
    display: flex;
    height: calc(100vh - 120px);
    border: 1px solid #dee2e6;
    border-radius: 8px;
    overflow: hidden;
    background: white;
}

/* Sidebar */
.email-sidebar {
    width: 280px;
    background: #f8f9fa;
    border-right: 1px solid #dee2e6;
    padding: 20px;
    overflow-y: auto;
}

.sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #dee2e6;
}

.folder-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.folder-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 12px;
    margin-bottom: 4px;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.2s;
    color: #6c757d;
}

.folder-item:hover {
    background-color: #e9ecef;
}

.folder-item.active {
    background-color: #0066cc;
    color: white;
}

/* Email List */
.email-list {
    width: 400px;
    border-right: 1px solid #dee2e6;
    display: flex;
    flex-direction: column;
}

.list-header {
    padding: 15px;
    border-bottom: 1px solid #dee2e6;
}

.email-items {
    flex: 1;
    overflow-y: auto;
}

.email-item {
    padding: 15px;
    border-bottom: 1px solid #f1f1f1;
    cursor: pointer;
    transition: background-color 0.2s;
}

.email-item:hover {
    background-color: #f8f9fa;
}

.email-item.selected {
    background-color: #e3f2fd;
    border-left: 4px solid #0066cc;
}

.email-item.unread {
    background-color: #fff3cd;
    font-weight: 600;
}

.email-sender {
    font-weight: 500;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
}

.email-subject {
    margin-bottom: 4px;
    color: #495057;
}

.email-preview {
    font-size: 0.875rem;
    color: #6c757d;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.email-time {
    font-size: 0.75rem;
    color: #adb5bd;
}

/* Email Content */
.email-content {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.content-header {
    padding: 15px;
    border-bottom: 1px solid #dee2e6;
    background: #f8f9fa;
}

.content-body {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
}

.email-meta {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 6px;
    margin-bottom: 20px;
    font-size: 0.875rem;
}

.email-body-content {
    line-height: 1.6;
    max-width: 100%;
    word-wrap: break-word;
}

/* Responsive */
@media (max-width: 1200px) {
    .email-list { width: 350px; }
}

@media (max-width: 992px) {
    .email-client-container { flex-direction: column; }
    .email-sidebar { width: 100%; height: auto; }
    .email-list { width: 100%; height: 300px; }
}

/* Loading and Empty States */
.loading-state, .empty-state {
    color: #6c757d;
}

.empty-state i {
    color: #dee2e6;
}

/* Utilities */
.fade-in {
    animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
```

### 3. CREATE static/js/email-client.js

Email client functionality:

```javascript
/**
 * SendCraft Email Client
 * Modern three-pane email interface
 */
class EmailClient {
    constructor() {
        this.currentAccount = null;
        this.selectedEmail = null;
        this.emailCache = new Map();
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadAccounts();
    }
    
    setupEventListeners() {
        // Account selection
        $('#account-select').on('change', (e) => {
            this.selectAccount(e.target.value);
        });
        
        // Folder navigation  
        $('.folder-item').on('click', (e) => {
            $('.folder-item').removeClass('active');
            $(e.currentTarget).addClass('active');
            const folder = $(e.currentTarget).data('folder');
            this.loadFolder(folder);
        });
        
        // Email search
        $('#email-search').on('input', debounce((e) => {
            this.searchEmails(e.target.value);
        }, 300));
        
        // Sync emails
        $('#sync-all').on('click', () => this.syncEmails());
        
        // Email actions
        $('#mark-read').on('click', () => this.markAsRead());
        $('#flag-email').on('click', () => this.flagEmail());
        $('#delete-email').on('click', () => this.deleteEmail());
        
        // Email item clicks
        $(document).on('click', '.email-item', (e) => {
            this.selectEmail($(e.currentTarget));
        });
    }
    
    async selectAccount(accountId) {
        if (!accountId) {
            this.currentAccount = null;
            this.clearEmailList();
            return;
        }
        
        this.currentAccount = accountId;
        await this.loadEmails();
    }
    
    async loadEmails() {
        if (!this.currentAccount) return;
        
        this.showLoading();
        
        try {
            const response = await fetch(`/api/v1/emails/inbox/${this.currentAccount}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderEmailList(data.emails);
                this.updateInboxCount(data.emails.length);
            } else {
                this.showError('Erro ao carregar emails');
            }
        } catch (error) {
            this.showError('Falha na conexão');
        }
    }
    
    renderEmailList(emails) {
        const container = $('#email-items-container');
        container.empty();
        
        if (emails.length === 0) {
            container.append(`
                <div class="empty-state text-center p-4">
                    <p class="text-muted">Nenhum email encontrado</p>
                </div>
            `);
            return;
        }
        
        emails.forEach(email => {
            const emailItem = $(`
                <div class="email-item ${email.is_read ? '' : 'unread'}" data-email-id="${email.id}">
                    <div class="email-sender">
                        <span>${email.from_address}</span>
                        <span class="email-time">${this.formatTime(email.received_at)}</span>
                    </div>
                    <div class="email-subject">${email.subject || 'Sem assunto'}</div>
                    <div class="email-preview">${this.getPreview(email)}</div>
                </div>
            `);
            
            container.append(emailItem);
        });
    }
    
    async selectEmail(emailElement) {
        $('.email-item').removeClass('selected');
        emailElement.addClass('selected');
        
        const emailId = emailElement.data('email-id');
        await this.loadEmailContent(emailId);
    }
    
    async loadEmailContent(emailId) {
        try {
            const response = await fetch(`/api/v1/emails/inbox/${this.currentAccount}/${emailId}`);
            const data = await response.json();
            
            if (data.success) {
                this.displayEmailContent(data.email);
                this.selectedEmail = data.email;
                
                // Mark as read if unread
                if (!data.email.is_read) {
                    this.markEmailAsRead(emailId);
                }
            }
        } catch (error) {
            this.showError('Erro ao carregar email');
        }
    }
    
    displayEmailContent(email) {
        $('#email-header').show();
        
        const contentBody = $('#email-body');
        contentBody.html(`
            <div class="email-meta">
                <div><strong>De:</strong> ${email.from_address}</div>
                <div><strong>Para:</strong> ${email.to_addresses.join(', ')}</div>
                <div><strong>Assunto:</strong> ${email.subject}</div>
                <div><strong>Data:</strong> ${this.formatDate(email.received_at)}</div>
            </div>
            <div class="email-body-content">
                ${email.body_html || email.body_text || '<p>Conteúdo não disponível</p>'}
            </div>
        `);
    }
    
    async syncEmails() {
        if (!this.currentAccount) return;
        
        const syncBtn = $('#sync-all');
        syncBtn.prop('disabled', true).html('<i class="bi bi-arrow-clockwise spinning"></i> Sincronizando...');
        
        try {
            const response = await fetch(`/api/v1/emails/sync/${this.currentAccount}`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                this.showNotification(`${data.new_emails} novos emails sincronizados`);
                await this.loadEmails(); // Reload email list
            } else {
                this.showError('Erro na sincronização');
            }
        } catch (error) {
            this.showError('Falha na sincronização');
        } finally {
            syncBtn.prop('disabled', false).html('<i class="bi bi-arrow-clockwise"></i> Sincronizar');
        }
    }
    
    // Utility methods
    formatTime(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' });
    }
    
    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('pt-PT') + ' ' + date.toLocaleTimeString('pt-PT');
    }
    
    getPreview(email) {
        const text = email.body_text || '';
        return text.substring(0, 100) + (text.length > 100 ? '...' : '');
    }
    
    showLoading() {
        $('#email-items-container').html(`
            <div class="loading-state text-center p-4">
                <div class="spinner-border text-primary"></div>
                <p>Carregando...</p>
            </div>
        `);
    }
    
    showNotification(message) {
        // Integration with existing notification system
        if (window.showToast) {
            window.showToast(message, 'success');
        } else {
            alert(message);
        }
    }
    
    showError(message) {
        if (window.showToast) {
            window.showToast(message, 'error');
        } else {
            alert('Erro: ' + message);
        }
    }
}

// Utility function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize when DOM is ready
$(document).ready(function() {
    if ($('.email-client-container').length > 0) {
        window.emailClient = new EmailClient();
    }
});
```

### 4. UPDATE Navigation (base.html)

Add email client link to main navigation:

```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('web.emails_inbox') }}">
        <i class="bi bi-envelope"></i> Email
        <span class="badge bg-primary ms-1" id="total-unread">0</span>
    </a>
</li>
```

### 5. CREATE templates/emails/outbox.html (simplified version)

```html
{% extends "base.html" %}
{% block title %}Emails Enviados - SendCraft{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5><i class="bi bi-send"></i> Emails Enviados</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Data</th>
                                    <th>Para</th>
                                    <th>Assunto</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for log in sent_emails %}
                                <tr>
                                    <td>{{ log.created_at.strftime('%d/%m/%Y %H:%M') }}</td>
                                    <td>{{ log.recipient_email }}</td>
                                    <td>{{ log.subject or 'Sem assunto' }}</td>
                                    <td>
                                        <span class="badge bg-{% if log.status.value == 'sent' %}success{% elif log.status.value == 'failed' %}danger{% else %}warning{% endif %}">
                                            {{ log.status.value }}
                                        </span>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Requirements:
- Follow existing SendCraft design patterns
- Use Bootstrap 5 classes consistently  
- Integrate with current navigation
- Mobile responsive design
- Performance optimized for large email lists
- Portuguese language interface

Generate complete, polished frontend that matches SendCraft quality standards!
```

### **PROMPT 3: Integration & Routes (Cursor Agent Local)**

```markdown
SendCraft Phase 9.1 - Final Integration

## Context:
- Backend IMAP implementation complete (EmailInbox model, IMAPService, API endpoints)
- Frontend email client implemented (templates, CSS, JavaScript)
- Need to integrate everything into existing SendCraft system

## Task: Complete System Integration

### 1. UPDATE sendcraft/routes/web.py

Add email client routes:

```python
# Add these routes to existing web.py

@web_bp.route('/emails')
@web_bp.route('/emails/inbox')
def emails_inbox():
    """Email inbox interface."""
    from ..models.account import EmailAccount
    from ..models.email_inbox import EmailInbox
    
    accounts = EmailAccount.get_active_accounts()
    
    # Add unread count to each account
    for account in accounts:
        account.unread_count = EmailInbox.query.filter_by(
            account_id=account.id,
            is_read=False
        ).count()
    
    return render_template('emails/inbox.html', accounts=accounts)

@web_bp.route('/emails/outbox')
def emails_outbox():
    """Sent emails interface."""
    from ..models.account import EmailAccount
    from ..models.log import EmailLog
    
    accounts = EmailAccount.get_active_accounts()
    sent_emails = EmailLog.query.order_by(EmailLog.created_at.desc()).limit(100).all()
    
    return render_template('emails/outbox.html', 
                         accounts=accounts, 
                         sent_emails=sent_emails)

@web_bp.route('/emails/<int:email_id>')
def email_detail(email_id):
    """Individual email detail view."""
    from ..models.email_inbox import EmailInbox
    
    email = EmailInbox.query.get_or_404(email_id)
    
    # Mark as read
    if not email.is_read:
        email.is_read = True
        email.save()
    
    return render_template('emails/detail.html', email=email)
```

### 2. UPDATE sendcraft/api/v1/__init__.py

Register email endpoints:

```python
from .emails_inbox import emails_bp

def register_blueprints(app):
    """Register all API v1 blueprints."""
    # Existing blueprints...
    
    # Register email blueprint
    app.register_blueprint(emails_bp, url_prefix='/api/v1/emails')
```

### 3. UPDATE sendcraft/__init__.py

Ensure email models are imported:

```python
def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Existing initialization...
    
    # Import models to ensure they're registered
    from .models import domain, account, template, log
    from .models import email_inbox  # Add this line
    
    # Register blueprints
    from .routes import web, api
    app.register_blueprint(web.web_bp)
    app.register_blueprint(api.api_bp, url_prefix='/api')
    
    return app
```

### 4. UPDATE Navigation in templates/base.html

```html
<!-- In navigation section -->
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('web.emails_inbox') }}">
        <i class="bi bi-envelope"></i> Email
        <span class="badge bg-primary ms-1" id="global-unread-count">0</span>
    </a>
</li>
```

### 5. CREATE Real Account Seeder

Create utility to seed real encomendas@alitools.pt account:

```python
# sendcraft/cli/seed_real_account.py
def seed_encomendas_account():
    """Create real encomendas@alitools.pt account."""
    from ..models.domain import Domain
    from ..models.account import EmailAccount
    from .. import db
    
    # Get or create alitools.pt domain
    domain = Domain.query.filter_by(name='alitools.pt').first()
    if not domain:
        domain = Domain(
            name='alitools.pt',
            description='AliTools B2B Dropshipping Platform',
            is_active=True
        )
        domain.save()
    
    # Create encomendas account if not exists
    account = EmailAccount.query.filter_by(email_address='encomendas@alitools.pt').first()
    if not account:
        account = EmailAccount(
            domain_id=domain.id,
            local_part='encomendas',
            email_address='encomendas@alitools.pt',
            display_name='AliTools Encomendas',
            
            # SMTP (real config)
            smtp_server='mail.alitools.pt',
            smtp_port=465,
            smtp_username='encomendas@alitools.pt',
            use_tls=False,
            use_ssl=True,
            
            # IMAP (real config)
            imap_server='mail.alitools.pt',
            imap_port=993,
            imap_use_ssl=True,
            
            is_active=True,
            daily_limit=1000,
            monthly_limit=10000
        )
        
        # Set real password
        from flask import current_app
        encryption_key = current_app.config['ENCRYPTION_KEY']
        account.set_password('6f2zniWMN6aUFaD', encryption_key)
        account.save()
        
        print(f"✅ Created encomendas@alitools.pt with real configuration")
        return account
    
    print(f"✅ Account encomendas@alitools.pt already exists")
    return account
```

### 6. ADD Flask CLI Command

In sendcraft/cli.py:

```python
@click.command()
def seed_real_account():
    """Seed real encomendas@alitools.pt account."""
    from .cli.seed_real_account import seed_encomendas_account
    
    with current_app.app_context():
        account = seed_encomendas_account()
        click.echo(f"Account created: {account.email_address}")

def register_commands(app):
    """Register CLI commands."""
    # Existing commands...
    app.cli.add_command(seed_real_account)
```

### 7. UPDATE Database Migration

Ensure migration includes all IMAP fields:

```python
def upgrade():
    # Add IMAP fields to email_accounts
    op.add_column('email_accounts', sa.Column('imap_server', sa.String(200), server_default='mail.alitools.pt'))
    op.add_column('email_accounts', sa.Column('imap_port', sa.Integer(), server_default='993'))
    op.add_column('email_accounts', sa.Column('imap_use_ssl', sa.Boolean(), server_default=True))
    op.add_column('email_accounts', sa.Column('imap_use_tls', sa.Boolean(), server_default=False))
    op.add_column('email_accounts', sa.Column('last_sync', sa.DateTime()))
    op.add_column('email_accounts', sa.Column('auto_sync_enabled', sa.Boolean(), server_default=True))
    op.add_column('email_accounts', sa.Column('sync_interval_minutes', sa.Integer(), server_default='5'))
    
    # Create email_inbox table
    op.create_table('email_inbox',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.String(255), nullable=False),
        sa.Column('from_address', sa.String(255), nullable=False),
        sa.Column('to_addresses', sa.JSON()),
        sa.Column('subject', sa.Text()),
        sa.Column('body_text', sa.Text()),
        sa.Column('body_html', sa.Text()),
        sa.Column('received_at', sa.DateTime(), nullable=False),
        sa.Column('size_bytes', sa.Integer()),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('is_flagged', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('attachments', sa.JSON()),
        sa.Column('raw_headers', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['account_id'], ['email_accounts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id')
    )
    
    # Create indexes
    op.create_index('ix_email_inbox_account_id', 'email_inbox', ['account_id'])
    op.create_index('ix_email_inbox_received_at', 'email_inbox', ['received_at'])
    op.create_index('ix_email_inbox_is_read', 'email_inbox', ['is_read'])
    op.create_index('ix_email_inbox_from_address', 'email_inbox', ['from_address'])
```

### 8. PERFORMANCE OPTIMIZATION

Add to config for better IMAP performance:

```python
class DevelopmentConfig(Config):
    # Existing config...
    
    # IMAP Connection Settings
    IMAP_CONNECTION_TIMEOUT = 30
    IMAP_READ_TIMEOUT = 60  
    EMAIL_SYNC_BATCH_SIZE = 50
    EMAIL_CACHE_SIZE = 100
```

## Integration Checklist:

- [ ] Routes registered and working
- [ ] API endpoints accessible  
- [ ] Models imported correctly
- [ ] Navigation updated
- [ ] Database migration applied
- [ ] Real account seeded
- [ ] Email client JavaScript loading
- [ ] CSS styles applied
- [ ] IMAP connection working
- [ ] Email sync functional

## Testing:

After implementation, test:
1. `python rundev.py` - should start without errors
2. Navigate to http://localhost:5000/emails/inbox
3. Select encomendas@alitools.pt account
4. Click "Sincronizar" - should fetch real emails
5. Click on email item - should display content

Complete all integration points to have fully functional email management system!
```

---

## 📋 **RESUMO EXECUTIVO - PRÓXIMOS PASSOS**

### **ORDEM DE EXECUÇÃO RECOMENDADA:**

1. **Setup Environment** (5 min) - User executa
2. **Prompt 1 → Claude 4.1 Opus** (15 min) - Backend IMAP  
3. **Apply Migration** (2 min) - User executa: `flask db upgrade`
4. **Prompt 2 → Claude 4.1 Opus** (20 min) - Frontend Client
5. **Prompt 3 → Cursor Agent** (10 min) - Integration  
6. **Seed Real Account** (2 min) - User executa
7. **Testing & Validation** (6 min) - User testa

**TOTAL: ~1 hora para sistema completo de email management enterprise-grade!**

### **RESULTADO FINAL:**
- ✅ Email Client moderno three-pane
- ✅ IMAP sync com mail.alitools.pt  
- ✅ Interface responsiva e profissional
- ✅ Real-time email management
- ✅ Configurações REAIS funcionais
- ✅ API completa para integrações futuras

**O SendCraft transformar-se-á numa solução completa de email management que rivaliza com ferramentas comerciais!** 🚀