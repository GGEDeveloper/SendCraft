// SendCraft Frontend JavaScript

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    initializeConfirmButtons();
    initializeFormValidation();
    initializeHTMXHandlers();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Handle confirmation dialogs
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

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// HTMX event handlers
function initializeHTMXHandlers() {
    // After HTMX swaps content
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        initializeTooltips();
        initializeConfirmButtons();
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

// Utility functions
const SendCraft = {
    // Show toast notification
    showToast: function(message, type = 'info') {
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        const toastElement = document.createElement('div');
        toastElement.innerHTML = toastHtml;
        toastContainer.appendChild(toastElement.firstElementChild);
        
        const toast = new bootstrap.Toast(toastElement.firstElementChild);
        toast.show();
        
        // Remove from DOM after hiding
        toastElement.firstElementChild.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    },
    
    // Copy text to clipboard
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Copiado para a área de transferência!', 'success');
        }).catch(() => {
            this.showToast('Erro ao copiar', 'danger');
        });
    },
    
    // Format date
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('pt-PT');
    },
    
    // Toggle loading state
    setLoading: function(element, loading) {
        if (loading) {
            element.classList.add('loading');
            element.setAttribute('disabled', 'disabled');
        } else {
            element.classList.remove('loading');
            element.removeAttribute('disabled');
        }
    },
    
    // Confirm action
    confirm: function(message, onConfirm) {
        if (confirm(message)) {
            onConfirm();
        }
    }
};

// Global error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    // Don't show toast for every JS error, just log
});

// Make SendCraft utilities globally available
window.SendCraft = SendCraft;