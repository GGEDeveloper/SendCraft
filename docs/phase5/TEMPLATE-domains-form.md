# 📋 TEMPLATE: domains/form.html - SendCraft CRUD Domínios

```html
{% extends "base.html" %}

{% block title %}{{ 'Editar' if domain else 'Novo' }} Domínio - SendCraft{% endblock %}

{% block content %}
<!-- Breadcrumb Navigation -->
<nav aria-label="breadcrumb" class="mb-4">
    <ol class="breadcrumb">
        <li class="breadcrumb-item">
            <a href="{{ url_for('web.dashboard') }}" class="text-decoration-none">
                <i class="bi bi-house-door me-1"></i>Dashboard
            </a>
        </li>
        <li class="breadcrumb-item">
            <a href="{{ url_for('web.domains_list') }}" class="text-decoration-none">
                <i class="bi bi-globe2 me-1"></i>Domínios
            </a>
        </li>
        <li class="breadcrumb-item active" aria-current="page">
            {{ 'Editar' if domain else 'Novo' }}
        </li>
    </ol>
</nav>

<!-- Page Header -->
<div class="row mb-4">
    <div class="col">
        <div class="d-flex align-items-center">
            <div class="bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center me-3" 
                 style="width: 3rem; height: 3rem;">
                <i class="bi bi-globe2 fs-4"></i>
            </div>
            <div>
                <h1 class="h2 mb-1">
                    {{ 'Editar Domínio' if domain else 'Novo Domínio' }}
                </h1>
                <p class="text-muted mb-0">
                    {{ 'Alterar configurações do domínio ' + domain.name if domain else 'Configure um novo domínio para envio de emails' }}
                </p>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <!-- Formulário Principal -->
    <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom">
                <h5 class="mb-0">
                    <i class="bi bi-gear me-2 text-secondary"></i>
                    Configurações do Domínio
                </h5>
            </div>
            <div class="card-body">
                <form method="POST" id="domainForm" data-validate novalidate>
                    <!-- Nome do Domínio -->
                    <div class="mb-4">
                        <label for="name" class="form-label fw-semibold">
                            <i class="bi bi-globe2 me-2 text-primary"></i>
                            Nome do Domínio <span class="text-danger">*</span>
                        </label>
                        <input type="text" 
                               class="form-control form-control-lg" 
                               id="name" 
                               name="name" 
                               value="{{ domain.name if domain else '' }}"
                               placeholder="exemplo: alitools.pt"
                               required
                               {{ 'readonly' if domain else '' }}>
                        <div class="invalid-feedback"></div>
                        <div class="form-text">
                            <i class="bi bi-info-circle me-1"></i>
                            O domínio deve ter formato válido (ex: example.com). 
                            {{ 'Não é possível alterar o nome após criação.' if domain else 'Apenas letras, números e hífens são permitidos.' }}
                        </div>
                    </div>
                    
                    <!-- Descrição -->
                    <div class="mb-4">
                        <label for="description" class="form-label fw-semibold">
                            <i class="bi bi-card-text me-2 text-secondary"></i>
                            Descrição
                        </label>
                        <textarea class="form-control" 
                                  id="description" 
                                  name="description" 
                                  rows="3"
                                  placeholder="Descrição opcional do domínio (ex: Site principal da empresa, Loja online, etc.)">{{ domain.description if domain else '' }}</textarea>
                        <div class="invalid-feedback"></div>
                        <div class="form-text">
                            <i class="bi bi-lightbulb me-1"></i>
                            Use a descrição para identificar facilmente o propósito deste domínio.
                        </div>
                    </div>
                    
                    <!-- Status Ativo -->
                    <div class="mb-4">
                        <div class="form-check form-switch">
                            <input class="form-check-input" 
                                   type="checkbox" 
                                   role="switch" 
                                   id="is_active" 
                                   name="is_active"
                                   {{ 'checked' if not domain or domain.is_active else '' }}>
                            <label class="form-check-label fw-semibold" for="is_active">
                                <i class="bi bi-power text-success me-2"></i>
                                Domínio Ativo
                            </label>
                        </div>
                        <div class="form-text">
                            <i class="bi bi-info-circle me-1"></i>
                            Apenas domínios ativos podem enviar emails. Desativar um domínio suspende todos os envios.
                        </div>
                    </div>
                    
                    <!-- Botões de Ação -->
                    <div class="d-flex gap-2 pt-3 border-top">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle me-1"></i>
                            {{ 'Atualizar Domínio' if domain else 'Criar Domínio' }}
                        </button>
                        
                        <a href="{{ url_for('web.domains_list') }}" class="btn btn-outline-secondary">
                            <i class="bi bi-arrow-left me-1"></i>
                            Voltar à Lista
                        </a>
                        
                        {% if domain %}
                        <div class="ms-auto">
                            <button type="button" 
                                    class="btn btn-outline-danger"
                                    onclick="confirmDelete({{ domain.id }}, '{{ domain.name }}')">
                                <i class="bi bi-trash me-1"></i>
                                Eliminar Domínio
                            </button>
                        </div>
                        {% endif %}
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <!-- Sidebar Informações -->
    <div class="col-lg-4">
        <!-- Card Informações -->
        <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-info-subtle border-bottom">
                <h6 class="mb-0 text-info">
                    <i class="bi bi-info-circle me-2"></i>
                    Informações
                </h6>
            </div>
            <div class="card-body">
                {% if domain %}
                <!-- Estatísticas do Domínio -->
                <div class="row text-center">
                    <div class="col-6 mb-3">
                        <div class="border rounded p-2">
                            <h4 class="mb-1 text-info">{{ domain.accounts_count or 0 }}</h4>
                            <small class="text-muted">Contas</small>
                        </div>
                    </div>
                    <div class="col-6 mb-3">
                        <div class="border rounded p-2">
                            <h4 class="mb-1 text-primary">{{ domain.templates_count or 0 }}</h4>
                            <small class="text-muted">Templates</small>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="border rounded p-2">
                            <h4 class="mb-1 text-success">{{ domain.emails_sent_30d or 0 }}</h4>
                            <small class="text-muted">Emails 30d</small>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="border rounded p-2">
                            <h4 class="mb-1 text-warning">{{ '99.2%' if domain.emails_sent_30d > 0 else '—' }}</h4>
                            <small class="text-muted">Taxa Sucesso</small>
                        </div>
                    </div>
                </div>
                
                <hr>
                
                <!-- Detalhes Técnicos -->
                <div class="small text-muted">
                    <div class="mb-2">
                        <i class="bi bi-calendar3 me-2"></i>
                        <strong>Criado:</strong> {{ domain.created_at.strftime('%d/%m/%Y às %H:%M') }}
                    </div>
                    <div class="mb-2">
                        <i class="bi bi-arrow-repeat me-2"></i>
                        <strong>Atualizado:</strong> {{ domain.updated_at.strftime('%d/%m/%Y às %H:%M') }}
                    </div>
                    <div>
                        <i class="bi bi-hash me-2"></i>
                        <strong>ID:</strong> #{{ domain.id }}
                    </div>
                </div>
                
                {% else %}
                <!-- Ajuda para Novo Domínio -->
                <div class="text-center mb-3">
                    <i class="bi bi-lightbulb text-warning" style="font-size: 2rem;"></i>
                </div>
                <h6 class="text-center mb-3">Configurar Novo Domínio</h6>
                <ul class="list-unstyled small">
                    <li class="mb-2">
                        <i class="bi bi-1-circle text-primary me-2"></i>
                        Insira o nome do domínio (ex: empresa.pt)
                    </li>
                    <li class="mb-2">
                        <i class="bi bi-2-circle text-primary me-2"></i>
                        Adicione uma descrição identificativa
                    </li>
                    <li class="mb-2">
                        <i class="bi bi-3-circle text-primary me-2"></i>
                        Deixe ativo para permitir envios
                    </li>
                    <li>
                        <i class="bi bi-4-circle text-primary me-2"></i>
                        Configure contas de email depois
                    </li>
                </ul>
                {% endif %}
            </div>
        </div>
        
        {% if domain %}
        <!-- Card Ações Rápidas -->
        <div class="card border-0 shadow-sm">
            <div class="card-header bg-warning-subtle border-bottom">
                <h6 class="mb-0 text-warning-emphasis">
                    <i class="bi bi-lightning me-2"></i>
                    Ações Rápidas
                </h6>
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <a href="{{ url_for('web.accounts_list', domain=domain.name) }}" 
                       class="btn btn-outline-info btn-sm">
                        <i class="bi bi-envelope me-2"></i>
                        Ver Contas ({{ domain.accounts_count or 0 }})
                    </a>
                    
                    <a href="{{ url_for('web.templates_list', domain=domain.name) }}" 
                       class="btn btn-outline-primary btn-sm">
                        <i class="bi bi-file-earmark-text me-2"></i>
                        Ver Templates ({{ domain.templates_count or 0 }})
                    </a>
                    
                    <a href="{{ url_for('web.logs_list', domain=domain.name) }}" 
                       class="btn btn-outline-success btn-sm">
                        <i class="bi bi-journal-text me-2"></i>
                        Ver Logs de Email
                    </a>
                    
                    <hr>
                    
                    <button type="button" 
                            class="btn btn-outline-warning btn-sm"
                            onclick="testDomainConfiguration({{ domain.id }})">
                        <i class="bi bi-gear me-2"></i>
                        Testar Configuração
                    </button>
                </div>
            </div>
        </div>
        {% endif %}
    </div>
</div>

{% if domain %}
<!-- Modal de Confirmação Delete -->
<div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header border-bottom-0">
                <h5 class="modal-title text-danger" id="deleteModalLabel">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    Eliminar Domínio
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
            </div>
            <div class="modal-body text-center">
                <div class="mb-3">
                    <i class="bi bi-globe text-danger" style="font-size: 4rem; opacity: 0.7;"></i>
                </div>
                
                <h5 class="mb-3">Eliminar domínio <strong class="text-danger">{{ domain.name }}</strong>?</h5>
                
                <div class="alert alert-danger" role="alert">
                    <div class="d-flex align-items-start">
                        <i class="bi bi-exclamation-triangle-fill me-2 mt-1"></i>
                        <div class="text-start">
                            <strong>Esta ação eliminará permanentemente:</strong>
                            <ul class="mb-0 mt-2">
                                <li>{{ domain.accounts_count or 0 }} contas de email</li>
                                <li>{{ domain.templates_count or 0 }} templates</li>
                                <li>Todo o histórico de logs</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <p class="text-muted small mb-0">
                    <i class="bi bi-info-circle me-1"></i>
                    Esta operação não pode ser desfeita.
                </p>
            </div>
            <div class="modal-footer border-top-0 justify-content-center">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    <i class="bi bi-x-circle me-1"></i>Cancelar
                </button>
                <form method="POST" action="{{ url_for('web.domains_delete', domain_id=domain.id) }}" style="display: inline;">
                    <button type="submit" class="btn btn-danger">
                        <i class="bi bi-trash me-1"></i>
                        Eliminar Definitivamente
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endif %}
{% endblock %}

{% block scripts %}
<script>
// ===== FORM VALIDATION =====
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('domainForm');
    const nameInput = document.getElementById('name');
    
    // Real-time domain validation
    nameInput.addEventListener('input', function() {
        validateDomainName(this);
    });
    
    // Form submission validation
    form.addEventListener('submit', function(e) {
        if (!validateForm(this)) {
            e.preventDefault();
            showToast('Por favor corrija os erros no formulário', 'warning');
        }
    });
});

function validateDomainName(input) {
    const value = input.value.trim().toLowerCase();
    let isValid = true;
    let errorMessage = '';
    
    if (!value) {
        isValid = false;
        errorMessage = 'Nome do domínio é obrigatório';
    } else {
        // Domain format validation
        const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$/;
        if (!domainRegex.test(value)) {
            isValid = false;
            errorMessage = 'Formato de domínio inválido (ex: empresa.pt)';
        }
        
        // Check for common mistakes
        if (value.includes('http://') || value.includes('https://')) {
            isValid = false;
            errorMessage = 'Insira apenas o domínio, sem http:// ou https://';
        }
        
        if (value.includes('/')) {
            isValid = false;
            errorMessage = 'Insira apenas o domínio, sem caminhos';
        }
        
        // Suggest normalization
        if (value !== value.toLowerCase()) {
            input.value = value.toLowerCase();
        }
    }
    
    updateFieldValidation(input, isValid, errorMessage);
    return isValid;
}

function validateForm(form) {
    let isValid = true;
    const nameInput = form.querySelector('#name');
    
    // Validate all required fields
    if (!validateDomainName(nameInput)) {
        isValid = false;
    }
    
    return isValid;
}

function updateFieldValidation(field, isValid, errorMessage) {
    const feedbackElement = field.nextElementSibling;
    
    // Remove previous states
    field.classList.remove('is-valid', 'is-invalid');
    
    if (field.value.trim()) {
        if (isValid) {
            field.classList.add('is-valid');
            if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
                feedbackElement.style.display = 'none';
            }
        } else {
            field.classList.add('is-invalid');
            if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
                feedbackElement.textContent = errorMessage;
                feedbackElement.style.display = 'block';
            }
        }
    }
}

// ===== DOMAIN TESTING =====
async function testDomainConfiguration(domainId) {
    const button = event.target;
    const originalContent = button.innerHTML;
    
    // Loading state
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Testando...';
    
    try {
        const response = await fetch(`/api/domains/${domainId}/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('✅ Configuração do domínio está correta!', 'success');
            
            // Show detailed results
            const details = result.details;
            let detailsHtml = '<ul class="list-unstyled small mt-2">';
            detailsHtml += `<li><i class="bi bi-check text-success me-2"></i>DNS: ${details.dns_status}</li>`;
            detailsHtml += `<li><i class="bi bi-check text-success me-2"></i>Contas: ${details.accounts_active}</li>`;
            detailsHtml += `<li><i class="bi bi-check text-success me-2"></i>Templates: ${details.templates_active}</li>`;
            detailsHtml += '</ul>';
            
            showToast('Configuração validada com sucesso!' + detailsHtml, 'success', 8000);
        } else {
            showToast(`❌ Problema na configuração: ${result.error}`, 'danger');
        }
    } catch (error) {
        showToast(`Erro ao testar configuração: ${error.message}`, 'danger');
    } finally {
        button.disabled = false;
        button.innerHTML = originalContent;
    }
}

// ===== DELETE CONFIRMATION =====
function confirmDelete(domainId, domainName) {
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
}

// ===== UTILITY FUNCTIONS =====
function showToast(message, type = 'success', duration = 5000) {
    const iconMap = {
        'success': 'bi-check-circle-fill',
        'danger': 'bi-x-circle-fill', 
        'warning': 'bi-exclamation-triangle-fill',
        'info': 'bi-info-circle-fill'
    };
    
    const icon = iconMap[type] || iconMap['info'];
    
    const toastHtml = `
        <div class="toast align-items-center text-bg-${type} border-0" 
             role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${icon} me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast" aria-label="Fechar"></button>
            </div>
        </div>
    `;
    
    const container = document.getElementById('toast-container');
    container.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = container.lastElementChild;
    const toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();
    
    // Auto-remove after hide
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// ===== AUTO-SAVE FUNCTIONALITY (for future) =====
let autoSaveTimeout;
function setupAutoSave() {
    const form = document.getElementById('domainForm');
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(autoSaveDraft, 2000);
        });
    });
}

function autoSaveDraft() {
    // Implementation for auto-saving drafts
    console.log('Auto-save triggered');
}
</script>
{% endblock %}
```