/**
 * SendCraft Phase 9.1 - Email Client Application
 * 
 * This JavaScript module handles:
 * - Email inbox functionality
 * - Real-time email updates
 * - Email search and filtering
 * - Email actions (mark as read, delete, etc.)
 * - WebSocket communication for live updates
 * - Responsive UI interactions
 */

class EmailClientApp {
    constructor() {
        this.emails = [];
        this.currentEmailId = null;
        this.isLoading = false;
        this.refreshInterval = null;
        this.socket = null;
        
        // API endpoints
        this.endpoints = {
            getEmails: '/emails/api/inbox/emails',
            getThreads: '/emails/api/inbox/threads',
            searchEmails: '/emails/api/inbox/search',
            markAsRead: '/emails/api/inbox/mark-read',
            deleteEmail: '/emails/api/inbox/delete'
        };
        
        // DOM elements
        this.elements = {};
    }
    
    /**
     * Initialize the email client application
     */
    init() {
        this.initElements();
        this.bindEvents();
        this.loadEmails();
        this.startAutoRefresh();
        
        console.log('EmailClientApp initialized');
    }
    
    /**
     * Initialize DOM element references
     */
    initElements() {
        this.elements = {
            emailList: document.getElementById('email-list'),
            loadingIndicator: document.getElementById('loading-indicator'),
            emptyState: document.getElementById('empty-state'),
            searchInput: document.getElementById('search-input'),
            searchBtn: document.getElementById('search-btn'),
            refreshBtn: document.getElementById('refresh-btn'),
            markAllReadBtn: document.getElementById('mark-all-read-btn'),
            inboxCount: document.getElementById('inbox-count'),
            emailDetailModal: document.getElementById('emailDetailModal'),
            emailDetailTitle: document.getElementById('emailDetailTitle'),
            emailDetailBody: document.getElementById('emailDetailBody'),
            deleteEmailBtn: document.getElementById('delete-email-btn')
        };
    }
    
    /**
     * Bind event listeners
     */
    bindEvents() {
        // Search functionality
        this.elements.searchInput.addEventListener('input', this.debounce(this.handleSearch.bind(this), 300));
        this.elements.searchBtn.addEventListener('click', this.handleSearch.bind(this));
        
        // Action buttons
        this.elements.refreshBtn.addEventListener('click', this.handleRefresh.bind(this));
        this.elements.markAllReadBtn.addEventListener('click', this.handleMarkAllRead.bind(this));
        this.elements.deleteEmailBtn.addEventListener('click', this.handleDeleteEmail.bind(this));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
        
        // Modal events
        this.elements.emailDetailModal.addEventListener('hidden.bs.modal', this.handleModalClose.bind(this));
    }
    
    /**
     * Load emails from the server
     */
    async loadEmails(limit = 50) {
        try {
            this.setLoading(true);
            
            const response = await fetch(`${this.endpoints.getEmails}?limit=${limit}`);
            const data = await response.json();
            
            if (response.ok) {
                this.emails = data.emails || [];
                this.renderEmails();
                this.updateInboxCount();
            } else {
                this.showError('Failed to load emails: ' + data.error);
            }
        } catch (error) {
            console.error('Error loading emails:', error);
            this.showError('Failed to load emails. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }
    
    /**
     * Render emails in the list
     */
    renderEmails() {
        if (!this.elements.emailList) return;
        
        if (this.emails.length === 0) {
            this.showEmptyState();
            return;
        }
        
        this.hideEmptyState();
        
        const emailListHTML = this.emails.map(email => this.createEmailItemHTML(email)).join('');
        this.elements.emailList.innerHTML = emailListHTML;
        
        // Add click handlers to email items
        this.elements.emailList.querySelectorAll('.email-item').forEach(item => {
            item.addEventListener('click', () => this.handleEmailClick(item.dataset.emailId));
        });
        
        // Add action button handlers
        this.elements.emailList.querySelectorAll('.mark-read-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleMarkAsRead(btn.dataset.emailId);
            });
        });
        
        this.elements.emailList.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleDeleteEmail(btn.dataset.emailId);
            });
        });
    }
    
    /**
     * Create HTML for a single email item
     */
    createEmailItemHTML(email) {
        const isUnread = !email.read;
        const date = new Date(email.date).toLocaleDateString();
        const preview = email.preview || email.body?.substring(0, 100) + '...';
        
        return `
            <div class="email-item ${isUnread ? 'unread' : 'read'} fade-in" data-email-id="${email.id}">
                <div class="email-meta">
                    <span class="email-sender">${this.escapeHtml(email.sender)}</span>
                    <span class="email-date">${date}</span>
                </div>
                <div class="email-subject">${this.escapeHtml(email.subject)}</div>
                <div class="email-preview">${this.escapeHtml(preview)}</div>
                <div class="email-actions-inline">
                    <button class="btn btn-outline-primary btn-sm mark-read-btn" data-email-id="${email.id}">
                        <i class="fas fa-check"></i>
                    </button>
                    <button class="btn btn-outline-danger btn-sm delete-btn" data-email-id="${email.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    /**
     * Handle email click
     */
    handleEmailClick(emailId) {
        const email = this.emails.find(e => e.id === emailId);
        if (!email) return;
        
        this.currentEmailId = emailId;
        this.showEmailDetail(email);
        
        // Mark as read if unread
        if (!email.read) {
            this.handleMarkAsRead(emailId);
        }
    }
    
    /**
     * Show email detail in modal
     */
    showEmailDetail(email) {
        if (!this.elements.emailDetailTitle || !this.elements.emailDetailBody) return;
        
        this.elements.emailDetailTitle.textContent = email.subject;
        
        const emailDetailHTML = `
            <div class="email-detail-header">
                <div class="email-detail-subject">${this.escapeHtml(email.subject)}</div>
                <div class="email-detail-meta">
                    <span><strong>From:</strong> ${this.escapeHtml(email.sender)}</span>
                    <span>${new Date(email.date).toLocaleString()}</span>
                </div>
            </div>
            <div class="email-detail-body">
                ${email.body || '<p>No content available</p>'}
            </div>
        `;
        
        this.elements.emailDetailBody.innerHTML = emailDetailHTML;
        
        // Show modal
        const modal = new bootstrap.Modal(this.elements.emailDetailModal);
        modal.show();
    }
    
    /**
     * Handle search
     */
    async handleSearch() {
        const query = this.elements.searchInput.value.trim();
        
        if (!query) {
            this.loadEmails();
            return;
        }
        
        try {
            this.setLoading(true);
            
            const response = await fetch(`${this.endpoints.searchEmails}?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (response.ok) {
                this.emails = data.results || [];
                this.renderEmails();
            } else {
                this.showError('Search failed: ' + data.error);
            }
        } catch (error) {
            console.error('Error searching emails:', error);
            this.showError('Search failed. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }
    
    /**
     * Handle refresh
     */
    handleRefresh() {
        this.loadEmails();
    }
    
    /**
     * Handle mark as read
     */
    async handleMarkAsRead(emailId) {
        try {
            const response = await fetch(this.endpoints.markAsRead, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email_id: emailId })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Update local email state
                const email = this.emails.find(e => e.id === emailId);
                if (email) {
                    email.read = true;
                }
                
                // Update UI
                const emailItem = this.elements.emailList.querySelector(`[data-email-id="${emailId}"]`);
                if (emailItem) {
                    emailItem.classList.remove('unread');
                    emailItem.classList.add('read');
                }
                
                this.updateInboxCount();
            } else {
                this.showError('Failed to mark email as read');
            }
        } catch (error) {
            console.error('Error marking email as read:', error);
            this.showError('Failed to mark email as read');
        }
    }
    
    /**
     * Handle mark all as read
     */
    async handleMarkAllRead() {
        const unreadEmails = this.emails.filter(email => !email.read);
        
        for (const email of unreadEmails) {
            await this.handleMarkAsRead(email.id);
        }
    }
    
    /**
     * Handle delete email
     */
    async handleDeleteEmail(emailId) {
        if (!emailId) {
            emailId = this.currentEmailId;
        }
        
        if (!emailId) return;
        
        if (!confirm('Are you sure you want to delete this email?')) {
            return;
        }
        
        try {
            const response = await fetch(this.endpoints.deleteEmail, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email_id: emailId })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Remove from local array
                this.emails = this.emails.filter(e => e.id !== emailId);
                
                // Update UI
                const emailItem = this.elements.emailList.querySelector(`[data-email-id="${emailId}"]`);
                if (emailItem) {
                    emailItem.remove();
                }
                
                // Close modal if deleting current email
                if (emailId === this.currentEmailId) {
                    const modal = bootstrap.Modal.getInstance(this.elements.emailDetailModal);
                    if (modal) {
                        modal.hide();
                    }
                }
                
                this.updateInboxCount();
            } else {
                this.showError('Failed to delete email');
            }
        } catch (error) {
            console.error('Error deleting email:', error);
            this.showError('Failed to delete email');
        }
    }
    
    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcuts(event) {
        // R key for refresh
        if (event.key === 'r' && (event.ctrlKey || event.metaKey)) {
            event.preventDefault();
            this.handleRefresh();
        }
        
        // Escape key to close modal
        if (event.key === 'Escape') {
            const modal = bootstrap.Modal.getInstance(this.elements.emailDetailModal);
            if (modal) {
                modal.hide();
            }
        }
    }
    
    /**
     * Handle modal close
     */
    handleModalClose() {
        this.currentEmailId = null;
    }
    
    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        // Refresh every 30 seconds
        this.refreshInterval = setInterval(() => {
            if (!this.isLoading) {
                this.loadEmails();
            }
        }, 30000);
    }
    
    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    /**
     * Set loading state
     */
    setLoading(loading) {
        this.isLoading = loading;
        
        if (this.elements.loadingIndicator) {
            this.elements.loadingIndicator.style.display = loading ? 'block' : 'none';
        }
        
        if (this.elements.refreshBtn) {
            this.elements.refreshBtn.disabled = loading;
            const icon = this.elements.refreshBtn.querySelector('i');
            if (icon) {
                icon.className = loading ? 'fas fa-spinner fa-spin' : 'fas fa-sync-alt';
            }
        }
    }
    
    /**
     * Show empty state
     */
    showEmptyState() {
        if (this.elements.emptyState) {
            this.elements.emptyState.classList.remove('d-none');
        }
        if (this.elements.emailList) {
            this.elements.emailList.innerHTML = '';
        }
    }
    
    /**
     * Hide empty state
     */
    hideEmptyState() {
        if (this.elements.emptyState) {
            this.elements.emptyState.classList.add('d-none');
        }
    }
    
    /**
     * Update inbox count
     */
    updateInboxCount() {
        if (this.elements.inboxCount) {
            const unreadCount = this.emails.filter(email => !email.read).length;
            this.elements.inboxCount.textContent = unreadCount;
            this.elements.inboxCount.style.display = unreadCount > 0 ? 'inline' : 'none';
        }
    }
    
    /**
     * Show error message
     */
    showError(message) {
        // Simple alert for now - could be enhanced with a toast notification
        alert(message);
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Debounce function
     */
    debounce(func, wait) {
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
    
    /**
     * Cleanup method
     */
    destroy() {
        this.stopAutoRefresh();
        
        // Remove event listeners
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EmailClientApp;
}
