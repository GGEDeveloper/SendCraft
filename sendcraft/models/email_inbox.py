"""Modelo de Email Inbox para SendCraft."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime, 
    ForeignKey, Index, func, LargeBinary
)
from sqlalchemy.orm import relationship, Query
from sqlalchemy.ext.hybrid import hybrid_property
import json

from .base import BaseModel, TimestampMixin
from ..utils.logging import get_logger

logger = get_logger(__name__)


class EmailInbox(BaseModel, TimestampMixin):
    """
    Representa um email recebido no inbox.
    
    Attributes:
        account_id: ID da conta de email associada
        message_id: Message-ID único do email (cabeçalho RFC)
        uid: UID do email no servidor IMAP
        from_address: Endereço do remetente
        from_name: Nome do remetente
        to_address: Endereço do destinatário principal
        cc_addresses: Endereços CC (separados por vírgula)
        bcc_addresses: Endereços BCC (separados por vírgula)
        subject: Assunto do email
        body_text: Corpo do email em texto plano
        body_html: Corpo do email em HTML
        received_at: Data/hora de recebimento
        is_read: Se o email foi lido
        is_flagged: Se o email está marcado/favorito
        is_deleted: Se o email foi marcado como deletado
        has_attachments: Se o email tem anexos
        attachments_json: JSON com metadados dos anexos
        raw_headers: Cabeçalhos originais do email
        thread_id: ID da thread/conversa
        in_reply_to: Message-ID do email respondido
        references: Referências de emails anteriores na thread
        size_bytes: Tamanho do email em bytes
        folder: Pasta/folder IMAP
        labels: Labels/tags do email
        priority: Prioridade do email (1-5)
    """
    
    __tablename__ = 'email_inbox'
    
    # Relacionamento com conta
    account_id = Column(Integer, ForeignKey('email_accounts.id'), nullable=False)
    account = relationship('EmailAccount', back_populates='inbox_emails')
    
    # Identificadores únicos
    message_id = Column(String(500), index=True)  # Message-ID do cabeçalho
    uid = Column(String(100))  # UID do IMAP
    
    # Endereços
    from_address = Column(String(200), nullable=False, index=True)
    from_name = Column(String(200))
    to_address = Column(Text)  # Pode ter múltiplos
    cc_addresses = Column(Text)  # Múltiplos separados por vírgula
    bcc_addresses = Column(Text)  # Múltiplos separados por vírgula
    reply_to = Column(String(200))
    
    # Conteúdo
    subject = Column(String(500), index=True)
    body_text = Column(Text)
    body_html = Column(Text)
    
    # Timestamps
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    is_flagged = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    is_answered = Column(Boolean, default=False, nullable=False)
    is_draft = Column(Boolean, default=False, nullable=False)
    
    # Anexos
    has_attachments = Column(Boolean, default=False, nullable=False, index=True)
    attachments_json = Column(Text)  # JSON com metadados
    attachment_count = Column(Integer, default=0)
    
    # Metadados
    raw_headers = Column(Text)  # Cabeçalhos originais
    size_bytes = Column(Integer, default=0)
    
    # Threading
    thread_id = Column(String(200), index=True)  # Para agrupar conversas
    in_reply_to = Column(String(500))  # Message-ID respondido
    references = Column(Text)  # Referências da thread
    
    # Organização
    folder = Column(String(100), default='INBOX', index=True)
    labels = Column(Text)  # Labels/tags separados por vírgula
    priority = Column(Integer, default=3)  # 1=Highest, 5=Lowest
    
    # Índices compostos para performance
    __table_args__ = (
        Index('idx_account_received', 'account_id', 'received_at'),
        Index('idx_account_folder', 'account_id', 'folder'),
        Index('idx_account_read', 'account_id', 'is_read'),
        Index('idx_account_thread', 'account_id', 'thread_id'),
        Index('idx_message_unique', 'account_id', 'message_id', unique=True),
    )
    
    def __repr__(self) -> str:
        return f'<EmailInbox {self.id}: {self.subject[:30]}...>'
    
    def __init__(self, **kwargs):
        """Inicializa email inbox."""
        # Parse anexos se fornecido como lista
        if 'attachments' in kwargs and isinstance(kwargs['attachments'], list):
            kwargs['attachments_json'] = json.dumps(kwargs.pop('attachments'))
            kwargs['attachment_count'] = len(json.loads(kwargs['attachments_json']))
            kwargs['has_attachments'] = kwargs['attachment_count'] > 0
        
        super().__init__(**kwargs)
    
    @hybrid_property
    def attachments(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de anexos parseada.
        
        Returns:
            Lista de dicionários com metadados dos anexos
        """
        if self.attachments_json:
            try:
                return json.loads(self.attachments_json)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @attachments.setter
    def attachments(self, value: List[Dict[str, Any]]):
        """
        Define anexos.
        
        Args:
            value: Lista de anexos
        """
        if value:
            self.attachments_json = json.dumps(value)
            self.attachment_count = len(value)
            self.has_attachments = True
        else:
            self.attachments_json = None
            self.attachment_count = 0
            self.has_attachments = False
    
    @hybrid_property
    def label_list(self) -> List[str]:
        """
        Retorna labels como lista.
        
        Returns:
            Lista de labels
        """
        if self.labels:
            return [label.strip() for label in self.labels.split(',')]
        return []
    
    @label_list.setter
    def label_list(self, value: List[str]):
        """
        Define labels a partir de lista.
        
        Args:
            value: Lista de labels
        """
        if value:
            self.labels = ', '.join(value)
        else:
            self.labels = None
    
    @classmethod
    def get_by_message_id(cls, account_id: int, message_id: str) -> Optional['EmailInbox']:
        """
        Busca email por message_id.
        
        Args:
            account_id: ID da conta
            message_id: Message-ID do email
            
        Returns:
            Email ou None
        """
        return cls.query.filter_by(
            account_id=account_id, 
            message_id=message_id
        ).first()
    
    @classmethod
    def get_unread_count(cls, account_id: int, folder: str = 'INBOX') -> int:
        """
        Conta emails não lidos.
        
        Args:
            account_id: ID da conta
            folder: Pasta IMAP
            
        Returns:
            Número de emails não lidos
        """
        return cls.query.filter_by(
            account_id=account_id,
            folder=folder,
            is_read=False,
            is_deleted=False
        ).count()
    
    @classmethod
    def get_inbox_emails(
        cls, 
        account_id: int, 
        page: int = 1, 
        per_page: int = 50, 
        folder: str = 'INBOX',
        unread_only: bool = False,
        has_attachments_only: bool = False,
        search_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retorna emails paginados do inbox.
        
        Args:
            account_id: ID da conta
            page: Página atual
            per_page: Itens por página
            folder: Pasta IMAP
            unread_only: Filtrar apenas não lidos
            has_attachments_only: Filtrar apenas com anexos
            search_query: Query de busca
            
        Returns:
            Dicionário com emails e informações de paginação
        """
        query = cls.query.filter_by(
            account_id=account_id,
            folder=folder,
            is_deleted=False
        )
        
        # Aplicar filtros
        if unread_only:
            query = query.filter_by(is_read=False)
        
        if has_attachments_only:
            query = query.filter_by(has_attachments=True)
        
        if search_query:
            search_pattern = f'%{search_query}%'
            query = query.filter(
                (cls.subject.ilike(search_pattern)) |
                (cls.from_address.ilike(search_pattern)) |
                (cls.from_name.ilike(search_pattern)) |
                (cls.body_text.ilike(search_pattern))
            )
        
        # Ordenar por data de recebimento (mais recente primeiro)
        query = query.order_by(cls.received_at.desc())
        
        # Paginar
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            'emails': [email.to_dict() for email in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_num': pagination.prev_num,
            'next_num': pagination.next_num
        }
    
    @classmethod
    def get_threads(
        cls, 
        account_id: int, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retorna threads/conversas agrupadas.
        
        Args:
            account_id: ID da conta
            limit: Limite de threads
            
        Returns:
            Lista de threads com emails agrupados
        """
        from sqlalchemy import desc
        
        # Buscar threads únicas
        thread_ids = cls.query.with_entities(
            cls.thread_id,
            func.max(cls.received_at).label('last_received')
        ).filter(
            cls.account_id == account_id,
            cls.is_deleted == False,
            cls.thread_id != None
        ).group_by(
            cls.thread_id
        ).order_by(
            desc('last_received')
        ).limit(limit).all()
        
        threads = []
        for thread_id, last_received in thread_ids:
            # Buscar emails da thread
            thread_emails = cls.query.filter_by(
                account_id=account_id,
                thread_id=thread_id,
                is_deleted=False
            ).order_by(cls.received_at.asc()).all()
            
            if thread_emails:
                threads.append({
                    'thread_id': thread_id,
                    'subject': thread_emails[0].subject,
                    'email_count': len(thread_emails),
                    'unread_count': sum(1 for e in thread_emails if not e.is_read),
                    'has_attachments': any(e.has_attachments for e in thread_emails),
                    'participants': list(set([e.from_address for e in thread_emails])),
                    'last_received': last_received.isoformat() if last_received else None,
                    'emails': [e.to_dict(compact=True) for e in thread_emails]
                })
        
        return threads
    
    def mark_as_read(self, commit: bool = True) -> 'EmailInbox':
        """
        Marca email como lido.
        
        Args:
            commit: Se deve fazer commit
            
        Returns:
            Self para method chaining
        """
        self.is_read = True
        return self.save(commit=commit)
    
    def mark_as_unread(self, commit: bool = True) -> 'EmailInbox':
        """
        Marca email como não lido.
        
        Args:
            commit: Se deve fazer commit
            
        Returns:
            Self para method chaining
        """
        self.is_read = False
        return self.save(commit=commit)
    
    def toggle_flag(self, commit: bool = True) -> 'EmailInbox':
        """
        Alterna flag/favorito do email.
        
        Args:
            commit: Se deve fazer commit
            
        Returns:
            Self para method chaining
        """
        self.is_flagged = not self.is_flagged
        return self.save(commit=commit)
    
    def soft_delete(self, commit: bool = True) -> 'EmailInbox':
        """
        Marca email como deletado (soft delete).
        
        Args:
            commit: Se deve fazer commit
            
        Returns:
            Self para method chaining
        """
        self.is_deleted = True
        return self.save(commit=commit)
    
    def move_to_folder(self, folder: str, commit: bool = True) -> 'EmailInbox':
        """
        Move email para outra pasta.
        
        Args:
            folder: Nome da pasta
            commit: Se deve fazer commit
            
        Returns:
            Self para method chaining
        """
        self.folder = folder
        return self.save(commit=commit)
    
    def add_label(self, label: str, commit: bool = True) -> 'EmailInbox':
        """
        Adiciona label ao email.
        
        Args:
            label: Label a adicionar
            commit: Se deve fazer commit
            
        Returns:
            Self para method chaining
        """
        labels = self.label_list
        if label not in labels:
            labels.append(label)
            self.label_list = labels
            self.save(commit=commit)
        return self
    
    def remove_label(self, label: str, commit: bool = True) -> 'EmailInbox':
        """
        Remove label do email.
        
        Args:
            label: Label a remover
            commit: Se deve fazer commit
            
        Returns:
            Self para method chaining
        """
        labels = self.label_list
        if label in labels:
            labels.remove(label)
            self.label_list = labels
            self.save(commit=commit)
        return self
    
    def to_dict(self, compact: bool = False, include_body: bool = True) -> Dict[str, Any]:
        """
        Converte modelo para dicionário.
        
        Args:
            compact: Se deve retornar versão compacta
            include_body: Se deve incluir corpo do email
            
        Returns:
            Dicionário com os dados
        """
        # Campos básicos sempre incluídos
        data = {
            'id': self.id,
            'account_id': self.account_id,
            'message_id': self.message_id,
            'from_address': self.from_address,
            'from_name': self.from_name,
            'subject': self.subject,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'date': self.received_at.isoformat() if self.received_at else None,  # Explicit date field for frontend
            'is_read': self.is_read,
            'is_flagged': self.is_flagged,
            'has_attachments': self.has_attachments,
            'attachment_count': self.attachment_count,
            'folder': self.folder
        }
        
        # Versão completa
        if not compact:
            data.update({
                'uid': self.uid,
                'to_address': self.to_address,
                'cc_addresses': self.cc_addresses,
                'bcc_addresses': self.bcc_addresses,
                'reply_to': self.reply_to,
                'is_deleted': self.is_deleted,
                'is_answered': self.is_answered,
                'is_draft': self.is_draft,
                'attachments': self.attachments,
                'size_bytes': self.size_bytes,
                'thread_id': self.thread_id,
                'in_reply_to': self.in_reply_to,
                'references': self.references,
                'labels': self.label_list,
                'priority': self.priority,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            })
            
            # Incluir corpo se solicitado
            if include_body:
                data['body_text'] = self.body_text
                data['body_html'] = self.body_html
        
        return data
    
    def to_json(self, compact: bool = False) -> str:
        """
        Converte modelo para JSON.
        
        Args:
            compact: Se deve retornar versão compacta
            
        Returns:
            String JSON
        """
        return json.dumps(self.to_dict(compact=compact))