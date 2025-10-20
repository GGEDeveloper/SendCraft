"""Modelo de Domínio para SendCraft."""
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from typing import List, Optional

from .base import BaseModel, TimestampMixin


class Domain(BaseModel, TimestampMixin):
    """
    Representa um domínio de email (ex: alitools.pt).
    
    Attributes:
        name: Nome do domínio
        is_active: Se o domínio está ativo
        description: Descrição opcional
        spf_record: Registro SPF configurado
        dkim_selector: Seletor DKIM
        accounts: Contas de email associadas
        templates: Templates de email associados
    """
    
    __tablename__ = 'domains'
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text)
    spf_record = Column(Text)
    dkim_selector = Column(String(50))
    
    # Relationships
    accounts = relationship('EmailAccount', back_populates='domain', lazy='dynamic', cascade='all, delete-orphan')
    templates = relationship('EmailTemplate', back_populates='domain', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f'<Domain {self.name}>'
    
    @classmethod
    def get_by_name(cls, name: str) -> Optional['Domain']:
        """
        Busca domínio por nome.
        
        Args:
            name: Nome do domínio
            
        Returns:
            Instância do domínio ou None
        """
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def get_active_domains(cls) -> List['Domain']:
        """
        Retorna todos os domínios ativos.
        
        Returns:
            Lista de domínios ativos
        """
        return cls.query.filter_by(is_active=True).all()
    
    def get_active_accounts(self):
        """
        Retorna contas ativas deste domínio.
        
        Returns:
            Query de contas ativas
        """
        return self.accounts.filter_by(is_active=True)
    
    def get_active_templates(self):
        """
        Retorna templates ativos deste domínio.
        
        Returns:
            Query de templates ativos
        """
        return self.templates.filter_by(is_active=True)
    
    def get_account_by_local_part(self, local_part: str) -> Optional['EmailAccount']:
        """
        Busca conta por parte local do email.
        
        Args:
            local_part: Parte local (antes do @)
            
        Returns:
            Conta de email ou None
        """
        return self.accounts.filter_by(local_part=local_part).first()
    
    def get_template_by_key(self, template_key: str) -> Optional['EmailTemplate']:
        """
        Busca template por chave.
        
        Args:
            template_key: Chave única do template
            
        Returns:
            Template ou None
        """
        return self.templates.filter_by(template_key=template_key, is_active=True).first()
    
    def count_accounts(self) -> int:
        """
        Conta número de contas do domínio.
        
        Returns:
            Número de contas
        """
        return self.accounts.count()
    
    def count_active_accounts(self) -> int:
        """
        Conta número de contas ativas do domínio.
        
        Returns:
            Número de contas ativas
        """
        return self.accounts.filter_by(is_active=True).count()
    
    def count_templates(self) -> int:
        """
        Conta número de templates do domínio.
        
        Returns:
            Número de templates
        """
        return self.templates.count()
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """
        Converte modelo para dicionário.
        
        Args:
            include_relationships: Se deve incluir relacionamentos
            
        Returns:
            Dicionário com os dados
        """
        data = super().to_dict()
        
        if include_relationships:
            data['accounts_count'] = self.count_accounts()
            data['active_accounts_count'] = self.count_active_accounts()
            data['templates_count'] = self.count_templates()
        
        return data