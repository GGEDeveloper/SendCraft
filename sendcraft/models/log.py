"""Modelo de Log de Email para SendCraft."""
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum

from .base import BaseModel
from ..utils.logging import get_logger

logger = get_logger(__name__)


class EmailStatus(str, Enum):
    """Status possíveis de um email."""
    PENDING = 'pending'
    SENDING = 'sending'
    SENT = 'sent'
    FAILED = 'failed'
    BOUNCED = 'bounced'
    DELIVERED = 'delivered'
    OPENED = 'opened'
    CLICKED = 'clicked'


class EmailLog(BaseModel):
    """
    Log de envio de emails.
    
    Attributes:
        account_id: ID da conta que enviou
        template_id: ID do template usado (opcional)
        recipient_email: Email do destinatário
        sender_email: Email do remetente
        subject: Assunto do email
        status: Status do envio
        message_id: ID da mensagem SMTP
        smtp_response: Resposta do servidor SMTP
        error_message: Mensagem de erro (se houver)
        variables_used: Variáveis utilizadas no template
        sent_at: Timestamp de envio
        delivered_at: Timestamp de entrega
        opened_at: Timestamp de abertura
        clicked_at: Timestamp de clique
        user_agent: User agent do cliente (para tracking)
        ip_address: IP de origem da requisição
    """
    
    __tablename__ = 'email_logs'
    
    # Relationships
    account_id = Column(Integer, ForeignKey('email_accounts.id'), nullable=False)
    account = relationship('EmailAccount', back_populates='logs')
    
    template_id = Column(Integer, ForeignKey('email_templates.id'), nullable=True)
    template = relationship('EmailTemplate', back_populates='logs')
    
    # Email details
    recipient_email = Column(String(200), nullable=False, index=True)
    sender_email = Column(String(200), nullable=False)
    subject = Column(Text)
    
    # Status tracking
    status = Column(
        SQLEnum(EmailStatus),
        nullable=False,
        default=EmailStatus.PENDING,
        index=True
    )
    message_id = Column(String(500), index=True)
    smtp_response = Column(Text)
    error_message = Column(Text)
    
    # Template data
    variables_used = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    sent_at = Column(DateTime, index=True)
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    
    # Request tracking
    user_agent = Column(String(500))
    ip_address = Column(String(45))  # Supports IPv6
    
    def __repr__(self) -> str:
        return f'<EmailLog {self.id}: {self.recipient_email} ({self.status})>'
    
    @classmethod
    def get_recent_logs(cls, limit: int = 50) -> List['EmailLog']:
        """
        Retorna logs recentes.
        
        Args:
            limit: Número máximo de logs
            
        Returns:
            Lista de logs recentes
        """
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_logs_by_account(cls, account_id: int, limit: int = 100) -> List['EmailLog']:
        """
        Retorna logs de uma conta específica.
        
        Args:
            account_id: ID da conta
            limit: Número máximo de logs
            
        Returns:
            Lista de logs da conta
        """
        return cls.query.filter_by(account_id=account_id)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_logs_by_recipient(cls, recipient_email: str, limit: int = 100) -> List['EmailLog']:
        """
        Retorna logs para um destinatário específico.
        
        Args:
            recipient_email: Email do destinatário
            limit: Número máximo de logs
            
        Returns:
            Lista de logs
        """
        return cls.query.filter_by(recipient_email=recipient_email)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_logs_by_status(cls, status: EmailStatus, limit: int = 100) -> List['EmailLog']:
        """
        Retorna logs por status.
        
        Args:
            status: Status do email
            limit: Número máximo de logs
            
        Returns:
            Lista de logs com o status
        """
        return cls.query.filter_by(status=status)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_failed_logs(cls, days: int = 7, limit: int = 100) -> List['EmailLog']:
        """
        Retorna logs de emails falhados.
        
        Args:
            days: Número de dias para buscar
            limit: Número máximo de logs
            
        Returns:
            Lista de logs falhados
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return cls.query.filter(
            cls.status == EmailStatus.FAILED,
            cls.created_at >= cutoff_date
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_stats_by_account(cls, account_id: int, days: int = 30) -> Dict[str, int]:
        """
        Retorna estatísticas de uma conta.
        
        Args:
            account_id: ID da conta
            days: Número de dias para análise
            
        Returns:
            Dicionário com estatísticas por status
        """
        from sqlalchemy import func
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        stats = cls.query.filter(
            cls.account_id == account_id,
            cls.created_at >= cutoff_date
        ).with_entities(
            cls.status,
            func.count(cls.id).label('count')
        ).group_by(cls.status).all()
        
        return {stat.status.value if stat.status else 'unknown': stat.count for stat in stats}
    
    @classmethod
    def get_global_stats(cls, days: int = 30) -> Dict[str, Any]:
        """
        Retorna estatísticas globais.
        
        Args:
            days: Número de dias para análise
            
        Returns:
            Dicionário com estatísticas globais
        """
        from sqlalchemy import func
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Contar por status
        status_stats = cls.query.filter(
            cls.created_at >= cutoff_date
        ).with_entities(
            cls.status,
            func.count(cls.id).label('count')
        ).group_by(cls.status).all()
        
        # Total de emails
        total = cls.query.filter(cls.created_at >= cutoff_date).count()
        
        # Taxa de sucesso
        sent_count = sum(s.count for s in status_stats 
                        if s.status in [EmailStatus.SENT, EmailStatus.DELIVERED])
        success_rate = (sent_count / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'by_status': {s.status.value: s.count for s in status_stats},
            'success_rate': round(success_rate, 2),
            'period_days': days
        }
    
    def mark_sending(self) -> None:
        """Marca email como enviando."""
        self.status = EmailStatus.SENDING
        self.save()
    
    def mark_sent(self, message_id: str, smtp_response: Optional[str] = None) -> None:
        """
        Marca email como enviado.
        
        Args:
            message_id: ID da mensagem SMTP
            smtp_response: Resposta do servidor SMTP
        """
        self.status = EmailStatus.SENT
        self.message_id = message_id
        self.smtp_response = smtp_response
        self.sent_at = datetime.utcnow()
        self.save()
        logger.info(f"Email {self.id} marked as sent")
    
    def mark_failed(self, error_message: str) -> None:
        """
        Marca email como falhou.
        
        Args:
            error_message: Mensagem de erro
        """
        self.status = EmailStatus.FAILED
        self.error_message = error_message
        self.save()
        logger.error(f"Email {self.id} marked as failed: {error_message}")
    
    def mark_delivered(self) -> None:
        """Marca email como entregue."""
        self.status = EmailStatus.DELIVERED
        self.delivered_at = datetime.utcnow()
        self.save()
        logger.info(f"Email {self.id} marked as delivered")
    
    def mark_opened(self, user_agent: Optional[str] = None, ip_address: Optional[str] = None) -> None:
        """
        Marca email como aberto.
        
        Args:
            user_agent: User agent do cliente
            ip_address: IP do cliente
        """
        if self.status not in [EmailStatus.OPENED, EmailStatus.CLICKED]:
            self.status = EmailStatus.OPENED
            self.opened_at = self.opened_at or datetime.utcnow()
            
            if user_agent:
                self.user_agent = user_agent
            if ip_address:
                self.ip_address = ip_address
            
            self.save()
            logger.info(f"Email {self.id} marked as opened")
    
    def mark_clicked(self, user_agent: Optional[str] = None, ip_address: Optional[str] = None) -> None:
        """
        Marca email como clicado.
        
        Args:
            user_agent: User agent do cliente
            ip_address: IP do cliente
        """
        self.status = EmailStatus.CLICKED
        self.clicked_at = self.clicked_at or datetime.utcnow()
        
        # Também marcar como aberto se não estiver
        if not self.opened_at:
            self.opened_at = datetime.utcnow()
        
        if user_agent:
            self.user_agent = user_agent
        if ip_address:
            self.ip_address = ip_address
        
        self.save()
        logger.info(f"Email {self.id} marked as clicked")
    
    def get_duration(self) -> Optional[timedelta]:
        """
        Calcula duração entre criação e envio.
        
        Returns:
            Duração ou None
        """
        if self.sent_at and self.created_at:
            return self.sent_at - self.created_at
        return None
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """
        Converte modelo para dicionário.
        
        Args:
            include_relationships: Se deve incluir relacionamentos
            
        Returns:
            Dicionário com os dados
        """
        data = super().to_dict()
        
        # Converter enum para string
        if 'status' in data and data['status']:
            data['status'] = data['status'].value if isinstance(data['status'], EmailStatus) else data['status']
        
        if include_relationships:
            if self.account:
                data['account_email'] = self.account.email_address
            
            if self.template:
                data['template_key'] = self.template.template_key
                data['template_name'] = self.template.template_name
            
            # Calcular duração
            duration = self.get_duration()
            if duration:
                data['duration_seconds'] = duration.total_seconds()
        
        return data