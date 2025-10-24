"""
External API Routes for SendCraft
REST API for external applications (AliTools.pt integration)
"""
from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from typing import Dict, Any

from ..models import Domain, EmailAccount, EmailTemplate, EmailLog
from ..models.log import EmailStatus
from ..services.smtp_service import SMTPService
from ..services.auth_service import require_account_api_key
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Create blueprint for external API
external_api_bp = Blueprint('external_api', __name__, url_prefix='/api/v1')


@external_api_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """
    Health check endpoint for external API.
    
    GET /api/v1/health
    
    Returns:
        200: System is healthy
    """
    return jsonify({
        'status': 'healthy',
        'service': 'SendCraft External API',
        'version': '1.0.0'
    }), 200


@external_api_bp.route('/send/direct', methods=['POST'])
@cross_origin()
@require_account_api_key
def send_direct_email():
    """
    Send direct email without template.
    
    POST /api/v1/send/direct
    Authorization: Bearer <api_key>
    
    Request Body:
    {
        "domain": "alitools.pt",
        "account": "encomendas",
        "to": "customer@example.com",
        "subject": "Order Confirmation",
        "html": "<h1>Thank you!</h1>",
        "text": "Thank you for your order!"
    }
    
    Returns:
        200: Email sent successfully
        400: Invalid request
        401: Authentication required
        404: Account/domain not found
        429: Rate limit exceeded
        500: Server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'JSON body required',
                'message': 'Request must include a JSON body'
            }), 400
        
        # Validate required fields
        required_fields = ['domain', 'account', 'to', 'subject']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields,
                'required': required_fields
            }), 400
        
        # Validate content
        if not data.get('html') and not data.get('text'):
            return jsonify({
                'error': 'Content required',
                'message': 'At least one content field (html or text) is required'
            }), 400
        
        # Get domain
        domain = Domain.query.filter_by(name=data['domain']).first()
        if not domain:
            return jsonify({
                'error': 'Domain not found',
                'message': f"Domain '{data['domain']}' not found"
            }), 404
        
        if not domain.is_active:
            return jsonify({
                'error': 'Domain inactive',
                'message': f"Domain '{data['domain']}' is not active"
            }), 400
        
        # Get account
        account_email = f"{data['account']}@{data['domain']}"
        account = EmailAccount.query.filter_by(email_address=account_email).first()
        if not account:
            return jsonify({
                'error': 'Account not found',
                'message': f"Account '{account_email}' not found"
            }), 404
        
        if not account.is_active:
            return jsonify({
                'error': 'Account inactive',
                'message': f"Account '{account_email}' is not active"
            }), 400
        
        # Check account limits
        within_limits, limit_msg = account.is_within_limits()
        if not within_limits:
            return jsonify({
                'error': 'Account limit exceeded',
                'message': limit_msg
            }), 429
        
        # Create log
        log = EmailLog(
            account_id=account.id,
            recipient_email=data['to'],
            sender_email=account.email_address,
            subject=data['subject'],
            status=EmailStatus.PENDING,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(log)
        db.session.commit()
        
        # Mark as sending
        log.mark_sending()
        
        # Send email
        encryption_key = current_app.config.get('SECRET_KEY', '')
        smtp_service = SMTPService(encryption_key)
        success, message, message_id = smtp_service.send_email(
            account=account,
            to_email=data['to'],
            subject=data['subject'],
            html_content=data.get('html'),
            text_content=data.get('text'),
            from_name=data.get('from_name')
        )
        
        # Update log
        if success:
            log.mark_sent(message_id or '', message)
            logger.info(f"External API: Email sent - {log.id} from {account.email_address} to {data['to']}")
        else:
            log.mark_failed(message)
            logger.error(f"External API: Email failed - {log.id} - {message}")
        
        # Return result
        return jsonify({
            'success': success,
            'log_id': log.id,
            'message': message,
            'message_id': message_id,
            'from': account.email_address,
            'to': data['to'],
            'subject': data['subject']
        }), 200 if success else 500
        
    except Exception as e:
        logger.error(f"External API send_direct error: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@external_api_bp.route('/send/template', methods=['POST'])
@cross_origin()
@require_account_api_key
def send_template_email():
    """
    Send email using template.
    
    POST /api/v1/send/template
    Authorization: Bearer <api_key>
    
    Request Body:
    {
        "domain": "alitools.pt",
        "account": "encomendas",
        "template": "order_confirmation",
        "to": "customer@example.com",
        "variables": {
            "customer_name": "João Silva",
            "order_number": "ALI-2025-001",
            "total": "149.99"
        }
    }
    
    Returns:
        200: Email sent successfully
        400: Invalid request
        401: Authentication required
        404: Account/template not found
        429: Rate limit exceeded
        500: Server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'JSON body required',
                'message': 'Request must include a JSON body'
            }), 400
        
        # Validate required fields
        required_fields = ['domain', 'account', 'to', 'template']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields,
                'required': required_fields
            }), 400
        
        # Get domain
        domain = Domain.query.filter_by(name=data['domain']).first()
        if not domain:
            return jsonify({
                'error': 'Domain not found',
                'message': f"Domain '{data['domain']}' not found"
            }), 404
        
        if not domain.is_active:
            return jsonify({
                'error': 'Domain inactive',
                'message': f"Domain '{data['domain']}' is not active"
            }), 400
        
        # Get account
        account_email = f"{data['account']}@{data['domain']}"
        account = EmailAccount.query.filter_by(email_address=account_email).first()
        if not account:
            return jsonify({
                'error': 'Account not found',
                'message': f"Account '{account_email}' not found"
            }), 404
        
        if not account.is_active:
            return jsonify({
                'error': 'Account inactive',
                'message': f"Account '{account_email}' is not active"
            }), 400
        
        # Check account limits
        within_limits, limit_msg = account.is_within_limits()
        if not within_limits:
            return jsonify({
                'error': 'Account limit exceeded',
                'message': limit_msg
            }), 429
        
        # Get template
        template = EmailTemplate.query.filter_by(
            domain_id=domain.id,
            template_key=data['template']
        ).first()
        
        if not template:
            return jsonify({
                'error': 'Template not found',
                'message': f"Template '{data['template']}' not found for domain '{data['domain']}'"
            }), 404
        
        if not template.is_active:
            return jsonify({
                'error': 'Template inactive',
                'message': f"Template '{data['template']}' is not active"
            }), 400
        
        # Validate variables
        variables = data.get('variables', {})
        is_valid, missing_vars = template.validate_variables(variables)
        
        if not is_valid:
            return jsonify({
                'error': 'Missing required template variables',
                'missing_variables': missing_vars,
                'required_variables': template.variables_required,
                'optional_variables': template.variables_optional
            }), 400
        
        # Create log
        log = EmailLog(
            account_id=account.id,
            template_id=template.id,
            recipient_email=data['to'],
            sender_email=account.email_address,
            subject=template.render_subject(variables),
            status=EmailStatus.PENDING,
            variables_used=variables,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(log)
        db.session.commit()
        
        # Mark as sending
        log.mark_sending()
        
        # Render content
        try:
            subject = template.render_subject(variables)
            html_content = template.render_html(variables)
            text_content = template.render_text(variables)
        except Exception as e:
            log.mark_failed(f"Template rendering error: {str(e)}")
            return jsonify({
                'error': 'Template rendering error',
                'message': str(e)
            }), 400
        
        # Send email
        encryption_key = current_app.config.get('SECRET_KEY', '')
        smtp_service = SMTPService(encryption_key)
        success, message, message_id = smtp_service.send_email(
            account=account,
            to_email=data['to'],
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            from_name=data.get('from_name')
        )
        
        # Update log
        if success:
            log.mark_sent(message_id or '', message)
            logger.info(f"External API: Template email sent - {log.id} from {account.email_address} to {data['to']}")
        else:
            log.mark_failed(message)
            logger.error(f"External API: Template email failed - {log.id} - {message}")
        
        # Return result
        return jsonify({
            'success': success,
            'log_id': log.id,
            'message': message,
            'message_id': message_id,
            'template_used': template.template_key,
            'variables_count': len(variables),
            'from': account.email_address,
            'to': data['to']
        }), 200 if success else 500
        
    except Exception as e:
        logger.error(f"External API send_template error: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@external_api_bp.route('/accounts/<domain>', methods=['GET'])
@cross_origin()
@require_account_api_key
def list_domain_accounts(domain: str):
    """
    List accounts for a domain.
    
    GET /api/v1/accounts/<domain>
    Authorization: Bearer <api_key>
    
    Returns:
        200: List of accounts
        404: Domain not found
    """
    try:
        domain_obj = Domain.query.filter_by(name=domain).first()
        if not domain_obj:
            return jsonify({
                'error': 'Domain not found',
                'message': f"Domain '{domain}' not found"
            }), 404
        
        accounts = EmailAccount.query.filter_by(domain_id=domain_obj.id).all()
        
        accounts_data = []
        for account in accounts:
            accounts_data.append({
                'email': account.email_address,
                'display_name': account.display_name,
                'is_active': account.is_active,
                'daily_limit': account.daily_limit,
                'monthly_limit': account.monthly_limit,
                'emails_sent_today': account.count_emails_sent_today(),
                'emails_sent_this_month': account.count_emails_sent_this_month()
            })
        
        return jsonify({
            'domain': domain,
            'accounts': accounts_data,
            'count': len(accounts_data)
        }), 200
        
    except Exception as e:
        logger.error(f"External API list_accounts error: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@external_api_bp.route('/templates/<domain>', methods=['GET'])
@cross_origin()
@require_account_api_key
def list_domain_templates(domain: str):
    """
    List templates for a domain.
    
    GET /api/v1/templates/<domain>
    Authorization: Bearer <api_key>
    
    Returns:
        200: List of templates
        404: Domain not found
    """
    try:
        domain_obj = Domain.query.filter_by(name=domain).first()
        if not domain_obj:
            return jsonify({
                'error': 'Domain not found',
                'message': f"Domain '{domain}' not found"
            }), 404
        
        templates = EmailTemplate.query.filter_by(domain_id=domain_obj.id).all()
        
        templates_data = []
        for template in templates:
            templates_data.append({
                'key': template.template_key,
                'name': template.template_name,
                'subject': template.subject,
                'category': template.category,
                'is_active': template.is_active,
                'required_variables': template.variables_required,
                'optional_variables': template.variables_optional
            })
        
        return jsonify({
            'domain': domain,
            'templates': templates_data,
            'count': len(templates_data)
        }), 200
        
    except Exception as e:
        logger.error(f"External API list_templates error: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

