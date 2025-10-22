# 📋 TEMPLATE: accounts/form.html - SendCraft CRUD Contas Email

```html
{% extends "base.html" %}

{% block title %}{{ 'Editar' if account else 'Nova' }} Conta Email - SendCraft{% endblock %}

{% block content %}
<!-- Breadcrumb -->
<nav aria-label="breadcrumb" class="mb-4">
    <ol class="breadcrumb">
        <li class="breadcrumb-item">
            <a href="{{ url_for('web.dashboard') }}" class="text-decoration-none">
                <i class="bi bi-house-door me-1"></i>Dashboard
            </a>
        </li>
        <li class="breadcrumb-item">
            <a href="{{ url_for('web.accounts_list') }}" class="text-decoration-none">
                <i class="bi bi-envelope me-1"></i>Contas
            </a>
        </li>
        <li class="breadcrumb-item active">{{ 'Editar' if account else 'Nova' }}</li>
    </ol>
</nav>

<!-- Header -->
<div class="row mb-4">
    <div class="col">
        <div class="d-flex align-items-center">
            <div class="bg-success-subtle text-success rounded-circle d-flex align-items-center justify-content-center me-3" 
                 style="width: 3rem; height: 3rem;">
                <i class="bi bi-envelope fs-4"></i>
            </div>
            <div>
                <h1 class="h2 mb-1">
                    {{ 'Editar Conta Email' if account else 'Nova Conta Email' }}
                </h1>
                <p class="text-muted mb-0">
                    {{ account.email_address if account else 'Configure uma nova conta SMTP para envios' }}
                </p>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <!-- Formulário Principal -->
    <div class="col-lg-8">
        <form method="POST" id="accountForm" data-validate novalidate>
            
            <!-- Informações Básicas -->
            <div class="card mb-4 border-0 shadow-sm">
                <div class="card-header bg-primary-subtle border-bottom">
                    <h5 class="mb-0 text-primary-emphasis">
                        <i class="bi bi-person-badge me-2"></i>
                        Informações Básicas
                    </h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <!-- Domínio -->
                        <div class="col-md-6 mb-3">
                            <label for="domain_id" class="form-label fw-semibold">
                                <i class="bi bi-globe2 me-2 text-primary"></i>
                                Domínio <span class="text-danger">*</span>
                            </label>
                            <select class="form-select" id="domain_id" name="domain_id" required>
                                <option value="">Selecionar domínio...</option>
                                {% for domain in domains %}
                                    <option value="{{ domain.id }}" 
                                            {{ 'selected' if account and account.domain_id == domain.id }}>
                                        {{ domain.name }}
                                        {% if not domain.is_active %} (Inativo){% endif %}
                                    </option>
                                {% endfor %}
                            </select>
                            <div class="invalid-feedback"></div>
                        </div>
                        
                        <!-- Local Part -->
                        <div class="col-md-6 mb-3">
                            <label for="local_part" class="form-label fw-semibold">
                                <i class="bi bi-at me-2 text-success"></i>
                                Parte Local <span class="text-danger">*</span>
                            </label>
                            <div class="input-group">
                                <input type="text" 
                                       class="form-control" 
                                       id="local_part" 
                                       name="local_part" 
                                       value="{{ account.local_part if account else '' }}"
                                       placeholder="encomendas"
                                       required>
                                <span class="input-group-text" id="domainSuffix">@domínio</span>
                            </div>
                            <div class="invalid-feedback"></div>
                            <div class="form-text">A parte antes do @ (ex: encomendas@dominio.pt)</div>
                        </div>
                    </div>
                    
                    <!-- Nome de Exibição -->
                    <div class="mb-3">
                        <label for="display_name" class="form-label fw-semibold">
                            <i class="bi bi-card-text me-2 text-info"></i>
                            Nome de Exibição
                        </label>
                        <input type="text" 
                               class="form-control" 
                               id="display_name" 
                               name="display_name" 
                               value="{{ account.display_name if account else '' }}"
                               placeholder="AliTools Encomendas">
                        <div class="form-text">Nome que aparece como remetente (ex: AliTools Encomendas)</div>
                    </div>
                </div>
            </div>
            
            <!-- Configurações SMTP -->
            <div class="card mb-4 border-0 shadow-sm">
                <div class="card-header bg-warning-subtle border-bottom">
                    <h5 class="mb-0 text-warning-emphasis">
                        <i class="bi bi-gear-wide-connected me-2"></i>
                        Configurações SMTP
                    </h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <!-- Servidor SMTP -->
                        <div class="col-md-8 mb-3">
                            <label for="smtp_server" class="form-label fw-semibold">
                                <i class="bi bi-server me-2 text-primary"></i>
                                Servidor SMTP <span class="text-danger">*</span>
                            </label>
                            <input type="text" 
                                   class="form-control" 
                                   id="smtp_server" 
                                   name="smtp_server" 
                                   value="{{ account.smtp_server if account else 'smtp.antispamcloud.com' }}"
                                   placeholder="smtp.exemplo.com"
                                   required>
                            <div class="invalid-feedback"></div>
                        </div>
                        
                        <!-- Porta -->
                        <div class="col-md-4 mb-3">
                            <label for="smtp_port" class="form-label fw-semibold">
                                <i class="bi bi-door-open me-2 text-info"></i>
                                Porta <span class="text-danger">*</span>
                            </label>
                            <input type="number" 
                                   class="form-control" 
                                   id="smtp_port" 
                                   name="smtp_port" 
                                   value="{{ account.smtp_port if account else 587 }}"
                                   min="1" max="65535"
                                   required>
                            <div class="invalid-feedback"></div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <!-- Username -->
                        <div class="col-md-6 mb-3">
                            <label for="smtp_username" class="form-label fw-semibold">
                                <i class="bi bi-person me-2 text-success"></i>
                                Username SMTP <span class="text-danger">*</span>
                            </label>
                            <input type="text" 
                                   class="form-control" 
                                   id="smtp_username" 
                                   name="smtp_username" 
                                   value="{{ account.smtp_username if account else '' }}"
                                   autocomplete="username"
                                   required>
                            <div class="invalid-feedback"></div>
                        </div>
                        
                        <!-- Password -->
                        <div class="col-md-6 mb-3">
                            <label for="smtp_password" class="form-label fw-semibold">
                                <i class="bi bi-key me-2 text-warning"></i>
                                Password SMTP {{ '' if not account else '(deixar vazio para manter)' }}
                                {% if not account %}<span class="text-danger">*</span>{% endif %}
                            </label>
                            <div class="input-group">
                                <input type="password" 
                                       class="form-control" 
                                       id="smtp_password" 
                                       name="smtp_password"
                                       autocomplete="new-password"
                                       {{ 'required' if not account else '' }}>
                                <button class="btn btn-outline-secondary" type="button" id="togglePassword">
                                    <i class="bi bi-eye"></i>
                                </button>
                            </div>
                            <div class="invalid-feedback"></div>
                            {% if account %}
                            <div class="form-text text-warning">
                                <i class="bi bi-shield-lock me-1"></i>
                                Password atual está encriptada e segura
                            </div>
                            {% endif %}
                        </div>
                    </div>
                    
                    <!-- Configurações Segurança -->
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <div class="form-check form-switch">
                                <input class="form-check-input" 
                                       type="checkbox" 
                                       id="use_tls" 
                                       name="use_tls"
                                       {{ 'checked' if not account or account.use_tls }}>
                                <label class="form-check-label fw-semibold" for="use_tls">
                                    <i class="bi bi-shield-check text-success me-2"></i>
                                    Usar TLS (recomendado)
                                </label>
                            </div>
                        </div>
                        
                        <div class="col-md-6 mb-3">
                            <div class="form-check form-switch">
                                <input class="form-check-input" 
                                       type="checkbox" 
                                       id="use_ssl" 
                                       name="use_ssl"
                                       {{ 'checked' if account and account.use_ssl }}>
                                <label class="form-check-label fw-semibold" for="use_ssl">
                                    <i class="bi bi-shield-lock text-primary me-2"></i>
                                    Usar SSL
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Limites de Envio -->
            <div class="card mb-4 border-0 shadow-sm">
                <div class="card-header bg-info-subtle border-bottom">
                    <h5 class="mb-0 text-info-emphasis">
                        <i class="bi bi-speedometer me-2"></i>
                        Limites de Envio
                    </h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="daily_limit" class="form-label fw-semibold">
                                <i class="bi bi-calendar-day me-2 text-warning"></i>
                                Limite Diário <span class="text-danger">*</span>
                            </label>
                            <div class="input-group">
                                <input type="number" 
                                       class="form-control" 
                                       id="daily_limit" 
                                       name="daily_limit" 
                                       value="{{ account.daily_limit if account else 1000 }}"
                                       min="1" max="10000"
                                       required>
                                <span class="input-group-text">emails/dia</span>
                            </div>
                            <div class="invalid-feedback"></div>
                        </div>
                        
                        <div class="col-md-6 mb-3">
                            <label for="monthly_limit" class="form-label fw-semibold">
                                <i class="bi bi-calendar-month me-2 text-primary"></i>
                                Limite Mensal <span class="text-danger">*</span>
                            </label>
                            <div class="input-group">
                                <input type="number" 
                                       class="form-control" 
                                       id="monthly_limit" 
                                       name="monthly_limit" 
                                       value="{{ account.monthly_limit if account else 20000 }}"
                                       min="1" max="100000"
                                       required>
                                <span class="input-group-text">emails/mês</span>
                            </div>
                            <div class="invalid-feedback"></div>
                        </div>
                    </div>
                    
                    {% if account %}
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card bg-warning-subtle">
                                <div class="card-body text-center py-2">
                                    <strong>Enviados Hoje</strong><br>
                                    <span class="h5 text-warning">{{ account.emails_sent_today }}</span> / {{ account.daily_limit }}
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card bg-primary-subtle">
                                <div class="card-body text-center py-2">
                                    <strong>Enviados Mês</strong><br>
                                    <span class="h5 text-primary">{{ account.emails_sent_this_month }}</span> / {{ account.monthly_limit }}
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <!-- Status e Ações -->
            <div class="card mb-4 border-0 shadow-sm">
                <div class="card-header bg-light border-bottom">
                    <h5 class="mb-0">
                        <i class="bi bi-toggles me-2 text-secondary"></i>
                        Status e Configurações
                    </h5>
                </div>
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-6">
                            <div class="form-check form-switch">
                                <input class="form-check-input" 
                                       type="checkbox" 
                                       role="switch" 
                                       id="is_active" 
                                       name="is_active"
                                       {{ 'checked' if not account or account.is_active }}>
                                <label class="form-check-label fw-semibold" for="is_active">
                                    <i class="bi bi-power text-success me-2"></i>
                                    Conta Ativa
                                </label>
                            </div>
                            <small class="text-muted">Apenas contas ativas podem enviar emails</small>
                        </div>
                        
                        {% if account %}
                        <div class="col-md-6">
                            <button type="button" 
                                    class="btn btn-outline-info"
                                    onclick="testCurrentSMTP()"
                                    id="testSMTPBtn">
                                <i class="bi bi-wifi me-2"></i>
                                Testar Conexão SMTP
                            </button>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
            
            <!-- Botões de Ação -->
            <div class="card border-0 shadow-sm">
                <div class="card-body">
                    <div class="d-flex gap-2 justify-content-between">
                        <div class="d-flex gap-2">
                            <button type="submit" class="btn btn-success">
                                <i class="bi bi-check-circle me-1"></i>
                                {{ 'Atualizar Conta' if account else 'Criar Conta' }}
                            </button>
                            
                            <a href="{{ url_for('web.accounts_list') }}" class="btn btn-outline-secondary">
                                <i class="bi bi-arrow-left me-1"></i>
                                Voltar
                            </a>
                        </div>
                        
                        {% if account %}
                        <button type="button" 
                                class="btn btn-outline-danger"
                                onclick="confirmDeleteAccount({{ account.id }}, '{{ account.email_address }}')">
                            <i class="bi bi-trash me-1"></i>
                            Eliminar Conta
                        </button>
                        {% endif %}
                    </div>
                </div>
            </div>
        </form>
    </div>
    
    <!-- Sidebar -->
    <div class="col-lg-4">
        <!-- Preview Email Address -->
        <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-success-subtle">
                <h6 class="mb-0 text-success-emphasis">
                    <i class="bi bi-envelope-at me-2"></i>
                    Preview Email
                </h6>
            </div>
            <div class="card-body text-center">
                <div class="mb-3">
                    <div class="bg-light border rounded p-3">
                        <i class="bi bi-envelope-open text-muted fs-1 mb-2"></i>
                        <div class="h5 mb-2" id="emailPreview">
                            <span id="previewLocal">{{ account.local_part if account else 'conta' }}</span>@<span id="previewDomain">{{ account.domain.name if account else 'dominio.pt' }}</span>
                        </div>
                        <small class="text-muted" id="previewDisplay">{{ account.display_name if account else 'Nome de Exibição' }}</small>
                    </div>
                </div>
                
                {% if account %}
                <div class="row text-center small">
                    <div class="col-6">
                        <div class="border rounded p-2">
                            <strong class="text-success">{{ account.emails_sent_today }}</strong>
                            <br><small class="text-muted">Hoje</small>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="border rounded p-2">
                            <strong class="text-primary">{{ account.emails_sent_this_month }}</strong>
                            <br><small class="text-muted">Mês</small>
                        </div>
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
        
        <!-- SMTP Help -->
        <div class="card border-0 shadow-sm">
            <div class="card-header bg-info-subtle">
                <h6 class="mb-0 text-info-emphasis">
                    <i class="bi bi-question-circle me-2"></i>
                    Ajuda SMTP
                </h6>
            </div>
            <div class="card-body">
                <div class="accordion accordion-flush" id="smtpHelp">
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#commonProviders">
                                Provedores Comuns
                            </button>
                        </h2>
                        <div id="commonProviders" class="accordion-collapse collapse" data-bs-parent="#smtpHelp">
                            <div class="accordion-body small">
                                <strong>Gmail:</strong><br>
                                smtp.gmail.com:587 (TLS)<br><br>
                                <strong>Outlook:</strong><br>
                                smtp-mail.outlook.com:587<br><br>
                                <strong>cPanel:</strong><br>
                                mail.seudominio.pt:587
                            </div>
                        </div>
                    </div>
                    
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#smtpPorts">
                                Portas SMTP
                            </button>
                        </h2>
                        <div id="smtpPorts" class="accordion-collapse collapse" data-bs-parent="#smtpHelp">
                            <div class="accordion-body small">
                                <strong>587:</strong> TLS (recomendado)<br>
                                <strong>465:</strong> SSL<br>
                                <strong>25:</strong> Sem encriptação<br>
                                <strong>2525:</strong> Alternativa
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Modal Delete -->
{% if account %}
<div class="modal fade" id="deleteAccountModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header border-bottom-0">
                <h5 class="modal-title text-danger">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    Eliminar Conta Email
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body text-center">
                <i class="bi bi-envelope text-danger" style="font-size: 3rem;"></i>
                <h6 class="my-3">Eliminar <strong class="text-danger">{{ account.email_address }}</strong>?</h6>
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Esta ação eliminará o histórico de emails e não pode ser desfeita.
                </div>
            </div>
            <div class="modal-footer border-top-0 justify-content-center">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <form method="POST" action="{{ url_for('web.accounts_delete', account_id=account.id) }}">
                    <button type="submit" class="btn btn-danger">
                        <i class="bi bi-trash me-1"></i>Eliminar
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
// ===== FORM FUNCTIONALITY =====
document.addEventListener('DOMContentLoaded', function() {
    setupFormInteractions();
    setupValidation();
});

function setupFormInteractions() {
    // Update email preview when inputs change
    const domainSelect = document.getElementById('domain_id');
    const localPartInput = document.getElementById('local_part');
    const displayNameInput = document.getElementById('display_name');
    
    domainSelect.addEventListener('change', updateEmailPreview);
    localPartInput.addEventListener('input', updateEmailPreview);
    displayNameInput.addEventListener('input', updateEmailPreview);
    
    // Password toggle
    const passwordInput = document.getElementById('smtp_password');
    const toggleBtn = document.getElementById('togglePassword');
    
    toggleBtn.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        this.innerHTML = type === 'password' ? '<i class="bi bi-eye"></i>' : '<i class="bi bi-eye-slash"></i>';
    });
    
    // Port suggestions based on TLS/SSL
    const tlsCheckbox = document.getElementById('use_tls');
    const sslCheckbox = document.getElementById('use_ssl');
    const portInput = document.getElementById('smtp_port');
    
    tlsCheckbox.addEventListener('change', function() {
        if (this.checked && sslCheckbox.checked) {
            sslCheckbox.checked = false;
        }
        if (this.checked && portInput.value === '465') {
            portInput.value = '587';
        }
    });
    
    sslCheckbox.addEventListener('change', function() {
        if (this.checked && tlsCheckbox.checked) {
            tlsCheckbox.checked = false;
        }
        if (this.checked && portInput.value === '587') {
            portInput.value = '465';
        }
    });
}

function updateEmailPreview() {
    const domainSelect = document.getElementById('domain_id');
    const localPart = document.getElementById('local_part').value || 'conta';
    const displayName = document.getElementById('display_name').value || 'Nome de Exibição';
    
    const selectedDomain = domainSelect.options[domainSelect.selectedIndex];
    const domainName = selectedDomain && selectedDomain.value ? selectedDomain.text.split(' ')[0] : 'dominio.pt';
    
    document.getElementById('previewLocal').textContent = localPart;
    document.getElementById('previewDomain').textContent = domainName;
    document.getElementById('previewDisplay').textContent = displayName;
    
    // Update domain suffix in local part input
    document.getElementById('domainSuffix').textContent = '@' + domainName;
}

// ===== SMTP TESTING =====
async function testCurrentSMTP() {
    const button = document.getElementById('testSMTPBtn');
    const originalContent = button.innerHTML;
    
    // Get form data
    const formData = new FormData(document.getElementById('accountForm'));
    const testData = {
        smtp_server: formData.get('smtp_server'),
        smtp_port: parseInt(formData.get('smtp_port')),
        smtp_username: formData.get('smtp_username'),
        smtp_password: formData.get('smtp_password'),
        use_tls: formData.get('use_tls') === 'on',
        use_ssl: formData.get('use_ssl') === 'on'
    };
    
    // Validation
    if (!testData.smtp_server || !testData.smtp_port || !testData.smtp_username) {
        showToast('Preencha os campos SMTP obrigatórios primeiro', 'warning');
        return;
    }
    
    // Loading state
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Testando conexão...';
    
    try {
        const response = await fetch('/api/smtp/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(testData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('✅ Configuração SMTP válida!', 'success');
            showSMTPTestDetails(result.details, true);
        } else {
            showToast(`❌ Erro SMTP: ${result.error}`, 'danger');
            showSMTPTestDetails(result.details, false);
        }
        
    } catch (error) {
        showToast('Erro ao testar SMTP', 'danger');
    } finally {
        button.disabled = false;
        button.innerHTML = originalContent;
    }
}

function showSMTPTestDetails(details, success) {
    const alertClass = success ? 'success' : 'danger';
    const icon = success ? 'check-circle' : 'x-circle';
    
    const detailsHtml = `
        <div class="alert alert-${alertClass}" role="alert">
            <h6 class="alert-heading">
                <i class="bi bi-${icon}-fill me-2"></i>
                Teste de Conexão SMTP
            </h6>
            <div class="row">
                <div class="col-md-6">
                    <strong>Servidor:</strong> ${details.server}<br>
                    <strong>Porta:</strong> ${details.port}<br>
                    <strong>Segurança:</strong> ${details.security}
                </div>
                <div class="col-md-6">
                    <strong>Tempo:</strong> ${details.response_time}ms<br>
                    <strong>Status:</strong> ${details.status}<br>
                    <strong>Código:</strong> ${details.code}
                </div>
            </div>
            <hr>
            <small><strong>Mensagem:</strong> ${details.message}</small>
        </div>
    `;
    
    // Insert after SMTP card
    const smtpCard = document.querySelector('.card .bg-warning-subtle').closest('.card');
    const existingAlert = smtpCard.nextElementSibling;
    if (existingAlert && existingAlert.classList.contains('alert')) {
        existingAlert.remove();
    }
    
    smtpCard.insertAdjacentHTML('afterend', detailsHtml);
    
    // Scroll to results
    smtpCard.nextElementSibling.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ===== FORM VALIDATION =====
function setupValidation() {
    const form = document.getElementById('accountForm');
    
    // Real-time validation
    form.querySelectorAll('input, select').forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => {
            if (input.classList.contains('is-invalid')) {
                validateField(input);
            }
        });
    });
    
    // Form submission validation
    form.addEventListener('submit', function(e) {
        if (!validateAccountForm()) {
            e.preventDefault();
            showToast('Corrija os erros no formulário', 'warning');
        }
    });
}

function validateAccountForm() {
    let isValid = true;
    
    // Validate required fields
    const requiredFields = ['domain_id', 'local_part', 'smtp_server', 'smtp_port', 'smtp_username', 'daily_limit', 'monthly_limit'];
    
    {% if not account %}
    requiredFields.push('smtp_password');
    {% endif %}
    
    requiredFields.forEach(fieldName => {
        const field = document.getElementById(fieldName);
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
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
    
    // Specific validations
    switch (field.name) {
        case 'local_part':
            if (value && !/^[a-zA-Z0-9._-]+$/.test(value)) {
                isValid = false;
                errorMessage = 'Apenas letras, números, pontos, hífens e underscores';
            }
            break;
            
        case 'smtp_port':
            const port = parseInt(value);
            if (value && (port < 1 || port > 65535)) {
                isValid = false;
                errorMessage = 'Porta deve estar entre 1 e 65535';
            }
            break;
            
        case 'daily_limit':
        case 'monthly_limit':
            const limit = parseInt(value);
            if (value && limit < 1) {
                isValid = false;
                errorMessage = 'Limite deve ser maior que 0';
            }
            break;
    }
    
    // Update field state
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        
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

// ===== DELETE CONFIRMATION =====
function confirmDeleteAccount(accountId, accountEmail) {
    const modal = new bootstrap.Modal(document.getElementById('deleteAccountModal'));
    modal.show();
}

// ===== UTILITY FUNCTIONS =====
function showToast(message, type = 'success', duration = 5000) {
    const toastHtml = `
        <div class="toast align-items-center text-bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    const container = document.getElementById('toast-container');
    container.insertAdjacentHTML('beforeend', toastHtml);
    
    const toast = new bootstrap.Toast(container.lastElementChild, { delay: duration });
    toast.show();
}
</script>
{% endblock %}
```