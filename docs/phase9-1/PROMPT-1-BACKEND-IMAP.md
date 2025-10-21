# 📧 PROMPT 1: SendCraft Backend IMAP Implementation

## Context:
- Existing Flask app with SQLAlchemy models (EmailAccount, EmailLog, EmailTemplate)
- Need to implement IMAP email receiving functionality  
- Current structure: sendcraft/models/, sendcraft/services/, sendcraft/api/v1/
- Project uses MySQL database with proper relationships and foreign keys
- Existing encryption system for SMTP passwords using AESCipher

## Task: Implement Complete IMAP Backend Foundation

### 1. NEW MODEL: EmailInbox (sendcraft/models/email_inbox.py)

Create complete SQLAlchemy model with these specifications:

```python
class EmailInbox(BaseModel, TimestampMixin):
    """
    Model for received emails via IMAP.
    Must follow existing SendCraft patterns and integrate with EmailAccount.
    """
    __tablename__ = 'email_inbox'
    
    # Required fields:
    account_id = Column(Integer, ForeignKey('email_accounts.id'), nullable=False)
    message_id = Column(String(255), unique=True, nullable=False, index=True)
    thread_id = Column(String(255), index=True)  # For conversation grouping
    
    # Email content fields
    from_address = Column(String(255), nullable=False, index=True)
    to_addresses = Column(JSON)  # Multiple recipients support
    cc_addresses = Column(JSON)  # CC recipients
    bcc_addresses = Column(JSON)  # BCC recipients  
    subject = Column(Text)
    body_text = Column(LONGTEXT)
    body_html = Column(LONGTEXT)
    
    # Metadata
    received_at = Column(DateTime, nullable=False, index=True)
    size_bytes = Column(Integer)
    importance = Column(Enum('low', 'normal', 'high'), default='normal')
    
    # Status flags
    is_read = Column(Boolean, default=False, index=True)
    is_flagged = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Rich metadata
    attachments = Column(JSON)  # Attachment metadata
    raw_headers = Column(JSON)  # Original email headers
    
    # AI/Search fields
    category = Column(String(100))  # auto-categorized
    priority_score = Column(Float)  # calculated importance
    
    # Relationships
    account = relationship('EmailAccount', back_populates='inbox_emails')
```

Include methods for:
- Email search and filtering
- Conversation threading
- Read/unread status management
- Category management
- JSON serialization for API responses

### 2. EXTEND EmailAccount Model (modify sendcraft/models/account.py)

Add IMAP configuration fields:

```python
# Add to existing EmailAccount class:
# IMAP Configuration
imap_server = Column(String(200), default='imap.gmail.com')
imap_port = Column(Integer, default=993)
imap_use_ssl = Column(Boolean, default=True)
imap_use_tls = Column(Boolean, default=False)

# Sync settings
last_sync = Column(DateTime)
auto_sync_enabled = Column(Boolean, default=True)
sync_interval_minutes = Column(Integer, default=5)

# Relationships
inbox_emails = relationship('EmailInbox', back_populates='account', lazy='dynamic')
```

Add methods for IMAP configuration and sync management.

### 3. NEW SERVICE: IMAPService (sendcraft/services/imap_service.py)

Implement robust IMAP client with:

```python
class IMAPService:
    """
    Modern IMAP client with connection pooling, error handling, and real-time sync.
    Follows SendCraft service patterns with proper logging and error handling.
    """
    
    def __init__(self, account: EmailAccount, encryption_key: str):
        # Initialize with account and decryption capability
        
    def connect(self) -> imaplib.IMAP4_SSL:
        # Secure IMAP connection with proper error handling
        
    def fetch_recent_emails(self, limit: int = 50) -> List[Dict]:
        # Fetch and parse recent emails with full metadata
        
    def fetch_email_by_uid(self, uid: str) -> Dict:
        # Fetch specific email by UID
        
    def parse_email_message(self, raw_email: bytes) -> Dict:
        # Parse raw email into structured data
        
    def mark_as_read(self, uid: str) -> bool:
        # Mark email as read on IMAP server
        
    def search_emails(self, criteria: Dict) -> List[Dict]:
        # Advanced IMAP search with multiple criteria
        
    def start_idle_sync(self, callback: Callable) -> None:
        # IMAP IDLE for real-time email notifications
        
    def sync_account_emails(self) -> Dict:
        # Full account synchronization with progress tracking
```

Include comprehensive error handling, connection pooling, and integration with existing logging system.

### 4. NEW SERVICE: RealtimeEmailService (sendcraft/services/realtime_service.py)

Implement SocketIO integration:

```python
class RealtimeEmailService:
    """
    Real-time email synchronization using SocketIO.
    Coordinates IMAP sync with frontend notifications.
    """
    
    def __init__(self, socketio):
        # Initialize with SocketIO instance
        
    def start_account_sync(self, account_id: int, user_session: str):
        # Start real-time sync for specific account
        
    def broadcast_new_email(self, email_data: Dict, user_session: str):
        # Broadcast new email to connected clients
        
    def broadcast_sync_status(self, status: Dict, user_session: str):
        # Broadcast sync progress and status
        
    def handle_sync_events(self):
        # SocketIO event handlers for sync operations
```

### 5. API ENDPOINTS: Email Inbox Management (sendcraft/api/v1/emails_inbox.py)

Create comprehensive API with these endpoints:

```python
# GET /api/v1/emails/inbox/<account_id>
# List inbox emails with pagination, filters, search

# GET /api/v1/emails/inbox/<account_id>/<email_id>  
# Get specific email details with full content

# POST /api/v1/emails/sync/<account_id>
# Trigger manual IMAP sync for account

# PUT /api/v1/emails/inbox/<account_id>/<email_id>/read
# Mark email as read/unread

# PUT /api/v1/emails/inbox/<account_id>/<email_id>/flag
# Flag/unflag email

# DELETE /api/v1/emails/inbox/<account_id>/<email_id>
# Delete email (move to trash)

# GET /api/v1/emails/search/<account_id>
# Advanced email search with multiple criteria
```

Include proper authentication, error handling, and response formatting following existing API patterns.

### 6. DATABASE MIGRATION

Create Flask migration script:

```python
"""Add EmailInbox model and IMAP fields to EmailAccount"""

def upgrade():
    # Create email_inbox table with all fields and indexes
    # Add IMAP fields to email_accounts table  
    # Create necessary foreign keys and constraints
    # Add indexes for performance optimization

def downgrade():
    # Proper rollback procedures
```

## Requirements & Patterns to Follow:

### Code Quality:
- Follow existing SendCraft code patterns and style
- Use proper SQLAlchemy relationships and lazy loading
- Include comprehensive docstrings and type hints
- Implement proper error handling with logging
- Use existing encryption utilities for IMAP passwords

### Integration Points:
- Integrate with existing BaseModel and TimestampMixin
- Use current logging system (get_logger utility)
- Follow API response patterns from existing endpoints
- Maintain compatibility with current authentication system

### Performance Considerations:
- Implement connection pooling for IMAP connections
- Use proper database indexes for email search
- Optimize for large volumes of emails (10,000+ per account)
- Include pagination and lazy loading where appropriate

### Security:
- Secure IMAP credential handling using existing encryption
- Proper input validation and sanitization
- SQL injection prevention using SQLAlchemy ORM
- Rate limiting for API endpoints

Generate complete, production-ready code that seamlessly integrates with the existing SendCraft architecture and provides a robust foundation for email inbox management.