"""
API v1 Blueprint.
Define os endpoints da API RESTful versão 1.
"""
from flask import Blueprint, jsonify

# Criar blueprint principal
api_v1_bp = Blueprint('api_v1', __name__)

# Importar sub-blueprints
from . import send, accounts, templates, logs, health

# Registrar sub-blueprints
api_v1_bp.register_blueprint(send.bp)
api_v1_bp.register_blueprint(accounts.bp)
api_v1_bp.register_blueprint(templates.bp)
api_v1_bp.register_blueprint(logs.bp)
api_v1_bp.register_blueprint(health.bp)

# Rota raiz da API
@api_v1_bp.route('/', methods=['GET'])
def api_info():
    """Informações sobre a API v1."""
    return jsonify({
        'version': '1.0.0',
        'service': 'SendCraft Email Manager API',
        'endpoints': {
            'health': '/api/v1/health',
            'status': '/api/v1/status',
            'send': {
                'template': 'POST /api/v1/send',
                'direct': 'POST /api/v1/send/direct',
                'test': 'POST /api/v1/send/test/<domain>/<account>'
            },
            'accounts': {
                'list': 'GET /api/v1/accounts/<domain>',
                'get': 'GET /api/v1/accounts/<domain>/<local_part>'
            },
            'templates': {
                'list': 'GET /api/v1/templates/<domain>',
                'get': 'GET /api/v1/templates/<domain>/<template_key>',
                'preview': 'POST /api/v1/templates/<domain>/<template_key>/preview'
            },
            'logs': {
                'list': 'GET /api/v1/logs',
                'get': 'GET /api/v1/logs/<log_id>',
                'stats': {
                    'account': 'GET /api/v1/stats/account/<account_id>',
                    'domain': 'GET /api/v1/stats/domain/<domain>',
                    'global': 'GET /api/v1/stats/global'
                }
            }
        },
        'authentication': 'Bearer token in Authorization header',
        'documentation': 'https://github.com/GGEDeveloper/SendCraft'
    })