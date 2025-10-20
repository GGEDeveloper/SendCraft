"""Endpoints de health check."""
from flask import Blueprint, jsonify, current_app, g
from datetime import datetime
import sys
import platform

from ...extensions import db
from ...services.auth_service import optional_api_key
from ...utils.logging import get_logger

bp = Blueprint('health', __name__)
logger = get_logger(__name__)


@bp.route('/health', methods=['GET'])
@optional_api_key
def health_check():
    """
    Health check básico.
    Endpoint público que retorna status básico do serviço.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': '1.0.0',
        'service': 'SendCraft Email Manager',
        'authenticated': getattr(g, 'authenticated', False)
    })


@bp.route('/status', methods=['GET'])
@optional_api_key
def detailed_status():
    """
    Status detalhado do sistema.
    Retorna informações adicionais se autenticado.
    """
    try:
        # Testar database
        db_status = 'unknown'
        db_error = None
        try:
            result = db.session.execute(db.text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            db_status = 'error'
            db_error = str(e)
            logger.error(f"Database connection error: {e}")
        
        # Info do sistema básica
        status_info = {
            'status': 'healthy' if db_status == 'connected' else 'degraded',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0',
            'service': 'SendCraft Email Manager',
            'system': {
                'python_version': sys.version.split()[0],
                'platform': platform.platform(),
                'processor': platform.processor() or 'unknown'
            },
            'database': {
                'status': db_status,
                'error': db_error
            },
            'config': {
                'debug': current_app.debug,
                'testing': current_app.testing,
                'env': current_app.config.get('ENV', 'unknown')
            }
        }
        
        # Info adicional se autenticado
        if hasattr(g, 'authenticated') and g.authenticated:
            try:
                from ...models import Domain, EmailAccount, EmailTemplate, EmailLog
                
                # Contar registros
                status_info['statistics'] = {
                    'domains': {
                        'total': Domain.query.count(),
                        'active': Domain.query.filter_by(is_active=True).count()
                    },
                    'accounts': {
                        'total': EmailAccount.query.count(),
                        'active': EmailAccount.query.filter_by(is_active=True).count()
                    },
                    'templates': {
                        'total': EmailTemplate.query.count(),
                        'active': EmailTemplate.query.filter_by(is_active=True).count()
                    },
                    'logs': {
                        'total': EmailLog.query.count(),
                        'last_24h': EmailLog.query.filter(
                            EmailLog.created_at >= db.func.datetime('now', '-1 day')
                        ).count() if db_status == 'connected' else 0
                    }
                }
                
                # Informação da chave API
                status_info['auth'] = {
                    'authenticated': True,
                    'key_name': getattr(g, 'api_key_name', 'unknown')
                }
                
            except Exception as e:
                logger.error(f"Error getting statistics: {e}")
                status_info['statistics'] = {'error': 'Failed to retrieve statistics'}
        else:
            status_info['auth'] = {
                'authenticated': False
            }
        
        return jsonify(status_info)
        
    except Exception as e:
        logger.error(f"Status endpoint error: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': 'Failed to retrieve system status',
            'message': str(e) if current_app.debug else 'Internal error'
        }), 500


@bp.route('/ping', methods=['GET'])
def ping():
    """
    Simple ping endpoint.
    No authentication required.
    """
    return jsonify({
        'pong': True,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })