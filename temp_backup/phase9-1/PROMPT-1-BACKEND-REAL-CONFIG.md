# 📧 PROMPT 1 UPDATED: SendCraft Backend IMAP - encomendas@alitools.pt

## Context:
- Existing Flask app with SQLAlchemy models (EmailAccount, EmailLog, EmailTemplate)
- Real email account: encomendas@alitools.pt with confirmed cPanel configurations
- Need IMAP email receiving functionality with REAL working credentials
- Current structure: sendcraft/models/, sendcraft/services/, sendcraft/api/v1/

## REAL EMAIL ACCOUNT CONFIGURATION (from cPanel):
```yaml
Email: encomendas@alitools.pt
Password: 6f2zniWMN6aUFaD

# IMAP Settings (Incoming - SSL/TLS Secure)
IMAP_SERVER: mail.alitools.pt
IMAP_PORT: 993
IMAP_SSL: true
IMAP_AUTH: true

# SMTP Settings (Outgoing - SSL/TLS Secure) 
SMTP_SERVER: mail.alitools.pt
SMTP_PORT: 465
SMTP_SSL: true
SMTP_AUTH: true
```

## Task: Implement Complete IMAP Backend with REAL Configuration

### 1. NEW MODEL: EmailInbox (sendcraft/models/email_inbox.py)

Create complete SQLAlchemy model for received emails:

```python
"""Modelo de Email Inbox para SendCraft."""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum

from .base import BaseModel, TimestampMixin
from ..utils.logging import get_logger

logger = get_logger(__name__)

class EmailInbox(BaseModel, TimestampMixin):
    """
    Modelo para emails recebidos via IMAP.
    Integra com EmailAccount e suporta conversação threading.
    """
    
    __tablename__ = 'email_inbox'
    
    # Relacionamentos
    account_id = Column(Integer, ForeignKey('email_accounts.id'), nullable=False, index=True)
    account = relationship('EmailAccount', back_populates='inbox_emails')
    
    # Identificadores únicos
    message_id = Column(String(255), unique=True, nullable=False, index=True)
    thread_id = Column(String(255), index=True)  # Para agrupamento conversacional
    
    # Conteúdo do email
    from_address = Column(String(255), nullable=False, index=True)
    to_addresses = Column(JSON)  # Lista de destinatários
    cc_addresses = Column(JSON)  # Lista CC
    bcc_addresses = Column(JSON)  # Lista BCC
    subject = Column(Text)
    body_text = Column(Text)  # Versão texto
    body_html = Column(Text)   # Versão HTML
    
    # Metadata
    received_at = Column(DateTime, nullable=False, index=True)
    size_bytes = Column(Integer)
    importance = Column(String(20), default='normal')  # low, normal, high
    
    # Flags de estado
    is_read = Column(Boolean, default=False, index=True)
    is_flagged = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Dados ricos
    attachments = Column(JSON)  # Metadata dos anexos
    raw_headers = Column(JSON)  # Headers originais do email
    
    # Campos para AI/Search
    category = Column(String(100))  # work, personal, newsletter, etc.
    priority_score = Column(Float, default=0.5)  # 0.0-1.0
    
    def __repr__(self) -> str:
        return f'<EmailInbox {self.id}: {self.subject[:50]}...>'
    
    @classmethod
    def get_inbox_emails(cls, account_id: int, page: int = 1, per_page: int = 50) -> List['EmailInbox']:
        """Retorna emails da inbox paginados."""
        return cls.query.filter_by(
            account_id=account_id,
            is_deleted=False,
            is_archived=False
        ).order_by(cls.received_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @classmethod
    def get_unread_count(cls, account_id: int) -> int:
        """Conta emails não lidos."""
        return cls.query.filter_by(
            account_id=account_id,
            is_read=False,
            is_deleted=False
        ).count()
    
    def mark_as_read(self) -> None:
        """Marca email como lido."""
        self.is_read = True
        self.save()
        logger.info(f"Email {self.id} marked as read")
    
    def to_dict(self, include_body: bool = False) -> dict:
        """Converte para dicionário para API."""
        data = {
            'id': self.id,
            'message_id': self.message_id,
            'from_address': self.from_address,
            'to_addresses': self.to_addresses,
            'subject': self.subject,
            'received_at': self.received_at.isoformat(),
            'is_read': self.is_read,
            'is_flagged': self.is_flagged,
            'size_bytes': self.size_bytes,
            'attachments': self.attachments or [],
            'category': self.category,
            'priority_score': self.priority_score
        }
        
        if include_body:
            data.update({
                'body_text': self.body_text,
                'body_html': self.body_html,
                'raw_headers': self.raw_headers
            })
        
        return data
```

### 2. EXTEND EmailAccount Model (modify sendcraft/models/account.py)

Add IMAP fields to existing EmailAccount class:

```python
# Add these fields to the existing EmailAccount class:

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
    """Retorna configuração IMAP para conexão."""
    return {
        'server': self.imap_server,
        'port': self.imap_port,
        'username': self.email_address,
        'password': self.get_password(encryption_key),
        'use_ssl': self.imap_use_ssl,
        'use_tls': self.imap_use_tls
    }
```

### 3. NEW SERVICE: IMAPService (sendcraft/services/imap_service.py)

Implement IMAP client specifically for mail.alitools.pt:

```python
"""Serviço IMAP para SendCraft - Configuração mail.alitools.pt."""
import imaplib
import email
import time
import threading
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from email.header import decode_header

from ..models.account import EmailAccount
from ..models.email_inbox import EmailInbox
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)

class IMAPService:
    """
    Cliente IMAP otimizado para mail.alitools.pt (SSL port 993).
    Suporta conexão segura, parsing de emails e sync real-time.
    """
    
    def __init__(self, account: EmailAccount, encryption_key: str):
        self.account = account
        self.encryption_key = encryption_key
        self.connection = None
        self._stop_sync = False
        
    def connect(self) -> imaplib.IMAP4_SSL:
        """Conecta ao servidor IMAP com SSL."""
        try:
            # Conectar especificamente para mail.alitools.pt:993 SSL
            connection = imaplib.IMAP4_SSL(
                host=self.account.imap_server or 'mail.alitools.pt',
                port=self.account.imap_port or 993
            )
            
            # Autenticar
            username = self.account.email_address
            password = self.account.get_password(self.encryption_key)
            
            connection.login(username, password)
            logger.info(f"IMAP connection established for {username}")
            
            return connection
            
        except Exception as e:
            logger.error(f"IMAP connection failed for {self.account.email_address}: {e}")
            raise
    
    def fetch_recent_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Busca emails recentes da INBOX."""
        emails = []
        
        try:
            with self.connect() as conn:
                # Selecionar INBOX
                conn.select('INBOX')
                
                # Buscar emails (mais recentes primeiro)
                typ, messages = conn.search(None, 'ALL')
                
                if typ != 'OK':
                    return emails
                
                message_ids = messages[0].split()
                
                # Pegar os últimos N emails
                for msg_id in message_ids[-limit:]:
                    try:
                        typ, msg_data = conn.fetch(msg_id, '(RFC822)')
                        
                        if typ == 'OK':
                            raw_email = msg_data[0][1]
                            parsed_email = self.parse_email_message(raw_email)
                            
                            if parsed_email:
                                emails.append(parsed_email)
                                
                    except Exception as e:
                        logger.error(f"Error fetching message {msg_id}: {e}")
                        continue
            
            logger.info(f"Fetched {len(emails)} emails for {self.account.email_address}")
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return emails
    
    def parse_email_message(self, raw_email: bytes) -> Optional[Dict[str, Any]]:
        """Converte raw email em dicionário estruturado."""
        try:
            msg = email.message_from_bytes(raw_email)
            
            # Headers básicos
            subject = self._decode_header(msg.get('Subject', ''))
            from_addr = self._decode_header(msg.get('From', ''))
            to_addr = self._decode_header(msg.get('To', ''))
            
            # Extrair conteúdo
            body_text, body_html = self._extract_body_content(msg)
            
            # Parse da data
            date_str = msg.get('Date', '')
            received_at = self._parse_date(date_str) or datetime.utcnow()
            
            return {
                'message_id': msg.get('Message-ID', ''),
                'subject': subject,
                'from_address': from_addr,
                'to_addresses': [to_addr] if to_addr else [],
                'cc_addresses': self._parse_addresses(msg.get('Cc', '')),
                'received_at': received_at,
                'body_text': body_text,
                'body_html': body_html,
                'size_bytes': len(raw_email),
                'raw_headers': dict(msg.items()),
                'attachments': self._extract_attachments(msg)
            }
            
        except Exception as e:
            logger.error(f"Error parsing email: {e}")
            return None
    
    def sync_account_emails(self) -> Dict[str, Any]:
        """Sincroniza emails da conta, salvando novos na database."""
        result = {
            'success': True,
            'new_emails': 0,
            'errors': [],
            'last_sync': datetime.utcnow()
        }
        
        try:
            # Buscar emails do servidor
            emails = self.fetch_recent_emails(limit=100)
            
            for email_data in emails:
                try:
                    # Verificar se já existe
                    existing = EmailInbox.query.filter_by(
                        message_id=email_data['message_id']
                    ).first()
                    
                    if not existing:
                        # Criar novo email
                        inbox_email = EmailInbox(
                            account_id=self.account.id,
                            **email_data
                        )
                        inbox_email.save()
                        result['new_emails'] += 1
                        
                except Exception as e:
                    error_msg = f"Error saving email: {e}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
            
            # Atualizar último sync
            self.account.last_sync = result['last_sync']
            self.account.save()
            
            logger.info(f"Sync completed for {self.account.email_address}: {result['new_emails']} new emails")
            
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            logger.error(f"Sync failed for {self.account.email_address}: {e}")
        
        return result
    
    def _decode_header(self, header: str) -> str:
        """Decodifica header do email."""
        if not header:
            return ''
        
        try:
            decoded_parts = decode_header(header)
            decoded_string = ''
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded_string += part
                    
            return decoded_string.strip()
            
        except Exception:
            return header
    
    def _extract_body_content(self, msg) -> tuple[str, str]:
        """Extrai conteúdo texto e HTML do email."""
        text_content = ''
        html_content = ''
        
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    
                    if content_type == 'text/plain':
                        text_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif content_type == 'text/html':
                        html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                content_type = msg.get_content_type()
                payload = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                
                if content_type == 'text/plain':
                    text_content = payload
                elif content_type == 'text/html':
                    html_content = payload
                else:
                    text_content = payload
                    
        except Exception as e:
            logger.error(f"Error extracting body content: {e}")
        
        return text_content, html_content
    
    def _parse_addresses(self, addresses: str) -> List[str]:
        """Parse endereços de email de uma string."""
        if not addresses:
            return []
        
        return [addr.strip() for addr in addresses.split(',') if addr.strip()]
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse data do email."""
        if not date_str:
            return None
        
        try:
            return email.utils.parsedate_to_datetime(date_str)
        except Exception:
            return None
    
    def _extract_attachments(self, msg) -> List[Dict[str, Any]]:
        """Extrai metadata dos anexos."""
        attachments = []
        
        try:
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': filename,
                            'content_type': part.get_content_type(),
                            'size': len(part.get_payload(decode=True) or b'')
                        })
        except Exception as e:
            logger.error(f"Error extracting attachments: {e}")
        
        return attachments
```

### 4. API ENDPOINTS: Email Inbox (sendcraft/api/v1/emails_inbox.py)

Create API endpoints for email management:

```python
"""API endpoints para gestão de email inbox."""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from ...models.account import EmailAccount
from ...models.email_inbox import EmailInbox
from ...services.imap_service import IMAPService
from ...utils.logging import get_logger

logger = get_logger(__name__)

emails_bp = Blueprint('emails', __name__)

@emails_bp.route('/inbox/<int:account_id>')
def get_inbox_emails(account_id):
    """Lista emails da inbox de uma conta."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        account = EmailAccount.query.get_or_404(account_id)
        
        # Buscar emails paginados
        pagination = EmailInbox.get_inbox_emails(account_id, page, per_page)
        emails = pagination.items
        
        return jsonify({
            'success': True,
            'account': {
                'id': account.id,
                'email_address': account.email_address,
                'unread_count': EmailInbox.get_unread_count(account_id)
            },
            'emails': [email.to_dict() for email in emails],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting inbox emails for account {account_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emails_bp.route('/inbox/<int:account_id>/<int:email_id>')
def get_email_details(account_id, email_id):
    """Obtém detalhes completos de um email."""
    try:
        email = EmailInbox.query.filter_by(
            id=email_id,
            account_id=account_id
        ).first_or_404()
        
        # Marcar como lido se ainda não estiver
        if not email.is_read:
            email.mark_as_read()
        
        return jsonify({
            'success': True,
            'email': email.to_dict(include_body=True)
        })
        
    except Exception as e:
        logger.error(f"Error getting email details {email_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emails_bp.route('/sync/<int:account_id>', methods=['POST'])
def sync_account_emails(account_id):
    """Sincroniza emails de uma conta via IMAP."""
    try:
        account = EmailAccount.query.get_or_404(account_id)
        encryption_key = current_app.config.get('ENCRYPTION_KEY')
        
        if not encryption_key:
            return jsonify({
                'success': False,
                'error': 'Encryption key not configured'
            }), 500
        
        # Executar sincronização IMAP
        imap_service = IMAPService(account, encryption_key)
        result = imap_service.sync_account_emails()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error syncing account {account_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@emails_bp.route('/inbox/<int:account_id>/<int:email_id>/read', methods=['PUT'])
def mark_email_read(account_id, email_id):
    """Marca email como lido/não lido."""
    try:
        is_read = request.json.get('is_read', True)
        
        email = EmailInbox.query.filter_by(
            id=email_id,
            account_id=account_id
        ).first_or_404()
        
        email.is_read = is_read
        email.save()
        
        return jsonify({
            'success': True,
            'email': email.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error updating read status for email {email_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

### 5. DATABASE MIGRATION

Create migration for new models:

```python
"""Add EmailInbox model and IMAP fields

Revision ID: add_email_inbox
Revises: previous_migration
Create Date: 2025-10-21 23:45:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = 'add_email_inbox'
down_revision = 'previous_migration'

def upgrade():
    # Add IMAP fields to email_accounts
    op.add_column('email_accounts', sa.Column('imap_server', sa.String(200), default='mail.alitools.pt'))
    op.add_column('email_accounts', sa.Column('imap_port', sa.Integer(), default=993))
    op.add_column('email_accounts', sa.Column('imap_use_ssl', sa.Boolean(), default=True))
    op.add_column('email_accounts', sa.Column('imap_use_tls', sa.Boolean(), default=False))
    op.add_column('email_accounts', sa.Column('last_sync', sa.DateTime()))
    op.add_column('email_accounts', sa.Column('auto_sync_enabled', sa.Boolean(), default=True))
    op.add_column('email_accounts', sa.Column('sync_interval_minutes', sa.Integer(), default=5))
    
    # Create email_inbox table
    op.create_table(
        'email_inbox',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('account_id', sa.Integer(), sa.ForeignKey('email_accounts.id'), nullable=False),
        sa.Column('message_id', sa.String(255), unique=True, nullable=False),
        sa.Column('thread_id', sa.String(255)),
        sa.Column('from_address', sa.String(255), nullable=False),
        sa.Column('to_addresses', sa.JSON()),
        sa.Column('cc_addresses', sa.JSON()),
        sa.Column('bcc_addresses', sa.JSON()),
        sa.Column('subject', sa.Text()),
        sa.Column('body_text', sa.Text()),
        sa.Column('body_html', sa.Text()),
        sa.Column('received_at', sa.DateTime(), nullable=False),
        sa.Column('size_bytes', sa.Integer()),
        sa.Column('importance', sa.String(20), default='normal'),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('is_flagged', sa.Boolean(), default=False),
        sa.Column('is_archived', sa.Boolean(), default=False),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('attachments', sa.JSON()),
        sa.Column('raw_headers', sa.JSON()),
        sa.Column('category', sa.String(100)),
        sa.Column('priority_score', sa.Float(), default=0.5),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create indexes for performance
    op.create_index('ix_email_inbox_account_id', 'email_inbox', ['account_id'])
    op.create_index('ix_email_inbox_message_id', 'email_inbox', ['message_id'])
    op.create_index('ix_email_inbox_received_at', 'email_inbox', ['received_at'])
    op.create_index('ix_email_inbox_is_read', 'email_inbox', ['is_read'])
    op.create_index('ix_email_inbox_from_address', 'email_inbox', ['from_address'])
    op.create_index('ix_email_inbox_compound_search', 'email_inbox', ['account_id', 'is_read', 'received_at'])

def downgrade():
    op.drop_table('email_inbox')
    
    # Remove IMAP fields from email_accounts
    op.drop_column('email_accounts', 'sync_interval_minutes')
    op.drop_column('email_accounts', 'auto_sync_enabled')
    op.drop_column('email_accounts', 'last_sync')
    op.drop_column('email_accounts', 'imap_use_tls')
    op.drop_column('email_accounts', 'imap_use_ssl')
    op.drop_column('email_accounts', 'imap_port')
    op.drop_column('email_accounts', 'imap_server')
```

### 6. SEED DATA for encomendas@alitools.pt

Create seed data with REAL configuration:

```python
# In seed data or CLI command
def seed_alitools_email_account():
    """Cria conta encomendas@alitools.pt com configurações reais."""
    from sendcraft.models.domain import Domain
    from sendcraft.models.account import EmailAccount
    
    # Criar domínio alitools.pt se não existir
    domain = Domain.query.filter_by(name='alitools.pt').first()
    if not domain:
        domain = Domain(
            name='alitools.pt',
            description='AliTools B2B Dropshipping Platform',
            is_active=True
        )
        domain.save()
    
    # Criar conta encomendas@alitools.pt com configurações reais
    account = EmailAccount.query.filter_by(email_address='encomendas@alitools.pt').first()
    if not account:
        account = EmailAccount(
            domain_id=domain.id,
            local_part='encomendas',
            email_address='encomendas@alitools.pt',
            display_name='AliTools Encomendas',
            
            # SMTP Configuration (real from cPanel)
            smtp_server='mail.alitools.pt',
            smtp_port=465,
            smtp_username='encomendas@alitools.pt',
            use_tls=False,
            use_ssl=True,
            
            # IMAP Configuration (real from cPanel)
            imap_server='mail.alitools.pt',
            imap_port=993,
            imap_use_ssl=True,
            imap_use_tls=False,
            
            # Sync settings
            auto_sync_enabled=True,
            sync_interval_minutes=5,
            
            is_active=True,
            daily_limit=1000,
            monthly_limit=10000
        )
        
        # Set encrypted password
        encryption_key = current_app.config['ENCRYPTION_KEY']
        account.set_password('6f2zniWMN6aUFaD', encryption_key)
        account.save()
        
        print(f"✅ Created encomendas@alitools.pt account with REAL configuration")
    
    return account
```

## Implementation Requirements:

1. **Use REAL configurations** from cPanel exactly as provided
2. **SSL/TLS security** - use port 993 SSL for IMAP, port 465 SSL for SMTP
3. **Error handling** for connection issues specific to mail.alitools.pt
4. **Password encryption** using existing AESCipher system
5. **Proper logging** for debugging IMAP/SMTP connections
6. **Performance optimization** for frequent email checking

## Testing Commands:

```bash
# Test IMAP connection
openssl s_client -connect mail.alitools.pt:993

# Test SMTP connection  
openssl s_client -connect mail.alitools.pt:465

# Test in Python
python3 -c "
from sendcraft.services.imap_service import IMAPService
from sendcraft.models.account import EmailAccount
account = EmailAccount.query.filter_by(email_address='encomendas@alitools.pt').first()
service = IMAPService(account, 'encryption_key')
result = service.sync_account_emails()
print(result)
"
```

Generate production-ready code that works immediately with the real encomendas@alitools.pt email account!