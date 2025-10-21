/**
 * SendCraft Frontend JavaScript
 * Sistema completo de funcionalidades para a interface web
 * @version 1.0.0
 */

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    initializeConfirmButtons();
    initializeFormValidation();
    initializeHTMXHandlers();
    setupRealtimeUpdates();
    setupAdvancedFeatures();
});

// ===== BOOTSTRAP COMPONENTS =====
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ===== CONFIRMATION DIALOGS =====
function initializeConfirmButtons() {
    document.querySelectorAll('[data-confirm]').forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

// ===== FORM VALIDATION =====
function initializeFormValidation() {
    // Bootstrap validation
    const forms = document.querySelectorAll('.needs-validation, [data-validate]');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Real-time validation
    const inputs = document.querySelectorAll('input[required], select[required], textarea[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Required validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'Este campo é obrigatório';
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Email inválido';
        }
    }
    
    // Update UI
    if (isValid) {
        field.classList.remove('is-invalid');
        if (value) field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        
        // Add feedback message
        let feedback = field.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentNode.insertBefore(feedback, field.nextSibling);
        }
        feedback.textContent = errorMessage;
    }
    
    return isValid;
}

// ===== HTMX HANDLERS =====
function initializeHTMXHandlers() {
    // After HTMX swaps content
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        initializeTooltips();
        initializeConfirmButtons();
    });
    
    // Loading states
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        const trigger = evt.detail.elt;
        if (trigger.tagName === 'BUTTON') {
            setLoadingState(trigger, true);
        }
    });
    
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        const trigger = evt.detail.elt;
        if (trigger.tagName === 'BUTTON') {
            setLoadingState(trigger, false);
        }
        
        // Handle success messages
        if (evt.detail.successful && evt.detail.xhr.status === 200) {
            try {
                const response = JSON.parse(evt.detail.xhr.response);
                if (response.message) {
                    SendCraft.showToast(response.message, response.type || 'success');
                }
            } catch (e) {
                // Response is not JSON, ignore
            }
        }
    });
    
    // On HTMX errors
    document.body.addEventListener('htmx:responseError', function(evt) {
        SendCraft.showToast('Erro na comunicação com o servidor', 'danger');
        console.error('HTMX Error:', evt.detail);
    });
    
    // On HTMX timeout
    document.body.addEventListener('htmx:timeout', function(evt) {
        SendCraft.showToast('Timeout na requisição', 'warning');
    });
}

// ===== REAL-TIME UPDATES =====
function setupRealtimeUpdates() {
    // Update dashboard stats every 30 seconds
    if (document.querySelector('.dashboard-stats')) {
        setInterval(updateDashboardStats, 30000);
    }
    
    // Update account stats every minute
    if (document.querySelector('.accounts-list')) {
        setInterval(updateAccountStats, 60000);
    }
}

async function updateDashboardStats() {
    try {
        const response = await fetch('/api/stats/live');
        const data = await response.json();
        
        // Update KPI cards
        updateKPIValue('domains-active', data.domains_active);
        updateKPIValue('accounts-active', data.accounts_active);
        updateKPIValue('emails-sent-24h', data.emails_sent_24h);
        updateKPIValue('emails-failed-24h', data.emails_failed_24h);
        
    } catch (error) {
        console.error('Error updating dashboard stats:', error);
    }
}

async function updateAccountStats() {
    try {
        const response = await fetch('/api/stats/accounts');
        const data = await response.json();
        
        data.accounts.forEach(account => {
            updateAccountRow(account);
        });
        
    } catch (error) {
        console.error('Error updating account stats:', error);
    }
}

function updateKPIValue(elementId, value) {
    const element = document.querySelector(`[data-kpi="${elementId}"]`);
    if (element) {
        const valueElement = element.querySelector('.kpi-value, h2, h4');
        if (valueElement && valueElement.textContent !== value.toString()) {
            valueElement.style.transform = 'scale(1.1)';
            valueElement.textContent = value;
            setTimeout(() => {
                valueElement.style.transform = 'scale(1)';
            }, 200);
        }
    }
}

function updateAccountRow(accountData) {
    const row = document.querySelector(`tr[data-account-id="${accountData.id}"]`);
    if (!row) return;
    
    // Update progress bars and counters
    const dailyProgress = row.querySelector('.progress-bar.daily');
    if (dailyProgress) {
        const percentage = (accountData.emails_sent_today / accountData.daily_limit) * 100;
        dailyProgress.style.width = `${percentage}%`;
    }
    
    const monthlyProgress = row.querySelector('.progress-bar.monthly');
    if (monthlyProgress) {
        const percentage = (accountData.emails_sent_this_month / accountData.monthly_limit) * 100;
        monthlyProgress.style.width = `${percentage}%`;
    }
}

// ===== ADVANCED FEATURES =====
function setupAdvancedFeatures() {
    // Checkbox select all
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.item-checkbox');
            checkboxes.forEach(cb => cb.checked = this.checked);
            updateBulkActions();
        });
    }
    
    // Individual checkboxes
    document.querySelectorAll('.item-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', updateBulkActions);
    });
}

function updateBulkActions() {
    const checkedCount = document.querySelectorAll('.item-checkbox:checked').length;
    const bulkActionsBtn = document.getElementById('bulkActionsBtn');
    
    if (bulkActionsBtn) {
        bulkActionsBtn.disabled = checkedCount === 0;
        const countElement = document.getElementById('selectedCount');
        if (countElement) {
            countElement.textContent = `(${checkedCount})`;
        }
    }
}

// ===== SMTP TESTING =====
async function testSMTPConnection(accountId) {
    const button = event.target.closest('button');
    const originalContent = button.innerHTML;
    
    setLoadingState(button, true);
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Testando...';
    
    try {
        const response = await fetch(`/api/accounts/${accountId}/test-smtp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const result = await response.json();
        
        if (result.success) {
            SendCraft.showToast('✅ Conexão SMTP bem-sucedida!', 'success');
            updateSMTPStatus(accountId, 'success');
        } else {
            SendCraft.showToast(`❌ Erro SMTP: ${result.error}`, 'danger');
            updateSMTPStatus(accountId, 'error');
        }
    } catch (error) {
        SendCraft.showToast('Erro ao testar conexão SMTP', 'danger');
        updateSMTPStatus(accountId, 'error');
    } finally {
        setLoadingState(button, false);
        setTimeout(() => {
            button.innerHTML = originalContent;
        }, 3000);
    }
}

function updateSMTPStatus(accountId, status) {
    const statusBadge = document.querySelector(`[data-smtp-status="${accountId}"]`);
    if (statusBadge) {
        statusBadge.className = `badge bg-${status === 'success' ? 'success' : 'danger'}`;
        statusBadge.innerHTML = status === 'success' 
            ? '<i class="bi bi-wifi me-1"></i>OK' 
            : '<i class="bi bi-wifi-off me-1"></i>Erro';
    }
}

// ===== LOADING STATES =====
function setLoadingState(element, loading) {
    if (!element) return;
    
    if (loading) {
        element.disabled = true;
        element.dataset.originalContent = element.innerHTML;
        
        if (!element.querySelector('.spinner-border')) {
            const spinner = '<span class="spinner-border spinner-border-sm me-1"></span>';
            element.innerHTML = spinner + 'Carregando...';
        }
    } else {
        element.disabled = false;
        if (element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
            delete element.dataset.originalContent;
        }
    }
}

// ===== SENDCRAFT UTILITIES =====
const SendCraft = {
    // Enhanced toast notification
    showToast: function(message, type = 'info', duration = 5000) {
        const iconMap = {
            'success': 'bi-check-circle-fill',
            'danger': 'bi-x-circle-fill',
            'error': 'bi-x-circle-fill',
            'warning': 'bi-exclamation-triangle-fill',
            'info': 'bi-info-circle-fill'
        };
        
        const icon = iconMap[type] || iconMap['info'];
        const bgClass = type === 'error' ? 'danger' : type;
        
        const toastHtml = `
            <div class="toast align-items-center text-bg-${bgClass} border-0" 
                 role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="bi ${icon} me-2"></i>${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                            data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            console.error('Toast container not found');
            return;
        }
        
        const wrapper = document.createElement('div');
        wrapper.innerHTML = toastHtml;
        const toastElement = wrapper.firstElementChild;
        toastContainer.appendChild(toastElement);
        
        const toast = new bootstrap.Toast(toastElement, { delay: duration });
        toast.show();
        
        // Remove from DOM after hiding
        toastElement.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    },
    
    // Copy to clipboard
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Copiado para a área de transferência!', 'success');
        }).catch(() => {
            this.showToast('Erro ao copiar', 'danger');
        });
    },
    
    // Format dates
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-PT');
    },
    
    formatDateTime: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('pt-PT');
    },
    
    // Loading overlay
    showLoading: function() {
        const overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
        overlay.style.background = 'rgba(0,0,0,0.5)';
        overlay.style.zIndex = '9999';
        overlay.innerHTML = `
            <div class="spinner-border text-light" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        `;
        document.body.appendChild(overlay);
    },
    
    hideLoading: function() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    },
    
    // Confirm modal
    confirm: function(title, message, onConfirm) {
        const modalHtml = `
            <div class="modal fade" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>${message}</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" id="confirmBtn">Confirmar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        const wrapper = document.createElement('div');
        wrapper.innerHTML = modalHtml;
        const modalElement = wrapper.firstElementChild;
        document.body.appendChild(modalElement);
        
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
        
        document.getElementById('confirmBtn').addEventListener('click', function() {
            onConfirm();
            modal.hide();
        });
        
        modalElement.addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    },
    
    // API helper
    api: async function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, mergedOptions);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'API error');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
};

// Global error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
});

// Make SendCraft utilities globally available
window.SendCraft = SendCraft;

// Also expose commonly used functions globally
window.testSMTPConnection = testSMTPConnection;
window.showToast = SendCraft.showToast.bind(SendCraft);