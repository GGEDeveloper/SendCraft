"""Routes para visualização de logs."""
from flask import render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta
from sqlalchemy import or_
from . import web_bp
from ..models import EmailLog, Domain, EmailAccount, EmailTemplate
from ..models.log import EmailStatus
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)


@web_bp.route('/logs')
def logs_list():
    """Lista de logs de email com filtros."""
    try:
        # Parâmetros de filtro
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        status_filter = request.args.get('status')
        domain_filter = request.args.get('domain')
        account_filter = request.args.get('account')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        search = request.args.get('search')
        
        # Query base
        query = EmailLog.query
        
        # Aplicar filtros
        if status_filter:
            try:
                status = EmailStatus(status_filter)
                query = query.filter_by(status=status)
            except ValueError:
                pass
        
        if domain_filter:
            domain = Domain.get_by_name(domain_filter)
            if domain:
                account_ids = [acc.id for acc in domain.accounts]
                if account_ids:
                    query = query.filter(EmailLog.account_id.in_(account_ids))
        
        if account_filter:
            account = EmailAccount.get_by_email(account_filter)
            if account:
                query = query.filter_by(account_id=account.id)
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(EmailLog.created_at >= from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(EmailLog.created_at < to_date)
            except ValueError:
                pass
        
        if search:
            query = query.filter(
                db.or_(
                    EmailLog.recipient_email.like(f'%{search}%'),
                    EmailLog.subject.like(f'%{search}%'),
                    EmailLog.message_id.like(f'%{search}%')
                )
            )
        
        # Ordenar por data decrescente
        query = query.order_by(EmailLog.created_at.desc())
        
        # Paginar
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        logs = pagination.items
        
        # Obter listas para filtros
        domains = Domain.query.filter_by(is_active=True).all()
        accounts = EmailAccount.query.filter_by(is_active=True).all()
        statuses = [status.value for status in EmailStatus]
        
        return render_template('logs/list.html',
                             logs=logs,
                             pagination=pagination,
                             domains=domains,
                             accounts=accounts,
                             statuses=statuses,
                             filters={
                                 'status': status_filter,
                                 'domain': domain_filter,
                                 'account': account_filter,
                                 'date_from': date_from,
                                 'date_to': date_to,
                                 'search': search
                             })
    
    except Exception as e:
        logger.error(f"Error listing logs: {e}", exc_info=True)
        flash('Erro ao carregar logs', 'danger')
        return redirect(url_for('web.dashboard'))


@web_bp.route('/logs/<int:log_id>')
def log_detail(log_id):
    """Detalhes completos de um log."""
    try:
        log = EmailLog.query.get_or_404(log_id)
        
        # Preparar dados para exibição
        log_data = {
            'id': log.id,
            'status': log.status.value if log.status else 'unknown',
            'account': log.account.email_address if log.account else 'N/A',
            'domain': log.account.domain.name if log.account and log.account.domain else 'N/A',
            'template': log.template.template_name if log.template else 'Envio direto',
            'template_key': log.template.template_key if log.template else None,
            'recipient_email': log.recipient_email,
            'sender_email': log.sender_email,
            'subject': log.subject,
            'message_id': log.message_id,
            'smtp_response': log.smtp_response,
            'error_message': log.error_message,
            'variables_used': log.variables_used,
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'created_at': log.created_at,
            'sent_at': log.sent_at,
            'delivered_at': log.delivered_at,
            'opened_at': log.opened_at,
            'clicked_at': log.clicked_at
        }
        
        # Calcular duração se enviado
        if log.sent_at and log.created_at:
            duration = log.sent_at - log.created_at
            log_data['duration_seconds'] = duration.total_seconds()
        else:
            log_data['duration_seconds'] = None
        
        return render_template('logs/detail.html', log=log_data)
    
    except Exception as e:
        logger.error(f"Error loading log {log_id}: {e}", exc_info=True)
        flash('Erro ao carregar detalhes do log', 'danger')
        return redirect(url_for('web.logs_list'))


@web_bp.route('/logs/<int:log_id>/resend', methods=['POST'])
def log_resend(log_id):
    """Reenviar email baseado em um log."""
    try:
        log = EmailLog.query.get_or_404(log_id)
        
        # Criar novo log como cópia
        new_log = EmailLog(
            account_id=log.account_id,
            template_id=log.template_id,
            recipient_email=log.recipient_email,
            sender_email=log.sender_email,
            subject=log.subject,
            status=EmailStatus.PENDING,
            variables_used=log.variables_used,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(new_log)
        db.session.commit()
        
        # TODO: Implementar reenvio real via EmailService
        flash('Email adicionado à fila de reenvio', 'info')
        logger.info(f"Log {log_id} queued for resend as log {new_log.id}")
        
        return redirect(url_for('web.log_detail', log_id=new_log.id))
        
    except Exception as e:
        logger.error(f"Error resending log {log_id}: {e}", exc_info=True)
        flash('Erro ao reenviar email', 'danger')
        return redirect(url_for('web.log_detail', log_id=log_id))


@web_bp.route('/logs/export')
def logs_export():
    """Exportar logs para CSV."""
    try:
        import csv
        from io import StringIO
        from flask import Response
        
        # Aplicar mesmos filtros da listagem
        query = EmailLog.query
        
        # TODO: Aplicar filtros da query string
        
        # Limitar a 10000 registros
        logs = query.order_by(EmailLog.created_at.desc()).limit(10000).all()
        
        # Criar CSV
        si = StringIO()
        writer = csv.writer(si)
        
        # Header
        writer.writerow([
            'ID', 'Data/Hora', 'Status', 'Remetente', 'Destinatário',
            'Assunto', 'Template', 'Message ID', 'Erro'
        ])
        
        # Dados
        for log in logs:
            writer.writerow([
                log.id,
                log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                log.status.value if log.status else '',
                log.sender_email,
                log.recipient_email,
                log.subject,
                log.template.template_name if log.template else '',
                log.message_id or '',
                log.error_message or ''
            ])
        
        # Preparar response
        output = si.getvalue()
        si.close()
        
        response = Response(output, mimetype='text/csv')
        response.headers['Content-Disposition'] = f'attachment; filename=sendcraft_logs_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
        
        logger.info(f"Exported {len(logs)} logs to CSV")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting logs: {e}", exc_info=True)
        flash('Erro ao exportar logs', 'danger')
        return redirect(url_for('web.logs_list'))