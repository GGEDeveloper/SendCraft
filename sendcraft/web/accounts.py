"""Routes para gestão de contas de email."""
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from . import web_bp
from ..models import Domain, EmailAccount, EmailLog
from ..services.smtp_service import SMTPService
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)


@web_bp.route('/accounts')
def accounts_list():
    """Lista todas as contas."""
    try:
        # Filtrar por domínio se especificado
        domain_id = request.args.get('domain_id', type=int)
        
        if domain_id:
            domain = Domain.query.get_or_404(domain_id)
            accounts = EmailAccount.query.filter_by(domain_id=domain_id).all()
            title = f"Contas de {domain.name}"
        else:
            accounts = EmailAccount.query.all()
            title = "Todas as Contas"
            domain = None
        
        # Adicionar estatísticas para cada conta
        accounts_data = []
        for account in accounts:
            account_data = {
                'id': account.id,
                'email_address': account.email_address,
                'display_name': account.display_name,
                'domain_name': account.domain.name,
                'is_active': account.is_active,
                'smtp_server': account.smtp_server,
                'smtp_port': account.smtp_port,
                'daily_limit': account.daily_limit,
                'monthly_limit': account.monthly_limit,
                'emails_sent_today': account.count_emails_sent_today(),
                'emails_sent_month': account.count_emails_sent_this_month(),
                'created_at': account.created_at
            }
            accounts_data.append(account_data)
        
        return render_template('accounts/list.html',
                             accounts=accounts_data,
                             title=title,
                             domain=domain)
    
    except Exception as e:
        logger.error(f"Error listing accounts: {e}", exc_info=True)
        flash('Erro ao carregar contas', 'danger')
        return redirect(url_for('web.dashboard'))


@web_bp.route('/accounts/<int:account_id>')
def account_detail(account_id):
    """Detalhes de uma conta."""
    try:
        account = EmailAccount.query.get_or_404(account_id)
        
        # Estatísticas de envio
        emails_sent_today = account.count_emails_sent_today()
        emails_sent_month = account.count_emails_sent_this_month()
        within_limits, limit_message = account.is_within_limits()
        
        # Logs recentes
        recent_logs = EmailLog.query.filter_by(
            account_id=account_id
        ).order_by(EmailLog.created_at.desc()).limit(20).all()
        
        # Estatísticas por status
        from ..models.log import EmailStatus
        stats = EmailLog.get_stats_by_account(account_id, days=30)
        
        return render_template('accounts/detail.html',
                             account=account,
                             emails_sent_today=emails_sent_today,
                             emails_sent_month=emails_sent_month,
                             within_limits=within_limits,
                             limit_message=limit_message,
                             recent_logs=recent_logs,
                             stats=stats)
    
    except Exception as e:
        logger.error(f"Error loading account {account_id}: {e}", exc_info=True)
        flash('Erro ao carregar detalhes da conta', 'danger')
        return redirect(url_for('web.accounts_list'))


@web_bp.route('/accounts/new', methods=['GET', 'POST'])
def account_new():
    """Criar nova conta."""
    # Buscar domínios para o select
    domains = Domain.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        try:
            domain_id = request.form.get('domain_id', type=int)
            local_part = request.form.get('local_part', '').strip()
            display_name = request.form.get('display_name', '').strip()
            smtp_server = request.form.get('smtp_server', '').strip()
            smtp_port = request.form.get('smtp_port', 587, type=int)
            smtp_username = request.form.get('smtp_username', '').strip()
            smtp_password = request.form.get('smtp_password', '').strip()
            use_tls = request.form.get('use_tls') == 'on'
            use_ssl = request.form.get('use_ssl') == 'on'
            daily_limit = request.form.get('daily_limit', 1000, type=int)
            monthly_limit = request.form.get('monthly_limit', 20000, type=int)
            
            # Validações
            if not domain_id or not local_part:
                flash('Domínio e parte local são obrigatórios', 'danger')
                return render_template('accounts/form.html', account=None, domains=domains)
            
            domain = Domain.query.get(domain_id)
            if not domain:
                flash('Domínio inválido', 'danger')
                return render_template('accounts/form.html', account=None, domains=domains)
            
            # Verificar se já existe
            email_address = f"{local_part}@{domain.name}"
            if EmailAccount.get_by_email(email_address):
                flash(f'Conta {email_address} já existe', 'danger')
                return render_template('accounts/form.html', account=None, domains=domains)
            
            # Criar conta
            account = EmailAccount.create(
                domain_id=domain_id,
                local_part=local_part,
                display_name=display_name,
                smtp_server=smtp_server,
                smtp_port=smtp_port,
                smtp_username=smtp_username or email_address,
                use_tls=use_tls,
                use_ssl=use_ssl,
                daily_limit=daily_limit,
                monthly_limit=monthly_limit,
                is_active=True
            )
            
            # Definir senha se fornecida
            if smtp_password:
                encryption_key = current_app.config.get('ENCRYPTION_KEY')
                account.set_password(smtp_password, encryption_key)
                account.save()
            
            flash(f'Conta {email_address} criada com sucesso!', 'success')
            logger.info(f"Account {email_address} created with ID {account.id}")
            return redirect(url_for('web.account_detail', account_id=account.id))
            
        except Exception as e:
            logger.error(f"Error creating account: {e}", exc_info=True)
            flash('Erro ao criar conta', 'danger')
            db.session.rollback()
    
    return render_template('accounts/form.html', account=None, domains=domains)


@web_bp.route('/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
def account_edit(account_id):
    """Editar conta."""
    account = EmailAccount.query.get_or_404(account_id)
    domains = Domain.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        try:
            account.display_name = request.form.get('display_name', '').strip()
            account.smtp_server = request.form.get('smtp_server', '').strip()
            account.smtp_port = request.form.get('smtp_port', 587, type=int)
            account.smtp_username = request.form.get('smtp_username', '').strip() or account.email_address
            account.use_tls = request.form.get('use_tls') == 'on'
            account.use_ssl = request.form.get('use_ssl') == 'on'
            account.daily_limit = request.form.get('daily_limit', 1000, type=int)
            account.monthly_limit = request.form.get('monthly_limit', 20000, type=int)
            account.is_active = request.form.get('is_active') == 'on'
            
            # Atualizar senha se fornecida
            new_password = request.form.get('smtp_password', '').strip()
            if new_password:
                encryption_key = current_app.config.get('ENCRYPTION_KEY')
                account.set_password(new_password, encryption_key)
            
            account.save()
            
            flash('Conta atualizada com sucesso!', 'success')
            logger.info(f"Account {account.email_address} updated")
            return redirect(url_for('web.account_detail', account_id=account.id))
            
        except Exception as e:
            logger.error(f"Error updating account {account_id}: {e}", exc_info=True)
            flash('Erro ao atualizar conta', 'danger')
            db.session.rollback()
    
    return render_template('accounts/form.html', account=account, domains=domains)


@web_bp.route('/accounts/<int:account_id>/test', methods=['POST'])
def account_test_smtp(account_id):
    """Testar conexão SMTP de uma conta."""
    try:
        account = EmailAccount.query.get_or_404(account_id)
        
        # Testar conexão
        encryption_key = current_app.config.get('ENCRYPTION_KEY')
        smtp_service = SMTPService(encryption_key)
        success, message = smtp_service.test_connection(account)
        
        if success:
            flash(f'Conexão SMTP testada com sucesso!', 'success')
            logger.info(f"SMTP test successful for {account.email_address}")
        else:
            flash(f'Erro no teste SMTP: {message}', 'danger')
            logger.error(f"SMTP test failed for {account.email_address}: {message}")
        
        return redirect(url_for('web.account_detail', account_id=account_id))
        
    except Exception as e:
        logger.error(f"Error testing SMTP for account {account_id}: {e}", exc_info=True)
        flash('Erro ao testar conexão SMTP', 'danger')
        return redirect(url_for('web.account_detail', account_id=account_id))


@web_bp.route('/accounts/<int:account_id>/delete', methods=['POST'])
def account_delete(account_id):
    """Deletar conta."""
    try:
        account = EmailAccount.query.get_or_404(account_id)
        email_address = account.email_address
        domain_id = account.domain_id
        
        # Verificar se tem logs
        if account.logs.count() > 0:
            flash('Não é possível deletar conta com logs de envio', 'warning')
            return redirect(url_for('web.account_detail', account_id=account_id))
        
        account.delete()
        
        flash(f'Conta {email_address} deletada com sucesso!', 'success')
        logger.info(f"Account {email_address} deleted")
        return redirect(url_for('web.accounts_list', domain_id=domain_id))
        
    except Exception as e:
        logger.error(f"Error deleting account {account_id}: {e}", exc_info=True)
        flash('Erro ao deletar conta', 'danger')
        db.session.rollback()
        return redirect(url_for('web.account_detail', account_id=account_id))