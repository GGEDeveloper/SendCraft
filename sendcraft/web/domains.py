"""Routes para gestão de domínios."""
from flask import render_template, request, redirect, url_for, flash, jsonify
from . import web_bp
from ..models import Domain, EmailAccount, EmailTemplate, EmailLog
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)


@web_bp.route('/domains')
def domains_list():
    """Lista de domínios."""
    try:
        domains = Domain.query.all()
        
        # Adicionar estatísticas para cada domínio
        domains_data = []
        for domain in domains:
            domain_data = {
                'id': domain.id,
                'name': domain.name,
                'is_active': domain.is_active,
                'description': domain.description,
                'spf_record': domain.spf_record,
                'dkim_selector': domain.dkim_selector,
                'accounts_total': domain.accounts.count(),
                'accounts_active': domain.accounts.filter_by(is_active=True).count(),
                'templates_total': domain.templates.count(),
                'templates_active': domain.templates.filter_by(is_active=True).count(),
                'created_at': domain.created_at,
                'updated_at': domain.updated_at
            }
            domains_data.append(domain_data)
        
        return render_template('domains/list.html', domains=domains_data)
    
    except Exception as e:
        logger.error(f"Error listing domains: {e}", exc_info=True)
        flash('Erro ao carregar domínios', 'danger')
        return redirect(url_for('web.dashboard'))


@web_bp.route('/domains/<int:domain_id>')
def domain_detail(domain_id):
    """Detalhes de um domínio."""
    try:
        domain = Domain.query.get_or_404(domain_id)
        
        # Contas do domínio
        accounts = []
        for account in domain.accounts.all():
            # Estatísticas de envio da conta
            emails_sent_today = account.count_emails_sent_today()
            emails_sent_month = account.count_emails_sent_this_month()
            
            accounts.append({
                'id': account.id,
                'email_address': account.email_address,
                'display_name': account.display_name,
                'is_active': account.is_active,
                'smtp_server': account.smtp_server,
                'smtp_port': account.smtp_port,
                'daily_limit': account.daily_limit,
                'monthly_limit': account.monthly_limit,
                'emails_sent_today': emails_sent_today,
                'emails_sent_month': emails_sent_month,
                'created_at': account.created_at
            })
        
        # Templates do domínio
        templates = []
        for template in domain.templates.all():
            templates.append({
                'id': template.id,
                'template_key': template.template_key,
                'template_name': template.template_name,
                'category': template.category,
                'is_active': template.is_active,
                'version': template.version,
                'created_at': template.created_at
            })
        
        # Estatísticas gerais
        stats = {
            'total_accounts': len(accounts),
            'active_accounts': sum(1 for a in accounts if a['is_active']),
            'total_templates': len(templates),
            'active_templates': sum(1 for t in templates if t['is_active']),
            'emails_sent_today': sum(a['emails_sent_today'] for a in accounts),
            'emails_sent_month': sum(a['emails_sent_month'] for a in accounts)
        }
        
        return render_template('domains/detail.html',
                             domain=domain,
                             accounts=accounts,
                             templates=templates,
                             stats=stats)
    
    except Exception as e:
        logger.error(f"Error loading domain {domain_id}: {e}", exc_info=True)
        flash('Erro ao carregar detalhes do domínio', 'danger')
        return redirect(url_for('web.domains_list'))


@web_bp.route('/domains/new', methods=['GET', 'POST'])
def domain_new():
    """Criar novo domínio."""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            spf_record = request.form.get('spf_record', '').strip()
            dkim_selector = request.form.get('dkim_selector', '').strip()
            
            # Validações
            if not name:
                flash('Nome do domínio é obrigatório', 'danger')
                return render_template('domains/form.html', domain=None)
            
            # Verificar se já existe
            if Domain.get_by_name(name):
                flash(f'Domínio {name} já existe', 'danger')
                return render_template('domains/form.html', domain=None)
            
            # Criar domínio
            domain = Domain.create(
                name=name,
                description=description,
                spf_record=spf_record,
                dkim_selector=dkim_selector,
                is_active=True
            )
            
            flash(f'Domínio {name} criado com sucesso!', 'success')
            logger.info(f"Domain {name} created with ID {domain.id}")
            return redirect(url_for('web.domain_detail', domain_id=domain.id))
            
        except Exception as e:
            logger.error(f"Error creating domain: {e}", exc_info=True)
            flash('Erro ao criar domínio', 'danger')
            db.session.rollback()
    
    return render_template('domains/form.html', domain=None)


@web_bp.route('/domains/<int:domain_id>/edit', methods=['GET', 'POST'])
def domain_edit(domain_id):
    """Editar domínio."""
    domain = Domain.query.get_or_404(domain_id)
    
    if request.method == 'POST':
        try:
            domain.description = request.form.get('description', '').strip()
            domain.spf_record = request.form.get('spf_record', '').strip()
            domain.dkim_selector = request.form.get('dkim_selector', '').strip()
            domain.is_active = request.form.get('is_active') == 'on'
            
            domain.save()
            
            flash('Domínio atualizado com sucesso!', 'success')
            logger.info(f"Domain {domain.name} updated")
            return redirect(url_for('web.domain_detail', domain_id=domain.id))
            
        except Exception as e:
            logger.error(f"Error updating domain {domain_id}: {e}", exc_info=True)
            flash('Erro ao atualizar domínio', 'danger')
            db.session.rollback()
    
    return render_template('domains/form.html', domain=domain)


@web_bp.route('/domains/<int:domain_id>/toggle', methods=['POST'])
def domain_toggle(domain_id):
    """Ativar/Desativar domínio via HTMX."""
    try:
        domain = Domain.query.get_or_404(domain_id)
        domain.is_active = not domain.is_active
        domain.save()
        
        status = 'ativado' if domain.is_active else 'desativado'
        logger.info(f"Domain {domain.name} {status}")
        
        # Retornar HTML parcial para HTMX
        return f'''
        <button class="btn btn-sm btn-{'success' if domain.is_active else 'secondary'}"
                hx-post="/domains/{domain.id}/toggle"
                hx-swap="outerHTML">
            <i class="bi bi-{'check' if domain.is_active else 'x'}-circle me-1"></i>
            {'Ativo' if domain.is_active else 'Inativo'}
        </button>
        '''
    
    except Exception as e:
        logger.error(f"Error toggling domain {domain_id}: {e}")
        return '', 500


@web_bp.route('/domains/<int:domain_id>/delete', methods=['POST'])
def domain_delete(domain_id):
    """Deletar domínio."""
    try:
        domain = Domain.query.get_or_404(domain_id)
        domain_name = domain.name
        
        # Verificar se tem contas ou templates
        if domain.accounts.count() > 0:
            flash('Não é possível deletar domínio com contas associadas', 'warning')
            return redirect(url_for('web.domain_detail', domain_id=domain_id))
        
        if domain.templates.count() > 0:
            flash('Não é possível deletar domínio com templates associados', 'warning')
            return redirect(url_for('web.domain_detail', domain_id=domain_id))
        
        domain.delete()
        
        flash(f'Domínio {domain_name} deletado com sucesso!', 'success')
        logger.info(f"Domain {domain_name} deleted")
        return redirect(url_for('web.domains_list'))
        
    except Exception as e:
        logger.error(f"Error deleting domain {domain_id}: {e}", exc_info=True)
        flash('Erro ao deletar domínio', 'danger')
        db.session.rollback()
        return redirect(url_for('web.domain_detail', domain_id=domain_id))