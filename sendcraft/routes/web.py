"""
SendCraft Web Interface Routes
Sistema completo de rotas web para gestão de emails
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, abort, current_app
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import smtplib

from sendcraft.models import Domain, EmailAccount, EmailTemplate, EmailLog
from sendcraft.models.log import EmailStatus
from sendcraft.extensions import db
from sendcraft.utils.logging import get_logger
from sendcraft.services.smtp_service import SMTPService
from sendcraft.services.email_service import EmailService
from sendcraft.services.template_service import TemplateService

logger = get_logger(__name__)

# Blueprint para rotas web
web_bp = Blueprint('web', __name__)


# ===== DASHBOARD =====
@web_bp.route('/')
def dashboard():
    """Dashboard principal - usar template existente"""
    try:
        # Estatísticas gerais
        stats = {
            'domains': Domain.query.count(),
            'active_domains': Domain.query.filter_by(is_active=True).count(),
            'accounts': EmailAccount.query.count(),
            'active_accounts': EmailAccount.query.filter_by(is_active=True).count(),
            'templates': EmailTemplate.query.count(),
            'active_templates': EmailTemplate.query.filter_by(is_active=True).count()
        }
        
        # Logs recentes (últimos 10)
        recent_logs = EmailLog.query.order_by(EmailLog.created_at.desc()).limit(10).all()
        
        # Estatísticas de envio (últimas 24h)
        yesterday = datetime.utcnow() - timedelta(days=1)
        email_stats = {
            'sent_24h': EmailLog.query.filter(
                EmailLog.created_at >= yesterday,
                EmailLog.status.in_([EmailStatus.SENT, EmailStatus.DELIVERED])
            ).count(),
            'failed_24h': EmailLog.query.filter(
                EmailLog.created_at >= yesterday, 
                EmailLog.status == EmailStatus.FAILED
            ).count(),
            'total_24h': EmailLog.query.filter(
                EmailLog.created_at >= yesterday
            ).count()
        }
        
        # Taxa de sucesso
        if email_stats['total_24h'] > 0:
            email_stats['success_rate'] = round(
                email_stats['sent_24h'] / email_stats['total_24h'] * 100, 1
            )
        else:
            email_stats['success_rate'] = 0
            
        # Domínios com estatísticas
        domains = []
        for domain in Domain.query.all():
            domain_data = {
                'id': domain.id,
                'name': domain.name,
                'is_active': domain.is_active,
                'description': domain.description,
                'accounts_count': domain.accounts.filter_by(is_active=True).count(),
                'templates_count': domain.templates.filter_by(is_active=True).count()
            }
            domains.append(domain_data)
        
        return render_template('dashboard.html',
                             stats=stats,
                             email_stats=email_stats,
                             recent_logs=recent_logs,
                             domains=domains)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}", exc_info=True)
        flash('Erro ao carregar dashboard', 'error')
        return render_template('dashboard.html', 
                             stats={}, email_stats={}, 
                             recent_logs=[], domains=[])


# ===== DOMAINS ROUTES =====
@web_bp.route('/domains')
def domains_list():
    """Lista paginada de domínios com filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        per_page = 20
        
        query = Domain.query
        
        # Aplicar filtros
        if search:
            query = query.filter(Domain.name.contains(search))
        
        if status_filter == 'active':
            query = query.filter_by(is_active=True)
        elif status_filter == 'inactive':
            query = query.filter_by(is_active=False)
        
        # Paginar
        domains = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Adicionar estatísticas para cada domínio
        for domain in domains.items:
            domain.accounts_count = domain.accounts.count()
            domain.templates_count = domain.templates.count()
            # Emails enviados nos últimos 30 dias
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            domain.emails_sent_30d = EmailLog.query.join(
                EmailAccount
            ).filter(
                EmailAccount.domain_id == domain.id,
                EmailLog.created_at >= thirty_days_ago,
                EmailLog.status.in_([EmailStatus.SENT, EmailStatus.DELIVERED])
            ).count()
        
        return render_template('domains/list.html',
                             domains=domains,
                             search=search,
                             status_filter=status_filter)
                             
    except Exception as e:
        logger.error(f"Error listing domains: {e}", exc_info=True)
        flash('Erro ao listar domínios', 'error')
        return redirect(url_for('web.dashboard'))


@web_bp.route('/domains/new', methods=['GET', 'POST'])
def domains_new():
    """Criar novo domínio"""
    if request.method == 'POST':
        try:
            import re
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            is_active = request.form.get('is_active') == 'on'
            
            # Validações
            if not name:
                raise ValueError('Nome do domínio é obrigatório')
            
            # Validar formato do domínio (regex)
            domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$'
            if not re.match(domain_pattern, name):
                raise ValueError('Nome de domínio inválido. Use formato: exemplo.com')
            
            # Verificar se já existe
            if Domain.query.filter_by(name=name).first():
                raise ValueError(f'Domínio {name} já existe')
            
            # Criar domínio
            domain = Domain.create(
                name=name,
                description=description,
                is_active=is_active
            )
            
            flash(f'Domínio {domain.name} criado com sucesso!', 'success')
            return redirect(url_for('web.domains_list'))
            
        except Exception as e:
            flash(f'Erro ao criar domínio: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('domains/form.html', domain=None)


@web_bp.route('/domains/<int:domain_id>/edit', methods=['GET', 'POST'])  
def domains_edit(domain_id):
    """Editar domínio existente"""
    domain = Domain.query.get_or_404(domain_id)
    
    if request.method == 'POST':
        try:
            domain.description = request.form.get('description', '').strip()
            domain.is_active = request.form.get('is_active') == 'on'
            
            domain.save()
            
            flash(f'Domínio {domain.name} atualizado com sucesso!', 'success')
            return redirect(url_for('web.domains_list'))
            
        except Exception as e:
            flash(f'Erro ao atualizar domínio: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('domains/form.html', domain=domain)


@web_bp.route('/domains/<int:domain_id>/toggle', methods=['POST'])
def domains_toggle(domain_id):
    """Ativar/Desativar domínio"""
    try:
        domain = Domain.query.get_or_404(domain_id)
        domain.is_active = not domain.is_active
        domain.save()
        
        status = 'ativado' if domain.is_active else 'desativado'
        flash(f'Domínio {domain.name} {status} com sucesso!', 'success')
        return redirect(url_for('web.domains_list'))
        
    except Exception as e:
        flash(f'Erro ao alterar status do domínio: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('web.domains_list'))


@web_bp.route('/domains/<int:domain_id>/delete', methods=['POST'])
def domains_delete(domain_id):
    """Eliminar domínio"""
    try:
        domain = Domain.query.get_or_404(domain_id)
        
        # Verificar se tem contas ativas
        active_accounts = domain.accounts.filter_by(is_active=True).count()
        if active_accounts > 0:
            flash(f'Não é possível eliminar domínio com {active_accounts} conta(s) ativa(s) associada(s)', 'warning')
            return redirect(url_for('web.domains_list'))
        
        # Verificar dependências gerais
        if domain.accounts.count() > 0 or domain.templates.count() > 0:
            flash('Não é possível eliminar domínio com contas ou templates associados', 'warning')
            return redirect(url_for('web.domains_list'))
        
        domain_name = domain.name
        domain.delete()
        
        flash(f'Domínio {domain_name} eliminado com sucesso!', 'success')
        return redirect(url_for('web.domains_list'))
        
    except Exception as e:
        flash(f'Erro ao eliminar domínio: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('web.domains_list'))


# ===== ACCOUNTS ROUTES =====
@web_bp.route('/accounts')
def accounts_list():
    """Lista contas email com filtros"""
    try:
        domain_filter = request.args.get('domain', '')
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        per_page = 20
        
        query = EmailAccount.query
        
        # Filtros
        if domain_filter:
            domain = Domain.query.filter_by(name=domain_filter).first()
            if domain:
                query = query.filter_by(domain_id=domain.id)
        
        if search:
            query = query.filter(EmailAccount.local_part.contains(search))
        
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        
        # Paginar
        accounts = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Adicionar estatísticas
        for account in accounts.items:
            account.emails_sent_today = account.count_emails_sent_today()
            account.emails_sent_this_month = account.count_emails_sent_this_month()
            account.email_address = f"{account.local_part}@{account.domain.name}"
            # Status SMTP
            account.smtp_status = 'untested'  # Pode ser: connected, error, untested
        
        domains = Domain.query.filter_by(is_active=True).all()
        
        return render_template('accounts/list.html',
                             accounts=accounts,
                             domains=domains,
                             domain_filter=domain_filter,
                             search=search)
                             
    except Exception as e:
        logger.error(f"Error listing accounts: {e}", exc_info=True)
        flash('Erro ao listar contas', 'error')
        return redirect(url_for('web.dashboard'))


@web_bp.route('/accounts/new', methods=['GET', 'POST'])
def accounts_new():
    """Criar nova conta de email"""
    domains = Domain.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        try:
            # Coletar dados do formulário
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
                'monthly_limit': request.form.get('monthly_limit', 20000, type=int),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            # Validações
            if not account_data['domain_id']:
                raise ValueError('Domínio é obrigatório')
            if not account_data['local_part']:
                raise ValueError('Parte local do email é obrigatória')
            if not account_data['smtp_server']:
                raise ValueError('Servidor SMTP é obrigatório')
            if not account_data['smtp_password']:
                raise ValueError('Password SMTP é obrigatória')
            
            # Criar conta com password encriptada
            account = EmailAccount(
                domain_id=account_data['domain_id'],
                local_part=account_data['local_part'],
                display_name=account_data['display_name'],
                smtp_server=account_data['smtp_server'],
                smtp_port=account_data['smtp_port'],
                smtp_username=account_data['smtp_username'],
                use_tls=account_data['use_tls'],
                use_ssl=account_data['use_ssl'],
                daily_limit=account_data['daily_limit'],
                monthly_limit=account_data['monthly_limit'],
                is_active=account_data['is_active'],
                # IMAP Configuration
                imap_server=request.form.get('imap_server', '').strip() or 'mail.alitools.pt',
                imap_port=request.form.get('imap_port', 993, type=int),
                imap_use_ssl=request.form.get('imap_use_ssl') == 'on',
                imap_use_tls=request.form.get('imap_use_tls') == 'on'
            )
            
            # Encriptar password antes de salvar
            encryption_key = current_app.config.get('SECRET_KEY', '')
            account.set_password(account_data['smtp_password'], encryption_key)
            account.save()
            
            email_address = f"{account.local_part}@{account.domain.name}"
            flash(f'Conta {email_address} criada com sucesso!', 'success')
            return redirect(url_for('web.accounts_list'))
            
        except Exception as e:
            flash(f'Erro ao criar conta: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('accounts/form.html', account=None, domains=domains)


@web_bp.route('/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
def accounts_edit(account_id):
    """Editar conta existente"""
    account = EmailAccount.query.get_or_404(account_id)
    domains = Domain.query.filter_by(is_active=True).all()
    
    # Adicionar campos calculados
    account.email_address = f"{account.local_part}@{account.domain.name}"
    account.emails_sent_today = account.count_emails_sent_today()
    account.emails_sent_this_month = account.count_emails_sent_this_month()
    
    if request.method == 'POST':
        try:
            # Atualizar dados
            account.domain_id = request.form.get('domain_id', type=int)
            account.local_part = request.form.get('local_part', '').strip()
            account.display_name = request.form.get('display_name', '').strip()
            account.smtp_server = request.form.get('smtp_server', '').strip()
            account.smtp_port = request.form.get('smtp_port', type=int)
            account.smtp_username = request.form.get('smtp_username', '').strip()
            account.use_tls = request.form.get('use_tls') == 'on'
            account.use_ssl = request.form.get('use_ssl') == 'on'
            account.daily_limit = request.form.get('daily_limit', type=int)
            account.monthly_limit = request.form.get('monthly_limit', type=int)
            account.is_active = request.form.get('is_active') == 'on'
            
            # Atualizar configurações IMAP
            account.imap_server = request.form.get('imap_server', '').strip() or 'mail.alitools.pt'
            account.imap_port = request.form.get('imap_port', 993, type=int)
            account.imap_use_ssl = request.form.get('imap_use_ssl') == 'on'
            account.imap_use_tls = request.form.get('imap_use_tls') == 'on'
            
            # Atualizar password apenas se fornecida
            new_password = request.form.get('smtp_password', '').strip()
            if new_password:
                encryption_key = current_app.config.get('SECRET_KEY', '')
                account.set_password(new_password, encryption_key)
            
            account.save()
            
            email_address = f"{account.local_part}@{account.domain.name}"
            flash(f'Conta {email_address} atualizada com sucesso!', 'success')
            return redirect(url_for('web.accounts_list'))
            
        except Exception as e:
            flash(f'Erro ao atualizar conta: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('accounts/form.html', account=account, domains=domains)


@web_bp.route('/accounts/<int:account_id>/delete', methods=['POST'])
def accounts_delete(account_id):
    """Eliminar conta"""
    try:
        account = EmailAccount.query.get_or_404(account_id)
        email_address = f"{account.local_part}@{account.domain.name}"
        
        # Verificar se tem emails vinculados
        emails_count = account.logs.count()
        inbox_count = account.inbox_emails.count()
        
        if emails_count > 0 or inbox_count > 0:
            flash(f'Não é possível eliminar conta com {emails_count} log(s) e {inbox_count} email(s) na caixa de entrada', 'warning')
            return redirect(url_for('web.accounts_list'))
        
        account.delete()
        
        flash(f'Conta {email_address} eliminada com sucesso!', 'success')
        return redirect(url_for('web.accounts_list'))
        
    except Exception as e:
        flash(f'Erro ao eliminar conta: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('web.accounts_list'))


# ===== API ACCESS MANAGEMENT =====
@web_bp.route('/accounts/<int:account_id>/api', methods=['GET'])
def accounts_api_access(account_id):
    """Gestão de acesso API para uma conta"""
    try:
        account = EmailAccount.query.get_or_404(account_id)
        
        # Preparar dados da API
        api_data = {
            'is_enabled': account.api_enabled,
            'has_key': bool(account.api_key_hash),
            'key_display': account.get_api_key_display(),
            'created_at': account.api_created_at,
            'last_used_at': account.api_last_used_at
        }
        
        return render_template('accounts/api_access.html', 
                             account=account, 
                             api_data=api_data)
    except Exception as e:
        logger.error(f"Error loading API access: {e}")
        flash('Erro ao carregar gestão de API', 'error')
        return redirect(url_for('web.accounts_list'))


@web_bp.route('/accounts/<int:account_id>/api/enable', methods=['POST'])
def accounts_api_enable(account_id):
    """Ativar/Desativar acesso API"""
    try:
        account = EmailAccount.query.get_or_404(account_id)
        
        # Toggle status
        account.api_enabled = not account.api_enabled
        
        # Se desativando, revogar chave
        if not account.api_enabled:
            account.revoke_api_key()
        
        account.save()
        
        status = 'ativado' if account.api_enabled else 'desativado'
        flash(f'Acesso API {status} com sucesso!', 'success')
        return redirect(url_for('web.accounts_api_access', account_id=account_id))
        
    except Exception as e:
        logger.error(f"Error toggling API access: {e}")
        flash(f'Erro ao alterar acesso API: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('web.accounts_api_access', account_id=account_id))


@web_bp.route('/accounts/<int:account_id>/api/generate', methods=['POST'])
def accounts_api_generate(account_id):
    """Gerar ou rotacionar API key"""
    try:
        account = EmailAccount.query.get_or_404(account_id)
        
        # Verificar se já tem chave (rotação)
        is_rotation = bool(account.api_key_hash)
        
        # Gerar nova chave
        api_key = account.generate_api_key()
        account.save()
        
        # Preparar dados da API atualizados
        api_data = {
            'is_enabled': account.api_enabled,
            'has_key': True,
            'key_display': account.get_api_key_display(),
            'created_at': account.api_created_at,
            'last_used_at': account.api_last_used_at
        }
        
        flash(f'API key {"rotacionada" if is_rotation else "gerada"} com sucesso! Guarde-a agora, não será mostrada novamente.', 'success')
        
        return render_template('accounts/api_access.html',
                             account=account,
                             api_data=api_data,
                             new_api_key=api_key)  # Passar chave para mostrar
        
    except Exception as e:
        logger.error(f"Error generating API key: {e}")
        flash(f'Erro ao gerar API key: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('web.accounts_api_access', account_id=account_id))


@web_bp.route('/accounts/<int:account_id>/api/revoke', methods=['POST'])
def accounts_api_revoke(account_id):
    """Revogar API key"""
    try:
        account = EmailAccount.query.get_or_404(account_id)
        
        if not account.api_key_hash:
            flash('Nenhuma chave para revogar', 'warning')
            return redirect(url_for('web.accounts_api_access', account_id=account_id))
        
        account.revoke_api_key()
        account.save()
        
        flash('API key revogada com sucesso!', 'success')
        return redirect(url_for('web.accounts_api_access', account_id=account_id))
        
    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        flash(f'Erro ao revogar API key: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('web.accounts_api_access', account_id=account_id))


# ===== TEMPLATES ROUTES =====
@web_bp.route('/templates')
def templates_list():
    """Lista templates por domínio"""
    try:
        domain_filter = request.args.get('domain', '')
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category', '')
        per_page = 20
        
        query = EmailTemplate.query
        
        # Filtros
        if domain_filter:
            domain = Domain.query.filter_by(name=domain_filter).first()
            if domain:
                query = query.filter_by(domain_id=domain.id)
        
        if category:
            query = query.filter_by(category=category)
        
        # Paginar
        templates = query.paginate(page=page, per_page=per_page, error_out=False)
        
        domains = Domain.query.filter_by(is_active=True).all()
        
        # Categorias únicas
        categories = db.session.query(EmailTemplate.category).distinct().all()
        categories = [c[0] for c in categories if c[0]]
        
        return render_template('templates/list.html',
                             templates=templates,
                             domains=domains,
                             categories=categories,
                             domain_filter=domain_filter,
                             category_filter=category)
                             
    except Exception as e:
        logger.error(f"Error listing templates: {e}", exc_info=True)
        flash('Erro ao listar templates', 'error')
        return redirect(url_for('web.dashboard'))


@web_bp.route('/templates/new', methods=['GET', 'POST'])
def templates_new():
    """Criar novo template"""
    domains = Domain.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        try:
            template_data = {
                'domain_id': request.form.get('domain_id', type=int),
                'template_key': request.form.get('template_key', '').strip(),
                'template_name': request.form.get('template_name', '').strip(),
                'subject': request.form.get('subject', '').strip(),
                'html_body': request.form.get('html_body', '').strip(),
                'text_body': request.form.get('text_body', '').strip(),
                'category': request.form.get('category', '').strip(),
                'variables': request.form.get('variables', '').strip(),
                'is_active': request.form.get('is_active') == 'on',
                'version': 1
            }
            
            # Validações
            if not template_data['domain_id']:
                raise ValueError('Domínio é obrigatório')
            if not template_data['template_key']:
                raise ValueError('Chave do template é obrigatória')
            if not template_data['template_name']:
                raise ValueError('Nome do template é obrigatório')
            if not template_data['subject']:
                raise ValueError('Assunto é obrigatório')
            
            # Criar template
            template = EmailTemplate.create(**template_data)
            
            flash(f'Template {template.template_name} criado com sucesso!', 'success')
            return redirect(url_for('web.templates_list'))
            
        except Exception as e:
            flash(f'Erro ao criar template: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('templates/editor.html', template=None, domains=domains)


@web_bp.route('/templates/<int:template_id>/edit', methods=['GET', 'POST'])
def templates_edit(template_id):
    """Editor de templates"""
    template = EmailTemplate.query.get_or_404(template_id)
    domains = Domain.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        try:
            # Atualizar template
            template.template_name = request.form.get('template_name', '').strip()
            template.subject = request.form.get('subject', '').strip()
            template.html_body = request.form.get('html_body', '').strip()
            template.text_body = request.form.get('text_body', '').strip()
            template.category = request.form.get('category', '').strip()
            template.variables = request.form.get('variables', '').strip()
            template.is_active = request.form.get('is_active') == 'on'
            template.version += 1
            
            template.save()
            
            flash(f'Template {template.template_name} atualizado com sucesso!', 'success')
            return redirect(url_for('web.templates_list'))
            
        except Exception as e:
            flash(f'Erro ao atualizar template: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('templates/editor.html', template=template, domains=domains)


@web_bp.route('/templates/<int:template_id>/preview', methods=['POST'])
def templates_preview(template_id):
    """Preview template com dados exemplo"""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        
        # Dados exemplo para preview
        sample_data = {
            'cliente_nome': 'João Silva',
            'encomenda_numero': 'ALI-2025-001',
            'total': '149.99',
            'data': datetime.now().strftime('%d/%m/%Y')
        }
        
        # Renderizar template
        service = TemplateService()
        preview_html = service.render_template_string(template.html_body, sample_data)
        preview_subject = service.render_template_string(template.subject, sample_data)
        
        return jsonify({
            'success': True,
            'html': preview_html,
            'subject': preview_subject
        })
        
    except Exception as e:
        logger.error(f"Error previewing template: {e}")
        return jsonify({'error': str(e)}), 500


@web_bp.route('/templates/<int:template_id>/delete', methods=['POST'])
def templates_delete(template_id):
    """Eliminar template"""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        template_name = template.template_name
        
        template.delete()
        
        flash(f'Template {template_name} eliminado com sucesso!', 'success')
        return redirect(url_for('web.templates_list'))
        
    except Exception as e:
        flash(f'Erro ao eliminar template: {str(e)}', 'error')
        db.session.rollback()
        return redirect(url_for('web.templates_list'))


# ===== LOGS ROUTES =====
@web_bp.route('/logs')
def logs_list():
    """Interface de logs com filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        domain_filter = request.args.get('domain', '')
        status_filter = request.args.get('status', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        per_page = 50
        
        query = EmailLog.query
        
        # Filtros
        if domain_filter:
            domain = Domain.query.filter_by(name=domain_filter).first()
            if domain:
                query = query.join(EmailAccount).filter(EmailAccount.domain_id == domain.id)
        
        if status_filter:
            try:
                status = EmailStatus(status_filter)
                query = query.filter_by(status=status)
            except ValueError:
                pass
        
        if date_from:
            try:
                dt = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(EmailLog.created_at >= dt)
            except ValueError:
                pass
        
        if date_to:
            try:
                dt = datetime.strptime(date_to, '%Y-%m-%d')
                dt = dt.replace(hour=23, minute=59, second=59)
                query = query.filter(EmailLog.created_at <= dt)
            except ValueError:
                pass
        
        # Ordenar por data descendente
        query = query.order_by(EmailLog.created_at.desc())
        
        # Paginar
        logs = query.paginate(page=page, per_page=per_page, error_out=False)
        
        domains = Domain.query.all()
        
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
        logger.error(f"Error listing logs: {e}", exc_info=True)
        flash('Erro ao listar logs', 'error')
        return redirect(url_for('web.dashboard'))


@web_bp.route('/logs/<int:log_id>')
def logs_detail(log_id):
    """Detalhe do log"""
    try:
        log = EmailLog.query.get_or_404(log_id)
        return render_template('logs/detail.html', log=log)
        
    except Exception as e:
        logger.error(f"Error loading log detail: {e}")
        flash('Erro ao carregar log', 'error')
        return redirect(url_for('web.logs_list'))


# ===== AJAX ENDPOINTS =====
@web_bp.route('/api/domains/<int:domain_id>/toggle', methods=['POST'])
def api_domain_toggle(domain_id):
    """Toggle domain status via AJAX"""
    try:
        domain = Domain.query.get_or_404(domain_id)
        domain.is_active = not domain.is_active
        domain.save()
        
        return jsonify({
            'success': True,
            'message': f'Domínio {"ativado" if domain.is_active else "desativado"} com sucesso',
            'details': {
                'domain_id': domain.id,
                'domain_name': domain.name,
                'is_active': domain.is_active
            }
        })
    except Exception as e:
        logger.error(f"Error toggling domain: {e}")
        return jsonify({
            'success': False,
            'error': 'internal_server_error',
            'message': str(e),
            'details': {}
        }), 500


@web_bp.route('/api/accounts/<int:account_id>/test-smtp', methods=['POST'])
def api_account_test_smtp(account_id):
    """Testar conexão SMTP via AJAX"""
    try:
        account = EmailAccount.query.get_or_404(account_id)
        encryption_key = current_app.config.get('SECRET_KEY', '')
        
        # Testar conexão de forma simples
        import smtplib
        import time
        
        start_time = time.time()
        result = {'success': False, 'error': None, 'response_time': 0}
        
        try:
            if account.use_ssl:
                server = smtplib.SMTP_SSL(account.smtp_server, account.smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(account.smtp_server, account.smtp_port, timeout=10)
                if account.use_tls:
                    server.starttls()
            
            # Tentar fazer login (sem logar password em texto plano)
            password = account.get_password(encryption_key)
            server.login(account.smtp_username, password)
            server.quit()
            
            result['success'] = True
            result['response_time'] = round((time.time() - start_time) * 1000, 2)
        except Exception as e:
            result['error'] = str(e)
            result['response_time'] = round((time.time() - start_time) * 1000, 2)
            logger.error(f"SMTP test failed for {account.email_address}: {str(e)}")
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Conexão SMTP estabelecida com sucesso!',
                'details': {
                    'server': account.smtp_server,
                    'port': account.smtp_port,
                    'tls': account.use_tls,
                    'ssl': account.use_ssl,
                    'response_time': result.get('response_time', 'N/A'),
                    'status': 'connected',
                    'code': result.get('code', 250),
                    'message': result.get('message', 'Conexão OK'),
                    'security': 'TLS' if account.use_tls else 'SSL' if account.use_ssl else 'None'
                }
            })
        else:
            # Portuguese error messages
            error_msg = result.get('error', 'Falha na conexão SMTP')
            if 'authentication' in error_msg.lower() or '535' in error_msg:
                error_msg = 'Credenciais SMTP inválidas'
            elif 'connection' in error_msg.lower() or 'timeout' in error_msg.lower():
                error_msg = 'Erro de conexão ao servidor SMTP'
            elif 'refused' in error_msg.lower():
                error_msg = 'Conexão recusada pelo servidor SMTP'
            
            return jsonify({
                'success': False,
                'error': error_msg,
                'details': {
                    'server': account.smtp_server,
                    'port': account.smtp_port,
                    'tls': account.use_tls,
                    'ssl': account.use_ssl,
                    'status': 'error',
                    'message': error_msg,
                    'security': 'TLS' if account.use_tls else 'SSL' if account.use_ssl else 'None'
                }
            })
            
    except Exception as e:
        logger.error(f"Error testing SMTP: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@web_bp.route('/api/accounts/<int:account_id>/test-imap', methods=['POST'])
def api_account_test_imap(account_id):
    """Testar conexão IMAP via AJAX com timeout de 60s"""
    try:
        account = EmailAccount.query.get_or_404(account_id)
        encryption_key = current_app.config.get('SECRET_KEY', '')
        
        import imaplib
        import time
        
        start_time = time.time()
        result = {'success': False, 'error': None, 'response_time': 0}
        
        try:
            # Configurar timeout de 60 segundos
            timeout = 60
            
            if account.imap_use_ssl:
                server = imaplib.IMAP4_SSL(account.imap_server, account.imap_port, timeout=timeout)
            else:
                server = imaplib.IMAP4(account.imap_server, account.imap_port, timeout=timeout)
                if account.imap_use_tls:
                    server.starttls()
            
            # Tentar fazer login (sem logar password em texto plano)
            password = account.get_password(encryption_key)
            server.login(account.email_address, password)
            
            # Testar seleção de INBOX
            server.select('INBOX', readonly=True)
            server.logout()
            
            result['success'] = True
            result['response_time'] = round((time.time() - start_time) * 1000, 2)
            
        except imaplib.IMAP4.error as e:
            result['error'] = f"Erro IMAP: {str(e)}"
            result['response_time'] = round((time.time() - start_time) * 1000, 2)
            logger.error(f"IMAP test failed for {account.email_address}: {str(e)}")
        except Exception as e:
            result['error'] = str(e)
            result['response_time'] = round((time.time() - start_time) * 1000, 2)
            logger.error(f"IMAP test error for {account.email_address}: {str(e)}")
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Conexão IMAP estabelecida com sucesso!',
                'details': {
                    'server': account.imap_server,
                    'port': account.imap_port,
                    'use_ssl': account.imap_use_ssl,
                    'use_tls': account.imap_use_tls,
                    'response_time': result.get('response_time', 'N/A'),
                    'status': 'connected',
                    'message': 'Conexão OK'
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Falha na conexão IMAP'),
                'details': {
                    'server': account.imap_server,
                    'port': account.imap_port,
                    'use_ssl': account.imap_use_ssl,
                    'use_tls': account.imap_use_tls,
                    'status': 'error',
                    'message': result.get('error', 'Connection failed')
                }
            })
            
    except Exception as e:
        logger.error(f"Error testing IMAP: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@web_bp.route('/api/accounts/<int:account_id>/toggle', methods=['POST'])
def api_account_toggle(account_id):
    """Toggle account status via AJAX"""
    try:
        account = EmailAccount.query.get_or_404(account_id)
        account.is_active = not account.is_active
        account.save()
        
        email_address = f"{account.local_part}@{account.domain.name}"
        
        return jsonify({
            'success': True,
            'message': f'Conta {email_address} {"ativada" if account.is_active else "desativada"} com sucesso',
            'is_active': account.is_active
        })
    except Exception as e:
        logger.error(f"Error toggling account: {e}")
        return jsonify({'error': str(e)}), 500


@web_bp.route('/api/domains/bulk', methods=['POST'])
def api_domains_bulk():
    """Operações em lote para domínios"""
    try:
        data = request.json
        action = data.get('action')
        domain_ids = data.get('domain_ids', [])
        
        if not action or not domain_ids:
            return jsonify({'error': 'Ação e IDs são obrigatórios'}), 400
        
        affected = 0
        
        for domain_id in domain_ids:
            domain = Domain.query.get(domain_id)
            if domain:
                if action == 'activate':
                    domain.is_active = True
                elif action == 'deactivate':
                    domain.is_active = False
                elif action == 'delete':
                    if domain.accounts.count() == 0 and domain.templates.count() == 0:
                        db.session.delete(domain)
                    else:
                        continue
                
                affected += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'affected': affected,
            'message': f'{affected} domínios processados com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Error in bulk operation: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@web_bp.route('/api/stats')
def api_stats():
    """API para estatísticas do dashboard"""
    try:
        days = int(request.args.get('days', 7))
        
        # Estatísticas por dia
        daily_stats = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            sent_count = EmailLog.query.filter(
                EmailLog.created_at >= start_date,
                EmailLog.created_at < end_date,
                EmailLog.status.in_([EmailStatus.SENT, EmailStatus.DELIVERED])
            ).count()
            
            failed_count = EmailLog.query.filter(
                EmailLog.created_at >= start_date,
                EmailLog.created_at < end_date,
                EmailLog.status == EmailStatus.FAILED
            ).count()
            
            daily_stats.append({
                'date': start_date.strftime('%Y-%m-%d'),
                'day_label': start_date.strftime('%d %b'),
                'sent': sent_count,
                'failed': failed_count,
                'total': sent_count + failed_count
            })
        
        daily_stats.reverse()
        
        return jsonify({
            'daily_stats': daily_stats,
            'period_days': days
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': 'Failed to load statistics'}), 500


@web_bp.route('/api/stats/live')
def api_stats_live():
    """Stats em tempo real para dashboard"""
    try:
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        stats = {
            'domains_active': Domain.query.filter_by(is_active=True).count(),
            'accounts_active': EmailAccount.query.filter_by(is_active=True).count(),
            'emails_sent_24h': EmailLog.query.filter(
                EmailLog.created_at >= yesterday,
                EmailLog.status.in_([EmailStatus.SENT, EmailStatus.DELIVERED])
            ).count(),
            'emails_failed_24h': EmailLog.query.filter(
                EmailLog.created_at >= yesterday,
                EmailLog.status == EmailStatus.FAILED
            ).count(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting live stats: {e}")
        return jsonify({'error': str(e)}), 500


@web_bp.route('/api/smtp/test', methods=['POST'])
def api_smtp_test():
    """Testar configuração SMTP genérica"""
    try:
        data = request.json
        
        # Testar conexão de forma simples
        import smtplib
        import time
        
        start_time = time.time()
        result = {'success': False, 'error': None, 'response_time': 0}
        
        try:
            if data.get('use_ssl', False):
                server = smtplib.SMTP_SSL(
                    data.get('smtp_server'),
                    data.get('smtp_port', 465),
                    timeout=10
                )
            else:
                server = smtplib.SMTP(
                    data.get('smtp_server'),
                    data.get('smtp_port', 587),
                    timeout=10
                )
                if data.get('use_tls', True):
                    server.starttls()
            
            server.login(data.get('smtp_username'), data.get('smtp_password'))
            server.quit()
            
            result['success'] = True
            result['response_time'] = round((time.time() - start_time) * 1000, 2)
        except Exception as e:
            result['error'] = str(e)
            result['response_time'] = round((time.time() - start_time) * 1000, 2)
        
        # Continuar com o resultado
        result_placeholder = smtp_service.test_connection_unused(
            smtp_server=data.get('smtp_server'),
            smtp_port=data.get('smtp_port', 587),
            smtp_username=data.get('smtp_username'),
            smtp_password=data.get('smtp_password'),
            use_tls=data.get('use_tls', True),
            use_ssl=data.get('use_ssl', False)
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'details': {
                    'server': data.get('smtp_server'),
                    'port': data.get('smtp_port'),
                    'security': 'TLS' if data.get('use_tls') else 'SSL' if data.get('use_ssl') else 'None',
                    'response_time': result.get('response_time', 'N/A'),
                    'status': 'OK',
                    'code': 250,
                    'message': 'Conexão estabelecida com sucesso'
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Falha na conexão'),
                'details': {
                    'server': data.get('smtp_server'),
                    'port': data.get('smtp_port'),
                    'security': 'TLS' if data.get('use_tls') else 'SSL' if data.get('use_ssl') else 'None',
                    'status': 'ERRO',
                    'message': result.get('error')
                }
            })
            
    except Exception as e:
        logger.error(f"Error testing SMTP: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@web_bp.route('/api/stats/accounts')
def api_stats_accounts():
    """Estatísticas de contas para atualização em tempo real"""
    try:
        accounts_data = []
        
        for account in EmailAccount.query.filter_by(is_active=True).all():
            accounts_data.append({
                'id': account.id,
                'emails_sent_today': account.count_emails_sent_today(),
                'emails_sent_this_month': account.count_emails_sent_this_month(),
                'daily_limit': account.daily_limit,
                'monthly_limit': account.monthly_limit
            })
        
        return jsonify({'accounts': accounts_data})
        
    except Exception as e:
        logger.error(f"Error getting account stats: {e}")
        return jsonify({'error': str(e)}), 500


# ===== EMAIL INBOX ROUTES =====
@web_bp.route('/emails/inbox')
@web_bp.route('/emails/inbox/<int:account_id>')
def emails_inbox(account_id=None):
    """Email inbox interface - three-pane email client with account switcher"""
    from ..models.account import EmailAccount
    
    # Get all active accounts for switcher
    all_accounts = EmailAccount.query.filter_by(is_active=True).all()
    
    if not all_accounts:
        flash('Nenhuma conta de email configurada. Por favor, configure uma conta primeiro.', 'warning')
        return redirect(url_for('web.accounts_list'))
    
    # Get the requested account or default to first
    if account_id:
        account = EmailAccount.query.filter_by(id=account_id, is_active=True).first()
        if not account:
            flash('Conta não encontrada', 'warning')
            account = all_accounts[0]
    else:
        account = all_accounts[0]
    
    # Build the complete email address if needed
    if not hasattr(account, 'email_address') or not account.email_address:
        account.email_address = f"{account.local_part}@{account.domain.name}"
    
    return render_template('emails/inbox.html', 
                         account=account,
                         all_accounts=all_accounts,
                         page_title=f'Caixa de Entrada - {account.email_address}')


@web_bp.route('/emails/send', methods=['POST'])
def emails_send():
    """Send email via SMTP with attachments support"""
    from ..models.account import EmailAccount
    from ..models.log import EmailLog, EmailStatus
    from ..services.smtp_service import SMTPService
    from ..utils.logging import get_logger
    import re
    import mimetypes
    import os
    
    logger = get_logger(__name__)
    
    try:
        # Get account ID
        account_id = request.form.get('account_id')
        if not account_id:
            return jsonify({
                'success': False,
                'message': 'ID da conta não fornecido'
            }), 400
        
        # Get account
        account = EmailAccount.query.get(int(account_id))
        if not account:
            return jsonify({
                'success': False,
                'message': 'Conta não encontrada'
            }), 404
        
        if not account.is_active:
            return jsonify({
                'success': False,
                'message': 'Conta não está ativa'
            }), 400
        
        # Validate required fields
        to_emails = request.form.get('to', '').strip()
        subject = request.form.get('subject', '').strip()
        body_html = request.form.get('body_html', '').strip()
        body_text = request.form.get('body_text', '').strip()
        
        if not to_emails or not subject or not body_html:
            return jsonify({
                'success': False,
                'message': 'Campos obrigatórios: Para, Assunto e Mensagem'
            }), 400
        
        # Validate email format
        email_list = [e.strip() for e in to_emails.split(',')]
        email_regex = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
        for email in email_list:
            if not email_regex.match(email):
                return jsonify({
                    'success': False,
                    'message': f'Email inválido: {email}'
                }), 400
        
        # Sanitize HTML (basic - strip script and iframe tags)
        # Remove script tags and their content
        body_html = re.sub(r'<script[^>]*>.*?</script>', '', body_html, flags=re.DOTALL | re.IGNORECASE)
        # Remove iframe tags
        body_html = re.sub(r'<iframe[^>]*>.*?</iframe>', '', body_html, flags=re.DOTALL | re.IGNORECASE)
        # Remove on* event handlers
        body_html = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', body_html, flags=re.IGNORECASE)
        
        # Process attachments
        attachments = []
        if 'attachments' in request.files:
            files = request.files.getlist('attachments')
            for file in files:
                if file and file.filename:
                    # Validate file size (5MB limit)
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    
                    if file_size > 5 * 1024 * 1024:  # 5MB
                        return jsonify({
                            'success': False,
                            'message': f'Anexo {file.filename} é demasiado grande (máximo 5MB)'
                        }), 400
                    
                    # Validate file extension
                    allowed_extensions = {'.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'}
                    file_ext = os.path.splitext(file.filename)[1].lower()
                    if file_ext not in allowed_extensions:
                        return jsonify({
                            'success': False,
                            'message': f'Tipo de ficheiro {file_ext} não permitido'
                        }), 400
                    
                    # Read file content
                    file_content = file.read()
                    file.seek(0)  # Reset file pointer
                    
                    # Get content type
                    content_type, _ = mimetypes.guess_type(file.filename)
                    if not content_type:
                        content_type = 'application/octet-stream'
                    
                    attachments.append({
                        'filename': file.filename,
                        'content': file_content,
                        'content_type': content_type
                    })
        
        # Create email log
        log = EmailLog(
            account_id=account.id,
            recipient_email=to_emails,
            sender_email=account.email_address,
            subject=subject,
            status=EmailStatus.PENDING
        )
        db.session.add(log)
        db.session.commit()
        
        # Mark as sending
        log.mark_sending()
        
        # Send via SMTP - Use same decryption method as CLI
        encryption_key = current_app.config.get('SECRET_KEY', '')
        smtp_service = SMTPService(encryption_key)
        success, message, message_id = smtp_service.send_email(
            account=account,
            to_email=email_list[0],  # Send to first email, CC the rest
            subject=subject,
            html_content=body_html,
            text_content=body_text,
            cc=email_list[1:] if len(email_list) > 1 else None,
            attachments=attachments if attachments else None
        )
        
        # Update log
        if success:
            log.mark_sent(message_id or '', message)
            logger.info(f"Email sent successfully from {account.email_address} to {to_emails}")
        else:
            log.mark_failed(message)
            logger.error(f"Email send failed: {message}")
        
        return jsonify({
            'success': success,
            'message': message,
            'log_id': log.id
        }), 200 if success else 500
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication error: {e}")
        return jsonify({
            'success': False,
            'message': 'Credenciais SMTP inválidas. Verifique o username e password.'
        }), 401
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"SMTP recipients refused: {e}")
        return jsonify({
            'success': False,
            'message': 'Destinatário recusado pelo servidor SMTP'
        }), 400
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro de envio SMTP. Verifique as configurações da conta de email.'
        }), 500
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro ao enviar email: {str(e)}'
        }), 500


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