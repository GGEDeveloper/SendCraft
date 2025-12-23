"""
Rotas da API para Campanhas de Email
Endpoints para criar, gerenciar e monitorar campanhas
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import and_

from ..models import EmailCampaign, CampaignRecipient, EmailAccount
from ..services.campaign_service import get_campaign_service
from ..extensions import db
from ..utils.logging import get_logger
from ..utils.decorators import require_auth

logger = get_logger(__name__)
campaign_bp = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')


@campaign_bp.route('', methods=['POST'])
@require_auth
def create_campaign():
    """
    POST /api/campaigns
    Cria nova campanha de email
    """
    try:
        data = request.get_json()
        
        # Validação básica
        required_fields = ['account_id', 'name', 'subject', 'html_content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Verificar se conta existe
        account = EmailAccount.query.get(data['account_id'])
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        # Criar campanha
        service = get_campaign_service()
        campaign = service.create_campaign(
            account_id=data['account_id'],
            name=data['name'],
            subject=data['subject'],
            html_content=data['html_content'],
            description=data.get('description'),
            text_content=data.get('text_content'),
            from_name=data.get('from_name'),
            reply_to=data.get('reply_to'),
            warmup_enabled=data.get('warmup_enabled', True),
            delay_between_emails=data.get('delay_between_emails', 180),
            batch_size=data.get('batch_size', 10),
            use_tracking_pixel=data.get('use_tracking_pixel', True),
            use_click_tracking=data.get('use_click_tracking', True)
        )
        
        return jsonify({
            'id': campaign.id,
            'name': campaign.name,
            'status': campaign.status,
            'created_at': campaign.created_at.isoformat()
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        return jsonify({'error': str(e)}), 500


@campaign_bp.route('/<int:campaign_id>', methods=['GET'])
@require_auth
def get_campaign(campaign_id):
    """
    GET /api/campaigns/{campaign_id}
    Retorna detalhes da campanha
    """
    try:
        campaign = EmailCampaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        service = get_campaign_service()
        stats = service.get_campaign_stats(campaign_id)
        
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Error getting campaign: {e}")
        return jsonify({'error': str(e)}), 500


@campaign_bp.route('/<int:campaign_id>/recipients', methods=['POST'])
@require_auth
def add_recipients(campaign_id):
    """
    POST /api/campaigns/{campaign_id}/recipients
    Adiciona destinatários à campanha
    
    Body:
    {
        "recipients": [
            {"email": "user@example.com", "name": "User Name", "variables": {"key": "value"}},
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        if 'recipients' not in data:
            return jsonify({'error': 'Missing recipients field'}), 400
        
        campaign = EmailCampaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        service = get_campaign_service()
        added, duplicates = service.add_recipients(
            campaign_id=campaign_id,
            recipients=data['recipients'],
            skip_duplicates=data.get('skip_duplicates', True)
        )
        
        return jsonify({
            'added': added,
            'duplicates': duplicates,
            'total_recipients': campaign.total_recipients
        }), 200
    
    except Exception as e:
        logger.error(f"Error adding recipients: {e}")
        return jsonify({'error': str(e)}), 500


@campaign_bp.route('/<int:campaign_id>/recipients/bulk', methods=['POST'])
@require_auth
def add_recipients_bulk(campaign_id):
    """
    POST /api/campaigns/{campaign_id}/recipients/bulk
    Adiciona destinatários via arquivo CSV ou JSON
    
    Suporta:
    - multipart/form-data com arquivo 'file'
    - application/json com array de recipients
    """
    try:
        campaign = EmailCampaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        recipients = []
        
        # Verificar se é upload de arquivo
        if 'file' in request.files:
            file = request.files['file']
            if file.filename.endswith('.csv'):
                # Processar CSV
                import csv
                import io
                
                stream = io.TextIOWrapper(file.stream, encoding='utf-8')
                reader = csv.DictReader(stream)
                
                for row in reader:
                    recipients.append({
                        'email': row.get('email', ''),
                        'name': row.get('name', ''),
                        'variables': {k: v for k, v in row.items() if k not in ['email', 'name']}
                    })
            
            elif file.filename.endswith('.json'):
                # Processar JSON
                import json
                recipients = json.load(file)
        
        else:
            # JSON no body
            data = request.get_json()
            recipients = data.get('recipients', [])
        
        if not recipients:
            return jsonify({'error': 'No recipients provided'}), 400
        
        service = get_campaign_service()
        added, duplicates = service.add_recipients(
            campaign_id=campaign_id,
            recipients=recipients,
            skip_duplicates=request.args.get('skip_duplicates', 'true').lower() == 'true'
        )
        
        return jsonify({
            'added': added,
            'duplicates': duplicates,
            'total_recipients': campaign.total_recipients
        }), 200
    
    except Exception as e:
        logger.error(f"Error adding bulk recipients: {e}")
        return jsonify({'error': str(e)}), 500


@campaign_bp.route('/<int:campaign_id>/start', methods=['POST'])
@require_auth
def start_campaign(campaign_id):
    """
    POST /api/campaigns/{campaign_id}/start
    Inicia execução da campanha
    """
    try:
        campaign = EmailCampaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        service = get_campaign_service()
        success = service.start_campaign(campaign_id)
        
        if success:
            return jsonify({
                'message': 'Campaign started',
                'campaign_id': campaign_id,
                'status': campaign.status
            }), 200
        else:
            return jsonify({'error': 'Failed to start campaign'}), 400
    
    except Exception as e:
        logger.error(f"Error starting campaign: {e}")
        return jsonify({'error': str(e)}), 500


@campaign_bp.route('/<int:campaign_id>/pause', methods=['POST'])
@require_auth
def pause_campaign(campaign_id):
    """
    POST /api/campaigns/{campaign_id}/pause
    Pausa execução da campanha
    """
    try:
        service = get_campaign_service()
        success = service.pause_campaign(campaign_id)
        
        if success:
            campaign = EmailCampaign.query.get(campaign_id)
            return jsonify({
                'message': 'Campaign paused',
                'campaign_id': campaign_id,
                'status': campaign.status
            }), 200
        else:
            return jsonify({'error': 'Failed to pause campaign'}), 400
    
    except Exception as e:
        logger.error(f"Error pausing campaign: {e}")
        return jsonify({'error': str(e)}), 500


@campaign_bp.route('/<int:campaign_id>/resume', methods=['POST'])
@require_auth
def resume_campaign(campaign_id):
    """
    POST /api/campaigns/{campaign_id}/resume
    Retoma execução da campanha pausada
    """
    try:
        service = get_campaign_service()
        success = service.resume_campaign(campaign_id)
        
        if success:
            campaign = EmailCampaign.query.get(campaign_id)
            return jsonify({
                'message': 'Campaign resumed',
                'campaign_id': campaign_id,
                'status': campaign.status
            }), 200
        else:
            return jsonify({'error': 'Failed to resume campaign'}), 400
    
    except Exception as e:
        logger.error(f"Error resuming campaign: {e}")
        return jsonify({'error': str(e)}), 500


@campaign_bp.route('/<int:campaign_id>/stats', methods=['GET'])
@require_auth
def get_stats(campaign_id):
    """
    GET /api/campaigns/{campaign_id}/stats
    Retorna estatísticas detalhadas da campanha
    """
    try:
        campaign = EmailCampaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        service = get_campaign_service()
        stats = service.get_campaign_stats(campaign_id)
        
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


@campaign_bp.route('/<int:campaign_id>/recipients', methods=['GET'])
@require_auth
def list_recipients(campaign_id):
    """
    GET /api/campaigns/{campaign_id}/recipients?status=pending&limit=100&offset=0
    Lista destinatários da campanha
    """
    try:
        campaign = EmailCampaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        status = request.args.get('status')  # pending, sent, failed, bounced
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        query = CampaignRecipient.query.filter_by(campaign_id=campaign_id)
        
        if status:
            query = query.filter_by(status=status)
        
        total = query.count()
        recipients = query.limit(limit).offset(offset).all()
        
        return jsonify({
            'total': total,
            'limit': limit,
            'offset': offset,
            'recipients': [
                {
                    'id': r.id,
                    'email': r.email,
                    'name': r.name,
                    'status': r.status,
                    'sent_at': r.sent_at.isoformat() if r.sent_at else None,
                    'opened': r.opened,
                    'clicked': r.clicked,
                    'complained': r.complained,
                }
                for r in recipients
            ]
        }), 200
    
    except Exception as e:
        logger.error(f"Error listing recipients: {e}")
        return jsonify({'error': str(e)}), 500


@campaign_bp.route('', methods=['GET'])
@require_auth
def list_campaigns():
    """
    GET /api/campaigns?account_id=1&status=running&limit=50&offset=0
    Lista campanhas
    """
    try:
        account_id = request.args.get('account_id')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        query = EmailCampaign.query
        
        if account_id:
            query = query.filter_by(account_id=account_id)
        
        if status:
            query = query.filter_by(status=status)
        
        total = query.count()
        campaigns = query.order_by(EmailCampaign.created_at.desc()).limit(limit).offset(offset).all()
        
        return jsonify({
            'total': total,
            'limit': limit,
            'offset': offset,
            'campaigns': [
                {
                    'id': c.id,
                    'name': c.name,
                    'status': c.status,
                    'total_recipients': c.total_recipients,
                    'sent': c.sent_count,
                    'failed': c.failed_count,
                    'warmup_phase': c.current_warmup_phase,
                    'created_at': c.created_at.isoformat()
                }
                for c in campaigns
            ]
        }), 200
    
    except Exception as e:
        logger.error(f"Error listing campaigns: {e}")
        return jsonify({'error': str(e)}), 500
