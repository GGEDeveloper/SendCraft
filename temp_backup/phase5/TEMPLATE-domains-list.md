# 📋 TEMPLATE: domains/list.html - SendCraft Gestão de Domínios

```html
{% extends "base.html" %}

{% block title %}Gestão de Domínios - SendCraft{% endblock %}

{% block content %}
<!-- Header com Breadcrumb -->
<div class="row mb-4">
    <div class="col">
        <!-- Breadcrumb Navigation -->
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item">
                    <a href="{{ url_for('web.dashboard') }}" class="text-decoration-none">
                        <i class="bi bi-house-door me-1"></i>Dashboard
                    </a>
                </li>
                <li class="breadcrumb-item active" aria-current="page">
                    <i class="bi bi-globe2 me-1"></i>Domínios
                </li>
            </ol>
        </nav>
        
        <!-- Page Header -->
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <h1 class="h2 mb-1">
                    <i class="bi bi-globe2 me-2 text-primary"></i>
                    Gestão de Domínios
                </h1>
                <p class="text-muted mb-0">Configure e gerencie domínios para envio de emails</p>
            </div>
            <div class="d-flex gap-2">
                <button class="btn btn-outline-secondary" data-bs-toggle="tooltip" title="Atualizar dados">
                    <i class="bi bi-arrow-clockwise"></i>
                </button>
                <a href="{{ url_for('web.domains_new') }}" class="btn btn-primary">
                    <i class="bi bi-plus-circle me-1"></i>
                    Novo Domínio
                </a>
            </div>
        </div>
    </div>
</div>

<!-- Filtros e Pesquisa -->
<div class="card mb-4 border-0 shadow-sm">
    <div class="card-header bg-light border-bottom-0">
        <h6 class="mb-0">
            <i class="bi bi-funnel me-2"></i>Filtros e Pesquisa
        </h6>
    </div>
    <div class="card-body">
        <form method="GET" class="row g-3">
            <!-- Campo de Pesquisa -->
            <div class="col-md-6">
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
                           placeholder="Procurar por nome do domínio..."
                           autocomplete="off">
                </div>
            </div>
            
            <!-- Filtro Status -->
            <div class="col-md-3">
                <label for="statusFilter" class="form-label visually-hidden">Status</label>
                <select name="status" id="statusFilter" class="form-select">
                    <option value="">Todos os status</option>
                    <option value="active" {{ 'selected' if status_filter == 'active' }}>
                        ✅ Apenas Ativos
                    </option>
                    <option value="inactive" {{ 'selected' if status_filter == 'inactive' }}>
                        ⏸️ Apenas Inativos
                    </option>
                </select>
            </div>
            
            <!-- Botões Ação -->
            <div class="col-md-3">
                <div class="d-flex gap-2">
                    <button type="submit" class="btn btn-outline-primary flex-fill">
                        <i class="bi bi-funnel me-1"></i>Aplicar
                    </button>
                    <a href="{{ url_for('web.domains_list') }}" 
                       class="btn btn-outline-secondary">
                        <i class="bi bi-x-circle"></i>
                    </a>
                </div>
            </div>
        </form>
    </div>
</div>

<!-- Estatísticas Rápidas -->
{% if domains and domains.total > 0 %}
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card text-center border-primary">
            <div class="card-body">
                <i class="bi bi-globe2 text-primary fs-1 mb-2"></i>
                <h4 class="mb-1">{{ domains.total }}</h4>
                <small class="text-muted">Total Domínios</small>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center border-success">
            <div class="card-body">
                <i class="bi bi-check-circle text-success fs-1 mb-2"></i>
                <h4 class="mb-1">{{ domains.items | selectattr('is_active') | list | length }}</h4>
                <small class="text-muted">Ativos</small>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center border-info">
            <div class="card-body">
                <i class="bi bi-envelope text-info fs-1 mb-2"></i>
                <h4 class="mb-1">{{ domains.items | sum(attribute='accounts_count') }}</h4>
                <small class="text-muted">Contas Totais</small>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center border-warning">
            <div class="card-body">
                <i class="bi bi-graph-up text-warning fs-1 mb-2"></i>
                <h4 class="mb-1">{{ domains.items | sum(attribute='emails_sent_30d') }}</h4>
                <small class="text-muted">Emails 30d</small>
            </div>
        </div>
    </div>
</div>
{% endif %}

<!-- Tabela Principal de Domínios -->
<div class="card border-0 shadow-sm">
    <div class="card-header bg-white border-bottom">
        <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
                <i class="bi bi-list-ul me-2 text-secondary"></i>
                Lista de Domínios
                {% if domains and domains.total %}
                    <span class="badge bg-primary-subtle text-primary ms-2">{{ domains.total }}</span>
                {% endif %}
            </h5>
            
            {% if domains and domains.items %}
            <div class="d-flex gap-2 align-items-center">
                <!-- Bulk Actions -->
                <div class="btn-group btn-group-sm">
                    <button type="button" class="btn btn-outline-secondary dropdown-toggle" 
                            data-bs-toggle="dropdown" 
                            id="bulkActionsBtn" 
                            disabled>
                        <i class="bi bi-gear me-1"></i>Ações em Lote <span id="selectedCount">(0)</span>
                    </button>
                    <ul class="dropdown-menu">
                        <li><button class="dropdown-item" onclick="bulkActivate()">
                            <i class="bi bi-check-circle text-success me-2"></i>Ativar Selecionados
                        </button></li>
                        <li><button class="dropdown-item" onclick="bulkDeactivate()">
                            <i class="bi bi-pause-circle text-warning me-2"></i>Desativar Selecionados
                        </button></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><button class="dropdown-item text-danger" onclick="bulkDelete()">
                            <i class="bi bi-trash me-2"></i>Eliminar Selecionados
                        </button></li>
                    </ul>
                </div>
                
                <!-- Export Options -->
                <div class="btn-group btn-group-sm">
                    <button type="button" class="btn btn-outline-primary dropdown-toggle" 
                            data-bs-toggle="dropdown">
                        <i class="bi bi-download me-1"></i>Exportar
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="{{ url_for('web.domains_export', format='csv') }}">
                            <i class="bi bi-filetype-csv me-2"></i>CSV
                        </a></li>
                        <li><a class="dropdown-item" href="{{ url_for('web.domains_export', format='json') }}">
                            <i class="bi bi-filetype-json me-2"></i>JSON
                        </a></li>
                    </ul>
                </div>
            </div>
            {% endif %}
        </div>
    </div>
    
    <div class="card-body p-0">
        {% if domains and domains.items %}
        <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead class="table-light sticky-top">
                    <tr>
                        <th class="ps-4" style="width: 50px;">
                            <div class="form-check">
                                <input class="form-check-input" 
                                       type="checkbox" 
                                       id="selectAll"
                                       title="Selecionar todos">
                                <label class="form-check-label" for="selectAll"></label>
                            </div>
                        </th>
                        <th class="sortable" data-sort="name">
                            <a href="#" class="text-decoration-none text-dark">
                                Domínio <i class="bi bi-arrow-up-down ms-1 text-muted"></i>
                            </a>
                        </th>
                        <th class="text-center">Status</th>
                        <th class="text-center sortable" data-sort="accounts_count">
                            <a href="#" class="text-decoration-none text-dark">
                                Contas <i class="bi bi-arrow-up-down ms-1 text-muted"></i>
                            </a>
                        </th>
                        <th class="text-center sortable" data-sort="templates_count">
                            <a href="#" class="text-decoration-none text-dark">
                                Templates <i class="bi bi-arrow-up-down ms-1 text-muted"></i>
                            </a>
                        </th>
                        <th class="text-center sortable" data-sort="emails_sent_30d">
                            <a href="#" class="text-decoration-none text-dark">
                                Emails 30d <i class="bi bi-arrow-up-down ms-1 text-muted"></i>
                            </a>
                        </th>
                        <th class="sortable" data-sort="created_at">
                            <a href="#" class="text-decoration-none text-dark">
                                Criado <i class="bi bi-arrow-up-down ms-1 text-muted"></i>
                            </a>
                        </th>
                        <th width="140" class="text-center">Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {% for domain in domains.items %}
                    <tr class="domain-row" data-domain-id="{{ domain.id }}">
                        <!-- Checkbox Selection -->
                        <td class="ps-4">
                            <div class="form-check">
                                <input class="form-check-input domain-checkbox" 
                                       type="checkbox" 
                                       value="{{ domain.id }}"
                                       id="domain_{{ domain.id }}">
                                <label class="form-check-label" for="domain_{{ domain.id }}"></label>
                            </div>
                        </td>
                        
                        <!-- Domain Info -->
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="avatar-sm bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center me-3">
                                    <i class="bi bi-globe2"></i>
                                </div>
                                <div>
                                    <h6 class="mb-0 fw-semibold">{{ domain.name }}</h6>
                                    {% if domain.description %}
                                        <small class="text-muted">{{ domain.description }}</small>
                                    {% else %}
                                        <small class="text-muted fst-italic">Sem descrição</small>
                                    {% endif %}
                                </div>
                            </div>
                        </td>
                        
                        <!-- Status -->
                        <td class="text-center">
                            {% if domain.is_active %}
                                <span class="badge rounded-pill bg-success-subtle text-success border border-success-subtle">
                                    <i class="bi bi-check-circle-fill me-1"></i>Ativo
                                </span>
                            {% else %}
                                <span class="badge rounded-pill bg-secondary-subtle text-secondary border border-secondary-subtle">
                                    <i class="bi bi-pause-circle-fill me-1"></i>Inativo
                                </span>
                            {% endif %}
                        </td>
                        
                        <!-- Accounts Count -->
                        <td class="text-center">
                            {% if domain.accounts_count > 0 %}
                                <span class="badge bg-info-subtle text-info fw-semibold">
                                    {{ domain.accounts_count }}
                                </span>
                                <br><small class="text-muted">contas</small>
                            {% else %}
                                <span class="text-muted">—</span>
                            {% endif %}
                        </td>
                        
                        <!-- Templates Count -->
                        <td class="text-center">
                            {% if domain.templates_count > 0 %}
                                <span class="badge bg-primary-subtle text-primary fw-semibold">
                                    {{ domain.templates_count }}
                                </span>
                                <br><small class="text-muted">templates</small>
                            {% else %}
                                <span class="text-muted">—</span>
                            {% endif %}
                        </td>
                        
                        <!-- Emails Sent -->
                        <td class="text-center">
                            {% if domain.emails_sent_30d > 0 %}
                                <span class="badge bg-success-subtle text-success fw-semibold">
                                    {{ domain.emails_sent_30d }}
                                </span>
                                <br><small class="text-muted">enviados</small>
                            {% else %}
                                <span class="text-muted">0</span>
                            {% endif %}
                        </td>
                        
                        <!-- Created Date -->
                        <td>
                            <small class="text-muted">
                                <i class="bi bi-calendar3 me-1"></i>
                                {{ domain.created_at.strftime('%d/%m/%Y') }}
                                <br>
                                <span class="text-muted opacity-75">
                                    {{ domain.created_at.strftime('%H:%M') }}
                                </span>
                            </small>
                        </td>
                        
                        <!-- Actions -->
                        <td class="text-center">
                            <div class="btn-group btn-group-sm">
                                <!-- Editar -->
                                <a href="{{ url_for('web.domains_edit', domain_id=domain.id) }}" 
                                   class="btn btn-outline-primary btn-sm"
                                   data-bs-toggle="tooltip"
                                   title="Editar domínio">
                                    <i class="bi bi-pencil"></i>
                                </a>
                                
                                <!-- Toggle Status -->
                                <button class="btn btn-outline-{{ 'warning' if domain.is_active else 'success' }} btn-sm"
                                        onclick="toggleDomainStatus({{ domain.id }}, {{ domain.is_active|lower }})"
                                        data-bs-toggle="tooltip"
                                        title="{{ 'Desativar' if domain.is_active else 'Ativar' }} domínio">
                                    <i class="bi bi-{{ 'pause' if domain.is_active else 'play' }}-fill"></i>
                                </button>
                                
                                <!-- View Details -->
                                <a href="{{ url_for('web.accounts_list', domain=domain.name) }}"
                                   class="btn btn-outline-info btn-sm"
                                   data-bs-toggle="tooltip"
                                   title="Ver contas do domínio">
                                    <i class="bi bi-envelope"></i>
                                </a>
                                
                                <!-- Delete -->
                                <button class="btn btn-outline-danger btn-sm"
                                        onclick="confirmDelete({{ domain.id }}, '{{ domain.name }}')"
                                        data-bs-toggle="tooltip"
                                        title="Eliminar domínio">
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
        {% if domains.pages > 1 %}
        <div class="card-footer bg-white border-top">
            <div class="row align-items-center">
                <div class="col">
                    <small class="text-muted">
                        Mostrando 
                        <strong>{{ ((domains.page - 1) * domains.per_page) + 1 }}</strong> a 
                        <strong>{{ domains.page * domains.per_page if domains.page * domains.per_page < domains.total else domains.total }}</strong> 
                        de <strong>{{ domains.total }}</strong> domínios
                    </small>
                </div>
                <div class="col-auto">
                    <nav aria-label="Navegação de páginas">
                        <ul class="pagination pagination-sm mb-0">
                            <!-- Previous -->
                            {% if domains.has_prev %}
                                <li class="page-item">
                                    <a class="page-link" 
                                       href="{{ url_for('web.domains_list', page=domains.prev_num, search=search, status=status_filter) }}"
                                       aria-label="Página anterior">
                                        <i class="bi bi-chevron-left"></i>
                                    </a>
                                </li>
                            {% else %}
                                <li class="page-item disabled">
                                    <span class="page-link"><i class="bi bi-chevron-left"></i></span>
                                </li>
                            {% endif %}
                            
                            <!-- Page Numbers -->
                            {% for page_num in domains.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2) %}
                                {% if page_num %}
                                    {% if page_num != domains.page %}
                                        <li class="page-item">
                                            <a class="page-link" 
                                               href="{{ url_for('web.domains_list', page=page_num, search=search, status=status_filter) }}">
                                                {{ page_num }}
                                            </a>
                                        </li>
                                    {% else %}
                                        <li class="page-item active" aria-current="page">
                                            <span class="page-link">
                                                {{ page_num }}
                                                <span class="visually-hidden">(atual)</span>
                                            </span>
                                        </li>
                                    {% endif %}
                                {% else %}
                                    <li class="page-item disabled">
                                        <span class="page-link">…</span>
                                    </li>
                                {% endif %}
                            {% endfor %}
                            
                            <!-- Next -->
                            {% if domains.has_next %}
                                <li class="page-item">
                                    <a class="page-link" 
                                       href="{{ url_for('web.domains_list', page=domains.next_num, search=search, status=status_filter) }}"
                                       aria-label="Próxima página">
                                        <i class="bi bi-chevron-right"></i>
                                    </a>
                                </li>
                            {% else %}
                                <li class="page-item disabled">
                                    <span class="page-link"><i class="bi bi-chevron-right"></i></span>
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
                <i class="bi bi-globe text-muted" style="font-size: 5rem; opacity: 0.3;"></i>
            </div>
            
            {% if search or status_filter %}
                <!-- Nenhum resultado para filtros -->
                <h4 class="text-muted mb-3">Nenhum Domínio Encontrado</h4>
                <p class="text-muted mb-4">
                    Não foram encontrados domínios que correspondam aos seus critérios de pesquisa.
                    <br>Experimente ajustar os filtros ou limpar a pesquisa.
                </p>
                <div class="d-flex gap-2 justify-content-center">
                    <a href="{{ url_for('web.domains_list') }}" class="btn btn-outline-secondary">
                        <i class="bi bi-arrow-clockwise me-1"></i>Limpar Filtros
                    </a>
                    <a href="{{ url_for('web.domains_new') }}" class="btn btn-primary">
                        <i class="bi bi-plus-circle me-1"></i>Novo Domínio
                    </a>
                </div>
            {% else %}
                <!-- Primeira vez / sem domínios -->
                <h4 class="text-muted mb-3">Nenhum Domínio Configurado</h4>
                <p class="text-muted mb-4">
                    Configure seu primeiro domínio para começar a enviar emails.
                    <br>Domínios servem para organizar e agrupar as suas contas de email.
                </p>
                <div class="card mx-auto" style="max-width: 400px;">
                    <div class="card-body text-center">
                        <h6 class="card-title">Como Começar:</h6>
                        <ol class="list-unstyled text-muted small text-start">
                            <li class="mb-2">
                                <i class="bi bi-1-circle text-primary me-2"></i>
                                Criar um domínio (ex: alitools.pt)
                            </li>
                            <li class="mb-2">
                                <i class="bi bi-2-circle text-primary me-2"></i>
                                Configurar contas de email
                            </li>
                            <li class="mb-2">
                                <i class="bi bi-3-circle text-primary me-2"></i>
                                Criar templates personalizados
                            </li>
                            <li>
                                <i class="bi bi-4-circle text-primary me-2"></i>
                                Começar a enviar emails!
                            </li>
                        </ol>
                    </div>
                </div>
                
                <div class="mt-4">
                    <a href="{{ url_for('web.domains_new') }}" class="btn btn-primary btn-lg">
                        <i class="bi bi-plus-circle me-2"></i>
                        Criar Primeiro Domínio
                    </a>
                </div>
            {% endif %}
        </div>
        {% endif %}
    </div>
</div>

<!-- Modals -->

<!-- Modal Confirmação Eliminação -->
<div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header border-bottom-0">
                <h5 class="modal-title" id="deleteModalLabel">
                    <i class="bi bi-exclamation-triangle text-warning me-2"></i>
                    Confirmar Eliminação
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
            </div>
            <div class="modal-body">
                <div class="text-center mb-3">
                    <i class="bi bi-globe text-danger" style="font-size: 3rem;"></i>
                </div>
                <p class="text-center mb-3">
                    Tem certeza que deseja eliminar o domínio 
                    <strong id="deleteDomainName" class="text-danger"></strong>?
                </p>
                
                <div class="alert alert-warning" role="alert">
                    <div class="d-flex">
                        <i class="bi bi-exclamation-triangle-fill me-2 mt-1"></i>
                        <div>
                            <strong>Atenção!</strong> Esta ação irá eliminar:
                            <ul class="mb-0 mt-2">
                                <li>Todas as contas de email associadas</li>
                                <li>Todos os templates do domínio</li> 
                                <li>Histórico de logs de email</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <p class="text-muted text-center small mb-0">
                    <i class="bi bi-info-circle me-1"></i>
                    Esta operação não pode ser desfeita.
                </p>
            </div>
            <div class="modal-footer border-top-0">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    <i class="bi bi-x-circle me-1"></i>Cancelar
                </button>
                <form id="deleteForm" method="POST" style="display: inline;">
                    <button type="submit" class="btn btn-danger">
                        <i class="bi bi-trash me-1"></i>Eliminar Definitivamente
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

<!-- Modal Bulk Actions -->
<div class="modal fade" id="bulkModal" tabindex="-1" aria-labelledby="bulkModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="bulkModalLabel">Ações em Lote</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p>Executar ação <strong id="bulkAction"></strong> em <strong id="bulkCount"></strong> domínios selecionados?</p>
                <ul id="bulkDomainsList" class="list-unstyled"></ul>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <button type="button" id="bulkConfirmBtn" class="btn btn-primary">Confirmar</button>
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
    setupCheckboxes();
    setupTableSorting();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ===== CHECKBOX FUNCTIONALITY =====
function setupCheckboxes() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const domainCheckboxes = document.querySelectorAll('.domain-checkbox');
    const bulkActionsBtn = document.getElementById('bulkActionsBtn');
    const selectedCount = document.getElementById('selectedCount');

    // Select All functionality
    selectAllCheckbox?.addEventListener('change', function() {
        domainCheckboxes.forEach(checkbox => {
            checkbox.checked = this.checked;
        });
        updateBulkActions();
    });

    // Individual checkbox change
    domainCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectAllState();
            updateBulkActions();
        });
    });

    function updateSelectAllState() {
        const checkedCount = document.querySelectorAll('.domain-checkbox:checked').length;
        const totalCount = domainCheckboxes.length;
        
        if (checkedCount === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (checkedCount === totalCount) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        }
    }

    function updateBulkActions() {
        const checkedCount = document.querySelectorAll('.domain-checkbox:checked').length;
        
        if (checkedCount > 0) {
            bulkActionsBtn.disabled = false;
            selectedCount.textContent = `(${checkedCount})`;
        } else {
            bulkActionsBtn.disabled = true;
            selectedCount.textContent = '(0)';
        }
    }
}

// ===== CRUD OPERATIONS =====

// Delete confirmation
function confirmDelete(domainId, domainName) {
    document.getElementById('deleteDomainName').textContent = domainName;
    document.getElementById('deleteForm').action = `/domains/${domainId}/delete`;
    
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
}

// Toggle domain status
async function toggleDomainStatus(domainId, isActive) {
    const button = document.querySelector(`[onclick*="toggleDomainStatus(${domainId}"]`);
    const originalContent = button.innerHTML;
    
    // Loading state
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
    
    try {
        const response = await fetch(`/api/domains/${domainId}/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Reload page to show updated status
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

// ===== BULK OPERATIONS =====
function bulkActivate() {
    executeBulkAction('activate', 'ativar');
}

function bulkDeactivate() {
    executeBulkAction('deactivate', 'desativar');
}

function bulkDelete() {
    executeBulkAction('delete', 'eliminar');
}

function executeBulkAction(action, actionText) {
    const selectedIds = Array.from(document.querySelectorAll('.domain-checkbox:checked'))
                            .map(cb => cb.value);
    
    if (selectedIds.length === 0) {
        showToast('Nenhum domínio selecionado', 'warning');
        return;
    }
    
    // Show confirmation modal
    document.getElementById('bulkAction').textContent = actionText;
    document.getElementById('bulkCount').textContent = selectedIds.length;
    
    const domainsList = document.getElementById('bulkDomainsList');
    domainsList.innerHTML = '';
    
    selectedIds.forEach(id => {
        const row = document.querySelector(`tr[data-domain-id="${id}"]`);
        const domainName = row.querySelector('h6').textContent;
        const li = document.createElement('li');
        li.innerHTML = `<i class="bi bi-globe2 me-2"></i>${domainName}`;
        domainsList.appendChild(li);
    });
    
    const confirmBtn = document.getElementById('bulkConfirmBtn');
    confirmBtn.onclick = () => performBulkAction(action, selectedIds);
    
    const modal = new bootstrap.Modal(document.getElementById('bulkModal'));
    modal.show();
}

async function performBulkAction(action, selectedIds) {
    const modal = bootstrap.Modal.getInstance(document.getElementById('bulkModal'));
    modal.hide();
    
    // Show loading
    showToast(`Executando ação em ${selectedIds.length} domínios...`, 'info');
    
    try {
        const response = await fetch('/api/domains/bulk', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                action: action,
                domain_ids: selectedIds
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(`${result.affected} domínios processados com sucesso`, 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        showToast(`Erro na operação em lote: ${error.message}`, 'danger');
    }
}

// ===== TABLE SORTING =====
function setupTableSorting() {
    document.querySelectorAll('.sortable').forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function(e) {
            e.preventDefault();
            const sortField = this.dataset.sort;
            const currentUrl = new URL(window.location);
            const currentSort = currentUrl.searchParams.get('sort');
            const currentOrder = currentUrl.searchParams.get('order');
            
            let newOrder = 'asc';
            if (currentSort === sortField && currentOrder === 'asc') {
                newOrder = 'desc';
            }
            
            currentUrl.searchParams.set('sort', sortField);
            currentUrl.searchParams.set('order', newOrder);
            
            window.location.href = currentUrl.toString();
        });
    });
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

// Auto-refresh data (every 2 minutes)
setInterval(() => {
    if (!document.querySelector('.modal.show')) {
        // Only refresh if no modals are open
        location.reload();
    }
}, 120000);
</script>
{% endblock %}
```