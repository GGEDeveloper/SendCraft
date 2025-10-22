# 🚀 SendCraft - Fase 5: Completar Interface Web Administrativa

## 📊 **ESTADO ATUAL (DESCOBERTA CRÍTICA)**

### ✅ **Interface Web 80% COMPLETA (Descoberta Incrível!)**
Após análise do repositório GitHub descobrimos que o SendCraft já tem uma interface web moderna praticamente completa:

#### **Base Sólida Existente:**
```
✅ templates/base.html - Layout Bootstrap 5 perfeito
✅ templates/dashboard.html - Dashboard KPIs funcional  
✅ static/css/app.css - Estilos SendCraft integrados
✅ static/js/app.js - JavaScript base implementado
✅ Bootstrap 5.3.2 + HTMX + Chart.js configurados
✅ Navegação completa (Dashboard, Domínios, Contas, Templates, Logs)
✅ Design system enterprise (cores AliTools integradas)
✅ Responsive mobile-first
✅ Toast notifications system
✅ Flash messages handling
```

### ❌ **Gap Crítico Identificado (20% Faltante):**
```
❌ sendcraft/routes/web.py - Flask web routes NÃO IMPLEMENTADAS
❌ templates/domains/list.html - CRUD domínios falta
❌ templates/accounts/list.html - CRUD contas falta
❌ templates/templates/editor.html - Editor templates falta
❌ JavaScript avançado - CRUD operations limitadas
```

---

## 🎯 **OBJETIVOS FASE 5**

### **Objetivo Principal**
Completar os 20% restantes da interface web para tornar SendCraft uma plataforma administrativa enterprise completa.

### **Objetivos Específicos**
1. **Implementar Flask web routes** - Conectar navegação existente
2. **Criar templates CRUD específicos** - Domínios, contas, templates  
3. **Expandir JavaScript avançado** - HTMX operations, validações
4. **Integrar com APIs existentes** - Conectar frontend com backend
5. **Testar interface completa** - Garantir funcionamento end-to-end

---

## 🏗️ **ARQUITETURA TÉCNICA**

### **Stack Confirmado (Perfeito!)**
```
Frontend:
├── Bootstrap 5.3.2 (responsive, components)
├── HTMX 1.9.6 (AJAX sem JavaScript complexo)  
├── Chart.js (dashboards e gráficos)
├── Bootstrap Icons (iconografia consistente)
├── Alpine.js (adicionar para reactivity)
└── CSS Custom (SendCraft branding Orange #FFA500)

Backend:
├── Flask Templates (Jinja2) - base.html perfeito
├── Flask Blueprints (web routes a implementar)
├── Services Layer (já existente)
├── REST APIs (100% funcionais)
└── MySQL Models (Domain, EmailAccount, EmailTemplate, EmailLog)
```

### **Estrutura de Ficheiros a Criar**
```
sendcraft/
├── routes/
│   └── web.py                 # ❌ CRIAR - Flask web routes
├── templates/
│   ├── base.html              # ✅ PERFEITO - não tocar
│   ├── dashboard.html         # ✅ FUNCIONAL - minor tweaks
│   ├── domains/
│   │   ├── list.html          # ❌ CRIAR - Lista domínios
│   │   └── form.html          # ❌ CRIAR - CRUD domínios
│   ├── accounts/
│   │   ├── list.html          # ❌ CRIAR - Lista contas
│   │   └── form.html          # ❌ CRIAR - CRUD contas
│   ├── templates/
│   │   ├── list.html          # ❌ CRIAR - Lista templates
│   │   └── editor.html        # ❌ CRIAR - Editor HTML
│   └── logs/
│       └── list.html          # ❌ CRIAR - Interface logs
└── static/
    ├── css/
    │   └── app.css            # ✅ EXPANDIR - adicionar componentes
    └── js/
        └── app.js             # ✅ EXPANDIR - CRUD operations
```

---

## 📋 **IMPLEMENTAÇÃO DETALHADA**

### **TASK 5.1: Flask Web Routes (CRÍTICO - 1.5h)**

#### **Criar sendcraft/routes/web.py:**
```python
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from sendcraft.services import (
    domains_service, accounts_service, templates_service, 
    stats_service, logs_service
)
from sendcraft.decorators import auth_required
from sendcraft.models import Domain, EmailAccount, EmailTemplate

web_bp = Blueprint('web', __name__)

# DASHBOARD - usar template existente
@web_bp.route('/')
@auth_required
def dashboard():
    stats = stats_service.get_global_stats()
    recent_logs = logs_service.get_recent_logs(limit=10)
    domains = domains_service.get_active_domains_with_stats()
    email_stats = stats_service.get_email_stats_24h()
    
    return render_template('dashboard.html',
                         stats=stats,
                         recent_logs=recent_logs,
                         domains=domains,
                         email_stats=email_stats)

# DOMAINS ROUTES
@web_bp.route('/domains')
@auth_required
def domains_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    domains = domains_service.get_paginated_domains(
        page=page, 
        per_page=20, 
        search=search
    )
    
    return render_template('domains/list.html', 
                         domains=domains, 
                         search=search)

@web_bp.route('/domains/new', methods=['GET', 'POST'])
@auth_required
def domains_new():
    if request.method == 'POST':
        try:
            domain_data = {
                'name': request.form.get('name'),
                'description': request.form.get('description'),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            domain = domains_service.create_domain(domain_data)
            flash(f'Domínio {domain.name} criado com sucesso!', 'success')
            return redirect(url_for('web.domains_list'))
            
        except Exception as e:
            flash(f'Erro ao criar domínio: {str(e)}', 'error')
    
    return render_template('domains/form.html', domain=None)

@web_bp.route('/domains/<int:domain_id>/edit', methods=['GET', 'POST'])
@auth_required
def domains_edit(domain_id):
    domain = domains_service.get_domain_by_id(domain_id)
    if not domain:
        flash('Domínio não encontrado', 'error')
        return redirect(url_for('web.domains_list'))
    
    if request.method == 'POST':
        try:
            domain_data = {
                'name': request.form.get('name'),
                'description': request.form.get('description'),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            domains_service.update_domain(domain_id, domain_data)
            flash(f'Domínio {domain.name} atualizado com sucesso!', 'success')
            return redirect(url_for('web.domains_list'))
            
        except Exception as e:
            flash(f'Erro ao atualizar domínio: {str(e)}', 'error')
    
    return render_template('domains/form.html', domain=domain)

@web_bp.route('/domains/<int:domain_id>/delete', methods=['POST'])
@auth_required
def domains_delete(domain_id):
    try:
        domain = domains_service.get_domain_by_id(domain_id)
        if domain:
            domains_service.delete_domain(domain_id)
            flash(f'Domínio {domain.name} eliminado com sucesso!', 'success')
        else:
            flash('Domínio não encontrado', 'error')
    except Exception as e:
        flash(f'Erro ao eliminar domínio: {str(e)}', 'error')
    
    return redirect(url_for('web.domains_list'))

# ACCOUNTS ROUTES
@web_bp.route('/accounts')
@auth_required
def accounts_list():
    domain_filter = request.args.get('domain')
    page = request.args.get('page', 1, type=int)
    
    accounts = accounts_service.get_paginated_accounts(
        page=page,
        per_page=20,
        domain_filter=domain_filter
    )
    
    domains = domains_service.get_all_domains()
    
    return render_template('accounts/list.html',
                         accounts=accounts,
                         domains=domains,
                         domain_filter=domain_filter)

# ... mais rotas para accounts, templates, logs
```

#### **Integrar no __init__.py:**
```python
# sendcraft/__init__.py - adicionar:
from sendcraft.routes.web import web_bp

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # ... configuração existente ...
    
    # Registrar blueprints
    from sendcraft.api.v1 import api_v1_bp
    from sendcraft.routes.web import web_bp  # NOVO
    
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    app.register_blueprint(web_bp)  # NOVO - sem prefix para web interface
    
    return app
```

### **TASK 5.2: Templates CRUD (1.5h)**

#### **templates/domains/list.html (Completo):**
```html
{% extends "base.html" %}
{% block title %}Domínios - SendCraft{% endblock %}

{% block content %}
<!-- Header com Breadcrumb -->
<div class="row mb-4">
    <div class="col">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="{{ url_for('web.dashboard') }}">Dashboard</a></li>
                <li class="breadcrumb-item active">Domínios</li>
            </ol>
        </nav>
        
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <h1 class="h2">
                    <i class="bi bi-globe2 me-2 text-primary"></i>
                    Gestão de Domínios
                </h1>
                <p class="text-muted">Configure e gerencie domínios para envio de emails</p>
            </div>
            <div>
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
    <div class="card-body">
        <form method="GET" class="row g-3 align-items-center">
            <div class="col-md-6">
                <div class="input-group">
                    <span class="input-group-text bg-light border-end-0">
                        <i class="bi bi-search text-muted"></i>
                    </span>
                    <input type="text" 
                           name="search" 
                           class="form-control border-start-0" 
                           value="{{ search }}" 
                           placeholder="Procurar por nome do domínio...">
                </div>
            </div>
            <div class="col-md-3">
                <select name="status" class="form-select">
                    <option value="">Todos os status</option>
                    <option value="active" {{ 'selected' if request.args.get('status') == 'active' }}>Ativos</option>
                    <option value="inactive" {{ 'selected' if request.args.get('status') == 'inactive' }}>Inativos</option>
                </select>
            </div>
            <div class="col-md-3">
                <div class="btn-group w-100">
                    <button type="submit" class="btn btn-outline-primary">
                        <i class="bi bi-funnel me-1"></i>Filtrar
                    </button>
                    <a href="{{ url_for('web.domains_list') }}" class="btn btn-outline-secondary">
                        <i class="bi bi-arrow-clockwise"></i>
                    </a>
                </div>
            </div>
        </form>
    </div>
</div>

<!-- Tabela de Domínios -->
<div class="card border-0 shadow-sm">
    <div class="card-header bg-white border-bottom">
        <h5 class="mb-0">
            <i class="bi bi-list-ul me-2"></i>
            Domínios Configurados
            {% if domains.total %}
                <span class="badge bg-primary ms-2">{{ domains.total }}</span>
            {% endif %}
        </h5>
    </div>
    
    <div class="card-body p-0">
        {% if domains.items %}
        <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead class="table-light">
                    <tr>
                        <th class="ps-4">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="selectAll">
                            </div>
                        </th>
                        <th>Domínio</th>
                        <th>Status</th>
                        <th class="text-center">Contas</th>
                        <th class="text-center">Templates</th>
                        <th class="text-center">Emails 30d</th>
                        <th>Criado</th>
                        <th width="120" class="text-center">Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {% for domain in domains.items %}
                    <tr>
                        <td class="ps-4">
                            <div class="form-check">
                                <input class="form-check-input domain-checkbox" 
                                       type="checkbox" 
                                       value="{{ domain.id }}">
                            </div>
                        </td>
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="avatar-sm bg-primary-subtle rounded me-3">
                                    <i class="bi bi-globe2 text-primary"></i>
                                </div>
                                <div>
                                    <h6 class="mb-1">{{ domain.name }}</h6>
                                    {% if domain.description %}
                                        <small class="text-muted">{{ domain.description }}</small>
                                    {% else %}
                                        <small class="text-muted fst-italic">Sem descrição</small>
                                    {% endif %}
                                </div>
                            </div>
                        </td>
                        <td>
                            {% if domain.is_active %}
                                <span class="badge rounded-pill bg-success-subtle text-success">
                                    <i class="bi bi-check-circle-fill me-1"></i>Ativo
                                </span>
                            {% else %}
                                <span class="badge rounded-pill bg-secondary-subtle text-secondary">
                                    <i class="bi bi-pause-circle-fill me-1"></i>Inativo
                                </span>
                            {% endif %}
                        </td>
                        <td class="text-center">
                            <span class="badge bg-info-subtle text-info">
                                {{ domain.accounts_count or 0 }}
                            </span>
                        </td>
                        <td class="text-center">
                            <span class="badge bg-primary-subtle text-primary">
                                {{ domain.templates_count or 0 }}
                            </span>
                        </td>
                        <td class="text-center">
                            <span class="badge bg-success-subtle text-success">
                                {{ domain.emails_sent_30d or 0 }}
                            </span>
                        </td>
                        <td>
                            <small class="text-muted">
                                {{ domain.created_at.strftime('%d/%m/%Y') }}
                            </small>
                        </td>
                        <td>
                            <div class="btn-group btn-group-sm">
                                <a href="{{ url_for('web.domains_edit', domain_id=domain.id) }}" 
                                   class="btn btn-outline-primary btn-sm"
                                   data-bs-toggle="tooltip"
                                   title="Editar">
                                    <i class="bi bi-pencil"></i>
                                </a>
                                
                                <button class="btn btn-outline-{{ 'warning' if domain.is_active else 'success' }} btn-sm"
                                        onclick="toggleDomainStatus({{ domain.id }}, {{ domain.is_active|lower }})"
                                        data-bs-toggle="tooltip"
                                        title="{{ 'Desativar' if domain.is_active else 'Ativar' }}">
                                    <i class="bi bi-{{ 'pause' if domain.is_active else 'play' }}"></i>
                                </button>
                                
                                <button class="btn btn-outline-danger btn-sm"
                                        onclick="confirmDelete({{ domain.id }}, '{{ domain.name }}')"
                                        data-bs-toggle="tooltip"
                                        title="Eliminar">
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
                        Mostrando {{ ((domains.page - 1) * domains.per_page) + 1 }} a 
                        {{ domains.page * domains.per_page if domains.page * domains.per_page < domains.total else domains.total }} 
                        de {{ domains.total }} domínios
                    </small>
                </div>
                <div class="col-auto">
                    <nav aria-label="Navegação de domínios">
                        <ul class="pagination pagination-sm mb-0">
                            {% for page_num in domains.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2) %}
                                {% if page_num %}
                                    {% if page_num != domains.page %}
                                        <li class="page-item">
                                            <a class="page-link" 
                                               href="{{ url_for('web.domains_list', page=page_num, search=search) }}">
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
                <i class="bi bi-globe text-muted" style="font-size: 4rem; opacity: 0.5;"></i>
            </div>
            <h4 class="text-muted">Nenhum Domínio Encontrado</h4>
            {% if search %}
                <p class="text-muted mb-4">
                    Não foram encontrados domínios para "<strong>{{ search }}</strong>".
                    <br>Tente ajustar os filtros de pesquisa.
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
                <p class="text-muted mb-4">
                    Configure seu primeiro domínio para começar a enviar emails.
                    <br>Domínios são necessários para organizar contas de email.
                </p>
                <a href="{{ url_for('web.domains_new') }}" class="btn btn-primary btn-lg">
                    <i class="bi bi-plus-circle me-2"></i>
                    Criar Primeiro Domínio
                </a>
            {% endif %}
        </div>
        {% endif %}
    </div>
</div>

<!-- Modal de Confirmação de Eliminação -->
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
                <p class="mb-3">
                    Tem certeza que deseja eliminar o domínio <strong id="deleteDomainName" class="text-danger"></strong>?
                </p>
                <div class="alert alert-warning" role="alert">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    <strong>Atenção:</strong> Esta ação eliminará também todas as contas de email 
                    e templates associados a este domínio. Esta operação não pode ser desfeita.
                </div>
            </div>
            <div class="modal-footer border-top-0">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    <i class="bi bi-x-circle me-1"></i>Cancelar
                </button>
                <form id="deleteForm" method="POST" style="display: inline;">
                    <button type="submit" class="btn btn-danger">
                        <i class="bi bi-trash me-1"></i>Eliminar Domínio
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
// Inicialização de tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});

// Seleção múltipla
document.getElementById('selectAll').addEventListener('change', function() {
    const checkboxes = document.querySelectorAll('.domain-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = this.checked;
    });
});

// Confirmação de eliminação
function confirmDelete(domainId, domainName) {
    document.getElementById('deleteDomainName').textContent = domainName;
    document.getElementById('deleteForm').action = `/domains/${domainId}/delete`;
    
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
}

// Toggle status do domínio
async function toggleDomainStatus(domainId, isActive) {
    const action = isActive ? 'deactivate' : 'activate';
    
    try {
        const response = await fetch(`/api/v1/domains/${domainId}/${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + getApiToken() // implementar
            }
        });
        
        if (response.ok) {
            location.reload();
        } else {
            showToast('Erro ao alterar status do domínio', 'error');
        }
    } catch (error) {
        showToast('Erro de conexão', 'error');
    }
}

// Função para mostrar toast (usar sistema existente)
function showToast(message, type = 'success') {
    // Implementação já existente no app.js base
    const toastHtml = `
        <div class="toast align-items-center text-bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    const container = document.getElementById('toast-container');
    container.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = container.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}
</script>
{% endblock %}
```

### **TASK 5.3: JavaScript Avançado (1h)**

#### **Expandir static/js/app.js:**
```javascript
// ADICIONAR ao app.js existente:

// ===== CRUD OPERATIONS VIA HTMX =====
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips Bootstrap
    initializeTooltips();
    
    // Setup HTMX error handling
    setupHTMXErrorHandling();
    
    // Setup form validations
    setupFormValidations();
    
    // Real-time updates
    if (document.getElementById('emailChart')) {
        setupRealTimeUpdates();
    }
});

// Inicializar tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// HTMX Error Handling
function setupHTMXErrorHandling() {
    // Global error handler
    document.addEventListener('htmx:responseError', function(event) {
        console.error('HTMX Error:', event.detail);
        showToast('Erro na operação. Tente novamente.', 'danger');
    });
    
    // Loading states
    document.addEventListener('htmx:beforeRequest', function(event) {
        const button = event.detail.elt;
        if (button.tagName === 'BUTTON') {
            button.disabled = true;
            const originalText = button.innerHTML;
            button.dataset.originalText = originalText;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Carregando...';
        }
    });
    
    document.addEventListener('htmx:afterRequest', function(event) {
        const button = event.detail.elt;
        if (button.tagName === 'BUTTON' && button.dataset.originalText) {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText;
            delete button.dataset.originalText;
        }
        
        // Handle success responses
        if (event.detail.successful && event.detail.xhr.status === 200) {
            try {
                const response = JSON.parse(event.detail.xhr.response);
                if (response.message) {
                    showToast(response.message, response.type || 'success');
                }
            } catch (e) {
                // Response não é JSON, ignorar
            }
        }
    });
}

// Toast Notification System (melhorado)
function showToast(message, type = 'success', duration = 5000) {
    const iconMap = {
        'success': 'bi-check-circle',
        'danger': 'bi-x-circle',
        'warning': 'bi-exclamation-triangle',
        'info': 'bi-info-circle'
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
    
    // Auto-remove após hide
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// Form Validation System
function setupFormValidations() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(this)) {
                event.preventDefault();
                showToast('Por favor corrija os erros no formulário', 'warning');
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
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
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Email inválido';
        }
    }
    
    // Domain validation
    if (field.name === 'name' && field.closest('form').id === 'domainForm') {
        const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$/;
        if (value && !domainRegex.test(value)) {
            isValid = false;
            errorMessage = 'Formato de domínio inválido';
        }
    }
    
    // Update UI
    const feedbackElement = field.nextElementSibling;
    
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
            feedbackElement.style.display = 'none';
        }
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        
        if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
            feedbackElement.textContent = errorMessage;
            feedbackElement.style.display = 'block';
        } else {
            // Create feedback element
            const feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.textContent = errorMessage;
            field.parentNode.insertBefore(feedback, field.nextSibling);
        }
    }
    
    return isValid;
}

// SMTP Testing (para accounts)
async function testSMTPConnection(accountId) {
    const button = document.querySelector(`[data-smtp-test="${accountId}"]`);
    if (!button) return;
    
    const originalContent = button.innerHTML;
    const originalClass = button.className;
    
    // Loading state
    button.disabled = true;
    button.className = 'btn btn-outline-secondary btn-sm';
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Testando...';
    
    try {
        const response = await fetch(`/api/v1/accounts/${accountId}/test-smtp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + getApiToken()
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('✅ Conexão SMTP bem-sucedida!', 'success');
            button.className = 'btn btn-outline-success btn-sm';
            button.innerHTML = '<i class="bi bi-check-circle"></i>';
            
            // Update status indicator
            const statusBadge = document.querySelector(`[data-smtp-status="${accountId}"]`);
            if (statusBadge) {
                statusBadge.className = 'badge bg-success-subtle text-success';
                statusBadge.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i>Conectado';
            }
        } else {
            showToast(`❌ Erro SMTP: ${result.error}`, 'danger');
            button.className = 'btn btn-outline-danger btn-sm';
            button.innerHTML = '<i class="bi bi-x-circle"></i>';
            
            // Update status indicator  
            const statusBadge = document.querySelector(`[data-smtp-status="${accountId}"]`);
            if (statusBadge) {
                statusBadge.className = 'badge bg-danger-subtle text-danger';
                statusBadge.innerHTML = '<i class="bi bi-x-circle-fill me-1"></i>Erro';
            }
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
            button.className = originalClass;
            button.innerHTML = originalContent;
        }, 3000);
    }
}

// Real-time Updates (dashboard)
function setupRealTimeUpdates() {
    // Update dashboard every 30 seconds
    setInterval(updateDashboardStats, 30000);
    
    // Update charts every 2 minutes
    setInterval(updateCharts, 120000);
}

async function updateDashboardStats() {
    try {
        const response = await fetch('/api/v1/stats/global');
        const stats = await response.json();
        
        // Update KPI cards
        updateKPICard('active-domains', stats.system.active_domains);
        updateKPICard('active-accounts', stats.system.active_accounts);
        updateKPICard('emails-today', stats.emails_today);
        updateKPICard('success-rate', `${stats.success_rate}%`);
        
    } catch (error) {
        console.error('Error updating dashboard stats:', error);
    }
}

function updateKPICard(cardId, value) {
    const card = document.querySelector(`[data-kpi="${cardId}"]`);
    if (card) {
        const valueElement = card.querySelector('.kpi-value');
        if (valueElement) {
            // Animate value change
            valueElement.style.transform = 'scale(1.1)';
            valueElement.textContent = value;
            
            setTimeout(() => {
                valueElement.style.transform = 'scale(1)';
            }, 200);
        }
    }
}

// API Token Management (implementar conforme auth system)
function getApiToken() {
    // TODO: Implementar conforme sistema de autenticação
    return localStorage.getItem('sendcraft_token') || 'default_token';
}

// Utility functions
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('pt-PT');
}

function formatDateTime(dateString) {
    return new Date(dateString).toLocaleString('pt-PT');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copiado para a área de transferência', 'success', 2000);
    }).catch(() => {
        showToast('Erro ao copiar', 'danger', 2000);
    });
}

// Export for global use
window.SendCraft = {
    showToast,
    testSMTPConnection,
    copyToClipboard,
    formatDate,
    formatDateTime
};
```

---

## ⏱️ **CRONOGRAMA DE EXECUÇÃO**

### **Dia 1: Core Implementation (3h)**
- **09:00-10:30**: TASK 5.1 - Flask web routes (1.5h)
- **10:45-12:15**: TASK 5.2 - Templates domains (1.5h)

### **Dia 1: Testing & Polish (1h)**  
- **14:00-15:00**: TASK 5.3 - JavaScript avançado + testing

**Total Fase 5**: 4 horas