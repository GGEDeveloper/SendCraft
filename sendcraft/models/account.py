"""Modelo de Conta de Email para SendCraft."""
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from typing import Optional, Dict, Any, List
from email_validator import validate_email, EmailNotValidError
from datetime import datetime

from .base import BaseModel, TimestampMixin
from ..utils.crypto import AESCipher
from ..utils.logging import get_logger

logger = get_logger(__name__)


class EmailAccount(BaseModel, TimestampMixin):
    """
    Representa uma conta de email SMTP.
    
    Attributes:
        domain_id: ID do domínio associado
        local_part: Parte local do email (antes do @)
        email_address: Endereço completo de email
        smtp_server: Servidor SMTP
        smtp_port: Porta SMTP
        smtp_username: Username para autenticação
        smtp_password: Password encriptada
        use_tls: Se deve usar TLS
        use_ssl: Se deve usar SSL
        is_active: Se a conta está ativa
        daily_limit: Limite diário de emails
        monthly_limit: Limite mensal de emails
        display_name: Nome de exibição
    """
    
    __tablename__ = 'email_accounts'
    
    # Domain relationship
    domain_id = Column(Integer, ForeignKey('domains.id'), nullable=False)
    domain = relationship('Domain', back_populates='accounts')
    
    # Email configuration
    local_part = Column(String(100), nullable=False)
    email_address = Column(String(200), unique=True, nullable=False, index=True)
    display_name = Column(String(200))
    
    # SMTP configuration
    smtp_server = Column(String(200), nullable=False, default='smtp.antispamcloud.com')
    smtp_port = Column(Integer, nullable=False, default=587)
    smtp_username = Column(String(200))
    smtp_password = Column(Text)  # Encrypted
    use_tls = Column(Boolean, default=True, nullable=False)
    use_ssl = Column(Boolean, default=False, nullable=False)
    
    # Status and limits
    is_active = Column(Boolean, default=True, nullable=False)
    daily_limit = Column(Integer, default=1000, nullable=False)
    monthly_limit = Column(Integer, default=20000, nullable=False)
    # IMAP Configuration
    imap_server = Column(String(200), default='mail.alitools.pt')
    imap_port = Column(Integer, default=993)
    imap_use_ssl = Column(Boolean, default=True)
    imap_use_tls = Column(Boolean, default=False)
    last_sync = Column(DateTime)
    auto_sync_enabled = Column(Boolean, default=True)
    sync_interval_minutes = Column(Integer, default=5)
    
    # Relationships
    logs = relationship('EmailLog', back_populates='account', lazy='dynamic', cascade='all, delete-orphan')
    inbox_emails = relationship('EmailInbox', back_populates='account', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f'<EmailAccount {self.email_address}>'
    
    def __init__(self, **kwargs):
        """
        Inicializa conta de email.
        Auto-gera email_address se não fornecido.
        """
        # Auto-generate email_address from local_part and domain
        if 'local_part' in kwargs and 'domain_id' in kwargs and 'email_address' not in kwargs:
            # Import aqui para evitar circular import
            from .domain import Domain
            domain = Domain.query.get(kwargs['domain_id'])
            if domain:
                kwargs['email_address'] = f"{kwargs['local_part']}@{domain.name}"
        
        # Set default smtp_username to email_address if not provided
        if 'smtp_username' not in kwargs and 'email_address' in kwargs:
            kwargs['smtp_username'] = kwargs['email_address']
        
        super().__init__(**kwargs)
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['EmailAccount']:
        """
        Busca conta por email.
        
        Args:
            email: Endereço de email
            
        Returns:
            Conta de email ou None
        """
        return cls.query.filter_by(email_address=email).first()
    
    @classmethod
    def get_active_accounts(cls) -> List['EmailAccount']:
        """
        Retorna todas as contas ativas.
        
        Returns:
            Lista de contas ativas
        """
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def get_accounts_by_domain(cls, domain_id: int, active_only: bool = False) -> List['EmailAccount']:
        """
        Retorna contas de um domínio.
        
        Args:
            domain_id: ID do domínio
            active_only: Se deve filtrar apenas ativas
            
        Returns:
            Lista de contas
        """
        query = cls.query.filter_by(domain_id=domain_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()
    
    def set_password(self, password: str, encryption_key: str) -> None:
        """
        Define password encriptada.
        
        Args:
            password: Password em texto plano
            encryption_key: Chave de encriptação
        """
        if password:
            cipher = AESCipher(encryption_key)
            self.smtp_password = cipher.encrypt(password)
            logger.debug(f"Password set for account {self.email_address}")
    
    def get_password(self, encryption_key: str) -> str:
        """
        Retorna password decriptada.
        
        Args:
            encryption_key: Chave de decriptação
            
        Returns:
            Password em texto plano
        """
        if not self.smtp_password:
            return ''
        
        try:
            cipher = AESCipher(encryption_key)
            return cipher.decrypt(self.smtp_password)
        except Exception as e:
            logger.error(f"Failed to decrypt password for {self.email_address}: {e}")
            return ''
    
    def validate_email(self) -> bool:
        """
        Valida formato do email.
        
        Returns:
            True se o email é válido
        """
        try:
            validate_email(self.email_address)
            return True
        except EmailNotValidError:
            return False
    
    def get_smtp_config(self, encryption_key: str) -> Dict[str, Any]:
        """
        Retorna configuração SMTP para uso.
        
        Args:
            encryption_key: Chave para decriptar password
            
        Returns:
            Dicionário com configuração SMTP
        """
        return {
            'server': self.smtp_server,
            'port': self.smtp_port,
            'username': self.smtp_username or self.email_address,
            'password': self.get_password(encryption_key),
            'use_tls': self.use_tls,
            'use_ssl': self.use_ssl,
            'from_email': self.email_address,
            'from_name': self.display_name or self.local_part
        }
    
    def get_imap_config(self, encryption_key: str) -> Dict[str, Any]:
        """
        Retorna configuração IMAP para conexão.
        
        Args:
            encryption_key: Chave para decriptar password
            
        Returns:
            Dicionário com configuração IMAP
        """
        return {
            'server': self.imap_server,
            'port': self.imap_port,
            'username': self.email_address,
            'password': self.get_password(encryption_key),
            'use_ssl': self.imap_use_ssl,
            'use_tls': self.imap_use_tls
        }
    
    def count_emails_sent_today(self) -> int:
        """
        Conta emails enviados hoje.
        
        Returns:
            Número de emails enviados hoje
        """
        from datetime import datetime, timedelta
        from .log import EmailLog, EmailStatus
        
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        
        return self.logs.filter(
            EmailLog.created_at >= today,
            EmailLog.created_at < tomorrow,
            EmailLog.status.in_([EmailStatus.SENT, EmailStatus.DELIVERED])
        ).count()
    
    def count_emails_sent_this_month(self) -> int:
        """
        Conta emails enviados este mês.
        
        Returns:
            Número de emails enviados este mês
        """
        from datetime import datetime
        from .log import EmailLog, EmailStatus
        
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        
        return self.logs.filter(
            EmailLog.created_at >= start_of_month,
            EmailLog.status.in_([EmailStatus.SENT, EmailStatus.DELIVERED])
        ).count()
    
    def is_within_limits(self) -> tuple[bool, str]:
        """
        Verifica se a conta está dentro dos limites.
        
        Returns:
            Tuple (is_within_limits, message)
        """
        daily_count = self.count_emails_sent_today()
        if daily_count >= self.daily_limit:
            return False, f"Daily limit reached ({self.daily_limit})"
        
        monthly_count = self.count_emails_sent_this_month()
        if monthly_count >= self.monthly_limit:
            return False, f"Monthly limit reached ({self.monthly_limit})"
        
        return True, "Within limits"
    
    def needs_sync(self) -> bool:
        """
        Verifica se a conta precisa de sincronização.
        
        Returns:
            True se precisa sincronizar
        """
        if not self.auto_sync_enabled:
            return False
        
        if not self.last_sync:
            return True
        
        from datetime import datetime, timedelta
        
        time_since_sync = datetime.utcnow() - self.last_sync
        sync_interval = timedelta(minutes=self.sync_interval_minutes)
        
        return time_since_sync >= sync_interval
    
    def update_last_sync(self, commit: bool = True) -> None:
        """
        Atualiza timestamp da última sincronização.
        
        Args:
            commit: Se deve fazer commit
        """
        self.last_sync = datetime.utcnow()
        if commit:
            self.save()
    
    def count_inbox_emails(self, unread_only: bool = False) -> int:
        """
        Conta emails no inbox.
        
        Args:
            unread_only: Se deve contar apenas não lidos
            
        Returns:
            Número de emails no inbox
        """
        from .email_inbox import EmailInbox
        
        query = self.inbox_emails.filter(
            EmailInbox.is_deleted == False,
            EmailInbox.folder == 'INBOX'
        )
        
        if unread_only:
            query = query.filter(EmailInbox.is_read == False)
        
        return query.count()
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """
        Converte modelo para dicionário.
        
        Args:
            include_relationships: Se deve incluir relacionamentos
            
        Returns:
            Dicionário com os dados
        """
        data = super().to_dict()
        
        # Não incluir password encriptada
        data.pop('smtp_password', None)
        
        # Converter datetime para ISO format
        if self.last_sync:
            data['last_sync'] = self.last_sync.isoformat()
        
        if include_relationships and self.domain:
            data['domain_name'] = self.domain.name
            data['emails_sent_today'] = self.count_emails_sent_today()
            data['emails_sent_this_month'] = self.count_emails_sent_this_month()
            data['inbox_email_count'] = self.count_inbox_emails()
            data['unread_email_count'] = self.count_inbox_emails(unread_only=True)
            data['needs_sync'] = self.needs_sync()
        
        return data