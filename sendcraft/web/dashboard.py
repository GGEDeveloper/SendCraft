"""Routes do dashboard principal."""
from flask import render_template, jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import func

from . import web_bp
from ..models import Domain, EmailAccount, EmailTemplate, EmailLog
from ..models.log import EmailStatus
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)


@web_bp.route('/')
def dashboard():
    """Dashboard principal com estatísticas."""
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
                EmailLog.status == EmailStatus.SENT
            ).count(),
            'failed_24h': EmailLog.query.filter(
                EmailLog.created_at >= yesterday, 
                EmailLog.status == EmailStatus.FAILED
            ).count(),
            'delivered_24h': EmailLog.query.filter(
                EmailLog.created_at >= yesterday,
                EmailLog.status == EmailStatus.DELIVERED
            ).count(),
            'total_24h': EmailLog.query.filter(
                EmailLog.created_at >= yesterday
            ).count()
        }
        
        # Taxa de sucesso
        if email_stats['total_24h'] > 0:
            email_stats['success_rate'] = round(
                (email_stats['sent_24h'] + email_stats['delivered_24h']) / 
                email_stats['total_24h'] * 100, 1
            )
        else:
            email_stats['success_rate'] = 0
        
        # Domínios para lista com contadores
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
        
        logger.info("Dashboard loaded successfully")
        
        return render_template('dashboard.html',
                             stats=stats,
                             email_stats=email_stats,
                             recent_logs=recent_logs,
                             domains=domains)
    
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}", exc_info=True)
        return render_template('error.html', error="Failed to load dashboard"), 500


@web_bp.route('/api/stats')
def api_stats():
    """API para estatísticas do dashboard (gráficos)."""
    try:
        # Parâmetros
        days = int(request.args.get('days', 7))
        
        # Estatísticas por dia
        daily_stats = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            # Contar emails por status
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
            
            pending_count = EmailLog.query.filter(
                EmailLog.created_at >= start_date,
                EmailLog.created_at < end_date,
                EmailLog.status == EmailStatus.PENDING
            ).count()
            
            daily_stats.append({
                'date': start_date.strftime('%Y-%m-%d'),
                'day_label': start_date.strftime('%d %b'),
                'sent': sent_count,
                'failed': failed_count,
                'pending': pending_count,
                'total': sent_count + failed_count + pending_count
            })
        
        # Inverter para ordem cronológica
        daily_stats.reverse()
        
        # Top domínios por volume
        top_domains = db.session.query(
            Domain.name,
            func.count(EmailLog.id).label('count')
        ).join(
            EmailAccount, Domain.id == EmailAccount.domain_id
        ).join(
            EmailLog, EmailAccount.id == EmailLog.account_id
        ).filter(
            EmailLog.created_at >= datetime.utcnow() - timedelta(days=days)
        ).group_by(Domain.name).order_by(func.count(EmailLog.id).desc()).limit(5).all()
        
        # Top templates usados
        top_templates = db.session.query(
            EmailTemplate.template_name,
            func.count(EmailLog.id).label('count')
        ).join(
            EmailLog, EmailTemplate.id == EmailLog.template_id
        ).filter(
            EmailLog.created_at >= datetime.utcnow() - timedelta(days=days),
            EmailLog.template_id.isnot(None)
        ).group_by(EmailTemplate.template_name).order_by(func.count(EmailLog.id).desc()).limit(5).all()
        
        return jsonify({
            'daily_stats': daily_stats,
            'top_domains': [{'name': d.name, 'count': d.count} for d in top_domains],
            'top_templates': [{'name': t.template_name, 'count': t.count} for t in top_templates],
            'period_days': days
        })
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return jsonify({'error': 'Failed to load statistics'}), 500


@web_bp.route('/api/dashboard/refresh')
def refresh_dashboard_stats():
    """Refresh dashboard statistics via HTMX."""
    try:
        # Estatísticas de envio (últimas 24h)
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        sent_count = EmailLog.query.filter(
            EmailLog.created_at >= yesterday,
            EmailLog.status.in_([EmailStatus.SENT, EmailStatus.DELIVERED])
        ).count()
        
        failed_count = EmailLog.query.filter(
            EmailLog.created_at >= yesterday, 
            EmailLog.status == EmailStatus.FAILED
        ).count()
        
        # Logs recentes
        recent_logs = EmailLog.query.order_by(EmailLog.created_at.desc()).limit(5).all()
        
        return render_template('partials/dashboard_stats.html',
                             sent_24h=sent_count,
                             failed_24h=failed_count,
                             recent_logs=recent_logs)
    
    except Exception as e:
        logger.error(f"Error refreshing dashboard: {e}")
        return "", 500