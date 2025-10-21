# 🎨 PROMPT 2: SendCraft Frontend Email Client Implementation

## Context:
- Existing Flask app with Bootstrap 5, Chart.js, jQuery, SocketIO ready
- Current templates in sendcraft/templates/, static files in sendcraft/static/
- Dashboard already implemented with modern card-based design
- Need modern three-pane email client interface similar to Superhuman/Mailspring
- Must integrate with existing design system and navigation

## Task: Implement Modern Email Client Frontend

### 1. EMAIL CLIENT TEMPLATES

#### sendcraft/templates/emails/inbox.html
Create three-pane email client layout:

```html
{% extends "base.html" %}
{% block title %}Inbox - SendCraft{% endblock %}

{% block content %}
<div class="email-client-container h-100">
    <!-- Sidebar - Accounts & Folders -->
    <div class="email-sidebar">
        <div class="sidebar-header">
            <h5><i class="bi bi-envelope me-2"></i>Email</h5>
            <button class="btn btn-primary btn-sm" id="compose-email">
                <i class="bi bi-plus"></i>
            </button>
        </div>
        
        <!-- Account Switcher -->
        <div class="account-switcher mb-3">
            <select class="form-select" id="account-selector">
                <option value="">All Accounts</option>
                {% for account in accounts %}
                <option value="{{ account.id }}" data-unread="{{ account.unread_count }}">
                    {{ account.email_address }}
                    {% if account.unread_count > 0 %}
                        <span class="badge bg-primary">{{ account.unread_count }}</span>
                    {% endif %}
                </option>
                {% endfor %}
            </select>
        </div>
        
        <!-- Smart Folders -->
        <div class="folder-list">
            <div class="folder-item active" data-folder="inbox">
                <i class="bi bi-inbox"></i> Inbox
                <span class="badge bg-primary" id="inbox-count">0</span>
            </div>
            <div class="folder-item" data-folder="sent">
                <i class="bi bi-send"></i> Sent
            </div>
            <div class="folder-item" data-folder="drafts">
                <i class="bi bi-file-earmark"></i> Drafts
            </div>
            <div class="folder-item" data-folder="archive">
                <i class="bi bi-archive"></i> Archive
            </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="sidebar-actions mt-3">
            <button class="btn btn-outline-primary btn-sm w-100 mb-2" id="sync-all">
                <i class="bi bi-arrow-clockwise"></i> Sync All
            </button>
            <button class="btn btn-outline-secondary btn-sm w-100" id="email-settings">
                <i class="bi bi-gear"></i> Settings
            </button>
        </div>
    </div>
    
    <!-- Email List -->
    <div class="email-list">
        <div class="list-header">
            <div class="search-bar">
                <input type="text" class="form-control" id="email-search" 
                       placeholder="Search emails...">
                <button class="btn btn-outline-secondary" id="search-btn">
                    <i class="bi bi-search"></i>
                </button>
            </div>
            
            <div class="list-actions">
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-secondary" id="select-all">
                        <i class="bi bi-check-square"></i>
                    </button>
                    <button class="btn btn-outline-secondary" id="mark-read" disabled>
                        <i class="bi bi-envelope-open"></i>
                    </button>
                    <button class="btn btn-outline-secondary" id="archive-selected" disabled>
                        <i class="bi bi-archive"></i>
                    </button>
                    <button class="btn btn-outline-danger" id="delete-selected" disabled>
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        </div>
        
        <div class="email-items" id="email-items-container">
            <!-- Dynamic email list populated by JavaScript -->
            <div class="loading-placeholder text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading emails...</span>
                </div>
            </div>
        </div>
        
        <!-- Pagination -->
        <div class="list-pagination">
            <nav aria-label="Email pagination">
                <ul class="pagination pagination-sm justify-content-center" id="email-pagination">
                    <!-- Dynamic pagination -->
                </ul>
            </nav>
        </div>
    </div>
    
    <!-- Email Preview/Composer -->
    <div class="email-content">
        <div class="content-header" id="email-header" style="display: none;">
            <!-- Email subject and actions -->
        </div>
        
        <div class="content-body" id="email-content-body">
            <div class="empty-state text-center py-5">
                <i class="bi bi-envelope text-muted" style="font-size: 4rem;"></i>
                <h4 class="text-muted mt-3">Select an email to view</h4>
                <p class="text-muted">Choose an email from the list to read its contents</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### sendcraft/templates/emails/outbox.html  
Create sent emails management interface with filtering and search.

#### sendcraft/templates/emails/compose.html
Create rich email composer with:
- Account selection dropdown
- To/CC/BCC fields with autocomplete
- Subject line
- Rich text editor (WYSIWYG)
- Template selector
- Attachment support
- Send/Save Draft/Discard actions

### 2. CSS FRAMEWORK (sendcraft/static/css/email-client.css)

Create comprehensive email client styles:

```css
/* Email Client Layout */
.email-client-container {
    display: flex;
    height: calc(100vh - 120px);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    background: white;
}

/* Sidebar Styles */
.email-sidebar {
    width: 280px;
    background: #f8f9fa;
    border-right: 1px solid #e9ecef;
    padding: 20px;
    overflow-y: auto;
}

.sidebar-header {
    display: flex;
    justify-content: between;
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
    align-items: center;
    justify-content: space-between;
    padding: 10px 12px;
    margin-bottom: 4px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #6c757d;
}

.folder-item:hover {
    background-color: #e9ecef;
    color: #495057;
}

.folder-item.active {
    background-color: #0066cc;
    color: white;
}

.folder-item i {
    margin-right: 10px;
    width: 16px;
}

/* Email List Styles */
.email-list {
    width: 400px;
    border-right: 1px solid #e9ecef;
    display: flex;
    flex-direction: column;
}

.list-header {
    padding: 20px;
    border-bottom: 1px solid #e9ecef;
    background: white;
    z-index: 10;
}

.search-bar {
    display: flex;
    gap: 8px;
    margin-bottom: 15px;
}

.list-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.email-items {
    flex: 1;
    overflow-y: auto;
}

/* Email Item Styles */
.email-item {
    padding: 16px 20px;
    border-bottom: 1px solid #f1f3f4;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
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

.email-item.unread .email-subject {
    color: #212529;
    font-weight: 600;
}

.email-sender {
    font-weight: 500;
    color: #495057;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.email-subject {
    color: #6c757d;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.email-preview {
    color: #adb5bd;
    font-size: 0.875rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.email-time {
    font-size: 0.75rem;
    color: #adb5bd;
}

/* Email Content Area */
.email-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: white;
}

.content-header {
    padding: 20px;
    border-bottom: 1px solid #e9ecef;
    background: white;
}

.content-body {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
}

.email-content-wrapper {
    max-width: 800px;
    margin: 0 auto;
}

.email-meta {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.email-body {
    line-height: 1.6;
    color: #495057;
}

/* Responsive Design */
@media (max-width: 1200px) {
    .email-list {
        width: 350px;
    }
}

@media (max-width: 992px) {
    .email-client-container {
        flex-direction: column;
    }
    
    .email-sidebar {
        width: 100%;
        height: auto;
        border-right: none;
        border-bottom: 1px solid #e9ecef;
    }
    
    .email-list {
        width: 100%;
        height: 300px;
        border-right: none;
        border-bottom: 1px solid #e9ecef;
    }
    
    .email-content {
        height: 400px;
    }
}

@media (max-width: 768px) {
    .email-sidebar {
        position: fixed;
        top: 0;
        left: -280px;
        height: 100vh;
        z-index: 1000;
        transition: left 0.3s ease;
    }
    
    .email-sidebar.open {
        left: 0;
    }
    
    .sidebar-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 999;
        display: none;
    }
    
    .sidebar-overlay.show {
        display: block;
    }
}

/* Dark Theme Support */
@media (prefers-color-scheme: dark) {
    .email-client-container {
        background: #1a1a1a;
        color: #e9ecef;
    }
    
    .email-sidebar {
        background: #2d2d2d;
        border-color: #404040;
    }
    
    .email-list {
        border-color: #404040;
    }
    
    .email-item {
        border-color: #404040;
    }
    
    .email-item:hover {
        background-color: #404040;
    }
    
    .email-item.unread {
        background-color: #3d3d00;
    }
}

/* Loading and Empty States */
.loading-placeholder {
    color: #6c757d;
}

.empty-state {
    color: #adb5bd;
}

/* Virtual Scrolling Optimization */
.virtual-list-container {
    height: 100%;
    overflow: auto;
}

.virtual-list-item {
    height: 80px;
    display: flex;
    align-items: center;
}

/* Animation for smooth interactions */
.fade-in {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.slide-in {
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from { transform: translateX(-20px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
```

### 3. JAVASCRIPT COMPONENTS

#### sendcraft/static/js/email-client/EmailClientApp.js
Main application controller with state management:

```javascript
/**
 * SendCraft Email Client Application
 * Modern email client with three-pane interface and real-time updates
 */
class EmailClientApp {
    constructor() {
        this.state = {
            activeAccount: null,
            selectedEmail: null,
            emailList: [],
            currentFolder: 'inbox',
            searchQuery: '',
            selectedEmails: new Set(),
            loading: false,
            syncStatus: {}
        };
        
        this.components = {
            emailList: new EmailList(this),
            emailPreview: new EmailPreview(this),
            emailComposer: new EmailComposer(this),
            realtimeUpdates: new RealtimeUpdates(this)
        };
        
        this.cache = new EmailCache(100); // Cache up to 100 emails
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadAccountList();
        this.components.realtimeUpdates.connect();
        
        // Load inbox for first account by default
        const firstAccount = document.querySelector('#account-selector option[value!=""]');
        if (firstAccount) {
            this.selectAccount(firstAccount.value);
        }
    }
    
    setupEventListeners() {
        // Account selection
        $('#account-selector').on('change', (e) => {
            this.selectAccount(e.target.value);
        });
        
        // Folder navigation
        $('.folder-item').on('click', (e) => {
            const folder = e.currentTarget.dataset.folder;
            this.selectFolder(folder);
        });
        
        // Search functionality
        $('#email-search').on('input', debounce((e) => {
            this.searchEmails(e.target.value);
        }, 300));
        
        // Bulk actions
        $('#select-all').on('click', () => this.toggleSelectAll());
        $('#mark-read').on('click', () => this.markSelectedAsRead());
        $('#archive-selected').on('click', () => this.archiveSelected());
        $('#delete-selected').on('click', () => this.deleteSelected());
        
        // Compose email
        $('#compose-email').on('click', () => this.composeEmail());
        
        // Manual sync
        $('#sync-all').on('click', () => this.syncAllAccounts());
        
        // Keyboard shortcuts
        this.setupKeyboardShortcuts();
    }
    
    async selectAccount(accountId) {
        if (!accountId) return;
        
        this.state.activeAccount = accountId;
        this.state.selectedEmail = null;
        this.state.selectedEmails.clear();
        
        // Update UI
        this.updateFolderCounts();
        await this.loadEmails();
        this.updateBulkActions();
    }
    
    async selectFolder(folder) {
        $('.folder-item').removeClass('active');
        $(`.folder-item[data-folder="${folder}"]`).addClass('active');
        
        this.state.currentFolder = folder;
        this.state.selectedEmail = null;
        this.state.selectedEmails.clear();
        
        await this.loadEmails();
        this.components.emailPreview.showEmptyState();
    }
    
    async loadEmails(page = 1) {
        if (!this.state.activeAccount) return;
        
        this.setState({ loading: true });
        
        try {
            const endpoint = this.getEmailEndpoint();
            const params = new URLSearchParams({
                page: page,
                per_page: 50,
                folder: this.state.currentFolder,
                search: this.state.searchQuery
            });
            
            const response = await fetch(`${endpoint}?${params}`);
            const data = await response.json();
            
            if (data.success) {
                this.state.emailList = data.emails;
                this.components.emailList.render(data.emails);
                this.updatePagination(data.pagination);
                
                // Cache emails
                data.emails.forEach(email => {
                    this.cache.set(email.id, email);
                });
            } else {
                this.showNotification('Error loading emails', 'error');
            }
        } catch (error) {
            console.error('Error loading emails:', error);
            this.showNotification('Failed to load emails', 'error');
        } finally {
            this.setState({ loading: false });
        }
    }
    
    getEmailEndpoint() {
        const baseUrl = '/api/v1/emails';
        if (this.state.currentFolder === 'inbox') {
            return `${baseUrl}/inbox/${this.state.activeAccount}`;
        } else if (this.state.currentFolder === 'sent') {
            return `${baseUrl}/sent/${this.state.activeAccount}`;
        }
        // Add other folder endpoints as needed
        return `${baseUrl}/inbox/${this.state.activeAccount}`;
    }
    
    setState(newState) {
        Object.assign(this.state, newState);
        this.updateUI();
    }
    
    updateUI() {
        // Update loading states
        if (this.state.loading) {
            $('.loading-placeholder').show();
        } else {
            $('.loading-placeholder').hide();
        }
        
        // Update sync status indicators
        Object.keys(this.state.syncStatus).forEach(accountId => {
            const status = this.state.syncStatus[accountId];
            $(`[data-account="${accountId}"] .sync-indicator`).attr('class', `sync-indicator ${status}`);
        });
    }
    
    // Additional methods for email operations, sync management, etc.
}

// Utility functions
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

// Initialize app when DOM is ready
$(document).ready(() => {
    window.emailApp = new EmailClientApp();
});
```

#### Additional Components:
- EmailList.js - Virtual scrolling email list with selection
- EmailPreview.js - Email content viewer with security
- EmailComposer.js - Rich text email composer
- RealtimeUpdates.js - SocketIO real-time synchronization

### 4. SOCKETIO INTEGRATION

Implement real-time updates for:
- New email notifications
- Sync status updates  
- Read/unread status changes
- Email count updates

### 5. PERFORMANCE OPTIMIZATIONS

- Virtual scrolling for large email lists
- Intelligent email content caching
- Lazy loading of images and attachments
- Debounced search and filtering
- Progressive enhancement for mobile

Generate complete, production-ready frontend code that provides exceptional user experience and integrates seamlessly with the existing SendCraft design system.