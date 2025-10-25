"""API v1 - Endpoints para Email Inbox."""
from flask import Blueprint, jsonify, request, current_app
from flask_cors import cross_origin
from typing import Dict, Any

from ...models import EmailAccount, EmailInbox
from ...services.imap_service import IMAPService
from ...extensions import db
from ...utils.logging import get_logger
from ..errors import APIError, BadRequest, NotFound, ServerError

logger = get_logger(__name__)

# Criar blueprint
bp = Blueprint('inbox', __name__, url_prefix='/emails/inbox')


@bp.route('/<int:account_id>', methods=['GET'])
@cross_origin()
def list_inbox_emails(account_id: int):
    """
    Lista emails do inbox de uma conta.
    
    GET /api/v1/inbox/<account_id>
    
    Query Parameters:
        page: Número da página (default: 1)
        per_page: Items por página (default: 50)
        folder: Pasta IMAP (default: INBOX)
        unread_only: Apenas não lidos (default: false)
        has_attachments: Apenas com anexos (default: false)
        search: Query de busca
    
    Returns:
        200: Lista paginada de emails
        404: Conta não encontrada
        500: Erro interno
    """
    try:
        # Buscar conta
        account = EmailAccount.get_by_id(account_id)
        if not account:
            raise NotFound(f"Account {account_id} not found")
        
        # Parâmetros de query
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        folder = request.args.get('folder', 'INBOX')
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        has_attachments = request.args.get('has_attachments', 'false').lower() == 'true'
        search_query = request.args.get('search', '')
        
        # Validar paginação
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 50
        
        # Buscar emails
        result = EmailInbox.get_inbox_emails(
            account_id=account_id,
            page=page,
            per_page=per_page,
            folder=folder,
            unread_only=unread_only,
            has_attachments_only=has_attachments,
            search_query=search_query
        )
        
        # Adicionar informações da conta
        result['account'] = {
            'id': account.id,
            'email': account.email_address,
            'display_name': account.display_name,
            'last_sync': account.last_sync.isoformat() if account.last_sync else None
        }
        
        return jsonify(result), 200
        
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error listing inbox emails: {e}")
        return jsonify({'error': 'Failed to list emails'}), 500


@bp.route('/<int:account_id>/<int:email_id>', methods=['GET'])
@cross_origin()
def get_inbox_email(account_id: int, email_id: int):
    """
    Busca email específico do inbox.
    
    GET /api/v1/inbox/<account_id>/<email_id>
    
    Returns:
        200: Detalhes do email
        404: Email ou conta não encontrada
        500: Erro interno
    """
    try:
        # Buscar conta
        account = EmailAccount.get_by_id(account_id)
        if not account:
            raise NotFound(f"Account {account_id} not found")
        
        # Buscar email
        email = EmailInbox.query.filter_by(
            id=email_id,
            account_id=account_id
        ).first()
        
        if not email:
            raise NotFound(f"Email {email_id} not found")
        
        # Marcar como lido automaticamente
        if not email.is_read:
            email.mark_as_read()
        
        return jsonify({
            'email': email.to_dict(compact=False, include_body=True)
        }), 200
        
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting email {email_id}: {e}")
        return jsonify({'error': 'Failed to get email'}), 500


@bp.route('/<int:account_id>/threads', methods=['GET'])
@cross_origin()
def list_email_threads(account_id: int):
    """
    Lista threads/conversas de email.
    
    GET /api/v1/inbox/<account_id>/threads
    
    Query Parameters:
        limit: Número máximo de threads (default: 50)
    
    Returns:
        200: Lista de threads
        404: Conta não encontrada
        500: Erro interno
    """
    try:
        # Buscar conta
        account = EmailAccount.get_by_id(account_id)
        if not account:
            raise NotFound(f"Account {account_id} not found")
        
        # Parâmetros
        limit = request.args.get('limit', 50, type=int)
        if limit < 1 or limit > 100:
            limit = 50
        
        # Buscar threads
        threads = EmailInbox.get_threads(account_id=account_id, limit=limit)
        
        return jsonify({
            'threads': threads,
            'total': len(threads),
            'account': {
                'id': account.id,
                'email': account.email_address
            }
        }), 200
        
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error listing threads: {e}")
        return jsonify({'error': 'Failed to list threads'}), 500


@bp.route('/sync/<int:account_id>', methods=['POST'])
@cross_origin()
def sync_account_inbox(account_id: int):
    """
    Sincroniza emails do servidor IMAP.
    
    POST /api/v1/inbox/sync/<account_id>
    
    Request Body (opcional):
        folder: Pasta para sincronizar (default: INBOX)
        limit: Limite de emails (default: 50)
        full_sync: Sincronização completa ignorando last_sync (default: false)
    
    Returns:
        200: Sincronização bem sucedida
        404: Conta não encontrada
        500: Erro de sincronização
    """
    try:
        # Buscar conta
        account = EmailAccount.get_by_id(account_id)
        if not account:
            raise NotFound(f"Account {account_id} not found")
        
        # Parâmetros do body
        data = request.get_json() or {}
        folder = data.get('folder', 'INBOX')
        limit = data.get('limit', 50)
        full_sync = data.get('full_sync', False)
        
        # Validar parâmetros
        if limit < 1 or limit > 200:
            limit = 50
        
        # Criar serviço IMAP
        imap_service = IMAPService(account)
        
        # Conectar ao servidor
        encryption_key = current_app.config.get('SECRET_KEY', '')
        config = account.get_imap_config(encryption_key)
        
        if not imap_service.connect(config):
            raise ServerError("Failed to connect to IMAP server")
        
        try:
            # Sincronizar emails
            synced_count = imap_service.sync_account_emails(
                account=account,
                folder=folder,
                limit=limit,
                since_last_sync=not full_sync
            )
            
            # Buscar estatísticas atualizadas
            unread_count = EmailInbox.get_unread_count(account_id, folder)
            total_count = EmailInbox.query.filter_by(
                account_id=account_id,
                folder=folder,
                is_deleted=False
            ).count()
            
            return jsonify({
                'success': True,
                'synced_count': synced_count,
                'total_emails': total_count,
                'unread_count': unread_count,
                'last_sync': account.last_sync.isoformat() if account.last_sync else None,
                'folder': folder
            }), 200
            
        finally:
            # Sempre desconectar
            imap_service.disconnect()
        
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except ServerError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Error syncing account {account_id}: {e}")
        return jsonify({'error': f'Sync failed: {str(e)}'}), 500


@bp.route('/<int:account_id>/<int:email_id>/read', methods=['PUT'])
@cross_origin()
def mark_email_read(account_id: int, email_id: int):
    """
    Marca email como lido/não lido.
    
    PUT /api/v1/inbox/<account_id>/<email_id>/read
    
    Request Body:
        is_read: true/false
    
    Returns:
        200: Status atualizado
        404: Email não encontrado
        400: Parâmetros inválidos
    """
    try:
        # Buscar email
        email = EmailInbox.query.filter_by(
            id=email_id,
            account_id=account_id
        ).first()
        
        if not email:
            raise NotFound(f"Email {email_id} not found")
        
        # Obter status desejado
        data = request.get_json()
        if not data or 'is_read' not in data:
            raise BadRequest("Missing 'is_read' parameter")
        
        is_read = data['is_read']
        
        # Atualizar status
        if is_read:
            email.mark_as_read()
        else:
            email.mark_as_unread()
        
        # Tentar atualizar no servidor IMAP também
        try:
            account = email.account
            imap_service = IMAPService(account)
            
            encryption_key = current_app.config.get('SECRET_KEY', '')
            config = account.get_imap_config(encryption_key)
            
            if imap_service.connect(config):
                imap_service.select_folder(email.folder)
                imap_service.mark_as_read(email.uid, is_read)
                imap_service.disconnect()
        except Exception as e:
            logger.warning(f"Could not update IMAP server: {e}")
        
        return jsonify({
            'success': True,
            'email_id': email.id,
            'is_read': email.is_read
        }), 200
        
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except BadRequest as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error marking email as read: {e}")
        return jsonify({'error': 'Failed to update email status'}), 500


@bp.route('/<int:account_id>/<int:email_id>/flag', methods=['PUT'])
@cross_origin()
def toggle_email_flag(account_id: int, email_id: int):
    """
    Alterna flag/favorito do email.
    
    PUT /api/v1/inbox/<account_id>/<email_id>/flag
    
    Returns:
        200: Flag alternada
        404: Email não encontrado
    """
    try:
        # Buscar email
        email = EmailInbox.query.filter_by(
            id=email_id,
            account_id=account_id
        ).first()
        
        if not email:
            raise NotFound(f"Email {email_id} not found")
        
        # Alternar flag
        email.toggle_flag()
        
        # Tentar atualizar no servidor IMAP
        try:
            account = email.account
            imap_service = IMAPService(account)
            
            encryption_key = current_app.config.get('SECRET_KEY', '')
            config = account.get_imap_config(encryption_key)
            
            if imap_service.connect(config):
                imap_service.select_folder(email.folder)
                imap_service.mark_as_flagged(email.uid, email.is_flagged)
                imap_service.disconnect()
        except Exception as e:
            logger.warning(f"Could not update IMAP server: {e}")
        
        return jsonify({
            'success': True,
            'email_id': email.id,
            'is_flagged': email.is_flagged
        }), 200
        
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error toggling flag: {e}")
        return jsonify({'error': 'Failed to toggle flag'}), 500


@bp.route('/<int:account_id>/<int:email_id>', methods=['DELETE'])
@cross_origin()
def delete_email(account_id: int, email_id: int):
    """
    Deleta email (soft delete).
    
    DELETE /api/v1/inbox/<account_id>/<email_id>
    
    Query Parameters:
        permanent: true para deletar permanentemente (default: false)
    
    Returns:
        200: Email deletado
        404: Email não encontrado
    """
    try:
        # Buscar email
        email = EmailInbox.query.filter_by(
            id=email_id,
            account_id=account_id
        ).first()
        
        if not email:
            raise NotFound(f"Email {email_id} not found")
        
        permanent = request.args.get('permanent', 'false').lower() == 'true'
        
        if permanent:
            # Deletar permanentemente do banco
            email.delete()
            
            # Tentar deletar do servidor IMAP
            try:
                account = email.account
                imap_service = IMAPService(account)
                
                encryption_key = current_app.config.get('SECRET_KEY', '')
                config = account.get_imap_config(encryption_key)
                
                if imap_service.connect(config):
                    imap_service.select_folder(email.folder)
                    imap_service.delete_email(email.uid, expunge=True)
                    imap_service.disconnect()
            except Exception as e:
                logger.warning(f"Could not delete from IMAP server: {e}")
        else:
            # Soft delete
            email.soft_delete()
        
        return jsonify({
            'success': True,
            'message': 'Email deleted successfully',
            'permanent': permanent
        }), 200
        
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting email: {e}")
        return jsonify({'error': 'Failed to delete email'}), 500


@bp.route('/<int:account_id>/<int:email_id>/move', methods=['PUT'])
@cross_origin()
def move_email(account_id: int, email_id: int):
    """
    Move email para outra pasta.
    
    PUT /api/v1/inbox/<account_id>/<email_id>/move
    
    Request Body:
        folder: Nome da pasta de destino
    
    Returns:
        200: Email movido
        404: Email não encontrado
        400: Pasta não especificada
    """
    try:
        # Buscar email
        email = EmailInbox.query.filter_by(
            id=email_id,
            account_id=account_id
        ).first()
        
        if not email:
            raise NotFound(f"Email {email_id} not found")
        
        # Obter pasta de destino
        data = request.get_json()
        if not data or 'folder' not in data:
            raise BadRequest("Missing 'folder' parameter")
        
        target_folder = data['folder']
        old_folder = email.folder
        
        # Atualizar no banco
        email.move_to_folder(target_folder)
        
        # Tentar mover no servidor IMAP
        try:
            account = email.account
            imap_service = IMAPService(account)
            
            encryption_key = current_app.config.get('SECRET_KEY', '')
            config = account.get_imap_config(encryption_key)
            
            if imap_service.connect(config):
                imap_service.select_folder(old_folder)
                imap_service.move_email(email.uid, target_folder)
                imap_service.disconnect()
        except Exception as e:
            logger.warning(f"Could not move on IMAP server: {e}")
        
        return jsonify({
            'success': True,
            'email_id': email.id,
            'folder': email.folder,
            'old_folder': old_folder
        }), 200
        
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except BadRequest as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error moving email: {e}")
        return jsonify({'error': 'Failed to move email'}), 500


@bp.route('/<int:account_id>/stats', methods=['GET'])
@cross_origin()
def get_inbox_stats(account_id: int):
    """
    Estatísticas do inbox da conta.
    
    GET /api/v1/inbox/<account_id>/stats
    
    Returns:
        200: Estatísticas do inbox
        404: Conta não encontrada
    """
    try:
        # Buscar conta
        account = EmailAccount.get_by_id(account_id)
        if not account:
            raise NotFound(f"Account {account_id} not found")
        
        # Calcular estatísticas
        total_emails = EmailInbox.query.filter_by(
            account_id=account_id,
            is_deleted=False
        ).count()
        
        unread_emails = EmailInbox.query.filter_by(
            account_id=account_id,
            is_read=False,
            is_deleted=False
        ).count()
        
        flagged_emails = EmailInbox.query.filter_by(
            account_id=account_id,
            is_flagged=True,
            is_deleted=False
        ).count()
        
        with_attachments = EmailInbox.query.filter_by(
            account_id=account_id,
            has_attachments=True,
            is_deleted=False
        ).count()
        
        # Contar por pasta
        from sqlalchemy import func
        folder_counts = db.session.query(
            EmailInbox.folder,
            func.count(EmailInbox.id).label('count')
        ).filter(
            EmailInbox.account_id == account_id,
            EmailInbox.is_deleted == False
        ).group_by(EmailInbox.folder).all()
        
        folders = {folder: count for folder, count in folder_counts}
        
        return jsonify({
            'account': {
                'id': account.id,
                'email': account.email_address,
                'last_sync': account.last_sync.isoformat() if account.last_sync else None
            },
            'stats': {
                'total_emails': total_emails,
                'unread_emails': unread_emails,
                'flagged_emails': flagged_emails,
                'with_attachments': with_attachments,
                'folders': folders
            }
        }), 200
        
    except NotFound as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting inbox stats: {e}")
        return jsonify({'error': 'Failed to get stats'}), 500