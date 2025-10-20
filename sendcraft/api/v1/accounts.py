"""Endpoints de gestão de contas."""
from flask import Blueprint, jsonify, request, current_app
from typing import Dict, Any

from ...models import Domain, EmailAccount
from ...services.auth_service import require_api_key
from ...extensions import db
from ...utils.logging import get_logger

bp = Blueprint('accounts', __name__, url_prefix='/accounts')
logger = get_logger(__name__)


@bp.route('/<domain>', methods=['GET'])
@require_api_key
def list_accounts(domain: str):
    """
    Lista contas de um domínio.
    
    Args:
        domain: Nome do domínio
    
    Query Parameters:
        active_only: Se deve retornar apenas contas ativas (default: false)
    
    Returns:
        JSON response with list of accounts
    """
    try:
        # Buscar domínio
        domain_obj = Domain.get_by_name(domain)
        if not domain_obj:
            return jsonify({
                'error': 'Domain not found',
                'message': f"Domain '{domain}' not found",
                'domain': domain,
                'accounts': []
            }), 404
        
        # Filtrar por status se solicitado
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        if active_only:
            accounts = EmailAccount.query.filter_by(
                domain_id=domain_obj.id,
                is_active=True
            ).all()
        else:
            accounts = EmailAccount.query.filter_by(domain_id=domain_obj.id).all()
        
        # Serializar contas
        accounts_data = []
        for acc in accounts:
            try:
                account_dict = {
                    'id': acc.id,
                    'local_part': acc.local_part,
                    'email_address': acc.email_address,
                    'display_name': acc.display_name,
                    'is_active': acc.is_active,
                    'smtp_server': acc.smtp_server,
                    'smtp_port': acc.smtp_port,
                    'use_tls': acc.use_tls,
                    'use_ssl': acc.use_ssl,
                    'daily_limit': acc.daily_limit,
                    'monthly_limit': acc.monthly_limit,
                    'emails_sent_today': acc.count_emails_sent_today(),
                    'emails_sent_this_month': acc.count_emails_sent_this_month(),
                    'created_at': acc.created_at.isoformat() + 'Z',
                    'updated_at': acc.updated_at.isoformat() + 'Z'
                }
                accounts_data.append(account_dict)
            except Exception as e:
                logger.error(f"Error serializing account {acc.id}: {e}")
                continue
        
        logger.info(f"Listed {len(accounts_data)} accounts for domain {domain}")
        
        return jsonify({
            'domain': domain,
            'domain_active': domain_obj.is_active,
            'total_accounts': len(accounts_data),
            'active_filter': active_only,
            'accounts': accounts_data
        })
        
    except Exception as e:
        logger.error(f"Error listing accounts for domain {domain}: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve accounts'
        }), 500


@bp.route('/<domain>/<local_part>', methods=['GET'])
@require_api_key
def get_account(domain: str, local_part: str):
    """
    Obtém detalhes de uma conta específica.
    
    Args:
        domain: Nome do domínio
        local_part: Parte local do email (antes do @)
    
    Returns:
        JSON response with account details
    """
    try:
        email_address = f"{local_part}@{domain}"
        account = EmailAccount.get_by_email(email_address)
        
        if not account:
            return jsonify({
                'error': 'Account not found',
                'message': f"Account '{email_address}' not found"
            }), 404
        
        # Obter estatísticas de envio
        try:
            emails_today = account.count_emails_sent_today()
            emails_month = account.count_emails_sent_this_month()
            within_limits, limit_message = account.is_within_limits()
        except Exception as e:
            logger.error(f"Error getting account stats: {e}")
            emails_today = 0
            emails_month = 0
            within_limits = True
            limit_message = "Unable to check limits"
        
        # Serializar conta com detalhes completos
        account_data = {
            'id': account.id,
            'local_part': account.local_part,
            'email_address': account.email_address,
            'display_name': account.display_name,
            'is_active': account.is_active,
            'smtp_server': account.smtp_server,
            'smtp_port': account.smtp_port,
            'smtp_username': account.smtp_username,
            'use_tls': account.use_tls,
            'use_ssl': account.use_ssl,
            'daily_limit': account.daily_limit,
            'monthly_limit': account.monthly_limit,
            'emails_sent_today': emails_today,
            'emails_sent_this_month': emails_month,
            'within_limits': within_limits,
            'limit_message': limit_message,
            'domain': {
                'id': account.domain.id,
                'name': account.domain.name,
                'is_active': account.domain.is_active,
                'description': account.domain.description
            },
            'created_at': account.created_at.isoformat() + 'Z',
            'updated_at': account.updated_at.isoformat() + 'Z'
        }
        
        logger.info(f"Retrieved account details for {email_address}")
        
        return jsonify(account_data)
        
    except Exception as e:
        logger.error(f"Error getting account {local_part}@{domain}: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve account details'
        }), 500


@bp.route('', methods=['GET'])
@require_api_key
def list_all_accounts():
    """
    Lista todas as contas do sistema.
    
    Query Parameters:
        domain: Filtrar por domínio
        active_only: Se deve retornar apenas contas ativas (default: false)
        limit: Número máximo de resultados (default: 100)
        offset: Offset para paginação (default: 0)
    
    Returns:
        JSON response with list of all accounts
    """
    try:
        # Parâmetros de query
        domain_filter = request.args.get('domain')
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        limit = min(int(request.args.get('limit', 100)), 500)  # Max 500
        offset = int(request.args.get('offset', 0))
        
        # Construir query
        query = EmailAccount.query
        
        if domain_filter:
            domain_obj = Domain.get_by_name(domain_filter)
            if domain_obj:
                query = query.filter_by(domain_id=domain_obj.id)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        # Total antes de paginar
        total = query.count()
        
        # Aplicar paginação
        accounts = query.limit(limit).offset(offset).all()
        
        # Serializar contas
        accounts_data = []
        for acc in accounts:
            try:
                account_dict = {
                    'id': acc.id,
                    'email_address': acc.email_address,
                    'display_name': acc.display_name,
                    'domain': acc.domain.name,
                    'is_active': acc.is_active,
                    'smtp_server': acc.smtp_server,
                    'created_at': acc.created_at.isoformat() + 'Z'
                }
                accounts_data.append(account_dict)
            except Exception as e:
                logger.error(f"Error serializing account {acc.id}: {e}")
                continue
        
        logger.info(f"Listed {len(accounts_data)} accounts (total: {total})")
        
        return jsonify({
            'total': total,
            'limit': limit,
            'offset': offset,
            'count': len(accounts_data),
            'filters': {
                'domain': domain_filter,
                'active_only': active_only
            },
            'accounts': accounts_data
        })
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid parameters',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error listing all accounts: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to retrieve accounts'
        }), 500