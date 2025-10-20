# 🤖 **FASE 4 - AGENTE AI: Interface Web e CLI**

**Continuação das FASES 1-3**  
**Repositório:** https://github.com/GGEDeveloper/SendCraft.git  
**Objetivo:** Implementar dashboard web e comandos CLI  

---

## 🎯 **PRÉ-REQUISITOS**

- FASES 1-3 completadas
- APIs funcionais com autenticação  
- Tag `v0.3-api-complete` criada

---

## 🖥️ **INTERFACE WEB**

### **1. WEB/__INIT__.PY**

```python
\"\"\"Blueprint para interface web.\"\"\"
from flask import Blueprint

web_bp = Blueprint('web', __name__)

from . import dashboard, domains, templates
```

### **2. WEB/DASHBOARD.PY**

```python
\"\"\"Routes do dashboard principal.\"\"\"
from flask import render_template, jsonify
from datetime import datetime, timedelta

from . import web_bp
from ..models.domain import Domain
from ..models.account import EmailAccount
from ..models.template import EmailTemplate
from ..models.log import EmailLog, EmailStatus


@web_bp.route('/')
def dashboard():
    \"\"\"Dashboard principal.\"\"\"
    # Estatísticas gerais
    stats = {
        'domains': Domain.query.count(),
        'active_domains': Domain.query.filter_by(is_active=True).count(),
        'accounts': EmailAccount.query.count(),
        'active_accounts': EmailAccount.query.filter_by(is_active=True).count(),
        'templates': EmailTemplate.query.count(),
        'active_templates': EmailTemplate.query.filter_by(is_active=True).count()
    }
    
    # Logs recentes
    recent_logs = EmailLog.query.order_by(EmailLog.created_at.desc()).limit(10).all()
    
    # Estatísticas de envio (últimas 24h)
    yesterday = datetime.utcnow() - timedelta(days=1)
    email_stats = {
        'sent_24h': EmailLog.query.filter(
            EmailLog.created_at >= yesterday,
            EmailLog.status == EmailStatus.SENT
        ).count(),
        'failed_24h': EmailLog.query.filter(
            EmailLog.created_at >= yesterday, 
            EmailLog.status == EmailStatus.FAILED
        ).count()
    }
    
    # Domínios para lista
    domains = Domain.query.all()
    
    return render_template('dashboard.html',
                         stats=stats,
                         email_stats=email_stats,
                         recent_logs=recent_logs,
                         domains=domains)


@web_bp.route('/api/stats')
def api_stats():
    \"\"\"API para estatísticas do dashboard.\"\"\"
    # Estatísticas por dia (últimos 7 dias)
    daily_stats = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        sent_count = EmailLog.query.filter(
            EmailLog.created_at >= start_date,
            EmailLog.created_at < end_date,
            EmailLog.status == EmailStatus.SENT
        ).count()
        
        failed_count = EmailLog.query.filter(
            EmailLog.created_at >= start_date,
            EmailLog.created_at < end_date,
            EmailLog.status == EmailStatus.FAILED
        ).count()
        
        daily_stats.append({
            'date': start_date.strftime('%Y-%m-%d'),
            'sent': sent_count,
            'failed': failed_count
        })
    
    return jsonify({
        'daily_stats': list(reversed(daily_stats))
    })
```

### **3. WEB/DOMAINS.PY**

```python
\"\"\"Routes para gestão de domínios.\"\"\"
from flask import render_template, request, redirect, url_for, flash, jsonify

from . import web_bp
from ..models.domain import Domain
from ..models.account import EmailAccount
from ..extensions import db


@web_bp.route('/domains')
def domains_list():
    \"\"\"Lista de domínios.\"\"\"
    domains = Domain.query.all()
    return render_template('domains/list.html', domains=domains)


@web_bp.route('/domains/<int:domain_id>')
def domain_detail(domain_id):
    \"\"\"Detalhes de um domínio.\"\"\"
    domain = Domain.query.get_or_404(domain_id)
    accounts = EmailAccount.query.filter_by(domain_id=domain_id).all()
    
    return render_template('domains/detail.html',
                         domain=domain,
                         accounts=accounts)


@web_bp.route('/domains/<int:domain_id>/accounts')
def domain_accounts(domain_id):
    \"\"\"Contas de um domínio.\"\"\"
    domain = Domain.query.get_or_404(domain_id)
    accounts = EmailAccount.query.filter_by(domain_id=domain_id).all()
    
    return render_template('domains/accounts.html',
                         domain=domain,
                         accounts=accounts)
```

---

## 🎨 **TEMPLATES HTML**

### **4. TEMPLATES/BASE.HTML**

```html
<!DOCTYPE html>
<html lang=\"pt\" data-bs-theme=\"light\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>{% block title %}SendCraft Email Manager{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
    
    <!-- Bootstrap Icons -->
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css\" rel=\"stylesheet\">
    
    <!-- HTMX -->
    <script src=\"https://unpkg.com/htmx.org@1.9.6\"></script>
    
    <!-- Chart.js -->
    <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
    
    <!-- Custom CSS -->
    <link href=\"{{ url_for('static', filename='css/app.css') }}\" rel=\"stylesheet\">
</head>
<body>
    <!-- Navigation -->
    <nav class=\"navbar navbar-expand-lg navbar-dark bg-dark\">
        <div class=\"container-fluid\">
            <a class=\"navbar-brand d-flex align-items-center\" href=\"{{ url_for('web.dashboard') }}\">
                <i class=\"bi bi-envelope-at me-2\"></i>
                <strong>SendCraft</strong>
            </a>
            
            <button class=\"navbar-toggler\" type=\"button\" data-bs-toggle=\"collapse\" data-bs-target=\"#navbarNav\">
                <span class=\"navbar-toggler-icon\"></span>
            </button>
            
            <div class=\"collapse navbar-collapse\" id=\"navbarNav\">
                <ul class=\"navbar-nav me-auto\">
                    <li class=\"nav-item\">
                        <a class=\"nav-link\" href=\"{{ url_for('web.dashboard') }}\">
                            <i class=\"bi bi-speedometer2 me-1\"></i>Dashboard
                        </a>
                    </li>
                    <li class=\"nav-item\">
                        <a class=\"nav-link\" href=\"{{ url_for('web.domains_list') }}\">
                            <i class=\"bi bi-globe2 me-1\"></i>Domínios
                        </a>
                    </li>
                    <li class=\"nav-item\">
                        <a class=\"nav-link\" href=\"#\">
                            <i class=\"bi bi-file-earmark-text me-1\"></i>Templates
                        </a>
                    </li>
                    <li class=\"nav-item\">
                        <a class=\"nav-link\" href=\"#\">
                            <i class=\"bi bi-journal-text me-1\"></i>Logs
                        </a>
                    </li>
                </ul>
                
                <ul class=\"navbar-nav\">
                    <li class=\"nav-item dropdown\">
                        <a class=\"nav-link dropdown-toggle\" href=\"#\" role=\"button\" data-bs-toggle=\"dropdown\">
                            <i class=\"bi bi-gear me-1\"></i>Configurações
                        </a>
                        <ul class=\"dropdown-menu\">
                            <li><a class=\"dropdown-item\" href=\"#\">API Keys</a></li>
                            <li><a class=\"dropdown-item\" href=\"#\">Configurações</a></li>
                            <li><hr class=\"dropdown-divider\"></li>
                            <li><a class=\"dropdown-item\" href=\"{{ url_for('api_v1.health_check') }}\" target=\"_blank\">Health Check</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class=\"container-fluid mt-3\">
                {% for category, message in messages %}
                    <div class=\"alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show\" role=\"alert\">
                        {{ message }}
                        <button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\"></button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <!-- Main Content -->
    <main class=\"container-fluid py-4\">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class=\"bg-light text-center py-3 mt-5\">
        <div class=\"container\">
            <small class=\"text-muted\">
                SendCraft Email Manager v1.0.0 &copy; 2025
                | <a href=\"https://github.com/GGEDeveloper/SendCraft\" target=\"_blank\" class=\"text-decoration-none\">GitHub</a>
            </small>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js\"></script>
    
    <!-- Custom JS -->
    <script src=\"{{ url_for('static', filename='js/app.js') }}\"></script>
    
    {% block scripts %}{% endblock %}
</body>
</html>
```

### **5. TEMPLATES/DASHBOARD.HTML**

```html
{% extends \"base.html\" %}

{% block title %}Dashboard - SendCraft{% endblock %}

{% block content %}
<div class=\"row mb-4\">
    <div class=\"col\">
        <h1 class=\"h2\">
            <i class=\"bi bi-speedometer2 me-2\"></i>
            Dashboard
        </h1>
        <p class=\"text-muted\">Visão geral do sistema de email</p>
    </div>
</div>

<!-- Statistics Cards -->
<div class=\"row mb-4\">
    <div class=\"col-md-3 mb-3\">
        <div class=\"card border-0 bg-primary text-white\">
            <div class=\"card-body\">
                <div class=\"d-flex justify-content-between align-items-center\">
                    <div>
                        <h5 class=\"card-title mb-1\">Domínios</h5>
                        <h2 class=\"mb-0\">{{ stats.active_domains }}</h2>
                        <small class=\"opacity-75\">{{ stats.domains }} total</small>
                    </div>
                    <i class=\"bi bi-globe2 fs-1 opacity-50\"></i>
                </div>
            </div>
        </div>
    </div>
    
    <div class=\"col-md-3 mb-3\">
        <div class=\"card border-0 bg-success text-white\">
            <div class=\"card-body\">
                <div class=\"d-flex justify-content-between align-items-center\">
                    <div>
                        <h5 class=\"card-title mb-1\">Contas</h5>
                        <h2 class=\"mb-0\">{{ stats.active_accounts }}</h2>
                        <small class=\"opacity-75\">{{ stats.accounts }} total</small>
                    </div>
                    <i class=\"bi bi-envelope fs-1 opacity-50\"></i>
                </div>
            </div>
        </div>
    </div>
    
    <div class=\"col-md-3 mb-3\">
        <div class=\"card border-0 bg-info text-white\">
            <div class=\"card-body\">
                <div class=\"d-flex justify-content-between align-items-center\">
                    <div>
                        <h5 class=\"card-title mb-1\">Templates</h5>
                        <h2 class=\"mb-0\">{{ stats.active_templates }}</h2>
                        <small class=\"opacity-75\">{{ stats.templates }} total</small>
                    </div>
                    <i class=\"bi bi-file-earmark-text fs-1 opacity-50\"></i>
                </div>
            </div>
        </div>
    </div>
    
    <div class=\"col-md-3 mb-3\">
        <div class=\"card border-0 bg-warning text-dark\">
            <div class=\"card-body\">
                <div class=\"d-flex justify-content-between align-items-center\">
                    <div>
                        <h5 class=\"card-title mb-1\">Enviados 24h</h5>
                        <h2 class=\"mb-0 text-success\">{{ email_stats.sent_24h }}</h2>
                        <small class=\"text-danger\">{{ email_stats.failed_24h }} falhas</small>
                    </div>
                    <i class=\"bi bi-graph-up fs-1 opacity-50\"></i>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Charts and Recent Activity -->
<div class=\"row\">
    <!-- Email Chart -->
    <div class=\"col-lg-8 mb-4\">
        <div class=\"card h-100\">
            <div class=\"card-header d-flex justify-content-between align-items-center\">
                <h5 class=\"mb-0\">
                    <i class=\"bi bi-bar-chart me-2\"></i>
                    Emails Enviados (Últimos 7 Dias)
                </h5>
                <div class=\"btn-group btn-group-sm\" role=\"group\">
                    <input type=\"radio\" class=\"btn-check\" name=\"chartPeriod\" id=\"chart7d\" autocomplete=\"off\" checked>
                    <label class=\"btn btn-outline-primary\" for=\"chart7d\">7 dias</label>
                    
                    <input type=\"radio\" class=\"btn-check\" name=\"chartPeriod\" id=\"chart30d\" autocomplete=\"off\">
                    <label class=\"btn btn-outline-primary\" for=\"chart30d\">30 dias</label>
                </div>
            </div>
            <div class=\"card-body\">
                <canvas id=\"emailChart\" width=\"400\" height=\"200\"></canvas>
            </div>
        </div>
    </div>
    
    <!-- Recent Logs -->
    <div class=\"col-lg-4 mb-4\">
        <div class=\"card h-100\">
            <div class=\"card-header d-flex justify-content-between align-items-center\">
                <h5 class=\"mb-0\">
                    <i class=\"bi bi-clock me-2\"></i>
                    Atividade Recente
                </h5>
                <a href=\"#\" class=\"btn btn-sm btn-outline-primary\">Ver Todos</a>
            </div>
            <div class=\"card-body p-0\">
                <div class=\"list-group list-group-flush\">
                    {% for log in recent_logs %}
                    <div class=\"list-group-item\">
                        <div class=\"d-flex w-100 justify-content-between align-items-start\">
                            <div class=\"flex-grow-1 me-2\">
                                <div class=\"d-flex align-items-center mb-1\">
                                    {% if log.status == 'sent' %}
                                        <i class=\"bi bi-check-circle-fill text-success me-2\"></i>
                                    {% elif log.status == 'failed' %}
                                        <i class=\"bi bi-x-circle-fill text-danger me-2\"></i>
                                    {% else %}
                                        <i class=\"bi bi-clock-fill text-warning me-2\"></i>
                                    {% endif %}
                                    <small class=\"fw-bold\">{{ log.recipient_email }}</small>
                                </div>
                                <p class=\"mb-1 small text-truncate\">{{ log.subject or 'Sem assunto' }}</p>
                                <small class=\"text-muted\">
                                    {{ log.account.email_address if log.account }}
                                </small>
                            </div>
                            <small class=\"text-nowrap text-muted\">
                                {{ log.created_at.strftime('%H:%M') }}
                            </small>
                        </div>
                    </div>
                    {% endfor %}
                    
                    {% if not recent_logs %}
                    <div class=\"list-group-item text-center py-4\">
                        <i class=\"bi bi-inbox text-muted fs-1\"></i>
                        <p class=\"text-muted mt-2 mb-0\">Nenhuma atividade recente</p>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Domains Overview -->
<div class=\"row\">
    <div class=\"col-12\">
        <div class=\"card\">
            <div class=\"card-header d-flex justify-content-between align-items-center\">
                <h5 class=\"mb-0\">
                    <i class=\"bi bi-globe2 me-2\"></i>
                    Domínios Configurados
                </h5>
                <a href=\"{{ url_for('web.domains_list') }}\" class=\"btn btn-primary btn-sm\">
                    <i class=\"bi bi-plus me-1\"></i>
                    Gerir Domínios
                </a>
            </div>
            <div class=\"card-body\">
                {% if domains %}
                <div class=\"row\">
                    {% for domain in domains %}
                    <div class=\"col-md-6 col-lg-4 mb-3\">
                        <div class=\"card {{ 'border-success' if domain.is_active else 'border-secondary' }}\">
                            <div class=\"card-body\">
                                <div class=\"d-flex justify-content-between align-items-start\">
                                    <div class=\"flex-grow-1\">
                                        <h6 class=\"card-title mb-2\">
                                            {{ domain.name }}
                                            {% if domain.is_active %}
                                                <span class=\"badge bg-success ms-1\">Ativo</span>
                                            {% else %}
                                                <span class=\"badge bg-secondary ms-1\">Inativo</span>
                                            {% endif %}
                                        </h6>
                                        <small class=\"text-muted\">
                                            {{ domain.accounts.filter_by(is_active=True).count() }} contas ativas<br>
                                            {{ domain.templates.filter_by(is_active=True).count() }} templates ativos
                                        </small>
                                    </div>
                                </div>
                                <div class=\"mt-3\">
                                    <a href=\"{{ url_for('web.domain_detail', domain_id=domain.id) }}\" 
                                       class=\"btn btn-sm btn-outline-primary\">
                                        Ver Detalhes
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class=\"text-center py-5\">
                    <i class=\"bi bi-globe text-muted\" style=\"font-size: 4rem;\"></i>
                    <h4 class=\"text-muted mt-3\">Nenhum Domínio Configurado</h4>
                    <p class=\"text-muted\">Configure seu primeiro domínio para começar a enviar emails.</p>
                    <a href=\"{{ url_for('web.domains_list') }}\" class=\"btn btn-primary\">
                        <i class=\"bi bi-plus me-1\"></i>
                        Adicionar Domínio
                    </a>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Load email statistics chart
    loadEmailChart();
});

async function loadEmailChart() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        const ctx = document.getElementById('emailChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.daily_stats.map(stat => {
                    const date = new Date(stat.date);
                    return date.toLocaleDateString('pt-PT', { 
                        month: 'short', 
                        day: 'numeric' 
                    });
                }),
                datasets: [{
                    label: 'Enviados',
                    data: data.daily_stats.map(stat => stat.sent),
                    borderColor: 'rgb(34, 197, 94)',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Falhas',
                    data: data.daily_stats.map(stat => stat.failed),
                    borderColor: 'rgb(239, 68, 68)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading chart data:', error);
        document.getElementById('emailChart').style.display = 'none';
    }
}
</script>
{% endblock %}
```

---

## 🖱️ **COMANDOS CLI**

### **6. CLI.PY**

```python
\"\"\"Comandos CLI para SendCraft.\"\"\"
import click
from flask.cli import with_appcontext
from typing import Optional

from .extensions import db
from .models.domain import Domain
from .models.account import EmailAccount
from .models.template import EmailTemplate
from .utils.crypto import AESCipher, generate_api_key


@click.command()
@with_appcontext
def init_db_command():
    \"\"\"Inicializa base de dados.\"\"\"
    db.create_all()
    click.echo('✅ Base de dados inicializada.')


@click.command()
@click.option('--key-name', required=True, help='Nome da API key')
@with_appcontext
def create_admin_command(key_name: str):
    \"\"\"Cria nova API key administrativa.\"\"\"
    api_key = generate_api_key('SC')
    click.echo(f'🔑 Nova API Key criada: {api_key}')
    click.echo(f'📝 Adicionar ao instance/config.py:')
    click.echo(f\"   API_KEYS['{key_name}'] = '{api_key}'\")


@click.command() 
@click.option('--domain', required=True, help='Nome do domínio')
@click.option('--description', help='Descrição do domínio')
@with_appcontext
def create_domain_command(domain: str, description: Optional[str]):
    \"\"\"Cria novo domínio.\"\"\"
    existing = Domain.get_by_name(domain)
    if existing:
        click.echo(f'❌ Domínio {domain} já existe.')
        return
    
    new_domain = Domain.create(
        name=domain,
        description=description,
        is_active=True
    )
    
    click.echo(f'✅ Domínio {domain} criado com ID {new_domain.id}.')


@click.command()
@click.option('--domain', required=True, help='Nome do domínio')
@click.option('--local-part', required=True, help='Parte local do email')
@click.option('--password', required=True, help='Password SMTP')
@click.option('--smtp-server', default='smtp.antispamcloud.com', help='Servidor SMTP')
@click.option('--smtp-port', default=587, help='Porta SMTP')
@click.option('--display-name', help='Nome de exibição')
@with_appcontext
def create_account_command(domain: str, local_part: str, password: str, 
                          smtp_server: str, smtp_port: int, display_name: Optional[str]):
    \"\"\"Cria nova conta de email.\"\"\"
    domain_obj = Domain.get_by_name(domain)
    if not domain_obj:
        click.echo(f'❌ Domínio {domain} não encontrado.')
        return
    
    email_address = f'{local_part}@{domain}'
    existing = EmailAccount.get_by_email(email_address)
    if existing:
        click.echo(f'❌ Conta {email_address} já existe.')
        return
    
    account = EmailAccount(
        domain_id=domain_obj.id,
        local_part=local_part,
        email_address=email_address,
        display_name=display_name,
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        smtp_username=email_address,
        use_tls=True,
        is_active=True
    )
    
    # Encriptar password
    from flask import current_app
    encryption_key = current_app.config.get('ENCRYPTION_KEY')
    if encryption_key:
        account.set_password(password, encryption_key)
    
    account.save()
    
    click.echo(f'✅ Conta {email_address} criada com ID {account.id}.')


@click.command()
@click.option('--domain', required=True, help='Nome do domínio')
@click.option('--key', required=True, help='Chave do template')
@click.option('--name', required=True, help='Nome do template')
@click.option('--subject', required=True, help='Template do assunto')
@click.option('--html-file', help='Arquivo HTML do template')
@click.option('--text-file', help='Arquivo de texto do template')
@with_appcontext
def create_template_command(domain: str, key: str, name: str, subject: str,
                           html_file: Optional[str], text_file: Optional[str]):
    \"\"\"Cria novo template de email.\"\"\"
    domain_obj = Domain.get_by_name(domain)
    if not domain_obj:
        click.echo(f'❌ Domínio {domain} não encontrado.')
        return
    
    existing = EmailTemplate.get_by_key(domain_obj.id, key)
    if existing:
        click.echo(f'❌ Template {key} já existe para domínio {domain}.')
        return
    
    html_content = ''
    text_content = ''
    
    if html_file:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            click.echo(f'❌ Arquivo HTML {html_file} não encontrado.')
            return
    
    if text_file:
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except FileNotFoundError:
            click.echo(f'❌ Arquivo texto {text_file} não encontrado.')
            return
    
    template = EmailTemplate.create(
        domain_id=domain_obj.id,
        template_key=key,
        template_name=name,
        subject_template=subject,
        html_template=html_content,
        text_template=text_content,
        is_active=True
    )
    
    click.echo(f'✅ Template {key} criado com ID {template.id}.')


# Register commands
init_db_command.name = 'init-db'
create_admin_command.name = 'create-admin'
create_domain_command.name = 'create-domain'
create_account_command.name = 'create-account'  
create_template_command.name = 'create-template'
```

---

## 📱 **ASSETS ESTÁTICOS**

### **7. STATIC/CSS/APP.CSS**

```css
/* SendCraft Custom Styles */

:root {
    --sc-primary: #0d6efd;
    --sc-success: #198754;
    --sc-warning: #ffc107;
    --sc-danger: #dc3545;
    --sc-info: #0dcaf0;
}

/* Loading states */
.loading {
    opacity: 0.6;
    pointer-events: none;
}

/* Cards enhancement */
.card {
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    border: 1px solid rgba(0, 0, 0, 0.125);
}

.card:hover {
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    transition: box-shadow 0.15s ease-in-out;
}

/* Status badges */
.status-sent { color: var(--sc-success); }
.status-failed { color: var(--sc-danger); }
.status-pending { color: var(--sc-warning); }

/* Chart containers */
.chart-container {
    position: relative;
    height: 300px;
}

/* Email list */
.email-log {
    border-left: 4px solid transparent;
}

.email-log.status-sent {
    border-left-color: var(--sc-success);
}

.email-log.status-failed {
    border-left-color: var(--sc-danger);
}

.email-log.status-pending {
    border-left-color: var(--sc-warning);
}

/* Responsive improvements */
@media (max-width: 768px) {
    .navbar-brand strong {
        display: none;
    }
    
    .card-body .h2 {
        font-size: 1.5rem;
    }
}

/* HTMX loading indicators */
.htmx-indicator {
    opacity: 0;
    transition: opacity 200ms ease-in;
}

.htmx-request .htmx-indicator {
    opacity: 1;
}

.htmx-request.htmx-indicator {
    opacity: 1;
}

/* Utility classes */
.text-monospace {
    font-family: 'SFMono-Regular', Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

.border-start-success {
    border-left: 4px solid var(--sc-success) !important;
}

.border-start-danger {
    border-left: 4px solid var(--sc-danger) !important;
}

.border-start-warning {
    border-left: 4px solid var(--sc-warning) !important;
}
```

### **8. STATIC/JS/APP.JS**

```javascript
// SendCraft Frontend JavaScript

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    initializeConfirmButtons();
    initializeFormValidation();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle=\"tooltip\"]'));
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

// Utility functions
const SendCraft = {
    // Show toast notification
    showToast: function(message, type = 'info') {
        const toastHtml = `
            <div class=\"toast align-items-center text-white bg-${type} border-0\" role=\"alert\">
                <div class=\"d-flex\">
                    <div class=\"toast-body\">${message}</div>
                    <button type=\"button\" class=\"btn-close btn-close-white me-2 m-auto\" data-bs-dismiss=\"toast\"></button>
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
    
    // HTMX error handler
    handleHTMXError: function(event) {
        console.error('HTMX Error:', event.detail);
        this.showToast('Erro na comunicação com o servidor', 'danger');
    }
};

// HTMX event listeners
document.addEventListener('htmx:responseError', SendCraft.handleHTMXError);
document.addEventListener('htmx:timeout', function() {
    SendCraft.showToast('Timeout na requisição', 'warning');
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    // Don't show toast for every JS error, just log
});
```

---

## ⚡ **PONTO DE CONTROLE FASE 4**

Testar interface web:

```bash
# Testar templates
python -c "from flask import Flask; app = Flask(__name__, template_folder='templates'); print('✅ Templates OK')"

# Testar blueprints
python -c "from sendcraft.web import web_bp; print('✅ Web Blueprint OK')"

# Testar CLI
flask --help  # Verificar se comandos SendCraft aparecem
```

**CRITÉRIOS DE ACEITAÇÃO:**
- [ ] Dashboard carrega corretamente
- [ ] Templates HTML bem estruturados
- [ ] Assets CSS/JS funcionais
- [ ] Comandos CLI implementados
- [ ] Bootstrap e HTMX integrados

---

## 🔄 **PRÓXIMA FASE**

Tag: `v0.4-web-interface`  
**Próxima:** **FASE 5: Deploy e Configuração Final**

**Interface completa e funcional!** 🎨