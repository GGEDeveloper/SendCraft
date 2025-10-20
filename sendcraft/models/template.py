"""Modelo de Template de Email para SendCraft."""
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from typing import Optional, List, Dict, Any
import json
from jinja2 import Template, TemplateError, meta, Environment

from .base import BaseModel, TimestampMixin
from ..utils.logging import get_logger

logger = get_logger(__name__)


class EmailTemplate(BaseModel, TimestampMixin):
    """
    Representa um template de email.
    
    Attributes:
        domain_id: ID do domínio associado
        template_key: Chave única do template
        template_name: Nome amigável
        description: Descrição do template
        subject_template: Template do assunto
        html_template: Template HTML
        text_template: Template texto plano
        variables_required: Variáveis obrigatórias (JSON)
        variables_optional: Variáveis opcionais (JSON)
        is_active: Se o template está ativo
        version: Versão do template
        category: Categoria do template
    """
    
    __tablename__ = 'email_templates'
    
    # Domain relationship
    domain_id = Column(Integer, ForeignKey('domains.id'), nullable=False)
    domain = relationship('Domain', back_populates='templates')
    
    # Template identification
    template_key = Column(String(100), nullable=False, index=True)
    template_name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), default='general')
    version = Column(Integer, default=1, nullable=False)
    
    # Template content
    subject_template = Column(Text, nullable=False)
    html_template = Column(Text)
    text_template = Column(Text)
    
    # Template variables
    variables_required = Column(JSON, default=list)
    variables_optional = Column(JSON, default=list)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    logs = relationship('EmailLog', back_populates='template', lazy='dynamic')
    
    def __repr__(self) -> str:
        return f'<EmailTemplate {self.template_key}@{self.domain.name if self.domain else "unknown"}>'
    
    @classmethod
    def get_by_key(cls, domain_id: int, template_key: str) -> Optional['EmailTemplate']:
        """
        Busca template por chave e domínio.
        
        Args:
            domain_id: ID do domínio
            template_key: Chave única do template
            
        Returns:
            Template ou None
        """
        return cls.query.filter_by(
            domain_id=domain_id,
            template_key=template_key,
            is_active=True
        ).first()
    
    @classmethod
    def get_active_templates(cls, domain_id: Optional[int] = None) -> List['EmailTemplate']:
        """
        Retorna templates ativos, opcionalmente filtrados por domínio.
        
        Args:
            domain_id: ID do domínio (opcional)
            
        Returns:
            Lista de templates ativos
        """
        query = cls.query.filter_by(is_active=True)
        if domain_id:
            query = query.filter_by(domain_id=domain_id)
        return query.all()
    
    @classmethod
    def get_by_category(cls, category: str, domain_id: Optional[int] = None) -> List['EmailTemplate']:
        """
        Retorna templates por categoria.
        
        Args:
            category: Categoria dos templates
            domain_id: ID do domínio (opcional)
            
        Returns:
            Lista de templates
        """
        query = cls.query.filter_by(category=category, is_active=True)
        if domain_id:
            query = query.filter_by(domain_id=domain_id)
        return query.all()
    
    def validate_variables(self, variables: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Valida se as variáveis fornecidas atendem aos requisitos.
        
        Args:
            variables: Dicionário de variáveis
            
        Returns:
            Tuple (is_valid, missing_variables)
        """
        required = self.variables_required or []
        missing = [var for var in required if var not in variables]
        return len(missing) == 0, missing
    
    def extract_variables(self) -> Dict[str, List[str]]:
        """
        Extrai variáveis usadas nos templates.
        
        Returns:
            Dicionário com variáveis encontradas em cada template
        """
        env = Environment()
        variables = {}
        
        # Extrair do subject
        if self.subject_template:
            try:
                ast = env.parse(self.subject_template)
                variables['subject'] = list(meta.find_undeclared_variables(ast))
            except Exception as e:
                logger.warning(f"Failed to parse subject template: {e}")
                variables['subject'] = []
        
        # Extrair do HTML
        if self.html_template:
            try:
                ast = env.parse(self.html_template)
                variables['html'] = list(meta.find_undeclared_variables(ast))
            except Exception as e:
                logger.warning(f"Failed to parse HTML template: {e}")
                variables['html'] = []
        
        # Extrair do texto
        if self.text_template:
            try:
                ast = env.parse(self.text_template)
                variables['text'] = list(meta.find_undeclared_variables(ast))
            except Exception as e:
                logger.warning(f"Failed to parse text template: {e}")
                variables['text'] = []
        
        return variables
    
    def render_subject(self, variables: Dict[str, Any]) -> str:
        """
        Renderiza o assunto do email.
        
        Args:
            variables: Dicionário de variáveis
            
        Returns:
            Assunto renderizado
            
        Raises:
            ValueError: Se houver erro na renderização
        """
        try:
            template = Template(self.subject_template)
            return template.render(**variables)
        except TemplateError as e:
            error_msg = f"Erro ao renderizar assunto: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def render_html(self, variables: Dict[str, Any]) -> Optional[str]:
        """
        Renderiza o corpo HTML do email.
        
        Args:
            variables: Dicionário de variáveis
            
        Returns:
            HTML renderizado ou None
            
        Raises:
            ValueError: Se houver erro na renderização
        """
        if not self.html_template:
            return None
        
        try:
            template = Template(self.html_template)
            return template.render(**variables)
        except TemplateError as e:
            error_msg = f"Erro ao renderizar HTML: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def render_text(self, variables: Dict[str, Any]) -> Optional[str]:
        """
        Renderiza o corpo texto do email.
        
        Args:
            variables: Dicionário de variáveis
            
        Returns:
            Texto renderizado ou None
            
        Raises:
            ValueError: Se houver erro na renderização
        """
        if not self.text_template:
            return None
        
        try:
            template = Template(self.text_template)
            return template.render(**variables)
        except TemplateError as e:
            error_msg = f"Erro ao renderizar texto: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def render_all(self, variables: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """
        Renderiza todos os componentes do template.
        
        Args:
            variables: Dicionário de variáveis
            
        Returns:
            Dicionário com subject, html e text renderizados
        """
        return {
            'subject': self.render_subject(variables),
            'html': self.render_html(variables),
            'text': self.render_text(variables)
        }
    
    def get_all_variables(self) -> List[str]:
        """
        Retorna todas as variáveis (obrigatórias + opcionais).
        
        Returns:
            Lista de variáveis únicas
        """
        required = self.variables_required or []
        optional = self.variables_optional or []
        return list(set(required + optional))
    
    def clone(self, new_key: Optional[str] = None) -> 'EmailTemplate':
        """
        Cria uma cópia do template.
        
        Args:
            new_key: Nova chave para o template clonado
            
        Returns:
            Novo template clonado
        """
        data = self.to_dict()
        
        # Remover campos que não devem ser clonados
        data.pop('id', None)
        data.pop('created_at', None)
        data.pop('updated_at', None)
        
        # Definir nova chave e incrementar versão
        if new_key:
            data['template_key'] = new_key
        else:
            data['template_key'] = f"{self.template_key}_copy"
        
        data['version'] = self.version + 1
        data['is_active'] = False  # Clonar como inativo por segurança
        
        return EmailTemplate.create(**data)
    
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
            if self.domain:
                data['domain_name'] = self.domain.name
            
            # Incluir variáveis extraídas
            data['extracted_variables'] = self.extract_variables()
            
            # Contar uso do template
            data['usage_count'] = self.logs.count()
        
        return data