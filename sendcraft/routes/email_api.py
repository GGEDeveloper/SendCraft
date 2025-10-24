"""
SendCraft Phase 15: Email Sending API
API para envio de emails com anexos para e-commerce
"""
from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from typing import Dict, Any, List, Optional
import base64
import time
import uuid
from datetime import datetime, timedelta

from ..models import Domain, EmailAccount, EmailLog
from ..models.log import EmailStatus
from ..services.smtp_service import SMTPService
from ..services.attachment_service import AttachmentService
from ..services.email_queue import get_email_queue
from ..services.auth_service import require_api_key
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Create blueprint for Phase 15 Email API
email_api_bp = Blueprint('email_api', __name__, url_prefix='/api/v1')


@email_api_bp.route('/send', methods=['POST'])
@cross_origin()
@require_api_key
def send_email():
    """
    Envio de email individual ou em lote com anexos.
    
    POST /api/v1/send
    Authorization: Bearer {api_key}
    Content-Type: application/json
    
    Payload:
    {
        "to": ["cliente@exemplo.com"],
        "cc": ["copia@exemplo.com"],
        "bcc": ["oculta@exemplo.com"],
        "subject": "Confirmação de Encomenda #12345",
        "html": "<h1>Obrigado pela sua compra!</h1>",
        "text": "Obrigado pela sua compra!",
        "attachments": [
            {
                "filename": "fatura-12345.pdf",
                "content_type": "application/pdf",
                "content": "base64_content"
            }
        ],
        "from_name": "Loja Online",
        "reply_to": "suporte@loja.com",
        "domain": "alitools.pt",
        "account": "encomendas",
        "bulk": false,
        "idempotency_key": "order-12345-confirmation"
    }
    
    Returns:
        200: Email sent successfully
        400: Validation error
        401: Authentication required
        404: Account/domain not found
        429: Rate limit exceeded
        500: Server error
    """
    try:
        start_time = time.time()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'validation_failed',
                'message': 'JSON body required'
            }), 400
        
        # Validate required fields
        required_fields = ['to', 'subject', 'domain', 'account']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': 'validation_failed',
                'message': f'Missing required fields: {", ".join(missing_fields)}',
                'details': {
                    'missing_fields': missing_fields,
                    'required_fields': required_fields
                }
            }), 400
        
        # Validate content
        if not data.get('html') and not data.get('text'):
            return jsonify({
                'success': False,
                'error': 'validation_failed',
                'message': 'At least one content field (html or text) is required'
            }), 400
        
        # Validate recipients
        to_emails = data.get('to', [])
        if not isinstance(to_emails, list) or len(to_emails) == 0:
            return jsonify({
                'success': False,
                'error': 'validation_failed',
                'message': 'Field "to" must be a non-empty array'
            }), 400
        
        # Check bulk limits
        if data.get('bulk', False) and len(to_emails) > 100:
            return jsonify({
                'success': False,
                'error': 'validation_failed',
                'message': 'Bulk emails limited to 100 recipients maximum',
                'details': {
                    'recipients_count': len(to_emails),
                    'max_allowed': 100
                }
            }), 400
        
        # Get domain and account
        domain = Domain.query.filter_by(name=data['domain']).first()
        if not domain or not domain.is_active:
            return jsonify({
                'success': False,
                'error': 'domain_not_found',
                'message': f"Domain '{data['domain']}' not found or inactive"
            }), 404
        
        account_email = f"{data['account']}@{data['domain']}"
        account = EmailAccount.query.filter_by(email_address=account_email).first()
        if not account or not account.is_active:
            return jsonify({
                'success': False,
                'error': 'account_not_found',
                'message': f"Account '{account_email}' not found or inactive"
            }), 404
        
        # Check account limits
        within_limits, limit_msg = account.is_within_limits()
        if not within_limits:
            return jsonify({
                'success': False,
                'error': 'rate_limit_exceeded',
                'message': limit_msg
            }), 429
        
        # Validate attachments if present
        attachments = data.get('attachments', [])
        if attachments:
            attachment_service = AttachmentService()
            validation_result = attachment_service.validate_attachments(attachments)
            if not validation_result['valid']:
                return jsonify({
                    'success': False,
                    'error': 'attachment_validation_failed',
                    'message': validation_result['message'],
                    'details': validation_result['details']
                }), 400
        
        # Check idempotency
        idempotency_key = data.get('idempotency_key')
        if idempotency_key:
            existing_log = EmailLog.query.filter_by(
                account_id=account.id,
                subject=data['subject'],
                recipient_email=to_emails[0] if len(to_emails) == 1 else None
            ).filter(
                EmailLog.variables_used['idempotency_key'].astext == idempotency_key
            ).first()
            
            if existing_log:
                return jsonify({
                    'success': True,
                    'message_id': f"MSG-{existing_log.id:06d}",
                    'status': 'duplicate_ignored',
                    'message': 'Email already sent with same idempotency key',
                    'recipients_processed': len(to_emails),
                    'recipients_success': to_emails,
                    'recipients_failed': [],
                    'attachments_processed': len(attachments),
                    'total_size_mb': sum(att.get('size_mb', 0) for att in attachments),
                    'processing_time_ms': int((time.time() - start_time) * 1000)
                }), 200
        
        # Process email(s)
        if data.get('bulk', False):
            # Bulk processing - queue for background
            result = _process_bulk_email(account, data, attachments, start_time)
        else:
            # Individual processing - send immediately
            result = _process_individual_email(account, data, attachments, start_time)
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        logger.error(f"Email API send error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'internal_server_error',
            'message': str(e)
        }), 500


@email_api_bp.route('/send/<message_id>/status', methods=['GET'])
@cross_origin()
@require_api_key
def get_send_status(message_id: str):
    """
    Consultar status de envio.
    
    GET /api/v1/send/{message_id}/status
    Authorization: Bearer {api_key}
    
    Returns:
        200: Status information
        404: Message not found
    """
    try:
        # Extract numeric ID from message_id (format: MSG-123456)
        if message_id.startswith('MSG-'):
            try:
                log_id = int(message_id[4:])
            except ValueError:
                return jsonify({
                    'error': 'invalid_message_id',
                    'message': 'Invalid message ID format'
                }), 400
        else:
            try:
                log_id = int(message_id)
            except ValueError:
                return jsonify({
                    'error': 'invalid_message_id',
                    'message': 'Invalid message ID format'
                }), 400
        
        # Get email log
        log = EmailLog.query.get(log_id)
        if not log:
            return jsonify({
                'error': 'message_not_found',
                'message': f'Message {message_id} not found'
            }), 404
        
        # Build response
        response = {
            'message_id': f"MSG-{log.id:06d}",
            'status': log.status.value,
            'created_at': log.created_at.isoformat() + 'Z',
            'recipients': [{
                'email': log.recipient_email,
                'status': log.status.value,
                'smtp_response': log.smtp_response or 'N/A'
            }],
            'attachments_count': len(log.variables_used.get('attachments', [])) if log.variables_used else 0,
            'error_message': log.error_message
        }
        
        if log.sent_at:
            response['sent_at'] = log.sent_at.isoformat() + 'Z'
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Email API status error: {e}", exc_info=True)
        return jsonify({
            'error': 'internal_server_error',
            'message': str(e)
        }), 500


@email_api_bp.route('/attachments/upload', methods=['POST'])
@cross_origin()
@require_api_key
def upload_attachment():
    """
    Upload prévio de anexos grandes.
    
    POST /api/v1/attachments/upload
    Authorization: Bearer {api_key}
    Content-Type: application/json
    
    Payload:
    {
        "filename": "catalogo-produtos.pdf",
        "content_type": "application/pdf",
        "content": "base64_content"
    }
    
    Returns:
        200: Attachment uploaded successfully
        400: Validation error
        500: Server error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'validation_failed',
                'message': 'JSON body required'
            }), 400
        
        # Validate required fields
        required_fields = ['filename', 'content_type', 'content']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': 'validation_failed',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Upload attachment using service
        attachment_service = AttachmentService()
        result = attachment_service.upload_attachment(data)
        
        if not result['success']:
            return jsonify({
                'error': result['error'],
                'message': result['message'],
                'details': result.get('details', {})
            }), 400
        
        return jsonify({
            'attachment_id': result['attachment_id'],
            'filename': result['filename'],
            'size_mb': result['size_mb'],
            'expires_at': result['expires_at']
        }), 200
        
    except Exception as e:
        logger.error(f"Email API upload error: {e}", exc_info=True)
        return jsonify({
            'error': 'internal_server_error',
            'message': str(e)
        }), 500




def _process_individual_email(account: EmailAccount, data: Dict[str, Any], attachments: List[Dict[str, Any]], start_time: float) -> Dict[str, Any]:
    """
    Processa envio de email individual.
    
    Args:
        account: Conta de email
        data: Dados do email
        attachments: Lista de anexos
        start_time: Timestamp de início
        
    Returns:
        Dict com resultado do processamento
    """
    try:
        # Create email log
        log = EmailLog(
            account_id=account.id,
            recipient_email=data['to'][0],  # Individual email
            sender_email=account.email_address,
            subject=data['subject'],
            status=EmailStatus.PENDING,
            variables_used={'idempotency_key': data.get('idempotency_key')},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(log)
        db.session.commit()
        
        # Mark as sending
        log.mark_sending()
        
        # Prepare attachments for SMTP service
        attachment_service = AttachmentService()
        smtp_attachments = attachment_service.prepare_attachments_for_smtp(attachments)
        
        # Send email
        encryption_key = current_app.config.get('SECRET_KEY', '')
        smtp_service = SMTPService(encryption_key)
        
        success, message, message_id = smtp_service.send_email(
            account=account,
            to_email=data['to'][0],
            subject=data['subject'],
            html_content=data.get('html'),
            text_content=data.get('text'),
            from_name=data.get('from_name'),
            reply_to=data.get('reply_to'),
            cc=data.get('cc'),
            bcc=data.get('bcc'),
            attachments=smtp_attachments if smtp_attachments else None
        )
        
        # Update log
        if success:
            log.mark_sent(message_id or '', message)
        else:
            log.mark_failed(message)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': success,
            'message_id': f"MSG-{log.id:06d}",
            'status': 'sent' if success else 'failed',
            'recipients_processed': 1,
            'recipients_success': [data['to'][0]] if success else [],
            'recipients_failed': [data['to'][0]] if not success else [],
            'attachments_processed': len(smtp_attachments),
            'total_size_mb': sum(len(att['content']) / (1024*1024) for att in smtp_attachments),
            'processing_time_ms': processing_time
        }
        
    except Exception as e:
        logger.error(f"Individual email processing error: {e}", exc_info=True)
        return {
            'success': False,
            'error': 'processing_failed',
            'message': str(e)
        }


def _process_bulk_email(account: EmailAccount, data: Dict[str, Any], attachments: List[Dict[str, Any]], start_time: float) -> Dict[str, Any]:
    """
    Processa envio de email em lote.
    
    Args:
        account: Conta de email
        data: Dados do email
        attachments: Lista de anexos
        start_time: Timestamp de início
        
    Returns:
        Dict com resultado do processamento
    """
    try:
        # Get email queue
        queue = get_email_queue()
        
        # Process bulk email using queue
        queue_item_id = queue.process_bulk_email(
            account=account,
            recipients=data['to'],
            subject=data['subject'],
            html_content=data.get('html'),
            text_content=data.get('text'),
            attachments=attachments,
            from_name=data.get('from_name'),
            reply_to=data.get('reply_to'),
            cc=data.get('cc'),
            bcc=data.get('bcc'),
            idempotency_key=data.get('idempotency_key')
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'success': True,
            'message_id': queue_item_id,
            'status': 'queued',
            'recipients_processed': len(data['to']),
            'recipients_success': [],
            'recipients_failed': [],
            'attachments_processed': len(attachments),
            'total_size_mb': sum(att.get('size_mb', 0) for att in attachments),
            'processing_time_ms': processing_time,
            'message': 'Bulk email queued for processing'
        }
        
    except Exception as e:
        logger.error(f"Bulk email processing error: {e}", exc_info=True)
        return {
            'success': False,
            'error': 'bulk_processing_failed',
            'message': str(e)
        }
