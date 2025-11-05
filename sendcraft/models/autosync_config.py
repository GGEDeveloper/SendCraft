"""
Modelo para configuração de autosync de emails.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, Interval, DateTime, Text
from sqlalchemy.orm import relationship
from typing import Optional, Dict, Any

from ..extensions import db


class AutosyncConfig(db.Model):
    """
    Configuração de autosync para sincronização automática de emails.
    
    Permite configurar sincronização automática por:
    - Domínio (todas as contas do domínio)
    - Conta individual
    """
    __tablename__ = 'autosync_configs'
    
    id = Column(Integer, primary_key=True)
    
    # Relacionamento: pode ser por domínio ou por conta
    domain_id = Column(Integer, ForeignKey('domains.id'), nullable=True, index=True)
    account_id = Column(Integer, ForeignKey('email_accounts.id'), nullable=True, index=True)
    
    # Configurações
    is_enabled = Column(Boolean, default=True, nullable=False)
    sync_interval_minutes = Column(Integer, default=30, nullable=False)  # Intervalo em minutos
    limit_per_sync = Column(Integer, default=50, nullable=False)  # Limite de emails por sincronização
    full_sync = Column(Boolean, default=False, nullable=False)  # Sincronização completa ou incremental
    
    # Configurações avançadas
    folder = Column(String(100), default='INBOX', nullable=False)  # Pasta a sincronizar
    sync_only_unread = Column(Boolean, default=False, nullable=False)  # Sincronizar apenas não lidos
    
    # Status e tracking
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String(20), nullable=True)  # success, failed, skipped
    last_sync_message = Column(Text, nullable=True)
    last_synced_count = Column(Integer, default=0, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    domain = relationship('Domain', backref='autosync_configs')
    account = relationship('EmailAccount', backref='autosync_configs')
    
    def __init__(self, **kwargs):
        """Inicializar configuração de autosync."""
        # Validar que tem domain_id OU account_id, mas não ambos
        if not kwargs.get('domain_id') and not kwargs.get('account_id'):
            raise ValueError("AutosyncConfig deve ter domain_id ou account_id")
        if kwargs.get('domain_id') and kwargs.get('account_id'):
            raise ValueError("AutosyncConfig não pode ter domain_id e account_id simultaneamente")
        
        super().__init__(**kwargs)
    
    def __repr__(self):
        scope = f"domain_id={self.domain_id}" if self.domain_id else f"account_id={self.account_id}"
        return f"<AutosyncConfig {scope} interval={self.sync_interval_minutes}min enabled={self.is_enabled}>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário."""
        return {
            'id': self.id,
            'domain_id': self.domain_id,
            'account_id': self.account_id,
            'is_enabled': self.is_enabled,
            'sync_interval_minutes': self.sync_interval_minutes,
            'limit_per_sync': self.limit_per_sync,
            'full_sync': self.full_sync,
            'folder': self.folder,
            'sync_only_unread': self.sync_only_unread,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'last_sync_status': self.last_sync_status,
            'last_sync_message': self.last_sync_message,
            'last_synced_count': self.last_synced_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def should_sync_now(self) -> bool:
        """Verificar se deve sincronizar agora baseado no intervalo."""
        if not self.is_enabled:
            return False
        
        if not self.last_sync_at:
            return True  # Nunca sincronizou
        
        from datetime import timedelta
        next_sync = self.last_sync_at + timedelta(minutes=self.sync_interval_minutes)
        return datetime.utcnow() >= next_sync
    
    @classmethod
    def get_by_domain(cls, domain_id: int) -> Optional['AutosyncConfig']:
        """Buscar configuração por domínio."""
        return cls.query.filter_by(domain_id=domain_id).first()
    
    @classmethod
    def get_by_account(cls, account_id: int) -> Optional['AutosyncConfig']:
        """Buscar configuração por conta."""
        return cls.query.filter_by(account_id=account_id).first()
    
    @classmethod
    def get_all_enabled(cls):
        """Buscar todas as configurações ativas."""
        return cls.query.filter_by(is_enabled=True).all()

