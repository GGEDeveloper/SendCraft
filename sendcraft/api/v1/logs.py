"""Endpoints de logs e estatísticas."""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

from ...models import Domain, EmailAccount, EmailLog
from ...models.log import EmailStatus
from ...services.auth_service import require_api_key
from ...utils.logging import get_logger

bp = Blueprint('logs', __name__)
logger = get_logger(__name__)


@bp.route('/logs', methods=['GET'])
@require_api_key
def list_logs():
    """
    Lista logs de emails.
    
    Query Parameters:
        domain: Filtrar por domínio
        account: Filtrar por email da conta
        recipient: Filtrar por email do destinatário
        status: Filtrar por status (pending/sent/failed/delivered)
        days: Número de dias para buscar (default: 7)
        limit: Número máximo de resultados (default: 50, max: 500)
        offset: Offset para paginação (default: 0)
        sort: Ordenação (created_at_desc/created_at_asc, default: created_at_desc)
    
    Returns:
        JSON response with list of email logs
    """
    try:
        # Parâmetros de query
        domain_filter = request.args.get('domain')
        account_filter = request.args.get('account')
        recipient_filter = request.args.get('recipient')
        status_filter = request.args.get('status')
        days = int(request.args.get('days', 7))
        limit = min(int(request.args.get('limit', 50)), 500)
        offset = int(request.args.get('offset', 0))
        sort = request.args.get('sort', 'created_at_desc')
        
        # Construir query
        query = EmailLog.query
        
        # Filtro por período
        if days > 0:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(EmailLog.created_at >= cutoff_date)
        
        # Filtro por domínio
        if domain_filter:
            domain_obj = Domain.get_by_name(domain_filter)
            if domain_obj:
                # Buscar contas do domínio
                account_ids = [acc.id for acc in domain_obj.accounts]
                if account_ids:
                    query = query.filter(EmailLog.account_id.in_(account_ids))
        
        # Filtro por conta
        if account_filter:
            account_obj = EmailAccount.get_by_email(account_filter)
            if account_obj:
                query = query.filter_by(account_id=account_obj.id)
        
        # Filtro por destinatário
        if recipient_filter:
            query = query.filter(EmailLog.recipient_email.like(f'%{recipient_filter}%'))
        
        # Filtro por status
        if status_filter:
            try:
                status_enum = EmailStatus(status_filter)
                query = query.filter_by(status=status_enum)
            except ValueError:
                logger.warning(f"Invalid status filter: {status_filter}")
        
        # Ordenação
        if sort == 'created_at_asc':
            query = query.order_by(EmailLog.created_at.asc())
        else:
            query = query.order_by(EmailLog.created_at.desc())
        
        # Total antes de paginar
        total = query.count()
        
        # Aplicar paginação
        logs = query.limit(limit).offset(offset).all()
        
        # Serializar logs
        logs_data = []
        for log in logs:
            try:
                log_dict = {
                    'id': log.id,
                    'account': log.account.email_address if log.account else None,
                    'recipient_email': log.recipient_email,
                    'sender_email': log.sender_email,
                    'subject': log.subject,
                    'status': log.status.value if log.status else 'unknown',
                    'message_id': log.message_id,
                    'template_used': log.template.template_key if log.template else None,
                    'created_at': log.created_at.isoformat() + 'Z',
                    'sent_at': log.sent_at.isoformat() + 'Z' if log.sent_at else None,
                    'delivered_at': log.delivered_at.isoformat() + 'Z' if log.delivered_at else None
                }
                
                # Incluir erro se houver
                if log.status == EmailStatus.FAILED and log.error_message:
                    log_dict['error_message'] = log.error_message
                
                logs_data.append(log_dict)
            except Exception as e:
                logger.error(f"Error serializing log {log.id}: {e}")
                continue
        
        logger.info(f"Listed {len(logs_data)} logs (total: {total})")
        
        return jsonify({
            'total': total,
            'limit': limit,
            'offset': offset,
            'count': len(logs_data),
            'filters': {
                'domain': domain_filter,
                'account': account_filter,
                'recipient': recipient_filter,
                'status': status_filter,
                'days': days,
                'sort': sort
            },
            'logs': logs_data
        })
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid parameters',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error listing logs: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve logs'
        }), 500


@bp.route('/logs/<int:log_id>', methods=['GET'])
@require_api_key
def get_log(log_id: int):
    """
    Obtém detalhes de um log específico.
    
    Args:
        log_id: ID do log
    
    Returns:
        JSON response with log details
    """
    try:
        log = EmailLog.get_by_id(log_id)
        
        if not log:
            return jsonify({
                'error': 'Log not found',
                'message': f"Log with ID {log_id} not found"
            }), 404
        
        # Serializar log completo
        log_data = {
            'id': log.id,
            'account': {
                'id': log.account.id if log.account else None,
                'email': log.account.email_address if log.account else None,
                'domain': log.account.domain.name if log.account and log.account.domain else None
            },
            'template': {
                'id': log.template.id if log.template else None,
                'key': log.template.template_key if log.template else None,
                'name': log.template.template_name if log.template else None
            } if log.template else None,
            'recipient_email': log.recipient_email,
            'sender_email': log.sender_email,
            'subject': log.subject,
            'status': log.status.value if log.status else 'unknown',
            'message_id': log.message_id,
            'smtp_response': log.smtp_response,
            'error_message': log.error_message,
            'variables_used': log.variables_used,
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'timestamps': {
                'created_at': log.created_at.isoformat() + 'Z',
                'sent_at': log.sent_at.isoformat() + 'Z' if log.sent_at else None,
                'delivered_at': log.delivered_at.isoformat() + 'Z' if log.delivered_at else None,
                'opened_at': log.opened_at.isoformat() + 'Z' if log.opened_at else None,
                'clicked_at': log.clicked_at.isoformat() + 'Z' if log.clicked_at else None
            }
        }
        
        logger.info(f"Retrieved log details for ID {log_id}")
        
        return jsonify(log_data)
        
    except Exception as e:
        logger.error(f"Error getting log {log_id}: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve log details'
        }), 500


@bp.route('/stats/account/<int:account_id>', methods=['GET'])
@require_api_key
def get_account_stats(account_id: int):
    """
    Obtém estatísticas de uma conta.
    
    Args:
        account_id: ID da conta
    
    Query Parameters:
        days: Número de dias para análise (default: 30)
    
    Returns:
        JSON response with account statistics
    """
    try:
        # Verificar se conta existe
        account = EmailAccount.get_by_id(account_id)
        if not account:
            return jsonify({
                'error': 'Account not found',
                'message': f"Account with ID {account_id} not found"
            }), 404
        
        # Parâmetros
        days = int(request.args.get('days', 30))
        
        # Obter estatísticas
        stats = EmailLog.get_stats_by_account(account_id, days)
        
        # Adicionar informações da conta
        stats_data = {
            'account': {
                'id': account.id,
                'email': account.email_address,
                'domain': account.domain.name if account.domain else None,
                'is_active': account.is_active
            },
            'period_days': days,
            'limits': {
                'daily_limit': account.daily_limit,
                'monthly_limit': account.monthly_limit,
                'emails_sent_today': account.count_emails_sent_today(),
                'emails_sent_this_month': account.count_emails_sent_this_month()
            },
            'stats_by_status': stats,
            'total_emails': sum(stats.values()),
            'success_rate': calculate_success_rate(stats)
        }
        
        logger.info(f"Retrieved stats for account {account_id}")
        
        return jsonify(stats_data)
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid parameters',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error getting account stats: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve account statistics'
        }), 500


@bp.route('/stats/domain/<domain>', methods=['GET'])
@require_api_key
def get_domain_stats(domain: str):
    """
    Obtém estatísticas de um domínio.
    
    Args:
        domain: Nome do domínio
    
    Query Parameters:
        days: Número de dias para análise (default: 30)
    
    Returns:
        JSON response with domain statistics
    """
    try:
        # Verificar se domínio existe
        domain_obj = Domain.get_by_name(domain)
        if not domain_obj:
            return jsonify({
                'error': 'Domain not found',
                'message': f"Domain '{domain}' not found"
            }), 404
        
        # Parâmetros
        days = int(request.args.get('days', 30))
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Obter estatísticas por conta
        accounts_stats = {}
        total_stats = {}
        
        for account in domain_obj.accounts:
            account_stats = EmailLog.get_stats_by_account(account.id, days)
            accounts_stats[account.email_address] = account_stats
            
            # Somar ao total
            for status, count in account_stats.items():
                total_stats[status] = total_stats.get(status, 0) + count
        
        # Preparar resposta
        stats_data = {
            'domain': {
                'name': domain_obj.name,
                'is_active': domain_obj.is_active,
                'total_accounts': domain_obj.count_accounts(),
                'active_accounts': domain_obj.count_active_accounts(),
                'total_templates': domain_obj.count_templates()
            },
            'period_days': days,
            'stats_by_status': total_stats,
            'total_emails': sum(total_stats.values()),
            'success_rate': calculate_success_rate(total_stats),
            'accounts_breakdown': accounts_stats
        }
        
        logger.info(f"Retrieved stats for domain {domain}")
        
        return jsonify(stats_data)
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid parameters',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error getting domain stats: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve domain statistics'
        }), 500


@bp.route('/stats/global', methods=['GET'])
@require_api_key
def get_global_stats():
    """
    Obtém estatísticas globais do sistema.
    
    Query Parameters:
        days: Número de dias para análise (default: 30)
    
    Returns:
        JSON response with global statistics
    """
    try:
        # Parâmetros
        days = int(request.args.get('days', 30))
        
        # Obter estatísticas globais
        stats = EmailLog.get_global_stats(days)
        
        # Adicionar informações do sistema
        from ...models import Domain, EmailAccount, EmailTemplate
        
        stats['system'] = {
            'total_domains': Domain.query.count(),
            'active_domains': Domain.query.filter_by(is_active=True).count(),
            'total_accounts': EmailAccount.query.count(),
            'active_accounts': EmailAccount.query.filter_by(is_active=True).count(),
            'total_templates': EmailTemplate.query.count(),
            'active_templates': EmailTemplate.query.filter_by(is_active=True).count()
        }
        
        logger.info("Retrieved global stats")
        
        return jsonify(stats)
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid parameters',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error getting global stats: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve global statistics'
        }), 500


def calculate_success_rate(stats: dict) -> float:
    """
    Calcula taxa de sucesso baseada nas estatísticas.
    
    Args:
        stats: Dicionário com contagens por status
    
    Returns:
        Taxa de sucesso em porcentagem
    """
    total = sum(stats.values())
    if total == 0:
        return 0.0
    
    success_statuses = ['sent', 'delivered', 'opened', 'clicked']
    success_count = sum(stats.get(status, 0) for status in success_statuses)
    
    return round((success_count / total) * 100, 2)