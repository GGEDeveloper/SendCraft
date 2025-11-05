"""
Serviço de autosync para sincronização automática de emails.
"""
import threading
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from flask import Flask, current_app

from ..models import AutosyncConfig, Domain
from ..models.account import EmailAccount
from ..services.imap_service import IMAPService
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)


class AutosyncService:
    """
    Serviço para sincronização automática de emails.
    
    Executa em thread separada e sincroniza emails baseado nas configurações
    de autosync ativas.
    """
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self._lock = threading.Lock()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Inicializar serviço com app Flask."""
        self.app = app
        
        # Registrar shutdown handler
        @app.teardown_appcontext
        def shutdown_autosync(error):
            if error:
                self.stop()
    
    def start(self):
        """Iniciar serviço de autosync."""
        with self._lock:
            if self.running:
                logger.warning("Autosync já está em execução")
                return
            
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info("✅ Autosync iniciado")
    
    def stop(self):
        """Parar serviço de autosync."""
        with self._lock:
            if not self.running:
                return
            
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            logger.info("⏹️ Autosync parado")
    
    def _run(self):
        """Loop principal do autosync."""
        logger.info("🔄 Autosync thread iniciada")
        
        while self.running:
            try:
                # Executar em contexto Flask
                with self.app.app_context():
                    self._sync_all_configs()
                
                # Aguardar 1 minuto antes da próxima verificação
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Erro no loop de autosync: {e}", exc_info=True)
                time.sleep(60)  # Continuar mesmo em caso de erro
    
    def _sync_all_configs(self):
        """Sincronizar todas as configurações que devem ser sincronizadas."""
        try:
            configs = AutosyncConfig.get_all_enabled()
            
            if not configs:
                return
            
            logger.debug(f"Verificando {len(configs)} configurações de autosync")
            
            for config in configs:
                if not config.should_sync_now():
                    continue
                
                try:
                    self._sync_config(config)
                except Exception as e:
                    logger.error(f"Erro ao sincronizar config {config.id}: {e}", exc_info=True)
                    config.last_sync_status = 'failed'
                    config.last_sync_message = str(e)
                    config.last_synced_count = 0
                    db.session.commit()
        
        except Exception as e:
            logger.error(f"Erro ao processar configurações de autosync: {e}", exc_info=True)
    
    def _sync_config(self, config: AutosyncConfig):
        """Sincronizar uma configuração específica."""
        encryption_key = current_app.config.get('ENCRYPTION_KEY') or current_app.config.get('SECRET_KEY', '')
        imap_service = IMAPService(encryption_key)
        
        if config.domain_id:
            # Sincronizar todas as contas do domínio
            self._sync_domain(config, imap_service)
        elif config.account_id:
            # Sincronizar conta específica
            self._sync_account(config, imap_service)
    
    def _sync_domain(self, config: AutosyncConfig, imap_service: IMAPService):
        """Sincronizar todas as contas de um domínio."""
        domain = Domain.query.get(config.domain_id)
        if not domain:
            logger.warning(f"Domínio {config.domain_id} não encontrado")
            return
        
        accounts = EmailAccount.query.filter_by(
            domain_id=config.domain_id,
            is_active=True
        ).all()
        
        if not accounts:
            logger.debug(f"Nenhuma conta ativa no domínio {domain.name}")
            config.last_sync_status = 'skipped'
            config.last_sync_message = 'Nenhuma conta ativa'
            config.last_synced_count = 0
            config.last_sync_at = datetime.utcnow()
            db.session.commit()
            return
        
        total_synced = 0
        successful_accounts = 0
        
        for account in accounts:
            try:
                count = self._sync_single_account(
                    account,
                    imap_service,
                    config.folder,
                    config.limit_per_sync,
                    config.full_sync,
                    config.sync_only_unread
                )
                total_synced += count
                successful_accounts += 1
            except Exception as e:
                logger.error(f"Erro ao sincronizar {account.email_address}: {e}")
        
        # Atualizar configuração
        config.last_sync_status = 'success'
        config.last_sync_message = f"{successful_accounts}/{len(accounts)} contas sincronizadas"
        config.last_synced_count = total_synced
        config.last_sync_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"✅ Domínio {domain.name}: {total_synced} emails sincronizados de {successful_accounts}/{len(accounts)} contas")
    
    def _sync_account(self, config: AutosyncConfig, imap_service: IMAPService):
        """Sincronizar conta específica."""
        account = EmailAccount.query.get(config.account_id)
        if not account:
            logger.warning(f"Conta {config.account_id} não encontrada")
            return
        
        if not account.is_active:
            logger.debug(f"Conta {account.email_address} não está ativa")
            config.last_sync_status = 'skipped'
            config.last_sync_message = 'Conta inativa'
            config.last_synced_count = 0
            config.last_sync_at = datetime.utcnow()
            db.session.commit()
            return
        
        try:
            count = self._sync_single_account(
                account,
                imap_service,
                config.folder,
                config.limit_per_sync,
                config.full_sync,
                config.sync_only_unread
            )
            
            config.last_sync_status = 'success'
            config.last_sync_message = f"{count} emails sincronizados"
            config.last_synced_count = count
            config.last_sync_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"✅ Conta {account.email_address}: {count} emails sincronizados")
            
        except Exception as e:
            raise  # Re-raise para ser capturado no _sync_config
    
    def _sync_single_account(
        self,
        account: EmailAccount,
        imap_service: IMAPService,
        folder: str,
        limit: int,
        full_sync: bool,
        sync_only_unread: bool
    ) -> int:
        """Sincronizar uma única conta."""
        try:
            encryption_key = current_app.config.get('ENCRYPTION_KEY') or current_app.config.get('SECRET_KEY', '')
            imap = IMAPService(account=account)
            
            # Obter configuração IMAP da conta
            imap_config = account.get_imap_config(encryption_key)
            
            # Conectar
            if not imap.connect(imap_config):
                raise Exception("Falha ao conectar ao servidor IMAP")
            
            try:
                # Usar método sync_account_emails do IMAPService
                synced_count = imap.sync_account_emails(
                    account=account,
                    folder=folder,
                    limit=limit,
                    since_last_sync=not full_sync
                )
                
                return synced_count
                
            finally:
                imap.disconnect()
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar conta {account.email_address}: {e}")
            raise


# Instância global do serviço
_autosync_service: Optional[AutosyncService] = None


def get_autosync_service(app: Flask = None) -> AutosyncService:
    """Obter instância do serviço de autosync."""
    global _autosync_service
    
    if _autosync_service is None:
        _autosync_service = AutosyncService(app)
    
    return _autosync_service


def start_autosync(app: Flask):
    """Iniciar autosync (chamado na inicialização do app)."""
    service = get_autosync_service(app)
    
    # Verificar se há configurações ativas
    with app.app_context():
        configs = AutosyncConfig.get_all_enabled()
        if configs:
            service.start()
            logger.info(f"✅ Autosync iniciado com {len(configs)} configurações ativas")
        else:
            logger.info("ℹ️ Nenhuma configuração de autosync ativa, serviço não iniciado")


def stop_autosync():
    """Parar autosync."""
    global _autosync_service
    
    if _autosync_service:
        _autosync_service.stop()

