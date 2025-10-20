"""Endpoints de envio de email."""
from flask import Blueprint, request, jsonify, current_app, g
from typing import Dict, Any
import logging

from ...models import Domain, EmailAccount, EmailTemplate, EmailLog
from ...models.log import EmailStatus
from ...services.smtp_service import SMTPService
from ...services.email_service import EmailService
from ...services.auth_service import require_api_key
from ...extensions import db
from ...utils.logging import get_logger

bp = Blueprint('send', __name__, url_prefix='/send')
logger = get_logger(__name__)


@bp.route('', methods=['POST'])
@require_api_key
def send_email():
    """
    Envia email usando template.
    
    JSON Body:
    {
        "domain": "alitools.pt",
        "account": "encomendas",
        "to": "cliente@exemplo.com",
        "template_key": "order_confirmation",
        "variables": {
            "customer_name": "João Silva",
            "order_number": "#12345"
        },
        "from_name": "ALITOOLS" (opcional)
    }
    
    Returns:
        JSON response with send status and details
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'JSON body required',
                'message': 'Request must include a JSON body with email data'
            }), 400
        
        # Validar campos obrigatórios
        required_fields = ['domain', 'account', 'to', 'template_key']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields,
                'required': required_fields
            }), 400
        
        # Buscar domínio
        domain = Domain.get_by_name(data['domain'])
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
        
        # Buscar conta
        account_email = f"{data['account']}@{data['domain']}"
        account = EmailAccount.get_by_email(account_email)
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
        
        # Verificar limites da conta
        within_limits, limit_msg = account.is_within_limits()
        if not within_limits:
            return jsonify({
                'error': 'Account limit exceeded',
                'message': limit_msg
            }), 429
        
        # Buscar template
        template = EmailTemplate.get_by_key(domain.id, data['template_key'])
        if not template:
            return jsonify({
                'error': 'Template not found',
                'message': f"Template '{data['template_key']}' not found for domain '{data['domain']}'"
            }), 404
        
        if not template.is_active:
            return jsonify({
                'error': 'Template inactive',
                'message': f"Template '{data['template_key']}' is not active"
            }), 400
        
        # Validar variáveis do template
        variables = data.get('variables', {})
        is_valid, missing_vars = template.validate_variables(variables)
        
        if not is_valid:
            return jsonify({
                'error': 'Missing required template variables',
                'missing_variables': missing_vars,
                'required_variables': template.variables_required,
                'optional_variables': template.variables_optional
            }), 400
        
        # Criar log inicial
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
        
        # Marcar como enviando
        log.mark_sending()
        
        # Renderizar conteúdo
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
        
        # Enviar email
        smtp_service = SMTPService(current_app.config.get('ENCRYPTION_KEY'))
        success, message, message_id = smtp_service.send_email(
            account=account,
            to_email=data['to'],
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            from_name=data.get('from_name')
        )
        
        # Atualizar log
        if success:
            log.mark_sent(message_id or '', message)
            logger.info(f"Email sent successfully: {log.id} from {account.email_address} to {data['to']}")
        else:
            log.mark_failed(message)
            logger.error(f"Email send failed: {log.id} - {message}")
        
        # Retornar resultado
        response_data = {
            'success': success,
            'log_id': log.id,
            'message': message,
            'message_id': message_id,
            'template_used': template.template_key,
            'variables_count': len(variables),
            'from': account.email_address,
            'to': data['to']
        }
        
        return jsonify(response_data), 200 if success else 500
        
    except ValueError as e:
        logger.error(f"Value error in send_email: {e}")
        return jsonify({
            'error': 'Invalid data',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in send_email: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred while sending email'
        }), 500


@bp.route('/direct', methods=['POST'])
@require_api_key
def send_direct():
    """
    Envia email direto sem template.
    
    JSON Body:
    {
        "domain": "alitools.pt",
        "account": "encomendas",
        "to": "cliente@exemplo.com",
        "subject": "Assunto do email",
        "html_content": "<h1>HTML content</h1>" (opcional),
        "text_content": "Text content" (opcional),
        "from_name": "ALITOOLS" (opcional)
    }
    
    Returns:
        JSON response with send status and details
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'JSON body required',
                'message': 'Request must include a JSON body with email data'
            }), 400
        
        # Validar campos obrigatórios
        required_fields = ['domain', 'account', 'to', 'subject']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields,
                'required': required_fields
            }), 400
        
        # Validar que há pelo menos um conteúdo
        if not data.get('html_content') and not data.get('text_content'):
            return jsonify({
                'error': 'Content required',
                'message': 'At least one content type (html_content or text_content) is required'
            }), 400
        
        # Buscar domínio
        domain = Domain.get_by_name(data['domain'])
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
        
        # Buscar conta
        account_email = f"{data['account']}@{data['domain']}"
        account = EmailAccount.get_by_email(account_email)
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
        
        # Verificar limites da conta
        within_limits, limit_msg = account.is_within_limits()
        if not within_limits:
            return jsonify({
                'error': 'Account limit exceeded',
                'message': limit_msg
            }), 429
        
        # Criar log
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
        
        # Marcar como enviando
        log.mark_sending()
        
        # Enviar email
        smtp_service = SMTPService(current_app.config.get('ENCRYPTION_KEY'))
        success, message, message_id = smtp_service.send_email(
            account=account,
            to_email=data['to'],
            subject=data['subject'],
            html_content=data.get('html_content'),
            text_content=data.get('text_content'),
            from_name=data.get('from_name')
        )
        
        # Atualizar log
        if success:
            log.mark_sent(message_id or '', message)
            logger.info(f"Direct email sent: {log.id} from {account.email_address} to {data['to']}")
        else:
            log.mark_failed(message)
            logger.error(f"Direct email failed: {log.id} - {message}")
        
        # Retornar resultado
        response_data = {
            'success': success,
            'log_id': log.id,
            'message': message,
            'message_id': message_id,
            'from': account.email_address,
            'to': data['to'],
            'subject': data['subject']
        }
        
        return jsonify(response_data), 200 if success else 500
        
    except Exception as e:
        logger.error(f"Unexpected error in send_direct: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred while sending email'
        }), 500


@bp.route('/test/<domain>/<account>', methods=['POST'])
@require_api_key
def test_smtp_connection(domain: str, account: str):
    """
    Testa conexão SMTP de uma conta.
    
    Args:
        domain: Nome do domínio
        account: Parte local da conta (antes do @)
    
    Returns:
        JSON response with connection test result
    """
    try:
        # Buscar domínio
        domain_obj = Domain.get_by_name(domain)
        if not domain_obj:
            return jsonify({
                'error': 'Domain not found',
                'message': f"Domain '{domain}' not found"
            }), 404
        
        # Buscar conta
        account_email = f"{account}@{domain}"
        account_obj = EmailAccount.get_by_email(account_email)
        if not account_obj:
            return jsonify({
                'error': 'Account not found',
                'message': f"Account '{account_email}' not found"
            }), 404
        
        # Testar conexão
        smtp_service = SMTPService(current_app.config.get('ENCRYPTION_KEY'))
        success, message = smtp_service.test_connection(account_obj)
        
        logger.info(f"SMTP test for {account_email}: {'success' if success else 'failed'}")
        
        return jsonify({
            'success': success,
            'message': message,
            'account': account_email,
            'smtp_server': account_obj.smtp_server,
            'smtp_port': account_obj.smtp_port,
            'use_tls': account_obj.use_tls,
            'use_ssl': account_obj.use_ssl
        }), 200 if success else 500
        
    except Exception as e:
        logger.error(f"SMTP test error: {e}", exc_info=True)
        return jsonify({
            'error': 'Test failed',
            'message': str(e)
        }), 500