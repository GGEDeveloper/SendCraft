"""Serviço de Templates para SendCraft."""
from typing import Dict, Any, Optional, List, Tuple
from jinja2 import Template, Environment, meta, TemplateError

from ..models import Domain, EmailTemplate
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)


class TemplateService:
    """Serviço para gestão e renderização de templates."""
    
    def __init__(self):
        """Inicializa serviço de templates."""
        self.env = Environment(autoescape=True)
    
    def create_template(
        self,
        domain_name: str,
        template_key: str,
        template_name: str,
        subject_template: str,
        html_template: Optional[str] = None,
        text_template: Optional[str] = None,
        description: Optional[str] = None,
        category: str = 'general',
        variables_required: Optional[List[str]] = None,
        variables_optional: Optional[List[str]] = None
    ) -> Tuple[bool, str, Optional[EmailTemplate]]:
        """
        Cria novo template.
        
        Args:
            domain_name: Nome do domínio
            template_key: Chave única do template
            template_name: Nome amigável
            subject_template: Template do assunto
            html_template: Template HTML
            text_template: Template texto
            description: Descrição
            category: Categoria
            variables_required: Variáveis obrigatórias
            variables_optional: Variáveis opcionais
            
        Returns:
            Tuple (success, message, template)
        """
        try:
            # Buscar domínio
            domain = Domain.get_by_name(domain_name)
            if not domain:
                return False, f"Domain {domain_name} not found", None
            
            # Verificar se template já existe
            existing = EmailTemplate.get_by_key(domain.id, template_key)
            if existing:
                return False, f"Template {template_key} already exists", None
            
            # Validar templates
            validation_errors = self.validate_template_syntax(
                subject_template, html_template, text_template
            )
            if validation_errors:
                return False, f"Template validation errors: {', '.join(validation_errors)}", None
            
            # Extrair variáveis dos templates
            extracted_vars = self.extract_variables(
                subject_template, html_template, text_template
            )
            all_vars = set()
            for vars_list in extracted_vars.values():
                all_vars.update(vars_list)
            
            # Se não foram especificadas variáveis, usar as extraídas
            if variables_required is None and variables_optional is None:
                variables_optional = list(all_vars)
            
            # Criar template
            template = EmailTemplate.create(
                domain_id=domain.id,
                template_key=template_key,
                template_name=template_name,
                subject_template=subject_template,
                html_template=html_template,
                text_template=text_template,
                description=description,
                category=category,
                variables_required=variables_required or [],
                variables_optional=variables_optional or [],
                is_active=True
            )
            
            logger.info(f"Template {template_key} created for domain {domain_name}")
            return True, "Template created successfully", template
            
        except Exception as e:
            error_msg = f"Error creating template: {str(e)}"
            logger.error(error_msg)
            db.session.rollback()
            return False, error_msg, None
    
    def update_template(
        self,
        domain_name: str,
        template_key: str,
        **updates
    ) -> Tuple[bool, str, Optional[EmailTemplate]]:
        """
        Atualiza template existente.
        
        Args:
            domain_name: Nome do domínio
            template_key: Chave do template
            **updates: Campos para atualizar
            
        Returns:
            Tuple (success, message, template)
        """
        try:
            # Buscar domínio e template
            domain = Domain.get_by_name(domain_name)
            if not domain:
                return False, f"Domain {domain_name} not found", None
            
            template = EmailTemplate.get_by_key(domain.id, template_key)
            if not template:
                return False, f"Template {template_key} not found", None
            
            # Validar novos templates se fornecidos
            if any(k in updates for k in ['subject_template', 'html_template', 'text_template']):
                subject = updates.get('subject_template', template.subject_template)
                html = updates.get('html_template', template.html_template)
                text = updates.get('text_template', template.text_template)
                
                validation_errors = self.validate_template_syntax(subject, html, text)
                if validation_errors:
                    return False, f"Template validation errors: {', '.join(validation_errors)}", None
            
            # Atualizar template
            template.update_from_dict(updates)
            
            # Incrementar versão se houve mudança no conteúdo
            if any(k in updates for k in ['subject_template', 'html_template', 'text_template']):
                template.version += 1
            
            template.save()
            
            logger.info(f"Template {template_key} updated for domain {domain_name}")
            return True, "Template updated successfully", template
            
        except Exception as e:
            error_msg = f"Error updating template: {str(e)}"
            logger.error(error_msg)
            db.session.rollback()
            return False, error_msg, None
    
    def delete_template(
        self,
        domain_name: str,
        template_key: str,
        soft_delete: bool = True
    ) -> Tuple[bool, str]:
        """
        Deleta template.
        
        Args:
            domain_name: Nome do domínio
            template_key: Chave do template
            soft_delete: Se deve apenas desativar
            
        Returns:
            Tuple (success, message)
        """
        try:
            # Buscar domínio e template
            domain = Domain.get_by_name(domain_name)
            if not domain:
                return False, f"Domain {domain_name} not found"
            
            template = EmailTemplate.get_by_key(domain.id, template_key)
            if not template:
                return False, f"Template {template_key} not found"
            
            if soft_delete:
                # Apenas desativar
                template.is_active = False
                template.save()
                message = "Template deactivated successfully"
            else:
                # Deletar permanentemente
                template.delete()
                message = "Template deleted successfully"
            
            logger.info(f"Template {template_key} {'deactivated' if soft_delete else 'deleted'}")
            return True, message
            
        except Exception as e:
            error_msg = f"Error deleting template: {str(e)}"
            logger.error(error_msg)
            db.session.rollback()
            return False, error_msg
    
    def render_template(
        self,
        domain_name: str,
        template_key: str,
        variables: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[Dict[str, str]]]:
        """
        Renderiza template com variáveis.
        
        Args:
            domain_name: Nome do domínio
            template_key: Chave do template
            variables: Variáveis para renderização
            
        Returns:
            Tuple (success, message, rendered_content)
        """
        try:
            # Buscar domínio e template
            domain = Domain.get_by_name(domain_name)
            if not domain:
                return False, f"Domain {domain_name} not found", None
            
            template = EmailTemplate.get_by_key(domain.id, template_key)
            if not template:
                return False, f"Template {template_key} not found", None
            
            if not template.is_active:
                return False, f"Template {template_key} is not active", None
            
            # Validar variáveis
            is_valid, missing = template.validate_variables(variables)
            if not is_valid:
                return False, f"Missing required variables: {', '.join(missing)}", None
            
            # Renderizar
            rendered = template.render_all(variables)
            
            return True, "Template rendered successfully", rendered
            
        except TemplateError as e:
            error_msg = f"Template rendering error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"Error rendering template: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def validate_template_syntax(
        self,
        subject_template: Optional[str],
        html_template: Optional[str],
        text_template: Optional[str]
    ) -> List[str]:
        """
        Valida sintaxe dos templates.
        
        Args:
            subject_template: Template do assunto
            html_template: Template HTML
            text_template: Template texto
            
        Returns:
            Lista de erros encontrados
        """
        errors = []
        
        if subject_template:
            try:
                Template(subject_template)
            except TemplateError as e:
                errors.append(f"Subject template error: {str(e)}")
        
        if html_template:
            try:
                Template(html_template)
            except TemplateError as e:
                errors.append(f"HTML template error: {str(e)}")
        
        if text_template:
            try:
                Template(text_template)
            except TemplateError as e:
                errors.append(f"Text template error: {str(e)}")
        
        return errors
    
    def extract_variables(
        self,
        subject_template: Optional[str],
        html_template: Optional[str],
        text_template: Optional[str]
    ) -> Dict[str, List[str]]:
        """
        Extrai variáveis dos templates.
        
        Args:
            subject_template: Template do assunto
            html_template: Template HTML
            text_template: Template texto
            
        Returns:
            Dicionário com variáveis por template
        """
        variables = {}
        
        if subject_template:
            try:
                ast = self.env.parse(subject_template)
                variables['subject'] = list(meta.find_undeclared_variables(ast))
            except Exception:
                variables['subject'] = []
        
        if html_template:
            try:
                ast = self.env.parse(html_template)
                variables['html'] = list(meta.find_undeclared_variables(ast))
            except Exception:
                variables['html'] = []
        
        if text_template:
            try:
                ast = self.env.parse(text_template)
                variables['text'] = list(meta.find_undeclared_variables(ast))
            except Exception:
                variables['text'] = []
        
        return variables
    
    def clone_template(
        self,
        domain_name: str,
        template_key: str,
        new_key: str,
        new_name: Optional[str] = None
    ) -> Tuple[bool, str, Optional[EmailTemplate]]:
        """
        Clona template existente.
        
        Args:
            domain_name: Nome do domínio
            template_key: Chave do template original
            new_key: Nova chave para o clone
            new_name: Novo nome (opcional)
            
        Returns:
            Tuple (success, message, cloned_template)
        """
        try:
            # Buscar template original
            domain = Domain.get_by_name(domain_name)
            if not domain:
                return False, f"Domain {domain_name} not found", None
            
            original = EmailTemplate.get_by_key(domain.id, template_key)
            if not original:
                return False, f"Template {template_key} not found", None
            
            # Verificar se nova chave já existe
            existing = EmailTemplate.get_by_key(domain.id, new_key)
            if existing:
                return False, f"Template {new_key} already exists", None
            
            # Clonar
            cloned = original.clone(new_key)
            if new_name:
                cloned.template_name = new_name
            cloned.save()
            
            logger.info(f"Template {template_key} cloned to {new_key}")
            return True, "Template cloned successfully", cloned
            
        except Exception as e:
            error_msg = f"Error cloning template: {str(e)}"
            logger.error(error_msg)
            db.session.rollback()
            return False, error_msg, None
    
    def list_templates(
        self,
        domain_name: Optional[str] = None,
        category: Optional[str] = None,
        active_only: bool = True
    ) -> List[EmailTemplate]:
        """
        Lista templates.
        
        Args:
            domain_name: Nome do domínio (opcional)
            category: Categoria (opcional)
            active_only: Se deve listar apenas ativos
            
        Returns:
            Lista de templates
        """
        query = EmailTemplate.query
        
        if domain_name:
            domain = Domain.get_by_name(domain_name)
            if domain:
                query = query.filter_by(domain_id=domain.id)
            else:
                return []
        
        if category:
            query = query.filter_by(category=category)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        return query.all()