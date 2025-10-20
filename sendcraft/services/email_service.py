"""Serviço de Email para SendCraft."""
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from flask import current_app

from ..models import Domain, EmailAccount, EmailTemplate, EmailLog
from ..models.log import EmailStatus
from ..services.smtp_service import SMTPService
from ..services.template_service import TemplateService
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    """Serviço principal para envio de emails."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Inicializa serviço de email.
        
        Args:
            encryption_key: Chave de encriptação (usa config se não fornecida)
        """
        self.encryption_key = encryption_key or current_app.config.get('ENCRYPTION_KEY')
        self.smtp_service = SMTPService(self.encryption_key)
        self.template_service = TemplateService()
    
    def send_email(
        self,
        domain_name: str,
        account_local_part: str,
        to_email: str,
        subject: Optional[str] = None,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        template_key: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        from_name: Optional[str] = None,
        track_opens: bool = False,
        track_clicks: bool = False,
        request_info: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Envia email com todas as funcionalidades.
        
        Args:
            domain_name: Nome do domínio
            account_local_part: Parte local da conta (antes do @)
            to_email: Email do destinatário
            subject: Assunto (se não usar template)
            html_content: Conteúdo HTML (se não usar template)
            text_content: Conteúdo texto (se não usar template)
            template_key: Chave do template a usar
            variables: Variáveis para o template
            from_name: Nome do remetente
            track_opens: Se deve rastrear aberturas
            track_clicks: Se deve rastrear cliques
            request_info: Informações da requisição (ip, user_agent)
            
        Returns:
            Tuple (success, message, log_id)
        """
        try:
            # Buscar domínio
            domain = Domain.get_by_name(domain_name)
            if not domain:
                return False, f"Domain {domain_name} not found", None
            
            if not domain.is_active:
                return False, f"Domain {domain_name} is not active", None
            
            # Buscar conta
            account = domain.get_account_by_local_part(account_local_part)
            if not account:
                return False, f"Account {account_local_part}@{domain_name} not found", None
            
            if not account.is_active:
                return False, f"Account {account.email_address} is not active", None
            
            # Verificar limites
            within_limits, limit_msg = account.is_within_limits()
            if not within_limits:
                return False, limit_msg, None
            
            # Preparar conteúdo
            template_id = None
            if template_key:
                # Usar template
                template = domain.get_template_by_key(template_key)
                if not template:
                    return False, f"Template {template_key} not found", None
                
                if not template.is_active:
                    return False, f"Template {template_key} is not active", None
                
                # Validar variáveis
                variables = variables or {}
                is_valid, missing = template.validate_variables(variables)
                if not is_valid:
                    return False, f"Missing required variables: {', '.join(missing)}", None
                
                # Renderizar template
                rendered = template.render_all(variables)
                subject = rendered['subject']
                html_content = rendered['html']
                text_content = rendered['text']
                template_id = template.id
            
            # Verificar se há conteúdo
            if not subject:
                return False, "Subject is required", None
            
            if not html_content and not text_content:
                return False, "Email must have HTML or text content", None
            
            # Adicionar tracking se solicitado
            if html_content:
                if track_opens:
                    html_content = self._add_open_tracking(html_content, to_email)
                if track_clicks:
                    html_content = self._add_click_tracking(html_content, to_email)
            
            # Criar log
            log = EmailLog.create(
                account_id=account.id,
                template_id=template_id,
                recipient_email=to_email,
                sender_email=account.email_address,
                subject=subject,
                status=EmailStatus.PENDING,
                variables_used=variables,
                user_agent=request_info.get('user_agent') if request_info else None,
                ip_address=request_info.get('ip_address') if request_info else None
            )
            
            # Marcar como enviando
            log.mark_sending()
            
            # Enviar via SMTP
            success, message, message_id = self.smtp_service.send_email(
                account=account,
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                from_name=from_name
            )
            
            # Atualizar log
            if success:
                log.mark_sent(message_id, message)
            else:
                log.mark_failed(message)
            
            logger.info(f"Email {'sent' if success else 'failed'}: {account.email_address} -> {to_email}")
            return success, message, log.id
            
        except Exception as e:
            error_msg = f"Error sending email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def send_template_email(
        self,
        domain_name: str,
        account_local_part: str,
        to_email: str,
        template_key: str,
        variables: Optional[Dict[str, Any]] = None,
        from_name: Optional[str] = None,
        request_info: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Envia email usando template.
        
        Args:
            domain_name: Nome do domínio
            account_local_part: Parte local da conta
            to_email: Email do destinatário
            template_key: Chave do template
            variables: Variáveis para o template
            from_name: Nome do remetente
            request_info: Informações da requisição
            
        Returns:
            Tuple (success, message, log_id)
        """
        return self.send_email(
            domain_name=domain_name,
            account_local_part=account_local_part,
            to_email=to_email,
            template_key=template_key,
            variables=variables,
            from_name=from_name,
            request_info=request_info
        )
    
    def send_bulk_template_emails(
        self,
        domain_name: str,
        account_local_part: str,
        template_key: str,
        recipients: List[Dict[str, Any]],
        from_name: Optional[str] = None,
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """
        Envia emails em massa usando template.
        
        Args:
            domain_name: Nome do domínio
            account_local_part: Parte local da conta
            template_key: Chave do template
            recipients: Lista de destinatários com variáveis
            from_name: Nome do remetente
            batch_size: Tamanho do lote para processamento
            
        Returns:
            Dicionário com estatísticas do envio
        """
        results = {
            'total': len(recipients),
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        # Processar em lotes
        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            
            for recipient in batch:
                email = recipient.get('email')
                variables = recipient.get('variables', {})
                
                success, message, log_id = self.send_template_email(
                    domain_name=domain_name,
                    account_local_part=account_local_part,
                    to_email=email,
                    template_key=template_key,
                    variables=variables,
                    from_name=from_name
                )
                
                if success:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'email': email,
                        'error': message
                    })
            
            # Commit após cada lote
            db.session.commit()
        
        return results
    
    def test_smtp_connection(
        self,
        domain_name: str,
        account_local_part: str
    ) -> Tuple[bool, str]:
        """
        Testa conexão SMTP de uma conta.
        
        Args:
            domain_name: Nome do domínio
            account_local_part: Parte local da conta
            
        Returns:
            Tuple (success, message)
        """
        try:
            # Buscar domínio e conta
            domain = Domain.get_by_name(domain_name)
            if not domain:
                return False, f"Domain {domain_name} not found"
            
            account = domain.get_account_by_local_part(account_local_part)
            if not account:
                return False, f"Account {account_local_part}@{domain_name} not found"
            
            # Testar conexão
            return self.smtp_service.test_connection(account)
            
        except Exception as e:
            error_msg = f"Error testing connection: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_email_stats(
        self,
        domain_name: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Obtém estatísticas de envio.
        
        Args:
            domain_name: Nome do domínio (opcional)
            days: Número de dias para análise
            
        Returns:
            Dicionário com estatísticas
        """
        if domain_name:
            # Estatísticas por domínio
            domain = Domain.get_by_name(domain_name)
            if not domain:
                return {'error': f"Domain {domain_name} not found"}
            
            stats = {
                'domain': domain_name,
                'accounts': {}
            }
            
            for account in domain.get_active_accounts():
                stats['accounts'][account.email_address] = EmailLog.get_stats_by_account(
                    account.id, days
                )
            
            return stats
        else:
            # Estatísticas globais
            return EmailLog.get_global_stats(days)
    
    def _add_open_tracking(self, html_content: str, recipient_email: str) -> str:
        """
        Adiciona pixel de tracking para aberturas.
        
        Args:
            html_content: Conteúdo HTML
            recipient_email: Email do destinatário
            
        Returns:
            HTML com tracking
        """
        # TODO: Implementar tracking pixel
        # Por enquanto, retorna conteúdo original
        return html_content
    
    def _add_click_tracking(self, html_content: str, recipient_email: str) -> str:
        """
        Adiciona tracking para cliques em links.
        
        Args:
            html_content: Conteúdo HTML
            recipient_email: Email do destinatário
            
        Returns:
            HTML com tracking de cliques
        """
        # TODO: Implementar tracking de cliques
        # Por enquanto, retorna conteúdo original
        return html_content