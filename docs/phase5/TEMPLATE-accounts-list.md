# 📋 TEMPLATE: accounts/list.html - SendCraft Gestão de Contas Email

```html
{% extends "base.html" %}

{% block title %}Gestão de Contas Email - SendCraft{% endblock %}

{% block content %}
<!-- Header com Breadcrumb -->
<div class="row mb-4">
    <div class="col">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item">
                    <a href="{{ url_for('web.dashboard') }}" class="text-decoration-none">
                        <i class="bi bi-house-door me-1"></i>Dashboard
                    </a>
                </li>
                <li class="breadcrumb-item active" aria-current="page">
                    <i class="bi bi-envelope me-1"></i>Contas Email
                </li>
            </ol>
        </nav>
        
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <h1 class="h2 mb-1">
                    <i class="bi bi-envelope me-2 text-success"></i>
                    Gestão de Contas Email
                </h1>
                <p class="text-muted mb-0">Configure contas SMTP para envio de emails</p>
            </div>
            <div class="d-flex gap-2">
                <button class="btn btn-outline-secondary" onclick="testAllSMTP()" data-bs-toggle="tooltip" title="Testar todas as conexões SMTP">
                    <i class="bi bi-wifi"></i>
                </button>
                <a href="{{ url_for('web.accounts_new') }}" class="btn btn-success">
                    <i class="bi bi-plus-circle me-1"></i>
                    Nova Conta
                </a>
            </div>
        </div>
    </div>
</div>

<!-- Filtros -->
<div class="card mb-4 border-0 shadow-sm">
    <div class="card-header bg-light border-bottom-0">
        <h6 class="mb-0">
            <i class="bi bi-funnel me-2"></i>Filtros e Pesquisa
        </h6>
    </div>
    <div class="card-body">
        <form method="GET" class="row g-3">
            <div class="col-md-4">
                <label for="searchInput" class="form-label visually-hidden">Pesquisar</label>
                <div class="input-group">
                    <span class="input-group-text bg-white border-end-0">
                        <i class="bi bi-search text-muted"></i>
                    </span>
                    <input type="text" 
                           id="searchInput"
                           name="search" 
                           class="form-control border-start-0" 
                           value="{{ search }}" 
                           placeholder="Procurar contas...">
                </div>
            </div>
            
            <div class="col-md-3">
                <select name="domain" class="form-select">
                    <option value="">Todos os domínios</option>
                    {% for domain_option in domains %}
                        <option value="{{ domain_option.name }}" 
                                {{ 'selected' if domain_filter == domain_option.name }}>
                            {{ domain_option.name }} ({{ domain_option.accounts_count }} contas)
                        </option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="col-md-2">
                <select name="status" class="form-select">
                    <option value="">Todos</option>
                    <option value="active" {{ 'selected' if request.args.get('status') == 'active' }}>Ativas</option>
                    <option value="inactive" {{ 'selected' if request.args.get('status') == 'inactive' }}>Inativas</option>
                    <option value="smtp_ok" {{ 'selected' if request.args.get('status') == 'smtp_ok' }}>SMTP OK</option>
                    <option value="smtp_error" {{ 'selected' if request.args.get('status') == 'smtp_error' }}>SMTP Erro</option>
                </select>
            </div>
            
            <div class="col-md-3">
                <div class="d-flex gap-2">
                    <button type="submit" class="btn btn-outline-primary flex-fill">
                        <i class="bi bi-funnel me-1"></i>Aplicar
                    </button>
                    <a href="{{ url_for('web.accounts_list') }}" class="btn btn-outline-secondary">
                        <i class="bi bi-x-circle"></i>
                    </a>
                </div>
            </div>
        </form>
    </div>
</div>

<!-- Stats Cards -->
{% if accounts and accounts.total > 0 %}
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card text-center border-success">
            <div class="card-body">
                <i class="bi bi-envelope-check text-success fs-1 mb-2"></i>
                <h4 class="mb-1">{{ accounts.items | selectattr('is_active') | list | length }}</h4>
                <small class="text-muted">Contas Ativas</small>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center border-info">
            <div class="card-body">
                <i class="bi bi-wifi text-info fs-1 mb-2"></i>
                <h4 class="mb-1">{{ accounts.items | selectattr('smtp_status', 'equalto', 'connected') | list | length }}</h4>
                <small class="text-muted">SMTP Conectado</small>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center border-warning">
            <div class="card-body">
                <i class="bi bi-graph-up text-warning fs-1 mb-2"></i>
                <h4 class="mb-1">{{ accounts.items | sum(attribute='emails_sent_today') }}</h4>
                <small class="text-muted">Enviados Hoje</small>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center border-primary">
            <div class="card-body">
                <i class="bi bi-envelope-paper text-primary fs-1 mb-2"></i>
                <h4 class="mb-1">{{ accounts.items | sum(attribute='emails_sent_this_month') }}</h4>
                <small class="text-muted">Mês Atual</small>
            </div>
        </div>
    </div>
</div>
{% endif %}

<!-- Tabela de Contas -->
<div class="card border-0 shadow-sm">
    <div class="card-header bg-white border-bottom">
        <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
                <i class="bi bi-list-ul me-2 text-secondary"></i>
                Contas de Email
                {% if accounts and accounts.total %}
                    <span class="badge bg-success-subtle text-success ms-2">{{ accounts.total }}</span>
                {% endif %}
            </h5>
        </div>
    </div>
    
    <div class="card-body p-0">
        {% if accounts and accounts.items %}
        <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead class="table-light">
                    <tr>
                        <th class="ps-4">Conta Email</th>
                        <th class="text-center">Status</th>
                        <th class="text-center">SMTP</th>
                        <th class="text-center">Hoje</th>
                        <th class="text-center">Limite Diário</th>
                        <th class="text-center">Mês</th>
                        <th class="text-center">Limite Mensal</th>
                        <th width="160" class="text-center">Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {% for account in accounts.items %}
                    <tr data-account-id="{{ account.id }}">
                        <td class="ps-4">
                            <div class="d-flex align-items-center">
                                <div class="avatar-sm bg-success-subtle text-success rounded-circle d-flex align-items-center justify-content-center me-3">
                                    <i class="bi bi-envelope"></i>
                                </div>
                                <div>
                                    <h6 class="mb-0 fw-semibold">{{ account.local_part }}@{{ account.domain.name }}</h6>
                                    <small class="text-muted">{{ account.display_name or 'Sem nome de exibição' }}</small>
                                </div>
                            </div>
                        </td>
                        
                        <td class="text-center">
                            {% if account.is_active %}
                                <span class="badge rounded-pill bg-success-subtle text-success">
                                    <i class="bi bi-check-circle-fill me-1"></i>Ativa
                                </span>
                            {% else %}
                                <span class="badge rounded-pill bg-secondary-subtle text-secondary">
                                    <i class="bi bi-pause-circle-fill me-1"></i>Inativa
                                </span>
                            {% endif %}
                        </td>
                        
                        <td class="text-center">
                            <span class="badge bg-{{ 'success' if account.smtp_status == 'connected' else 'warning' if account.smtp_status == 'untested' else 'danger' }}-subtle 
                                         text-{{ 'success' if account.smtp_status == 'connected' else 'warning' if account.smtp_status == 'untested' else 'danger' }}"
                                  data-smtp-status="{{ account.id }}">
                                {% if account.smtp_status == 'connected' %}
                                    <i class="bi bi-wifi me-1"></i>OK
                                {% elif account.smtp_status == 'error' %}
                                    <i class="bi bi-wifi-off me-1"></i>Erro
                                {% else %}
                                    <i class="bi bi-question-circle me-1"></i>Não testado
                                {% endif %}
                            </span>
                            <br>
                            <small class="text-muted">
                                {{ account.smtp_server }}:{{ account.smtp_port }}
                            </small>
                        </td>
                        
                        <td class="text-center">
                            <div class="d-flex flex-column align-items-center">
                                <span class="badge bg-info-subtle text-info fw-semibold">
                                    {{ account.emails_sent_today }}
                                </span>
                                <div class="progress mt-1" style="width: 60px; height: 4px;">
                                    <div class="progress-bar bg-info" 
                                         style="width: {{ (account.emails_sent_today / account.daily_limit * 100) if account.daily_limit else 0 }}%"></div>
                                </div>
                            </div>
                        </td>
                        
                        <td class="text-center">
                            <small class="text-muted">{{ account.daily_limit }}</small>
                        </td>
                        
                        <td class="text-center">
                            <div class="d-flex flex-column align-items-center">
                                <span class="badge bg-primary-subtle text-primary fw-semibold">
                                    {{ account.emails_sent_this_month }}
                                </span>
                                <div class="progress mt-1" style="width: 60px; height: 4px;">
                                    <div class="progress-bar bg-primary" 
                                         style="width: {{ (account.emails_sent_this_month / account.monthly_limit * 100) if account.monthly_limit else 0 }}%"></div>
                                </div>
                            </div>
                        </td>
                        
                        <td class="text-center">
                            <small class="text-muted">{{ account.monthly_limit }}</small>
                        </td>
                        
                        <td class="text-center">
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-info btn-sm"
                                        data-smtp-test="{{ account.id }}"
                                        onclick="testSMTPConnection({{ account.id }})"
                                        data-bs-toggle="tooltip"
                                        title="Testar conexão SMTP">
                                    <i class="bi bi-wifi"></i>
                                </button>
                                
                                <a href="{{ url_for('web.accounts_edit', account_id=account.id) }}" 
                                   class="btn btn-outline-primary btn-sm"
                                   data-bs-toggle="tooltip"
                                   title="Editar conta">
                                    <i class="bi bi-pencil"></i>
                                </a>
                                
                                <button class="btn btn-outline-{{ 'warning' if account.is_active else 'success' }} btn-sm"
                                        onclick="toggleAccountStatus({{ account.id }}, {{ account.is_active|lower }})"
                                        data-bs-toggle="tooltip"
                                        title="{{ 'Desativar' if account.is_active else 'Ativar' }} conta">
                                    <i class="bi bi-{{ 'pause' if account.is_active else 'play' }}-fill"></i>
                                </button>
                                
                                <button class="btn btn-outline-danger btn-sm"
                                        onclick="confirmDeleteAccount({{ account.id }}, '{{ account.email_address }}')"
                                        data-bs-toggle="tooltip"
                                        title="Eliminar conta">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- Paginação -->
        {% if accounts.pages > 1 %}
        <div class="card-footer bg-white border-top">
            <div class="row align-items-center">
                <div class="col">
                    <small class="text-muted">
                        Mostrando {{ ((accounts.page - 1) * accounts.per_page) + 1 }} a 
                        {{ accounts.page * accounts.per_page if accounts.page * accounts.per_page < accounts.total else accounts.total }} 
                        de {{ accounts.total }} contas
                    </small>
                </div>
                <div class="col-auto">
                    <nav aria-label="Navegação de contas">
                        <ul class="pagination pagination-sm mb-0">
                            {% if accounts.has_prev %}
                                <li class="page-item">
                                    <a class="page-link" 
                                       href="{{ url_for('web.accounts_list', page=accounts.prev_num, search=search, domain=domain_filter) }}">
                                        <i class="bi bi-chevron-left"></i>
                                    </a>
                                </li>
                            {% endif %}
                            
                            {% for page_num in accounts.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2) %}
                                {% if page_num %}
                                    {% if page_num != accounts.page %}
                                        <li class="page-item">
                                            <a class="page-link" 
                                               href="{{ url_for('web.accounts_list', page=page_num, search=search, domain=domain_filter) }}">
                                                {{ page_num }}
                                            </a>
                                        </li>
                                    {% else %}
                                        <li class="page-item active">
                                            <span class="page-link">{{ page_num }}</span>
                                        </li>
                                    {% endif %}
                                {% else %}
                                    <li class="page-item disabled">
                                        <span class="page-link">…</span>
                                    </li>
                                {% endif %}
                            {% endfor %}
                            
                            {% if accounts.has_next %}
                                <li class="page-item">
                                    <a class="page-link" 
                                       href="{{ url_for('web.accounts_list', page=accounts.next_num, search=search, domain=domain_filter) }}">
                                        <i class="bi bi-chevron-right"></i>
                                    </a>
                                </li>
                            {% endif %}
                        </ul>
                    </nav>
                </div>
            </div>
        </div>
        {% endif %}

        {% else %}
        <!-- Estado Vazio -->
        <div class="text-center py-5">
            <div class="mb-4">
                <i class="bi bi-envelope text-muted" style="font-size: 5rem; opacity: 0.3;"></i>
            </div>
            
            {% if search or domain_filter %}
                <h4 class="text-muted mb-3">Nenhuma Conta Encontrada</h4>
                <p class="text-muted mb-4">
                    Não foram encontradas contas que correspondam aos filtros aplicados.
                </p>
                <div class="d-flex gap-2 justify-content-center">
                    <a href="{{ url_for('web.accounts_list') }}" class="btn btn-outline-secondary">
                        <i class="bi bi-arrow-clockwise me-1"></i>Limpar Filtros
                    </a>
                    <a href="{{ url_for('web.accounts_new') }}" class="btn btn-success">
                        <i class="bi bi-plus-circle me-1"></i>Nova Conta
                    </a>
                </div>
            {% else %}
                <h4 class="text-muted mb-3">Nenhuma Conta Configurada</h4>
                <p class="text-muted mb-4">
                    Configure sua primeira conta de email para começar a enviar.
                    <br>Certifique-se de ter pelo menos um domínio criado primeiro.
                </p>
                
                {% if domains %}
                    <a href="{{ url_for('web.accounts_new') }}" class="btn btn-success btn-lg">
                        <i class="bi bi-plus-circle me-2"></i>
                        Criar Primeira Conta
                    </a>
                {% else %}
                    <div class="alert alert-info d-inline-block">
                        <i class="bi bi-info-circle me-2"></i>
                        <strong>Primeiro crie um domínio</strong> antes de configurar contas.
                    </div>
                    <br><br>
                    <a href="{{ url_for('web.domains_new') }}" class="btn btn-primary">
                        <i class="bi bi-globe2 me-1"></i>Criar Domínio
                    </a>
                {% endif %}
            {% endif %}
        </div>
        {% endif %}
    </div>
</div>

<!-- Modal Delete Account -->
<div class="modal fade" id="deleteAccountModal" tabindex="-1" aria-labelledby="deleteAccountModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header border-bottom-0">
                <h5 class="modal-title text-danger" id="deleteAccountModalLabel">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    Eliminar Conta Email
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body text-center">
                <div class="mb-3">
                    <i class="bi bi-envelope text-danger" style="font-size: 3rem; opacity: 0.7;"></i>
                </div>
                <h6 class="mb-3">Eliminar conta <strong id="deleteAccountEmail" class="text-danger"></strong>?</h6>
                
                <div class="alert alert-warning" role="alert">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    <strong>Esta ação irá:</strong>
                    <ul class="list-unstyled mt-2 mb-0">
                        <li>• Remover a conta permanentemente</li>
                        <li>• Eliminar histórico de emails enviados</li>
                        <li>• Impedir novos envios desta conta</li>
                    </ul>
                </div>
            </div>
            <div class="modal-footer border-top-0 justify-content-center">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    <i class="bi bi-x-circle me-1"></i>Cancelar
                </button>
                <form id="deleteAccountForm" method="POST" style="display: inline;">
                    <button type="submit" class="btn btn-danger">
                        <i class="bi bi-trash me-1"></i>Eliminar Conta
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

<!-- Modal SMTP Test Results -->
<div class="modal fade" id="smtpTestModal" tabindex="-1" aria-labelledby="smtpTestModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="smtpTestModalLabel">
                    <i class="bi bi-wifi me-2"></i>Resultado Teste SMTP
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div id="smtpTestResults"></div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    setupAutoRefresh();
});

function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ===== SMTP TESTING =====
async function testSMTPConnection(accountId) {
    const button = document.querySelector(`[data-smtp-test="${accountId}"]`);
    const statusBadge = document.querySelector(`[data-smtp-status="${accountId}"]`);
    const originalContent = button.innerHTML;
    
    // Loading state
    button.disabled = true;
    button.className = 'btn btn-outline-secondary btn-sm';
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Testando...';
    
    try {
        const response = await fetch(`/api/accounts/${accountId}/test-smtp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('✅ Conexão SMTP bem-sucedida!', 'success');
            
            // Update UI
            button.className = 'btn btn-outline-success btn-sm';
            button.innerHTML = '<i class="bi bi-check-circle"></i>';
            
            statusBadge.className = 'badge bg-success-subtle text-success';
            statusBadge.innerHTML = '<i class="bi bi-wifi me-1"></i>OK';
            
            // Show detailed results
            showSMTPTestResults(result.details);
            
        } else {
            showToast(`❌ Erro SMTP: ${result.error}`, 'danger');
            
            button.className = 'btn btn-outline-danger btn-sm';
            button.innerHTML = '<i class="bi bi-x-circle"></i>';
            
            statusBadge.className = 'badge bg-danger-subtle text-danger';
            statusBadge.innerHTML = '<i class="bi bi-wifi-off me-1"></i>Erro';
            
            // Show error details
            showSMTPTestResults(result.details, false);
        }
    } catch (error) {
        console.error('SMTP Test Error:', error);
        showToast('Erro ao testar conexão SMTP', 'danger');
        
        button.className = 'btn btn-outline-warning btn-sm';
        button.innerHTML = '<i class="bi bi-exclamation-triangle"></i>';
    } finally {
        button.disabled = false;
        
        // Restore original state after 3 seconds
        setTimeout(() => {
            button.className = 'btn btn-outline-info btn-sm';
            button.innerHTML = '<i class="bi bi-wifi"></i>';
        }, 3000);
    }
}

function showSMTPTestResults(details, success = true) {
    const resultsHtml = `
        <div class="alert alert-${success ? 'success' : 'danger'}" role="alert">
            <h6 class="alert-heading">
                <i class="bi bi-${success ? 'check-circle' : 'x-circle'}-fill me-2"></i>
                Resultado do Teste SMTP
            </h6>
            <hr>
            <div class="row">
                <div class="col-md-6">
                    <strong>Servidor:</strong><br>
                    <code>${details.server}:${details.port}</code>
                </div>
                <div class="col-md-6">
                    <strong>Segurança:</strong><br>
                    <span class="badge bg-${details.tls ? 'success' : 'secondary'}">${details.tls ? 'TLS' : 'Sem TLS'}</span>
                    <span class="badge bg-${details.ssl ? 'success' : 'secondary'}">${details.ssl ? 'SSL' : 'Sem SSL'}</span>
                </div>
            </div>
            <hr>
            <div class="small">
                <strong>Tempo resposta:</strong> ${details.response_time}ms<br>
                <strong>Mensagem:</strong> ${details.message}
            </div>
        </div>
    `;
    
    document.getElementById('smtpTestResults').innerHTML = resultsHtml;
    
    const modal = new bootstrap.Modal(document.getElementById('smtpTestModal'));
    modal.show();
}

// Test all SMTP connections
async function testAllSMTP() {
    const button = event.target;
    const originalContent = button.innerHTML;
    
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Testando...';
    
    try {
        const accountButtons = document.querySelectorAll('[data-smtp-test]');
        const results = [];
        
        for (const accountButton of accountButtons) {
            const accountId = accountButton.dataset.smtpTest;
            try {
                const response = await fetch(`/api/accounts/${accountId}/test-smtp`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const result = await response.json();
                results.push({ accountId, result });
            } catch (error) {
                results.push({ accountId, result: { success: false, error: error.message } });
            }
        }
        
        // Update all status badges
        results.forEach(({ accountId, result }) => {
            const statusBadge = document.querySelector(`[data-smtp-status="${accountId}"]`);
            if (statusBadge) {
                if (result.success) {
                    statusBadge.className = 'badge bg-success-subtle text-success';
                    statusBadge.innerHTML = '<i class="bi bi-wifi me-1"></i>OK';
                } else {
                    statusBadge.className = 'badge bg-danger-subtle text-danger';
                    statusBadge.innerHTML = '<i class="bi bi-wifi-off me-1"></i>Erro';
                }
            }
        });
        
        const successCount = results.filter(r => r.result.success).length;
        const totalCount = results.length;
        
        if (successCount === totalCount) {
            showToast(`✅ Todas as ${totalCount} conexões SMTP testadas com sucesso!`, 'success');
        } else {
            showToast(`⚠️ ${successCount}/${totalCount} conexões OK. ${totalCount - successCount} com problemas.`, 'warning');
        }
        
    } catch (error) {
        showToast('Erro ao testar conexões SMTP', 'danger');
    } finally {
        button.disabled = false;
        button.innerHTML = originalContent;
    }
}

// ===== ACCOUNT OPERATIONS =====
function confirmDeleteAccount(accountId, accountEmail) {
    document.getElementById('deleteAccountEmail').textContent = accountEmail;
    document.getElementById('deleteAccountForm').action = `/accounts/${accountId}/delete`;
    
    const modal = new bootstrap.Modal(document.getElementById('deleteAccountModal'));
    modal.show();
}

async function toggleAccountStatus(accountId, isActive) {
    const button = event.target.closest('button');
    const originalContent = button.innerHTML;
    
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
    
    try {
        const response = await fetch(`/api/accounts/${accountId}/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        showToast(`Erro ao alterar status: ${error.message}`, 'danger');
    } finally {
        button.disabled = false;
        button.innerHTML = originalContent;
    }
}

// ===== AUTO-REFRESH =====
function setupAutoRefresh() {
    // Auto-refresh every 5 minutes to update stats
    setInterval(() => {
        if (!document.querySelector('.modal.show')) {
            updateAccountStats();
        }
    }, 300000);
}

async function updateAccountStats() {
    try {
        const response = await fetch('/api/stats/accounts');
        const stats = await response.json();
        
        // Update progress bars and counters
        stats.accounts.forEach(account => {
            updateAccountRow(account);
        });
        
    } catch (error) {
        console.error('Error updating account stats:', error);
    }
}

function updateAccountRow(accountData) {
    const row = document.querySelector(`tr[data-account-id="${accountData.id}"]`);
    if (!row) return;
    
    // Update daily progress
    const dailyProgress = row.querySelector('.progress-bar:first-of-type');
    if (dailyProgress) {
        const dailyPercentage = (accountData.emails_sent_today / accountData.daily_limit) * 100;
        dailyProgress.style.width = `${dailyPercentage}%`;
    }
    
    // Update monthly progress
    const monthlyProgress = row.querySelector('.progress-bar:last-of-type');
    if (monthlyProgress) {
        const monthlyPercentage = (accountData.emails_sent_this_month / accountData.monthly_limit) * 100;
        monthlyProgress.style.width = `${monthlyPercentage}%`;
    }
    
    // Update counters
    const todayBadge = row.querySelector('.badge.bg-info-subtle');
    if (todayBadge) {
        todayBadge.textContent = accountData.emails_sent_today;
    }
    
    const monthBadge = row.querySelector('.badge.bg-primary-subtle');
    if (monthBadge) {
        monthBadge.textContent = accountData.emails_sent_this_month;
    }
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
        <div class="toast align-items-center text-bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${icon} me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    const container = document.getElementById('toast-container');
    container.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = container.lastElementChild;
    const toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}
</script>
{% endblock %}
```