"""
Rotas para configuração de autosync.
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from typing import Dict, Any

from ..models import AutosyncConfig, Domain, EmailAccount
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)

autosync_bp = Blueprint('autosync', __name__, url_prefix='/autosync')


@autosync_bp.route('')
def autosync_list():
    """Lista todas as configurações de autosync."""
    try:
        configs = AutosyncConfig.query.order_by(AutosyncConfig.created_at.desc()).all()
        
        # Buscar domínios e contas para formulário
        domains = Domain.query.filter_by(is_active=True).order_by(Domain.name).all()
        accounts = EmailAccount.query.filter_by(is_active=True).order_by(EmailAccount.email_address).all()
        
        return render_template('autosync/list.html',
                             configs=configs,
                             domains=domains,
                             accounts=accounts,
                             page_title='Autosync - Configurações')
        
    except Exception as e:
        logger.error(f"Error loading autosync list: {e}", exc_info=True)
        flash('Erro ao carregar configurações de autosync', 'error')
        return redirect(url_for('web.dashboard'))


@autosync_bp.route('/create', methods=['POST'])
def autosync_create():
    """Criar nova configuração de autosync."""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Validar dados
        domain_id = data.get('domain_id')
        account_id = data.get('account_id')
        
        if not domain_id and not account_id:
            return jsonify({'success': False, 'error': 'Deve especificar domain_id ou account_id'}), 400
        
        if domain_id and account_id:
            return jsonify({'success': False, 'error': 'Não pode especificar domain_id e account_id simultaneamente'}), 400
        
        # Verificar se já existe configuração
        if domain_id:
            existing = AutosyncConfig.get_by_domain(int(domain_id))
            if existing:
                return jsonify({'success': False, 'error': 'Já existe configuração para este domínio'}), 400
        
        if account_id:
            existing = AutosyncConfig.get_by_account(int(account_id))
            if existing:
                return jsonify({'success': False, 'error': 'Já existe configuração para esta conta'}), 400
        
        # Criar configuração
        config = AutosyncConfig(
            domain_id=int(domain_id) if domain_id else None,
            account_id=int(account_id) if account_id else None,
            is_enabled=data.get('is_enabled', 'true').lower() == 'true',
            sync_interval_minutes=int(data.get('sync_interval_minutes', 30)),
            limit_per_sync=int(data.get('limit_per_sync', 50)),
            full_sync=data.get('full_sync', 'false').lower() == 'true',
            folder=data.get('folder', 'INBOX'),
            sync_only_unread=data.get('sync_only_unread', 'false').lower() == 'true'
        )
        
        db.session.add(config)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'config': config.to_dict()}), 201
        else:
            flash('Configuração de autosync criada com sucesso!', 'success')
            return redirect(url_for('autosync.autosync_list'))
        
    except Exception as e:
        logger.error(f"Error creating autosync config: {e}", exc_info=True)
        db.session.rollback()
        
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash(f'Erro ao criar configuração: {str(e)}', 'error')
            return redirect(url_for('autosync.autosync_list'))


@autosync_bp.route('/<int:config_id>/update', methods=['POST'])
def autosync_update(config_id: int):
    """Atualizar configuração de autosync."""
    try:
        config = AutosyncConfig.query.get_or_404(config_id)
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Atualizar campos
        if 'is_enabled' in data:
            config.is_enabled = data['is_enabled'].lower() == 'true' if isinstance(data['is_enabled'], str) else bool(data['is_enabled'])
        
        if 'sync_interval_minutes' in data:
            config.sync_interval_minutes = int(data['sync_interval_minutes'])
        
        if 'limit_per_sync' in data:
            config.limit_per_sync = int(data['limit_per_sync'])
        
        if 'full_sync' in data:
            config.full_sync = data['full_sync'].lower() == 'true' if isinstance(data['full_sync'], str) else bool(data['full_sync'])
        
        if 'folder' in data:
            config.folder = data['folder']
        
        if 'sync_only_unread' in data:
            config.sync_only_unread = data['sync_only_unread'].lower() == 'true' if isinstance(data['sync_only_unread'], str) else bool(data['sync_only_unread'])
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'config': config.to_dict()}), 200
        else:
            flash('Configuração atualizada com sucesso!', 'success')
            return redirect(url_for('autosync.autosync_list'))
        
    except Exception as e:
        logger.error(f"Error updating autosync config: {e}", exc_info=True)
        db.session.rollback()
        
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash(f'Erro ao atualizar configuração: {str(e)}', 'error')
            return redirect(url_for('autosync.autosync_list'))


@autosync_bp.route('/<int:config_id>/delete', methods=['POST'])
def autosync_delete(config_id: int):
    """Eliminar configuração de autosync."""
    try:
        config = AutosyncConfig.query.get_or_404(config_id)
        db.session.delete(config)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True}), 200
        else:
            flash('Configuração eliminada com sucesso!', 'success')
            return redirect(url_for('autosync.autosync_list'))
        
    except Exception as e:
        logger.error(f"Error deleting autosync config: {e}", exc_info=True)
        db.session.rollback()
        
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash(f'Erro ao eliminar configuração: {str(e)}', 'error')
            return redirect(url_for('autosync.autosync_list'))

