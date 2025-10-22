# 🔧 PROMPT 3: SendCraft Integration & Optimization (Cursor Agent)

## Context:
- Backend IMAP services have been implemented (EmailInbox model, IMAPService, RealtimeEmailService, API endpoints)
- Frontend email client interface has been created (three-pane layout, CSS, JavaScript components)
- Need to integrate everything into the existing SendCraft application and optimize for production

## Task: Complete Integration and System Optimization

### 1. ROUTES INTEGRATION

#### Update sendcraft/routes/web.py:

Add email client routes:

```python
# Email Client Routes
@web_bp.route('/emails')
@web_bp.route('/emails/inbox')
def emails_inbox():
    """Email inbox interface"""
    accounts = EmailAccount.get_active_accounts()
    
    # Get unread counts for each account
    for account in accounts:
        account.unread_count = EmailInbox.query.filter_by(
            account_id=account.id,
            is_read=False
        ).count()
    
    return render_template('emails/inbox.html', 
                         accounts=accounts,
                         page_title='Inbox')

@web_bp.route('/emails/outbox')
def emails_outbox():
    """Sent emails interface"""
    accounts = EmailAccount.get_active_accounts()
    recent_sent = EmailLog.get_recent_logs(limit=50)
    
    return render_template('emails/outbox.html',
                         accounts=accounts, 
                         recent_logs=recent_sent,
                         page_title='Sent')

@web_bp.route('/emails/compose')
def emails_compose():
    """Email composer interface"""
    accounts = EmailAccount.get_active_accounts()
    templates = EmailTemplate.get_active_templates()
    
    return render_template('emails/compose.html',
                         accounts=accounts,
                         templates=templates,
                         page_title='Compose')

@web_bp.route('/emails/<int:email_id>')
def emails_detail(email_id):
    """Individual email detail view"""
    email = EmailInbox.query.get_or_404(email_id)
    
    # Mark as read if not already
    if not email.is_read:
        email.is_read = True
        email.save()
    
    return render_template('emails/email_detail.html',
                         email=email,
                         page_title=email.subject)
```

### 2. API INTEGRATION

#### Update sendcraft/api/v1/__init__.py:

Register new email endpoints:

```python
from .emails_inbox import emails_bp

def register_blueprints(app):
    """Register all API blueprints"""
    # Existing blueprints...
    app.register_blueprint(emails_bp, url_prefix='/api/v1/emails')
```

#### Create SocketIO Integration:

Update sendcraft/__init__.py to include SocketIO:

```python
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app(config_name='development'):
    app = Flask(__name__)
    # Existing configuration...
    
    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Initialize real-time email service
    from .services.realtime_service import RealtimeEmailService
    app.realtime_service = RealtimeEmailService(socketio)
    
    return app
```

### 3. DATABASE OPTIMIZATIONS

#### Create optimized indexes in migration:

```python
# In the EmailInbox migration, add these indexes:
op.create_index('ix_email_inbox_compound_search', 'email_inbox', 
                ['account_id', 'is_read', 'received_at'])
op.create_index('ix_email_inbox_fulltext', 'email_inbox', 
                ['subject', 'body_text'])
```

#### Add query optimization methods:

```python
# In EmailInbox model, add:
@classmethod
def get_inbox_optimized(cls, account_id, page=1, per_page=50, search=None):
    """Optimized inbox query with minimal data transfer"""
    query = cls.query.filter_by(account_id=account_id, is_deleted=False) \
                    .options(load_only('id', 'subject', 'from_address', 
                                     'received_at', 'is_read', 'is_flagged'))
    
    if search:
        query = query.filter(
            or_(cls.subject.contains(search),
                cls.from_address.contains(search))
        )
    
    return query.order_by(cls.received_at.desc()) \
                .paginate(page=page, per_page=per_page, error_out=False)
```

### 4. REAL-TIME FEATURES IMPLEMENTATION

#### Background IMAP sync process:

```python
# Create sendcraft/services/background_sync.py
import threading
import time
from flask import current_app

class BackgroundSyncManager:
    def __init__(self, app):
        self.app = app
        self.sync_threads = {}
        self.stop_events = {}
        
    def start_account_sync(self, account_id):
        """Start background sync for an account"""
        if account_id in self.sync_threads:
            return  # Already syncing
            
        stop_event = threading.Event()
        sync_thread = threading.Thread(
            target=self._sync_worker,
            args=(account_id, stop_event)
        )
        
        self.sync_threads[account_id] = sync_thread
        self.stop_events[account_id] = stop_event
        sync_thread.start()
    
    def _sync_worker(self, account_id, stop_event):
        """Background sync worker"""
        with self.app.app_context():
            while not stop_event.is_set():
                try:
                    self._perform_sync(account_id)
                except Exception as e:
                    current_app.logger.error(f"Sync error for account {account_id}: {e}")
                
                # Wait for next sync interval
                stop_event.wait(300)  # 5 minutes
    
    def _perform_sync(self, account_id):
        """Perform actual IMAP sync"""
        from .imap_service import IMAPService
        from ..models.account import EmailAccount
        
        account = EmailAccount.query.get(account_id)
        if account and account.auto_sync_enabled:
            imap_service = IMAPService(account, current_app.config['ENCRYPTION_KEY'])
            result = imap_service.sync_account_emails()
            
            # Broadcast sync status via SocketIO
            if hasattr(current_app, 'realtime_service'):
                current_app.realtime_service.broadcast_sync_status(
                    {'account_id': account_id, 'status': 'completed', 'result': result}
                )
```

### 5. ERROR HANDLING ENHANCEMENT

#### Comprehensive error handling:

```python
# Update API endpoints with proper error handling
@emails_bp.errorhandler(Exception)
def handle_api_error(error):
    """Global error handler for email API"""
    current_app.logger.error(f"Email API error: {str(error)}")
    
    if isinstance(error, imaplib.IMAP4.error):
        return jsonify({
            'success': False,
            'error': 'IMAP connection failed',
            'message': 'Unable to connect to email server'
        }), 503
    
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

# Add connection timeout handling
class TimeoutIMAPConnection:
    def __init__(self, timeout=30):
        self.timeout = timeout
    
    def __enter__(self):
        signal.signal(signal.SIGALRM, self._timeout_handler)
        signal.alarm(self.timeout)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)
        
    def _timeout_handler(self, signum, frame):
        raise TimeoutError("IMAP connection timeout")
```

### 6. PERFORMANCE TUNING

#### Frontend optimizations:

```javascript
// Add to EmailClientApp.js
class EmailCache {
    constructor(maxSize = 100) {
        this.cache = new Map();
        this.maxSize = maxSize;
    }
    
    get(key) {
        if (this.cache.has(key)) {
            const item = this.cache.get(key);
            this.cache.delete(key);
            this.cache.set(key, item); // Move to end (LRU)
            return item;
        }
        return null;
    }
    
    set(key, value) {
        if (this.cache.size >= this.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        this.cache.set(key, value);
    }
}

// Virtual scrolling implementation
class VirtualEmailList {
    constructor(container, itemHeight = 80) {
        this.container = container;
        this.itemHeight = itemHeight;
        this.scrollTop = 0;
        this.containerHeight = container.clientHeight;
        
        this.setupScrolling();
    }
    
    render(items) {
        const totalHeight = items.length * this.itemHeight;
        const visibleStart = Math.floor(this.scrollTop / this.itemHeight);
        const visibleEnd = Math.min(
            visibleStart + Math.ceil(this.containerHeight / this.itemHeight) + 5,
            items.length
        );
        
        // Render only visible items
        const visibleItems = items.slice(visibleStart, visibleEnd);
        this.renderItems(visibleItems, visibleStart, totalHeight);
    }
}
```

#### Backend optimizations:

```python
# Add connection pooling for IMAP
from sqlalchemy.pool import QueuePool

# Update database configuration
SQLALCHEMY_ENGINE_OPTIONS = {
    'poolclass': QueuePool,
    'pool_size': 20,
    'max_overflow': 30,
    'pool_pre_ping': True,
    'pool_recycle': 3600,
}

# Add email content compression
import gzip
import json

def compress_email_content(content):
    """Compress large email content"""
    if len(content) > 10000:  # Only compress large content
        compressed = gzip.compress(content.encode('utf-8'))
        return {
            'compressed': True,
            'data': compressed.hex()
        }
    return {'compressed': False, 'data': content}
```

### 7. TESTING INTEGRATION

#### Create comprehensive tests:

```python
# tests/test_email_client.py
class TestEmailClient:
    def test_inbox_route(self, client, auth_headers):
        """Test inbox route loads correctly"""
        response = client.get('/emails/inbox')
        assert response.status_code == 200
        assert b'email-client-container' in response.data
    
    def test_imap_service(self, sample_account):
        """Test IMAP service functionality"""
        imap_service = IMAPService(sample_account, 'test_key')
        # Add specific IMAP tests
    
    def test_realtime_updates(self, client, socketio_client):
        """Test SocketIO real-time updates"""
        # Test email notifications
        pass
    
    def test_email_search(self, client):
        """Test email search functionality"""
        response = client.get('/api/v1/emails/search/1?q=test')
        assert response.status_code == 200

# Create test fixtures for email data
@pytest.fixture
def sample_emails():
    """Sample email data for testing"""
    return [
        {
            'subject': 'Test Email 1',
            'from_address': 'test1@example.com',
            'body_text': 'This is a test email',
            'received_at': datetime.utcnow()
        }
        # Add more sample emails
    ]
```

### 8. CONFIGURATION UPDATES

#### Update configuration files:

```python
# Add to config.py
class Config:
    # Email client settings
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    IMAP_CONNECTION_TIMEOUT = 30
    EMAIL_CACHE_SIZE = 1000
    MAX_EMAIL_SYNC_WORKERS = 5
    EMAIL_SYNC_BATCH_SIZE = 100
    
    # Performance settings
    EMAIL_LIST_PAGE_SIZE = 50
    EMAIL_CONTENT_COMPRESSION = True
    VIRTUAL_SCROLLING_ENABLED = True

# Update requirements.txt
flask-socketio==5.9.0
email-validator==2.1.0
```

### 9. NAVIGATION INTEGRATION

#### Update main navigation:

```html
<!-- In base.html navigation -->
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('web.emails_inbox') }}">
        <i class="bi bi-envelope me-2"></i>
        Email
        <span class="badge bg-primary ms-1" id="global-unread-count">0</span>
    </a>
</li>
```

### 10. DEPLOYMENT PREPARATION

#### Create deployment script:

```bash
#!/bin/bash
# deploy_email_client.sh

echo "🚀 Deploying SendCraft Email Client..."

# Apply database migrations
flask db upgrade

# Install new dependencies
pip install -r requirements.txt

# Compile CSS and JS assets
python manage.py collect-static

# Restart background services
systemctl restart sendcraft-sync-workers

echo "✅ Email client deployed successfully!"
```

## Integration Checklist:

- [ ] Routes integrated with proper authentication
- [ ] SocketIO configured and working
- [ ] Database migrations applied
- [ ] Background sync processes running
- [ ] Error handling comprehensive
- [ ] Performance optimizations applied
- [ ] Tests passing
- [ ] Navigation updated
- [ ] Configuration complete
- [ ] Deployment ready

Implement all integration points ensuring seamless operation with the existing SendCraft system while maintaining high performance and reliability.