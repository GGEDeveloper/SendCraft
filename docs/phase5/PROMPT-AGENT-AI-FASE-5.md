# 🚀 PROMPT COMPLETO - Agent AI Flask Expert - SendCraft Interface Fase 5

## 🎯 **MISSÃO PRINCIPAL**

Tu és um **Flask Full-Stack Expert** especializado em interfaces administrativas enterprise. A tua missão é **completar a interface web do SendCraft** implementando as rotas Flask e templates CRUD que faltam.

---

## ⚠️ **CONTEXTO CRÍTICO**

### **DESCOBERTA**: Interface 80% Já Implementada!
Após análise do repositório GitHub `https://github.com/GGEDeveloper/SendCraft`, descobrimos:

#### **✅ O QUE JÁ EXISTE (NÃO TOCAR):**
```
✅ templates/base.html - Layout Bootstrap 5 PERFEITO
✅ templates/dashboard.html - Dashboard funcional com KPIs
✅ static/css/app.css - Estilos SendCraft integrados
✅ static/js/app.js - JavaScript base implementado
✅ Stack moderno: Bootstrap 5.3.2 + HTMX 1.9.6 + Chart.js
✅ Navegação completa no base.html
✅ Design enterprise com cores AliTools (#FFA500)
✅ Toast notifications system preparado
```

#### **❌ O QUE FALTA (IMPLEMENTAR):**
```
❌ sendcraft/routes/web.py - Flask web routes (CRÍTICO!)
❌ templates/domains/list.html + form.html
❌ templates/accounts/list.html + form.html  
❌ templates/templates/list.html + editor.html
❌ templates/logs/list.html
❌ JavaScript avançado para CRUD operations
```

---

## 🏗️ **ARQUITETURA EXISTENTE**

### **Backend Structure (NÃO ALTERAR):**
```
sendcraft/
├── __init__.py (factory pattern)
├── models/ (Domain, EmailAccount, EmailTemplate, EmailLog)
├── services/ (business logic layer)
├── api/v1/ (REST endpoints - 100% funcionais)
├── extensions.py (db, jwt, etc.)
└── utils/ (helpers)
```

### **APIs REST Existentes (USAR):**
```python
# Endpoints funcionais para integração:
GET /api/v1/health
GET /api/v1/stats/global  
GET /api/v1/domains
GET /api/v1/accounts/<domain>
GET /api/v1/templates/<domain>
GET /api/v1/logs
POST /api/v1/send/direct
# ... mais endpoints
```

---

## 🎯 **IMPLEMENTAÇÃO NECESSÁRIA**

### **TASK 1: CRIAR sendcraft/routes/web.py (CRÍTICO)**

```python
"""SendCraft Web Interface Routes"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, abort
from sendcraft.services import domains_service, accounts_service, templates_service, stats_service, logs_service
from sendcraft.decorators import auth_required
from sendcraft.models import Domain, EmailAccount, EmailTemplate, EmailLog
from sendcraft.extensions import db

web_bp = Blueprint('web', __name__)

# ===== DASHBOARD =====
@web_bp.route('/')
def dashboard():
    """Dashboard principal - usar template existente"""
    try:
        # Buscar dados via services existentes
        global_stats = stats_service.get_global_stats()
        email_stats = stats_service.get_email_stats_24h()
        recent_logs = logs_service.get_recent_logs(limit=10)
        domains = domains_service.get_active_domains_with_stats()
        
        return render_template('dashboard.html',
                             stats=global_stats,
                             email_stats=email_stats,
                             recent_logs=recent_logs,
                             domains=domains)
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', 
                             stats={}, email_stats={}, 
                             recent_logs=[], domains=[])

# ===== DOMAINS ROUTES =====
@web_bp.route('/domains')
def domains_list():
    """Lista paginada de domínios com filtros"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    
    try:
        # Usar service para buscar domínios
        domains = domains_service.get_paginated_domains(
            page=page,
            per_page=20,
            search=search,
            status_filter=status
        )
        
        return render_template('domains/list.html',
                             domains=domains,
                             search=search,
                             status_filter=status)
    except Exception as e:
        flash(f'Erro ao listar domínios: {str(e)}', 'error')
        return render_template('domains/list.html',
                             domains=None, search='', status_filter='')

@web_bp.route('/domains/new', methods=['GET', 'POST'])
def domains_new():
    """Criar novo domínio"""
    if request.method == 'POST':
        try:
            domain_data = {
                'name': request.form.get('name', '').strip(),
                'description': request.form.get('description', '').strip(),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            # Validações
            if not domain_data['name']:
                raise ValueError('Nome do domínio é obrigatório')
            
            # Criar via service
            domain = domains_service.create_domain(domain_data)
            
            flash(f'Domínio {domain.name} criado com sucesso!', 'success')
            return redirect(url_for('web.domains_list'))
            
        except Exception as e:
            flash(f'Erro ao criar domínio: {str(e)}', 'error')
    
    return render_template('domains/form.html', domain=None)

@web_bp.route('/domains/<int:domain_id>/edit', methods=['GET', 'POST'])  
def domains_edit(domain_id):
    """Editar domínio existente"""
    domain = domains_service.get_domain_by_id(domain_id)
    if not domain:
        flash('Domínio não encontrado', 'error')
        return redirect(url_for('web.domains_list'))
    
    if request.method == 'POST':
        try:
            domain_data = {
                'name': request.form.get('name', '').strip(),
                'description': request.form.get('description', '').strip(),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            # Atualizar via service
            domains_service.update_domain(domain_id, domain_data)
            
            flash(f'Domínio {domain.name} atualizado com sucesso!', 'success')
            return redirect(url_for('web.domains_list'))
            
        except Exception as e:
            flash(f'Erro ao atualizar domínio: {str(e)}', 'error')
    
    return render_template('domains/form.html', domain=domain)

@web_bp.route('/domains/<int:domain_id>/delete', methods=['POST'])
def domains_delete(domain_id):
    """Eliminar domínio"""
    try:
        domain = domains_service.get_domain_by_id(domain_id)
        if not domain:
            flash('Domínio não encontrado', 'error')
        else:
            domains_service.delete_domain(domain_id)
            flash(f'Domínio {domain.name} eliminado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao eliminar domínio: {str(e)}', 'error')
    
    return redirect(url_for('web.domains_list'))

# ===== ACCOUNTS ROUTES =====
@web_bp.route('/accounts')
def accounts_list():
    """Lista contas email com filtros"""
    domain_filter = request.args.get('domain', '')
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    try:
        accounts = accounts_service.get_paginated_accounts(
            page=page,
            per_page=20,
            domain_filter=domain_filter,
            search=search
        )
        
        domains = domains_service.get_all_active_domains()
        
        return render_template('accounts/list.html',
                             accounts=accounts,
                             domains=domains,
                             domain_filter=domain_filter,
                             search=search)
    except Exception as e:
        flash(f'Erro ao listar contas: {str(e)}', 'error')
        return render_template('accounts/list.html',
                             accounts=None, domains=[], 
                             domain_filter='', search='')

@web_bp.route('/accounts/new', methods=['GET', 'POST'])
def accounts_new():
    """Criar nova conta de email"""
    domains = domains_service.get_all_active_domains()
    
    if request.method == 'POST':
        try:
            account_data = {
                'domain_id': request.form.get('domain_id', type=int),
                'local_part': request.form.get('local_part', '').strip(),
                'display_name': request.form.get('display_name', '').strip(),
                'smtp_server': request.form.get('smtp_server', '').strip(),
                'smtp_port': request.form.get('smtp_port', 587, type=int),
                'smtp_username': request.form.get('smtp_username', '').strip(),
                'smtp_password': request.form.get('smtp_password', ''),
                'use_tls': request.form.get('use_tls') == 'on',
                'use_ssl': request.form.get('use_ssl') == 'on',
                'daily_limit': request.form.get('daily_limit', 1000, type=int),
                'monthly_limit': request.form.get('monthly_limit', 10000, type=int),
                'is_active': request.form.get('is_active', 'on') == 'on'
            }
            
            # Criar via service
            account = accounts_service.create_account(account_data)
            
            flash(f'Conta {account.email_address} criada com sucesso!', 'success')
            return redirect(url_for('web.accounts_list'))
            
        except Exception as e:
            flash(f'Erro ao criar conta: {str(e)}', 'error')
    
    return render_template('accounts/form.html', account=None, domains=domains)

@web_bp.route('/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
def accounts_edit(account_id):
    """Editar conta existente"""
    account = accounts_service.get_account_by_id(account_id)
    domains = domains_service.get_all_active_domains()
    
    if not account:
        flash('Conta não encontrada', 'error')
        return redirect(url_for('web.accounts_list'))
    
    if request.method == 'POST':
        try:
            account_data = {
                'domain_id': request.form.get('domain_id', type=int),
                'local_part': request.form.get('local_part', '').strip(),
                'display_name': request.form.get('display_name', '').strip(),
                'smtp_server': request.form.get('smtp_server', '').strip(),
                'smtp_port': request.form.get('smtp_port', type=int),
                'smtp_username': request.form.get('smtp_username', '').strip(),
                'use_tls': request.form.get('use_tls') == 'on',
                'use_ssl': request.form.get('use_ssl') == 'on',
                'daily_limit': request.form.get('daily_limit', type=int),
                'monthly_limit': request.form.get('monthly_limit', type=int),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            # Atualizar password apenas se fornecida
            if request.form.get('smtp_password'):
                account_data['smtp_password'] = request.form.get('smtp_password')
            
            accounts_service.update_account(account_id, account_data)
            
            flash(f'Conta {account.email_address} atualizada com sucesso!', 'success')
            return redirect(url_for('web.accounts_list'))
            
        except Exception as e:
            flash(f'Erro ao atualizar conta: {str(e)}', 'error')
    
    return render_template('accounts/form.html', account=account, domains=domains)

@web_bp.route('/accounts/<int:account_id>/delete', methods=['POST'])
def accounts_delete(account_id):
    """Eliminar conta"""
    try:
        account = accounts_service.get_account_by_id(account_id)
        if not account:
            flash('Conta não encontrada', 'error')
        else:
            accounts_service.delete_account(account_id)
            flash(f'Conta {account.email_address} eliminada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao eliminar conta: {str(e)}', 'error')
    
    return redirect(url_for('web.accounts_list'))

# ===== TEMPLATES ROUTES =====
@web_bp.route('/templates')
def templates_list():
    """Lista templates por domínio"""
    domain_filter = request.args.get('domain', '')
    page = request.args.get('page', 1, type=int)
    
    try:
        if domain_filter:
            templates = templates_service.get_templates_by_domain(domain_filter, page=page)
        else:
            templates = templates_service.get_all_templates_paginated(page=page)
            
        domains = domains_service.get_all_active_domains()
        
        return render_template('templates/list.html',
                             templates=templates,
                             domains=domains,
                             domain_filter=domain_filter)
    except Exception as e:
        flash(f'Erro ao listar templates: {str(e)}', 'error')
        return render_template('templates/list.html',
                             templates=None, domains=[], domain_filter='')

@web_bp.route('/templates/new', methods=['GET', 'POST'])
def templates_new():
    """Criar novo template"""
    domains = domains_service.get_all_active_domains()
    
    if request.method == 'POST':
        try:
            template_data = {
                'domain_id': request.form.get('domain_id', type=int),
                'key': request.form.get('key', '').strip(),
                'name': request.form.get('name', '').strip(),
                'subject': request.form.get('subject', '').strip(),
                'html_content': request.form.get('html_content', '').strip(),
                'text_content': request.form.get('text_content', '').strip(),
                'description': request.form.get('description', '').strip(),
                'is_active': request.form.get('is_active', 'on') == 'on'
            }
            
            template = templates_service.create_template(template_data)
            
            flash(f'Template {template.name} criado com sucesso!', 'success')
            return redirect(url_for('web.templates_list'))
            
        except Exception as e:
            flash(f'Erro ao criar template: {str(e)}', 'error')
    
    return render_template('templates/editor.html', template=None, domains=domains)

@web_bp.route('/templates/<int:template_id>/edit', methods=['GET', 'POST'])
def templates_edit(template_id):
    """Editor de templates"""
    template = templates_service.get_template_by_id(template_id)
    domains = domains_service.get_all_active_domains()
    
    if not template:
        flash('Template não encontrado', 'error')
        return redirect(url_for('web.templates_list'))
    
    if request.method == 'POST':
        try:
            template_data = {
                'domain_id': request.form.get('domain_id', type=int),
                'key': request.form.get('key', '').strip(),
                'name': request.form.get('name', '').strip(),
                'subject': request.form.get('subject', '').strip(),
                'html_content': request.form.get('html_content', '').strip(),
                'text_content': request.form.get('text_content', '').strip(),
                'description': request.form.get('description', '').strip(),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            templates_service.update_template(template_id, template_data)
            
            flash(f'Template {template.name} atualizado com sucesso!', 'success')
            return redirect(url_for('web.templates_list'))
            
        except Exception as e:
            flash(f'Erro ao atualizar template: {str(e)}', 'error')
    
    return render_template('templates/editor.html', template=template, domains=domains)

@web_bp.route('/templates/<int:template_id>/preview', methods=['POST'])
def templates_preview(template_id):
    """Preview template com dados exemplo"""
    try:
        template = templates_service.get_template_by_id(template_id)
        if not template:
            return jsonify({'error': 'Template não encontrado'}), 404
            
        # Dados exemplo para preview
        sample_data = {
            'cliente_nome': 'João Silva',
            'encomenda_numero': 'ALI-2025-001',
            'total': '149.99',
            'data': '21/10/2025'
        }
        
        preview_html = templates_service.render_template(template, sample_data)
        
        return jsonify({
            'success': True,
            'html': preview_html,
            'subject': templates_service.render_subject(template, sample_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== LOGS ROUTES =====
@web_bp.route('/logs')
def logs_list():
    """Interface de logs com filtros"""
    page = request.args.get('page', 1, type=int)
    domain_filter = request.args.get('domain', '')
    status_filter = request.args.get('status', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    try:
        logs = logs_service.get_paginated_logs(
            page=page,
            per_page=50,
            domain_filter=domain_filter,
            status_filter=status_filter,
            date_from=date_from,
            date_to=date_to
        )
        
        domains = domains_service.get_all_domains()
        
        return render_template('logs/list.html',
                             logs=logs,
                             domains=domains,
                             filters={
                                 'domain': domain_filter,
                                 'status': status_filter,
                                 'date_from': date_from,
                                 'date_to': date_to
                             })
    except Exception as e:
        flash(f'Erro ao listar logs: {str(e)}', 'error')
        return render_template('logs/list.html',
                             logs=None, domains=[], filters={})

@web_bp.route('/logs/<int:log_id>')
def logs_detail(log_id):
    """Detalhe do log"""
    try:
        log = logs_service.get_log_by_id(log_id)
        if not log:
            flash('Log não encontrado', 'error')
            return redirect(url_for('web.logs_list'))
            
        return render_template('logs/detail.html', log=log)
    except Exception as e:
        flash(f'Erro ao buscar log: {str(e)}', 'error')
        return redirect(url_for('web.logs_list'))

# ===== AJAX ENDPOINTS FOR FRONTEND =====
@web_bp.route('/api/domains/<int:domain_id>/toggle', methods=['POST'])
def api_domain_toggle(domain_id):
    """Toggle domain status via AJAX"""
    try:
        domain = domains_service.get_domain_by_id(domain_id)
        if not domain:
            return jsonify({'error': 'Domínio não encontrado'}), 404
            
        new_status = not domain.is_active
        domains_service.update_domain_status(domain_id, new_status)
        
        return jsonify({
            'success': True,
            'message': f'Domínio {"ativado" if new_status else "desativado"} com sucesso',
            'is_active': new_status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@web_bp.route('/api/accounts/<int:account_id>/test-smtp', methods=['POST'])
def api_account_test_smtp(account_id):
    """Testar conexão SMTP via AJAX"""
    try:
        result = accounts_service.test_smtp_connection(account_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@web_bp.route('/api/stats/live')
def api_stats_live():
    """Stats em tempo real para dashboard"""
    try:
        stats = stats_service.get_live_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ERROR HANDLERS
@web_bp.errorhandler(404)
def not_found_error(error):
    """Página 404 customizada"""
    return render_template('errors/404.html'), 404

@web_bp.errorhandler(500)
def internal_error(error):
    """Página 500 customizada"""
    db.session.rollback()
    return render_template('errors/500.html'), 500
```

### **TASK 2: ATUALIZAR sendcraft/__init__.py**

```python
# ADICIONAR ao create_app():
def create_app(config_name='development'):
    app = Flask(__name__)
    
    # ... configuração existente ...
    
    # Register blueprints
    from sendcraft.api.v1 import api_v1_bp
    from sendcraft.routes.web import web_bp  # NOVO
    
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    app.register_blueprint(web_bp)  # NOVO - web interface sem prefix
    
    return app
```

---

## 📝 **REQUIREMENTS ESPECÍFICOS**

### **Integração com Base Existente:**
1. **USAR** `templates/base.html` existente - está perfeito
2. **EXTENDER** dashboard existente - adicionar dados reais
3. **MANTER** stack Bootstrap 5 + HTMX + Chart.js
4. **SEGUIR** padrões de design já estabelecidos

### **Error Handling:**
- Flash messages para feedback user
- Try/catch em todas as operations
- Graceful degradation se APIs falharem
- Logging de erros

### **Performance:**
- Paginação em todas as listas
- Lazy loading para conteúdo pesado
- Cache de dados quando apropriado
- Otimização de queries

### **Security:**
- CSRF protection em forms
- Input validation (client + server)
- XSS protection via Jinja2
- Authentication em rotas protegidas

---

## 🎨 **DESIGN GUIDELINES**

### **Seguir Padrões Existentes:**
- Bootstrap 5 classes e componentes
- Cores: Orange #FFA500 (primary), Blue #1E40AF (secondary)
- Icons: Bootstrap Icons consistentes
- Spacing: Bootstrap spacing classes
- Typography: Bootstrap typography scale

### **UX Patterns:**
- Cards para agrupamento visual
- Modals para confirmações
- Toast notifications para feedback
- Loading states em operations assíncronas
- Breadcrumbs para navegação

---

## ⚡ **ORDEM DE IMPLEMENTAÇÃO**

### **Prioridade 1 (CRÍTICA):**
1. `sendcraft/routes/web.py` - todas as rotas
2. Registrar blueprint no `__init__.py`
3. `templates/domains/list.html` - página domínios

### **Prioridade 2 (ALTA):**
4. `templates/domains/form.html` - CRUD domínios
5. `templates/accounts/list.html` - página contas
6. `templates/accounts/form.html` - CRUD contas

### **Prioridade 3 (MÉDIA):**
7. `templates/templates/list.html` - página templates
8. `templates/templates/editor.html` - editor HTML
9. `templates/logs/list.html` - página logs

### **Prioridade 4 (POLISH):**
10. JavaScript avançado expansions
11. Error pages (404.html, 500.html)
12. CSS customizations

---

## 🧪 **TESTING REQUIREMENTS**

### **Functional Testing:**
- [ ] Todas as rotas respondem (sem 404)
- [ ] CRUD operations funcionam
- [ ] Forms validam corretamente
- [ ] HTMX operations sem erros
- [ ] Mobile responsive OK

### **Integration Testing:**
- [ ] APIs backend integram com frontend
- [ ] Database operations funcionam
- [ ] Authentication protege rotas
- [ ] Error handling graceful

---

## 🎯 **SUCCESS CRITERIA**

### **Interface Completa Funciona:**
✅ Dashboard carrega com KPIs reais  
✅ Domínios: listar, criar, editar, eliminar  
✅ Contas: listar, criar, editar, eliminar, testar SMTP  
✅ Templates: listar, criar, editar, preview  
✅ Logs: listar, filtrar, detalhe  
✅ Mobile responsive completo  
✅ Toast notifications funcionam  

**Quando tudo isto funcionar → SendCraft Interface 100% Enterprise Ready!** 🏆