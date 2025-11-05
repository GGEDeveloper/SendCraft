"""API v1 - Endpoints para visão de emails por domínio."""
from flask import Blueprint, jsonify, request, current_app
from flask_cors import cross_origin
from typing import Dict, Any, List
from datetime import datetime, timedelta

from ...models import Domain, EmailAccount, EmailInbox, EmailLog
from ...models.log import EmailStatus
from ...services.imap_service import IMAPService
from ...extensions import db
from ...utils.logging import get_logger
from ..errors import NotFound, ServerError

logger = get_logger(__name__)

# Criar blueprint
bp = Blueprint('domain_emails', __name__, url_prefix='/domains')


@bp.route('/<int:domain_id>/sync-all', methods=['POST'])
@cross_origin()
def sync_all_accounts(domain_id: int):
    """
    Sincroniza todas as contas ativas de um domínio.
    
    POST /api/v1/domains/<domain_id>/sync-all
    
    Request Body (opcional):
        folder: Pasta para sincronizar (default: INBOX)
        limit: Limite de emails por conta (default: 50)
        full_sync: Sincronização completa (default: false)
    
    Returns:
        200: Sincronização bem sucedida
        404: Domínio não encontrado
        500: Erro de sincronização
    """
    try:
        # Buscar domínio
        domain = Domain.query.get(domain_id)
        if not domain:
            raise NotFound(f"Domain {domain_id} not found")
        
        # Parâmetros do body
        data = request.get_json() or {}
        folder = data.get('folder', 'INBOX')
        limit = data.get('limit', 50)
        full_sync = data.get('full_sync', False)
        
        # Validar parâmetros
        if limit < 1 or limit > 200:
            limit = 50
        
        # Buscar todas as contas ativas do domínio
        accounts = EmailAccount.query.filter_by(
            domain_id=domain_id,
            is_active=True
        ).all()
        
        if not accounts:
            return jsonify({
                'success': True,
                'message': 'No active accounts found for this domain',
                'synced_accounts': 0,
                'total_synced': 0
            }), 200
        
        # Sincronizar cada conta
        encryption_key = current_app.config.get('ENCRYPTION_KEY') or current_app.config.get('SECRET_KEY', '')
        results = []
        total_synced = 0
        
        for account in accounts:
            try:
                imap_service = IMAPService(account)
                config = account.get_imap_config(encryption_key)
                
                if not imap_service.connect(config):
                    results.append({
                        'account': account.email_address,
                        'success': False,
                        'error': 'Failed to connect to IMAP server',
                        'synced_count': 0
                    })
                    continue
                
                try:
                    synced_count = imap_service.sync_account_emails(
                        account=account,
                        folder=folder,
                        limit=limit,
                        since_last_sync=not full_sync
                    )
                    total_synced += synced_count
                    results.append({
                        'account': account.email_address,
                        'success': True,
                        'synced_count': synced_count
                    })
                finally:
                    imap_service.disconnect()
                    
            except Exception as e:
                logger.error(f"Error syncing account {account.email_address}: {e}")
                results.append({
                    'account': account.email_address,
                    'success': False,
                    'error': str(e),
                    'synced_count': 0
                })
        
        successful = sum(1 for r in results if r.get('success'))
        
        return jsonify({
            'success': True,
            'domain': domain.name,
            'synced_accounts': successful,
            'total_accounts': len(accounts),
            'total_synced': total_synced,
            'results': results
        }), 200
        
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error syncing domain {domain_id}: {e}")
        return jsonify({'error': f'Sync failed: {str(e)}'}), 500


@bp.route('/<int:domain_id>/emails/received', methods=['GET'])
@cross_origin()
def get_received_emails(domain_id: int):
    """
    Busca últimos emails recebidos de todas as contas do domínio.
    
    GET /api/v1/domains/<domain_id>/emails/received
    
    Query Parameters:
        limit: Número de emails (default: 50, max: 200)
        days: Últimos N dias (default: 30)
        account_id: Filtrar por conta específica (opcional)
    
    Returns:
        200: Lista de emails recebidos
        404: Domínio não encontrado
    """
    try:
        domain = Domain.query.get(domain_id)
        if not domain:
            raise NotFound(f"Domain {domain_id} not found")
        
        # Parâmetros
        limit = min(request.args.get('limit', 50, type=int), 200)
        days = request.args.get('days', 30, type=int)
        account_id = request.args.get('account_id', type=int)
        
        # Data mínima
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Query base
        query = EmailInbox.query.join(EmailAccount).filter(
            EmailAccount.domain_id == domain_id,
            EmailInbox.is_deleted == False,
            EmailInbox.received_at >= since_date
        )
        
        # Filtrar por conta se especificado
        if account_id:
            query = query.filter(EmailInbox.account_id == account_id)
        
        # Ordenar por data de recebimento (mais recente primeiro)
        emails = query.order_by(EmailInbox.received_at.desc()).limit(limit).all()
        
        # Serializar
        emails_data = []
        for email in emails:
            emails_data.append({
                'id': email.id,
                'account_id': email.account_id,
                'account_email': email.account.email_address,
                'from_address': email.from_address,
                'from_name': email.from_name,
                'subject': email.subject,
                'body_preview': (email.body_text or email.body_html or '')[:200] if email.body_text or email.body_html else '',
                'received_at': email.received_at.isoformat() if email.received_at else None,
                'is_read': email.is_read,
                'is_flagged': email.is_flagged,
                'has_attachments': email.has_attachments,
                'folder': email.folder
            })
        
        return jsonify({
            'success': True,
            'domain': domain.name,
            'count': len(emails_data),
            'emails': emails_data
        }), 200
        
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching received emails for domain {domain_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:domain_id>/emails/sent', methods=['GET'])
@cross_origin()
def get_sent_emails(domain_id: int):
    """
    Busca últimos emails enviados de todas as contas do domínio.
    
    GET /api/v1/domains/<domain_id>/emails/sent
    
    Query Parameters:
        limit: Número de emails (default: 50, max: 200)
        days: Últimos N dias (default: 30)
        account_id: Filtrar por conta específica (opcional)
        status: Filtrar por status (sent, delivered, failed, etc.)
    
    Returns:
        200: Lista de emails enviados
        404: Domínio não encontrado
    """
    try:
        domain = Domain.query.get(domain_id)
        if not domain:
            raise NotFound(f"Domain {domain_id} not found")
        
        # Parâmetros
        limit = min(request.args.get('limit', 50, type=int), 200)
        days = request.args.get('days', 30, type=int)
        account_id = request.args.get('account_id', type=int)
        status_filter = request.args.get('status')
        
        # Data mínima
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Query base
        query = EmailLog.query.join(EmailAccount).filter(
            EmailAccount.domain_id == domain_id,
            EmailLog.sent_at >= since_date
        )
        
        # Filtros opcionais
        if account_id:
            query = query.filter(EmailLog.account_id == account_id)
        
        if status_filter:
            try:
                status_enum = EmailStatus(status_filter)
                query = query.filter(EmailLog.status == status_enum)
            except ValueError:
                pass  # Status inválido, ignorar
        
        # Ordenar por data de envio (mais recente primeiro)
        logs = query.order_by(EmailLog.sent_at.desc()).limit(limit).all()
        
        # Serializar
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log.id,
                'account_id': log.account_id,
                'account_email': log.account.email_address,
                'recipient_email': log.recipient_email,
                'subject': log.subject,
                'status': log.status.value,
                'sent_at': log.sent_at.isoformat() if log.sent_at else None,
                'delivered_at': log.delivered_at.isoformat() if log.delivered_at else None,
                'error_message': log.error_message,
                'message_id': log.message_id
            })
        
        return jsonify({
            'success': True,
            'domain': domain.name,
            'count': len(logs_data),
            'emails': logs_data
        }), 200
        
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching sent emails for domain {domain_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:domain_id>/emails/unread', methods=['GET'])
@cross_origin()
def get_unread_emails(domain_id: int):
    """
    Busca todos os emails não lidos de todas as contas do domínio.
    
    GET /api/v1/domains/<domain_id>/emails/unread
    
    Query Parameters:
        limit: Número de emails (default: 100, max: 500)
        account_id: Filtrar por conta específica (opcional)
        folder: Filtrar por pasta (default: INBOX)
    
    Returns:
        200: Lista de emails não lidos
        404: Domínio não encontrado
    """
    try:
        domain = Domain.query.get(domain_id)
        if not domain:
            raise NotFound(f"Domain {domain_id} not found")
        
        # Parâmetros
        limit = min(request.args.get('limit', 100, type=int), 500)
        account_id = request.args.get('account_id', type=int)
        folder = request.args.get('folder', 'INBOX')
        
        # Query base
        query = EmailInbox.query.join(EmailAccount).filter(
            EmailAccount.domain_id == domain_id,
            EmailInbox.is_deleted == False,
            EmailInbox.is_read == False,
            EmailInbox.folder == folder
        )
        
        # Filtrar por conta se especificado
        if account_id:
            query = query.filter(EmailInbox.account_id == account_id)
        
        # Ordenar por data de recebimento (mais recente primeiro)
        emails = query.order_by(EmailInbox.received_at.desc()).limit(limit).all()
        
        # Serializar
        emails_data = []
        for email in emails:
            emails_data.append({
                'id': email.id,
                'account_id': email.account_id,
                'account_email': email.account.email_address,
                'from_address': email.from_address,
                'from_name': email.from_name,
                'subject': email.subject,
                'body_preview': (email.body_text or email.body_html or '')[:200] if email.body_text or email.body_html else '',
                'received_at': email.received_at.isoformat() if email.received_at else None,
                'is_flagged': email.is_flagged,
                'has_attachments': email.has_attachments,
                'folder': email.folder
            })
        
        return jsonify({
            'success': True,
            'domain': domain.name,
            'count': len(emails_data),
            'unread_count': len(emails_data),
            'emails': emails_data
        }), 200
        
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching unread emails for domain {domain_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:domain_id>/stats', methods=['GET'])
@cross_origin()
def get_domain_email_stats(domain_id: int):
    """
    Estatísticas de emails do domínio.
    
    GET /api/v1/domains/<domain_id>/stats
    
    Returns:
        200: Estatísticas do domínio
        404: Domínio não encontrado
    """
    try:
        domain = Domain.query.get(domain_id)
        if not domain:
            raise NotFound(f"Domain {domain_id} not found")
        
        # Contas do domínio
        accounts = EmailAccount.query.filter_by(domain_id=domain_id, is_active=True).all()
        
        # Estatísticas de emails recebidos
        total_received = EmailInbox.query.join(EmailAccount).filter(
            EmailAccount.domain_id == domain_id,
            EmailInbox.is_deleted == False
        ).count()
        
        unread_received = EmailInbox.query.join(EmailAccount).filter(
            EmailAccount.domain_id == domain_id,
            EmailInbox.is_deleted == False,
            EmailInbox.is_read == False
        ).count()
        
        # Estatísticas de emails enviados (últimos 30 dias)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        sent_30d = EmailLog.query.join(EmailAccount).filter(
            EmailAccount.domain_id == domain_id,
            EmailLog.sent_at >= thirty_days_ago,
            EmailLog.status.in_([EmailStatus.SENT, EmailStatus.DELIVERED])
        ).count()
        
        failed_30d = EmailLog.query.join(EmailAccount).filter(
            EmailAccount.domain_id == domain_id,
            EmailLog.sent_at >= thirty_days_ago,
            EmailLog.status == EmailStatus.FAILED
        ).count()
        
        # Recebidos hoje
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        received_today = EmailInbox.query.join(EmailAccount).filter(
            EmailAccount.domain_id == domain_id,
            EmailInbox.is_deleted == False,
            EmailInbox.received_at >= today
        ).count()
        
        return jsonify({
            'success': True,
            'domain': domain.name,
            'accounts_count': len(accounts),
            'received': {
                'total': total_received,
                'unread': unread_received,
                'today': received_today
            },
            'sent': {
                'last_30_days': sent_30d,
                'failed_last_30_days': failed_30d
            }
        }), 200
        
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching stats for domain {domain_id}: {e}")
        return jsonify({'error': str(e)}), 500

