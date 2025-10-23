/**
 * SendCraft Email Client
 * Complete three-pane email client with AJAX integration
 */

class EmailClient {
    constructor() {
        this.accountId = null;
        this.currentFolder = 'inbox';
        this.currentFilter = 'all';
        this.currentPage = 1;
        this.pageSize = 20;
        this.selectedEmails = new Set();
        this.currentEmail = null;
        this.emails = [];
        this.autoSyncInterval = null;
        this.searchQuery = '';
    }

    init() {
        // Get account ID from hidden input
        this.accountId = document.getElementById('accountId').value;
        
        if (!this.accountId) {
            this.showToast('Erro', 'ID da conta não encontrado', 'danger');
            return;
        }

        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial email list
        this.loadEmailList();
        
        // Setup auto-sync
        this.setupAutoSync();
        
        // Load statistics
        this.loadStatistics();
    }

    setupEventListeners() {
        // Account switcher
        const accountSwitcher = document.getElementById('accountSwitcher');
        if (accountSwitcher) {
            accountSwitcher.addEventListener('change', (e) => {
                const newAccountId = e.target.value;
                window.location.href = `/emails/inbox/${newAccountId}`;
            });
        }

        // Sync button
        const syncBtn = document.getElementById('syncEmailsBtn');
        if (syncBtn) {
            syncBtn.addEventListener('click', () => this.syncEmails());
        }

        // Folder navigation
        document.querySelectorAll('.folder-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const folder = e.currentTarget.dataset.folder;
                this.selectFolder(folder);
            });
        });

        // Filter tabs
        document.querySelectorAll('.nav-pills .nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const filter = e.currentTarget.dataset.filter;
                this.setFilter(filter);
            });
        });

        // Search
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.searchQuery = e.target.value;
                    this.currentPage = 1;
                    this.loadEmailList();
                }, 300);
            });
        }

        // Bulk actions
        document.getElementById('selectAllBtn')?.addEventListener('click', () => this.selectAllEmails());
        document.getElementById('markReadBtn')?.addEventListener('click', () => this.markSelectedAsRead());
        document.getElementById('markUnreadBtn')?.addEventListener('click', () => this.markSelectedAsUnread());
        document.getElementById('deleteSelectedBtn')?.addEventListener('click', () => this.deleteSelectedEmails());

        // Email content actions
        document.getElementById('backToListBtn')?.addEventListener('click', () => this.hideEmailContent());
        document.getElementById('replyBtn')?.addEventListener('click', () => this.replyToEmail());
        document.getElementById('replyAllBtn')?.addEventListener('click', () => this.replyAllToEmail());
        document.getElementById('forwardBtn')?.addEventListener('click', () => this.forwardEmail());
        document.getElementById('flagBtn')?.addEventListener('click', () => this.toggleEmailFlag());
        document.getElementById('markReadUnreadBtn')?.addEventListener('click', () => this.toggleEmailReadStatus());
        document.getElementById('deleteBtn')?.addEventListener('click', () => this.deleteCurrentEmail());
        document.getElementById('viewOriginalBtn')?.addEventListener('click', () => this.viewOriginalEmail());
        document.getElementById('showHeadersBtn')?.addEventListener('click', () => this.toggleHeaders());
        document.getElementById('printEmailBtn')?.addEventListener('click', () => this.printEmail());
        document.getElementById('remoteImagesBtn')?.addEventListener('click', () => this.toggleRemoteImages());

        // Mobile sidebar toggle
        document.getElementById('sidebarToggle')?.addEventListener('click', () => this.toggleSidebar());

        // Compose button
        document.getElementById('composeBtn')?.addEventListener('click', () => this.composeEmail());

        // Settings button
        document.getElementById('settingsBtn')?.addEventListener('click', () => this.openSettings());
    }

    async loadEmailList(page = 1) {
        this.currentPage = page;
        const listContainer = document.getElementById('emailItems');
        const loadingDiv = document.getElementById('emailListLoading');
        const emptyDiv = document.getElementById('emailListEmpty');

        // Show loading
        if (loadingDiv) loadingDiv.style.display = 'flex';
        if (emptyDiv) emptyDiv.style.display = 'none';
        if (listContainer) listContainer.innerHTML = '';

        try {
            // Build query parameters
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: this.pageSize,
                folder: this.currentFolder
            });

            if (this.currentFilter !== 'all') {
                params.append('filter', this.currentFilter);
            }

            if (this.searchQuery) {
                params.append('search', this.searchQuery);
            }

            // Fetch emails from API
            const response = await fetch(`/api/v1/emails/inbox/${this.accountId}?${params}`);
            
            if (!response.ok) {
                throw new Error('Falha ao carregar emails');
            }

            const data = await response.json();
            this.emails = data.emails || [];

            // Hide loading
            if (loadingDiv) loadingDiv.style.display = 'none';

            // Check if empty
            if (this.emails.length === 0) {
                if (emptyDiv) emptyDiv.style.display = 'flex';
                this.updatePagination(0, 1);
                return;
            }

            // Render email list
            this.renderEmailList();

            // Update pagination
            this.updatePagination(data.total || 0, data.pages || 1);

            // Update counts
            this.updateCounts(data);

        } catch (error) {
            console.error('Error loading emails:', error);
            if (loadingDiv) loadingDiv.style.display = 'none';
            if (emptyDiv) emptyDiv.style.display = 'flex';
            this.showToast('Erro', 'Falha ao carregar emails', 'danger');
        }
    }

    renderEmailList() {
        const container = document.getElementById('emailItems');
        if (!container) return;

        container.innerHTML = '';

        // Apply client-side filter if backend doesn't support
        let filteredEmails = this.emails;
        
        if (this.currentFilter === 'unread') {
            filteredEmails = this.emails.filter(email => !email.is_read);
        } else if (this.currentFilter === 'flagged') {
            filteredEmails = this.emails.filter(email => email.is_flagged);
        } else if (this.currentFilter === 'attachments') {
            filteredEmails = this.emails.filter(email => email.has_attachments);
        }

        filteredEmails.forEach(email => {
            const emailItem = this.createEmailItem(email);
            container.appendChild(emailItem);
        });
        
        // Update empty state if no emails after filtering
        const emptyDiv = document.getElementById('emailListEmpty');
        if (filteredEmails.length === 0 && emptyDiv) {
            emptyDiv.style.display = 'flex';
            const emptyTitle = emptyDiv.querySelector('h5');
            const emptyMessage = emptyDiv.querySelector('p');
            if (emptyTitle) emptyTitle.textContent = 'Nenhum email encontrado';
            if (emptyMessage) emptyMessage.textContent = `Nenhum email ${this.getFilterDescription()} encontrado.`;
        } else if (emptyDiv) {
            emptyDiv.style.display = 'none';
        }
    }
    
    getFilterDescription() {
        switch (this.currentFilter) {
            case 'unread': return 'não lido';
            case 'flagged': return 'marcado';
            case 'attachments': return 'com anexos';
            default: return '';
        }
    }

    createEmailItem(email) {
        const div = document.createElement('div');
        div.className = `email-item ${email.is_read ? 'read' : 'unread'}`;
        div.dataset.emailId = email.id;

        // Format date - use formatRelativeDate for consistent date handling
        const formattedDate = this.formatRelativeDate(email.date);

        // Create preview text
        const preview = email.body_text ? 
            email.body_text.substring(0, 100).replace(/\s+/g, ' ') : 
            'Sem pré-visualização disponível';

        div.innerHTML = `
            <input type="checkbox" class="form-check-input email-item-checkbox" 
                data-email-id="${email.id}">
            <div class="email-item-content">
                <div class="email-item-header">
                    <div class="email-item-from">
                        ${email.from_name || email.from_address}
                    </div>
                    <div class="email-item-icons">
                        ${email.has_attachments ? '<i class="bi bi-paperclip text-muted"></i>' : ''}
                        ${email.is_flagged ? '<i class="bi bi-flag-fill text-warning"></i>' : ''}
                    </div>
                    <div class="email-item-date">${formattedDate}</div>
                </div>
                <div class="email-item-subject">
                    ${email.subject || '(Sem assunto)'}
                </div>
                <div class="email-item-preview">
                    ${preview}
                </div>
            </div>
        `;

        // Add click event
        div.addEventListener('click', (e) => {
            if (!e.target.classList.contains('email-item-checkbox')) {
                this.selectEmail(email);
            }
        });

        // Add checkbox event
        const checkbox = div.querySelector('.email-item-checkbox');
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.selectedEmails.add(email.id);
            } else {
                this.selectedEmails.delete(email.id);
            }
            this.updateBulkActions();
        });

        return div;
    }

    async selectEmail(email) {
        // Remove previous selection
        document.querySelectorAll('.email-item.selected').forEach(item => {
            item.classList.remove('selected');
        });

        // Add selection to current item
        const emailItem = document.querySelector(`[data-email-id="${email.id}"]`);
        if (emailItem) {
            emailItem.classList.add('selected');
        }

        this.currentEmail = email;

        // Show email content
        this.showEmailContent(email);

        // Mark as read if unread
        if (!email.is_read) {
            await this.markEmailAsRead(email.id);
        }
    }

    showEmailContent(email) {
        const emptyDiv = document.getElementById('emailContentEmpty');
        const contentDiv = document.getElementById('emailContent');

        if (emptyDiv) emptyDiv.style.display = 'none';
        if (contentDiv) contentDiv.style.display = 'flex';

        // Update subject
        const subjectEl = document.getElementById('emailSubject');
        if (subjectEl) subjectEl.textContent = email.subject || '(Sem assunto)';

        // Update sender info
        const senderNameEl = document.getElementById('senderName');
        const senderEmailEl = document.getElementById('senderEmail');
        if (senderNameEl) senderNameEl.textContent = email.from_name || email.from_address;
        if (senderEmailEl) senderEmailEl.textContent = email.from_address;

        // Update date with relative format and full date on hover
        const dateEl = document.getElementById('emailDate');
        if (dateEl) {
            const relativeDate = this.formatRelativeDate(email.date);
            const fullDate = this.formatFullDate(email.date);
            dateEl.textContent = relativeDate;
            dateEl.title = fullDate; // Show full date on hover
        }

        // Update recipient
        const toEl = document.getElementById('emailTo');
        if (toEl) toEl.textContent = email.to_address || document.getElementById('accountEmail').value;

        // Update body with enhanced HTML rendering
        const bodyEl = document.getElementById('emailBody');
        if (bodyEl) {
            if (email.body_html) {
                // Enhanced HTML rendering with proper sanitization
                bodyEl.innerHTML = this.sanitizeAndRenderHtml(email.body_html);
                
                // Block remote images by default
                setTimeout(() => {
                    const images = bodyEl.querySelectorAll('img[src^="http"]');
                    images.forEach(img => {
                        img.dataset.originalSrc = img.src;
                        img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23ddd" width="100" height="100"/%3E%3Ctext x="50" y="50" text-anchor="middle" fill="%23999"%3EImagem bloqueada%3C/text%3E%3C/svg%3E';
                        img.dataset.blocked = 'true';
                    });
                }, 100);
            } else if (email.body_text) {
                // Convert text to HTML with proper formatting
                bodyEl.innerHTML = this.formatPlainText(email.body_text);
            } else {
                bodyEl.innerHTML = '<p class="text-muted">Sem conteúdo disponível</p>';
            }
        }

        // Update attachments
        this.showAttachments(email.attachments);

        // Update action buttons
        this.updateActionButtons(email);

        // Show content pane on mobile
        if (window.innerWidth < 768) {
            document.getElementById('emailContentPane')?.classList.add('show');
        }
    }

    hideEmailContent() {
        const emptyDiv = document.getElementById('emailContentEmpty');
        const contentDiv = document.getElementById('emailContent');

        if (emptyDiv) emptyDiv.style.display = 'flex';
        if (contentDiv) contentDiv.style.display = 'none';

        // Hide content pane on mobile
        if (window.innerWidth < 768) {
            document.getElementById('emailContentPane')?.classList.remove('show');
        }

        // Remove selection
        document.querySelectorAll('.email-item.selected').forEach(item => {
            item.classList.remove('selected');
        });

        this.currentEmail = null;
    }

    showAttachments(attachments) {
        const container = document.getElementById('emailAttachments');
        const list = document.getElementById('attachmentList');

        if (!container || !list) return;

        if (!attachments || attachments.length === 0) {
            container.style.display = 'none';
            return;
        }

        container.style.display = 'block';
        list.innerHTML = '';

        attachments.forEach(attachment => {
            const div = document.createElement('div');
            div.className = 'attachment-item';
            
            // Get appropriate icon based on file type
            const icon = this.getFileIcon(attachment.filename, attachment.content_type);
            
            // Create download link (we'll need to implement the API endpoint)
            const downloadUrl = `/api/v1/emails/inbox/${this.accountId}/attachments/${attachment.content_id || attachment.filename}`;
            
            div.innerHTML = `
                <i class="${icon}"></i>
                <span class="attachment-name">${this.escapeHtml(attachment.filename)}</span>
                <small class="text-muted ms-2">${this.formatFileSize(attachment.size || 0)}</small>
                <a href="${downloadUrl}" class="btn btn-sm btn-outline-primary ms-auto" download>
                    <i class="bi bi-download"></i> Transferir
                </a>
            `;
            list.appendChild(div);
        });
    }

    updateActionButtons(email) {
        // Update flag button
        const flagBtn = document.getElementById('flagBtn');
        if (flagBtn) {
            const icon = flagBtn.querySelector('i');
            if (email.is_flagged) {
                icon.className = 'bi bi-flag-fill text-warning';
            } else {
                icon.className = 'bi bi-flag';
            }
        }

        // Update read/unread button
        const readBtn = document.getElementById('markReadUnreadBtn');
        if (readBtn) {
            const icon = readBtn.querySelector('i');
            if (email.is_read) {
                icon.className = 'bi bi-envelope';
                readBtn.title = 'Marcar como Não Lido';
            } else {
                icon.className = 'bi bi-envelope-open';
                readBtn.title = 'Marcar como Lido';
            }
        }
    }

    async syncEmails() {
        const syncBtn = document.getElementById('syncEmailsBtn');
        if (syncBtn) {
            syncBtn.disabled = true;
            syncBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>A sincronizar...';
        }

        try {
            const response = await fetch(`/api/v1/emails/inbox/sync/${this.accountId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    folder: 'INBOX',
                    limit: 20,
                    full_sync: false
                })
            });

            if (!response.ok) {
                throw new Error('Falha na sincronização');
            }

            const result = await response.json();
            
            this.showToast('Sucesso', `Sincronização concluída. ${result.new_emails || 0} novos emails.`, 'success');
            
            // Reload email list
            await this.loadEmailList();
            
            // Update statistics
            await this.loadStatistics();

        } catch (error) {
            console.error('Sync error:', error);
            this.showToast('Erro', 'Falha na sincronização de emails', 'danger');
        } finally {
            if (syncBtn) {
                syncBtn.disabled = false;
                syncBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Sincronizar';
            }
        }
    }

    async markEmailAsRead(emailId) {
        try {
            const response = await fetch(`/api/v1/emails/inbox/${this.accountId}/${emailId}/read`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Falha ao marcar como lido');
            }

            // Update local email state
            const email = this.emails.find(e => e.id === emailId);
            if (email) {
                email.is_read = true;
            }

            // Update UI
            const emailItem = document.querySelector(`[data-email-id="${emailId}"]`);
            if (emailItem) {
                emailItem.classList.remove('unread');
                emailItem.classList.add('read');
            }

            // Update counts
            await this.loadStatistics();

        } catch (error) {
            console.error('Error marking email as read:', error);
        }
    }

    async toggleEmailReadStatus() {
        if (!this.currentEmail) return;

        const newStatus = !this.currentEmail.is_read;
        
        try {
            const endpoint = newStatus ? 'read' : 'unread';
            const response = await fetch(`/api/v1/emails/inbox/${this.accountId}/${this.currentEmail.id}/${endpoint}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Falha ao alterar status');
            }

            this.currentEmail.is_read = newStatus;
            
            // Update list item
            const emailItem = document.querySelector(`[data-email-id="${this.currentEmail.id}"]`);
            if (emailItem) {
                if (newStatus) {
                    emailItem.classList.remove('unread');
                    emailItem.classList.add('read');
                } else {
                    emailItem.classList.remove('read');
                    emailItem.classList.add('unread');
                }
            }

            // Update action button
            this.updateActionButtons(this.currentEmail);

            // Update counts
            await this.loadStatistics();

            this.showToast('Sucesso', `Email marcado como ${newStatus ? 'lido' : 'não lido'}`, 'success');

        } catch (error) {
            console.error('Error toggling read status:', error);
            this.showToast('Erro', 'Falha ao alterar status do email', 'danger');
        }
    }

    async toggleEmailFlag() {
        if (!this.currentEmail) return;

        const newStatus = !this.currentEmail.is_flagged;
        
        try {
            const endpoint = newStatus ? 'flag' : 'unflag';
            const response = await fetch(`/api/v1/emails/inbox/${this.accountId}/${this.currentEmail.id}/${endpoint}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Falha ao alterar marcação');
            }

            this.currentEmail.is_flagged = newStatus;
            
            // Update list item
            const emailItem = document.querySelector(`[data-email-id="${this.currentEmail.id}"] .email-item-icons`);
            if (emailItem) {
                const flagIcon = emailItem.querySelector('.bi-flag-fill');
                if (newStatus && !flagIcon) {
                    emailItem.insertAdjacentHTML('beforeend', '<i class="bi bi-flag-fill text-warning"></i>');
                } else if (!newStatus && flagIcon) {
                    flagIcon.remove();
                }
            }

            // Update action button
            this.updateActionButtons(this.currentEmail);

            // Update counts
            await this.loadStatistics();

            this.showToast('Sucesso', `Email ${newStatus ? 'marcado' : 'desmarcado'}`, 'success');

        } catch (error) {
            console.error('Error toggling flag:', error);
            this.showToast('Erro', 'Falha ao alterar marcação do email', 'danger');
        }
    }

    async deleteCurrentEmail() {
        if (!this.currentEmail) return;

        if (!confirm('Tem certeza que deseja eliminar este email?')) return;

        try {
            const response = await fetch(`/api/v1/emails/inbox/${this.accountId}/${this.currentEmail.id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Falha ao eliminar email');
            }

            this.showToast('Sucesso', 'Email eliminado com sucesso', 'success');

            // Hide content
            this.hideEmailContent();

            // Reload list
            await this.loadEmailList();

            // Update statistics
            await this.loadStatistics();

        } catch (error) {
            console.error('Error deleting email:', error);
            this.showToast('Erro', 'Falha ao eliminar email', 'danger');
        }
    }

    async deleteSelectedEmails() {
        if (this.selectedEmails.size === 0) {
            this.showToast('Aviso', 'Nenhum email selecionado', 'warning');
            return;
        }

        if (!confirm(`Tem certeza que deseja eliminar ${this.selectedEmails.size} email(s)?`)) return;

        try {
            const promises = Array.from(this.selectedEmails).map(emailId => 
                fetch(`/api/v1/emails/inbox/${this.accountId}/${emailId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
            );

            await Promise.all(promises);

            this.showToast('Sucesso', `${this.selectedEmails.size} email(s) eliminado(s)`, 'success');

            // Clear selection
            this.selectedEmails.clear();
            this.updateBulkActions();

            // Reload list
            await this.loadEmailList();

            // Update statistics
            await this.loadStatistics();

        } catch (error) {
            console.error('Error deleting emails:', error);
            this.showToast('Erro', 'Falha ao eliminar emails', 'danger');
        }
    }

    async markSelectedAsRead() {
        if (this.selectedEmails.size === 0) {
            this.showToast('Aviso', 'Nenhum email selecionado', 'warning');
            return;
        }

        try {
            const promises = Array.from(this.selectedEmails).map(emailId => 
                fetch(`/api/v1/emails/inbox/${this.accountId}/${emailId}/read`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
            );

            await Promise.all(promises);

            this.showToast('Sucesso', `${this.selectedEmails.size} email(s) marcado(s) como lido(s)`, 'success');

            // Update UI
            this.selectedEmails.forEach(emailId => {
                const emailItem = document.querySelector(`[data-email-id="${emailId}"]`);
                if (emailItem) {
                    emailItem.classList.remove('unread');
                    emailItem.classList.add('read');
                }
            });

            // Clear selection
            this.selectedEmails.clear();
            this.updateBulkActions();

            // Update statistics
            await this.loadStatistics();

        } catch (error) {
            console.error('Error marking emails as read:', error);
            this.showToast('Erro', 'Falha ao marcar emails como lidos', 'danger');
        }
    }

    async markSelectedAsUnread() {
        if (this.selectedEmails.size === 0) {
            this.showToast('Aviso', 'Nenhum email selecionado', 'warning');
            return;
        }

        try {
            const promises = Array.from(this.selectedEmails).map(emailId => 
                fetch(`/api/v1/emails/inbox/${this.accountId}/${emailId}/unread`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
            );

            await Promise.all(promises);

            this.showToast('Sucesso', `${this.selectedEmails.size} email(s) marcado(s) como não lido(s)`, 'success');

            // Update UI
            this.selectedEmails.forEach(emailId => {
                const emailItem = document.querySelector(`[data-email-id="${emailId}"]`);
                if (emailItem) {
                    emailItem.classList.remove('read');
                    emailItem.classList.add('unread');
                }
            });

            // Clear selection
            this.selectedEmails.clear();
            this.updateBulkActions();

            // Update statistics
            await this.loadStatistics();

        } catch (error) {
            console.error('Error marking emails as unread:', error);
            this.showToast('Erro', 'Falha ao marcar emails como não lidos', 'danger');
        }
    }

    selectAllEmails() {
        const checkboxes = document.querySelectorAll('.email-item-checkbox');
        const allSelected = this.selectedEmails.size === checkboxes.length;

        checkboxes.forEach(checkbox => {
            const emailId = parseInt(checkbox.dataset.emailId);
            checkbox.checked = !allSelected;
            
            if (!allSelected) {
                this.selectedEmails.add(emailId);
            } else {
                this.selectedEmails.delete(emailId);
            }
        });

        this.updateBulkActions();
    }

    updateBulkActions() {
        const bulkActions = document.getElementById('bulkActions');
        if (bulkActions) {
            bulkActions.style.display = this.selectedEmails.size > 0 ? 'block' : 'none';
        }

        // Update select all button text
        const selectAllBtn = document.getElementById('selectAllBtn');
        if (selectAllBtn) {
            const checkboxes = document.querySelectorAll('.email-item-checkbox');
            const allSelected = this.selectedEmails.size === checkboxes.length && checkboxes.length > 0;
            selectAllBtn.innerHTML = allSelected ? 
                '<i class="bi bi-x-square"></i> Desselecionar Todos' : 
                '<i class="bi bi-check-all"></i> Selecionar Todos';
        }
    }

    async loadStatistics() {
        try {
            const response = await fetch(`/api/v1/emails/inbox/${this.accountId}/stats`);
            
            if (!response.ok) {
                throw new Error('Falha ao carregar estatísticas');
            }

            const stats = await response.json();

            // Update sidebar stats
            document.getElementById('totalEmails').textContent = stats.total || 0;
            document.getElementById('unreadEmails').textContent = stats.unread || 0;
            document.getElementById('flaggedEmails').textContent = stats.flagged || 0;

            // Update folder counts
            document.getElementById('inboxCount').textContent = stats.inbox || 0;
            document.getElementById('sentCount').textContent = stats.sent || '';
            document.getElementById('draftsCount').textContent = stats.drafts || '';
            document.getElementById('trashCount').textContent = stats.trash || '';

            // Update unread badge
            document.getElementById('unreadBadge').textContent = stats.unread || 0;

        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    updateCounts(data) {
        // Update inbox count
        const inboxCount = document.getElementById('inboxCount');
        if (inboxCount && data.total) {
            inboxCount.textContent = data.total;
        }

        // Update unread badge
        const unreadBadge = document.getElementById('unreadBadge');
        if (unreadBadge && data.unread !== undefined) {
            unreadBadge.textContent = data.unread;
        }
    }

    updatePagination(total, pages) {
        const container = document.querySelector('#emailPagination .pagination');
        if (!container) return;

        container.innerHTML = '';

        if (pages <= 1) return;

        // Previous button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${this.currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `<a class="page-link" href="#" data-page="${this.currentPage - 1}">Anterior</a>`;
        container.appendChild(prevLi);

        // Page numbers
        const maxButtons = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxButtons / 2));
        let endPage = Math.min(pages, startPage + maxButtons - 1);

        if (endPage - startPage < maxButtons - 1) {
            startPage = Math.max(1, endPage - maxButtons + 1);
        }

        for (let i = startPage; i <= endPage; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${i === this.currentPage ? 'active' : ''}`;
            li.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
            container.appendChild(li);
        }

        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${this.currentPage === pages ? 'disabled' : ''}`;
        nextLi.innerHTML = `<a class="page-link" href="#" data-page="${this.currentPage + 1}">Próximo</a>`;
        container.appendChild(nextLi);

        // Add click events
        container.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(e.currentTarget.dataset.page);
                if (page && page !== this.currentPage) {
                    this.loadEmailList(page);
                }
            });
        });
    }

    selectFolder(folder) {
        // Update active folder
        document.querySelectorAll('.folder-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-folder="${folder}"]`)?.classList.add('active');

        this.currentFolder = folder;
        this.currentPage = 1;
        this.loadEmailList();
    }

    setFilter(filter) {
        // Update active filter UI
        document.querySelectorAll('.nav-pills .nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`)?.classList.add('active');

        // Set filter state
        this.currentFilter = filter;
        this.currentPage = 1;
        
        // Clear current email selection when filtering
        this.hideEmailContent();
        
        // Reload email list with new filter
        this.loadEmailList();
    }

    setupAutoSync() {
        // Clear existing interval
        if (this.autoSyncInterval) {
            clearInterval(this.autoSyncInterval);
        }

        // Setup new interval (5 minutes)
        this.autoSyncInterval = setInterval(() => {
            this.syncEmails();
        }, 5 * 60 * 1000);
    }

    toggleSidebar() {
        const sidebar = document.getElementById('emailSidebar');
        if (sidebar) {
            sidebar.classList.toggle('show');
        }
    }

    composeEmail() {
        // Open compose modal
        const modal = new bootstrap.Modal(document.getElementById('composeModal'));
        modal.show();
        
        // Setup form submission
        const form = document.getElementById('composeForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleComposeSubmit(e));
        }
    }

    async handleComposeSubmit(e) {
        e.preventDefault();
        
        const to = document.getElementById('composeTo').value.trim();
        const subject = document.getElementById('composeSubject').value.trim();
        const body = document.getElementById('composeBody').value.trim();
        const files = document.getElementById('composeAttachments').files;
        
        // Validation
        if (!to || !subject || !body) {
            this.showToast('Erro', 'Por favor, preencha todos os campos obrigatórios', 'danger');
            return;
        }
        
        // Validate email format
        const emails = to.split(',').map(e => e.trim());
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        for (const email of emails) {
            if (!emailRegex.test(email)) {
                this.showToast('Erro', `Email inválido: ${email}`, 'danger');
                return;
            }
        }
        
        // Show loading state
        const sendBtn = document.getElementById('sendEmailBtn');
        const originalText = sendBtn.innerHTML;
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...';
        
        try {
            // Prepare form data
            const formData = new FormData();
            formData.append('account_id', this.accountId);
            formData.append('to', emails.join(','));
            formData.append('subject', subject);
            formData.append('body_html', body);
            formData.append('body_text', body.replace(/<[^>]*>/g, '')); // Strip HTML for text version
            
            // Add attachments if any
            if (files.length > 0) {
                for (let i = 0; i < files.length; i++) {
                    formData.append('attachments', files[i]);
                }
            }
            
            // Send email
            const response = await fetch('/emails/send', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showToast('Sucesso', `Email enviado com sucesso para ${emails.join(', ')}`, 'success');
                
                // Close modal and reset form
                bootstrap.Modal.getInstance(document.getElementById('composeModal')).hide();
                document.getElementById('composeForm').reset();
                
                // Reload email list to show sent email
                this.loadEmailList();
            } else {
                this.showToast('Erro', result.message || 'Erro ao enviar email', 'danger');
            }
        } catch (error) {
            console.error('Send email error:', error);
            this.showToast('Erro', 'Erro de comunicação: ' + error.message, 'danger');
        } finally {
            // Restore button state
            sendBtn.disabled = false;
            sendBtn.innerHTML = originalText;
        }
    }

    openSettings() {
        // Redirect to account settings
        window.location.href = `/accounts/${this.accountId}/edit`;
    }

    replyToEmail() {
        // TODO: Implement reply functionality
        this.showToast('Info', 'Funcionalidade de resposta em desenvolvimento', 'info');
    }

    replyAllToEmail() {
        // TODO: Implement reply all functionality
        this.showToast('Info', 'Funcionalidade de responder a todos em desenvolvimento', 'info');
    }

    forwardEmail() {
        // TODO: Implement forward functionality
        this.showToast('Info', 'Funcionalidade de reencaminhamento em desenvolvimento', 'info');
    }

    viewOriginalEmail() {
        if (!this.currentEmail) return;
        
        const url = `/api/v1/emails/inbox/${this.accountId}/${this.currentEmail.id}/raw`;
        window.open(url, '_blank');
    }

    toggleHeaders() {
        const headersDiv = document.getElementById('emailHeaders');
        if (!headersDiv) return;
        
        const isVisible = headersDiv.style.display !== 'none';
        headersDiv.style.display = isVisible ? 'none' : 'block';
        
        const btn = document.getElementById('showHeadersBtn');
        if (btn) {
            btn.textContent = isVisible ? 'Mostrar Cabeçalhos' : 'Ocultar Cabeçalhos';
        }
    }

    printEmail() {
        if (!this.currentEmail) return;
        
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>${this.escapeHtml(this.currentEmail.subject || 'Email')}</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        .email-header { border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; }
                        .email-meta { margin-bottom: 15px; }
                        .email-body { line-height: 1.6; }
                    </style>
                </head>
                <body>
                    <div class="email-header">
                        <h2>${this.escapeHtml(this.currentEmail.subject || 'Sem assunto')}</h2>
                    </div>
                    <div class="email-meta">
                        <p><strong>De:</strong> ${this.escapeHtml(this.currentEmail.from_name || this.currentEmail.from_address)}</p>
                        <p><strong>Para:</strong> ${this.escapeHtml(this.currentEmail.to_address || '')}</p>
                        <p><strong>Data:</strong> ${this.formatFullDate(this.currentEmail.date)}</p>
                    </div>
                    <div class="email-body">
                        ${this.currentEmail.body_html ? this.sanitizeAndRenderHtml(this.currentEmail.body_html) : `<pre>${this.escapeHtml(this.currentEmail.body_text || '')}</pre>`}
                    </div>
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }

    toggleRemoteImages() {
        const emailBody = document.getElementById('emailBody');
        if (!emailBody) return;
        
        const images = emailBody.querySelectorAll('img[src^="http"]');
        let someBlocked = false;
        
        images.forEach(img => {
            if (img.style.display === 'none' || img.dataset.blocked === 'true') {
                someBlocked = true;
            }
        });
        
        const shouldShow = someBlocked;
        
        images.forEach(img => {
            if (shouldShow) {
                // Show image
                img.style.display = '';
                img.dataset.blocked = 'false';
                // Set actual src if it was blocked
                if (img.dataset.originalSrc) {
                    img.src = img.dataset.originalSrc;
                }
            } else {
                // Block image
                img.dataset.originalSrc = img.src;
                img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23ddd" width="100" height="100"/%3E%3Ctext x="50" y="50" text-anchor="middle" fill="%23999"%3EImagem bloqueada%3C/text%3E%3C/svg%3E';
                img.style.display = '';
                img.dataset.blocked = 'true';
            }
        });
        
        const btn = document.getElementById('remoteImagesBtn');
        if (btn) {
            btn.textContent = shouldShow ? 'Ocultar Imagens Remotas' : 'Mostrar Imagens Remotas';
            btn.classList.toggle('btn-outline-secondary', !shouldShow);
            btn.classList.toggle('btn-outline-warning', shouldShow);
        }
        
        this.showToast(
            'Info', 
            shouldShow ? 'Imagens remotas ativadas' : 'Imagens remotas bloqueadas', 
            'info'
        );
    }

    // Utility functions
    formatDate(date) {
        const now = new Date();
        const diff = now - date;
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) {
            // Today - show time
            return date.toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' });
        } else if (days === 1) {
            return 'Ontem';
        } else if (days < 7) {
            return date.toLocaleDateString('pt-PT', { weekday: 'short' });
        } else {
            return date.toLocaleDateString('pt-PT', { day: '2-digit', month: 'short' });
        }
    }

    formatRelativeDate(dateInput) {
        try {
            let date;
            
            // Handle multiple input formats
            if (typeof dateInput === 'string') {
                // Try parsing ISO string first
                if (dateInput.includes('T') || dateInput.includes('-')) {
                    date = new Date(dateInput);
                } else {
                    // Try parsing as timestamp
                    const timestamp = parseInt(dateInput);
                    if (!isNaN(timestamp)) {
                        date = new Date(timestamp > 1000000000000 ? timestamp : timestamp * 1000);
                    } else {
                        date = new Date(dateInput);
                    }
                }
            } else if (dateInput instanceof Date) {
                date = dateInput;
            } else if (typeof dateInput === 'number') {
                // Handle numeric timestamp
                date = new Date(dateInput > 1000000000000 ? dateInput : dateInput * 1000);
            } else {
                console.warn('Invalid date input type:', typeof dateInput, dateInput);
                return 'Data inválida';
            }
            
            // Validate parsed date
            if (isNaN(date.getTime())) {
                console.warn('Date parsing failed for:', dateInput);
                return 'Data inválida';
            }
            
            const now = new Date();
            const diffMs = now - date;
            const diffMinutes = Math.floor(diffMs / (1000 * 60));
            const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
            const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
            
            // Portuguese relative date formatting
            if (diffMinutes < 1) {
                return 'agora';
            } else if (diffMinutes < 60) {
                return `há ${diffMinutes} minuto${diffMinutes !== 1 ? 's' : ''}`;
            } else if (diffHours < 24) {
                return `há ${diffHours} hora${diffHours !== 1 ? 's' : ''}`;
            } else if (diffDays === 1) {
                return 'ontem';
            } else if (diffDays < 7) {
                return `há ${diffDays} dia${diffDays !== 1 ? 's' : ''}`;
            } else if (diffDays < 30) {
                const weeks = Math.floor(diffDays / 7);
                return `há ${weeks} semana${weeks !== 1 ? 's' : ''}`;
            } else if (diffDays < 365) {
                const months = Math.floor(diffDays / 30);
                return `há ${months} mês${months !== 1 ? 'es' : ''}`;
            } else {
                const years = Math.floor(diffDays / 365);
                return `há ${years} ano${years !== 1 ? 's' : ''}`;
            }
            
        } catch (error) {
            console.error('Date formatting error:', error, 'Input:', dateInput);
            return 'Data inválida';
        }
    }

    formatFullDate(dateInput) {
        try {
            let date;
            if (typeof dateInput === 'string') {
                date = new Date(dateInput);
            } else if (dateInput instanceof Date) {
                date = dateInput;
            } else if (typeof dateInput === 'number') {
                date = new Date(dateInput > 1000000000000 ? dateInput : dateInput * 1000);
            } else {
                return 'Data inválida';
            }
            
            if (isNaN(date.getTime())) {
                return 'Data inválida';
            }
            
            return date.toLocaleDateString('pt-PT', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            console.error('Full date formatting error:', error);
            return 'Data inválida';
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    sanitizeHtml(html) {
        // Basic HTML sanitization - in production, use a proper library like DOMPurify
        const div = document.createElement('div');
        div.innerHTML = html;
        
        // Remove script tags and event handlers
        div.querySelectorAll('script, link, style').forEach(el => el.remove());
        div.querySelectorAll('*').forEach(el => {
            Array.from(el.attributes).forEach(attr => {
                if (attr.name.startsWith('on')) {
                    el.removeAttribute(attr.name);
                }
            });
        });

        return div.innerHTML;
    }

    sanitizeAndRenderHtml(html) {
        // Enhanced HTML sanitization with better formatting
        const div = document.createElement('div');
        div.innerHTML = html;
        
        // Remove dangerous elements
        div.querySelectorAll('script, link, meta, base, object, embed, iframe, form').forEach(el => el.remove());
        
        // Remove inline event handlers
        div.querySelectorAll('*').forEach(el => {
            Array.from(el.attributes).forEach(attr => {
                if (attr.name.startsWith('on') || attr.name.startsWith('javascript:')) {
                    el.removeAttribute(attr.name);
                }
            });
        });
        
        // Preserve email styling but add our own container
        const container = document.createElement('div');
        container.className = 'email-html-content';
        container.innerHTML = div.innerHTML;
        
        return container.outerHTML;
    }

    formatPlainText(text) {
        // Convert plain text to formatted HTML
        const lines = text.split('\n');
        const formatted = lines.map(line => {
            // Detect email signatures
            if (line.match(/^(--|__|\|)/) || line.match(/^Atenciosamente|^Best regards|^Cordiais|^Sinceramente/i)) {
                return `<div class="email-signature">${this.escapeHtml(line)}</div>`;
            }
            
            // Detect quoted/reply text
            if (line.match(/^>/)) {
                return `<div class="email-quote">${this.escapeHtml(line)}</div>`;
            }
            
            // Empty lines
            if (line.trim() === '') {
                return '<br>';
            }
            
            // Regular paragraphs
            return `<p>${this.escapeHtml(line)}</p>`;
        }).join('');
        
        return `<div class="email-text-content">${formatted}</div>`;
    }

    getFileIcon(filename, contentType) {
        // Get appropriate Bootstrap icon based on file type
        const ext = filename.split('.').pop().toLowerCase();
        
        // Image files
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'].includes(ext)) {
            return 'bi bi-file-image';
        }
        
        // PDF files
        if (ext === 'pdf') {
            return 'bi bi-file-pdf';
        }
        
        // Word documents
        if (['doc', 'docx'].includes(ext)) {
            return 'bi bi-file-word';
        }
        
        // Excel spreadsheets
        if (['xls', 'xlsx'].includes(ext)) {
            return 'bi bi-file-excel';
        }
        
        // PowerPoint
        if (['ppt', 'pptx'].includes(ext)) {
            return 'bi bi-file-ppt';
        }
        
        // Archive files
        if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) {
            return 'bi bi-file-zip';
        }
        
        // Audio files
        if (['mp3', 'wav', 'ogg', 'flac'].includes(ext)) {
            return 'bi bi-file-music';
        }
        
        // Video files
        if (['mp4', 'avi', 'mov', 'wmv'].includes(ext)) {
            return 'bi bi-file-play';
        }
        
        // Code files
        if (['js', 'ts', 'py', 'java', 'html', 'css', 'xml', 'json'].includes(ext)) {
            return 'bi bi-file-code';
        }
        
        // Text files
        if (['txt', 'md', 'log'].includes(ext)) {
            return 'bi bi-file-text';
        }
        
        // Default
        return 'bi bi-file-earmark';
    }

    showToast(title, message, type = 'info') {
        const toastEl = document.getElementById('emailToast');
        const titleEl = document.getElementById('toastTitle');
        const messageEl = document.getElementById('toastMessage');

        if (!toastEl || !titleEl || !messageEl) return;

        // Update content
        titleEl.textContent = title;
        messageEl.textContent = message;

        // Update styling based on type
        const header = toastEl.querySelector('.toast-header');
        header.className = 'toast-header';
        
        const icon = header.querySelector('i');
        icon.className = 'bi me-2';
        
        switch (type) {
            case 'success':
                header.classList.add('bg-success', 'text-white');
                icon.classList.add('bi-check-circle');
                break;
            case 'danger':
                header.classList.add('bg-danger', 'text-white');
                icon.classList.add('bi-x-circle');
                break;
            case 'warning':
                header.classList.add('bg-warning');
                icon.classList.add('bi-exclamation-triangle');
                break;
            default:
                icon.classList.add('bi-info-circle');
        }

        // Show toast
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
    }
}

// Export for global use
window.EmailClient = EmailClient;