"""Serviço SMTP para SendCraft."""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formataddr, make_msgid
from email import encoders
from typing import Dict, Any, Optional, List, Tuple
import logging

from ..models.account import EmailAccount
from ..utils.crypto import AESCipher
from ..utils.logging import get_logger

logger = get_logger(__name__)


class SMTPService:
    """Serviço para envio de emails via SMTP."""
    
    def __init__(self, encryption_key: str):
        """
        Inicializa serviço SMTP.
        
        Args:
            encryption_key: Chave para decriptar passwords
        """
        self.encryption_key = encryption_key
        self.cipher = AESCipher(encryption_key)
    
    def test_connection(self, account: EmailAccount) -> Tuple[bool, str]:
        """
        Testa conexão SMTP com uma conta.
        
        Args:
            account: Conta de email para testar
            
        Returns:
            Tuple (success, message)
        """
        try:
            config = account.get_smtp_config(self.encryption_key)
            
            with self._create_smtp_connection(config) as server:
                # Se chegou aqui, a conexão foi bem-sucedida
                logger.info(f"SMTP connection test successful for {account.email_address}")
                return True, "Conexão SMTP estabelecida com sucesso"
                
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Erro de autenticação SMTP: {str(e)}"
            logger.error(f"SMTP authentication failed for {account.email_address}: {e}")
            return False, error_msg
            
        except smtplib.SMTPConnectError as e:
            error_msg = f"Erro de conexão SMTP: {str(e)}"
            logger.error(f"SMTP connection failed for {account.email_address}: {e}")
            return False, error_msg
            
        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"Servidor SMTP desconectado: {str(e)}"
            logger.error(f"SMTP server disconnected for {account.email_address}: {e}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Erro na conexão SMTP: {str(e)}"
            logger.error(f"SMTP test failed for {account.email_address}: {e}")
            return False, error_msg
    
    def send_email(
        self,
        account: EmailAccount,
        to_email: str,
        subject: str,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Envia email usando conta especificada.
        
        Args:
            account: Conta de email para envio
            to_email: Email do destinatário
            subject: Assunto do email
            html_content: Conteúdo HTML
            text_content: Conteúdo texto plano
            from_name: Nome do remetente (opcional)
            reply_to: Email de resposta (opcional)
            cc: Lista de emails CC (opcional)
            bcc: Lista de emails BCC (opcional)
            attachments: Lista de anexos (opcional)
            
        Returns:
            Tuple (success, message, message_id)
        """
        try:
            config = account.get_smtp_config(self.encryption_key)
            
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self._format_from_address(config, from_name)
            msg['To'] = to_email
            msg['Message-ID'] = make_msgid()
            
            # Headers opcionais
            if reply_to:
                msg['Reply-To'] = reply_to
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Adicionar conteúdo
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            if html_content:
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Se não há conteúdo, criar texto padrão
            if not text_content and not html_content:
                default_text = MIMEText('(Mensagem sem conteúdo)', 'plain', 'utf-8')
                msg.attach(default_text)
            
            # Adicionar anexos se houver
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Preparar lista de destinatários
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            # Enviar
            with self._create_smtp_connection(config) as server:
                server.send_message(msg, from_addr=config['from_email'], to_addrs=recipients)
                message_id = msg.get('Message-ID', '')
                
                success_msg = f"Email enviado com sucesso para {to_email}"
                logger.info(f"Email sent successfully from {account.email_address} to {to_email}")
                return True, success_msg, message_id
                
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Destinatário recusado: {str(e)}"
            logger.error(f"Recipients refused: {e}")
            return False, error_msg, None
            
        except smtplib.SMTPSenderRefused as e:
            error_msg = f"Remetente recusado: {str(e)}"
            logger.error(f"Sender refused: {e}")
            return False, error_msg, None
            
        except smtplib.SMTPDataError as e:
            error_msg = f"Erro de dados SMTP: {str(e)}"
            logger.error(f"SMTP data error: {e}")
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"Erro ao enviar email: {str(e)}"
            logger.error(f"Failed to send email: {e}")
            return False, error_msg, None
    
    def send_bulk_emails(
        self,
        account: EmailAccount,
        recipients: List[Dict[str, Any]],
        subject: str,
        html_template: Optional[str] = None,
        text_template: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Envia emails em massa.
        
        Args:
            account: Conta de email para envio
            recipients: Lista de destinatários com variáveis
            subject: Assunto do email
            html_template: Template HTML
            text_template: Template texto
            from_name: Nome do remetente
            
        Returns:
            Lista de resultados por destinatário
        """
        results = []
        
        for recipient in recipients:
            email = recipient.get('email')
            variables = recipient.get('variables', {})
            
            # Renderizar conteúdo para este destinatário
            try:
                from jinja2 import Template
                
                html_content = None
                if html_template:
                    html_tmpl = Template(html_template)
                    html_content = html_tmpl.render(**variables)
                
                text_content = None
                if text_template:
                    text_tmpl = Template(text_template)
                    text_content = text_tmpl.render(**variables)
                
                # Enviar email
                success, message, message_id = self.send_email(
                    account=account,
                    to_email=email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    from_name=from_name
                )
                
                results.append({
                    'email': email,
                    'success': success,
                    'message': message,
                    'message_id': message_id
                })
                
            except Exception as e:
                results.append({
                    'email': email,
                    'success': False,
                    'message': str(e),
                    'message_id': None
                })
        
        return results
    
    def _create_smtp_connection(self, config: Dict[str, Any]):
        """
        Cria conexão SMTP configurada.
        
        Args:
            config: Configuração SMTP da conta
            
        Returns:
            Objeto SMTP conectado e autenticado
        """
        server = config['server']
        port = config['port']
        username = config['username']
        password = config['password']
        use_tls = config['use_tls']
        use_ssl = config['use_ssl']
        
        logger.debug(f"Creating SMTP connection to {server}:{port}")
        
        # Criar conexão
        if use_ssl:
            context = ssl.create_default_context()
            smtp = smtplib.SMTP_SSL(server, port, context=context, timeout=30)
        else:
            smtp = smtplib.SMTP(server, port, timeout=30)
        
        # Configurar debug se em desenvolvimento
        smtp.set_debuglevel(0)  # Set to 1 for debug output
        
        # Ativar TLS se necessário
        if use_tls and not use_ssl:
            context = ssl.create_default_context()
            smtp.starttls(context=context)
        
        # Autenticar
        if username and password:
            smtp.login(username, password)
            logger.debug(f"SMTP authentication successful for {username}")
        
        return smtp
    
    def _format_from_address(self, config: Dict[str, Any], from_name: Optional[str] = None) -> str:
        """
        Formata endereço de remetente.
        
        Args:
            config: Configuração da conta
            from_name: Nome do remetente
            
        Returns:
            Endereço formatado
        """
        email = config['from_email']
        name = from_name or config.get('from_name', '')
        
        if name:
            return formataddr((name, email))
        return email
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]) -> None:
        """
        Adiciona anexo à mensagem.
        
        Args:
            msg: Mensagem MIME
            attachment: Dicionário com dados do anexo
        """
        filename = attachment.get('filename', 'attachment')
        content = attachment.get('content')
        content_type = attachment.get('content_type', 'application/octet-stream')
        
        if not content:
            return
        
        # Criar parte do anexo
        part = MIMEBase('application', 'octet-stream')
        
        # Se content é string, converter para bytes
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        part.set_payload(content)
        encoders.encode_base64(part)
        
        # Adicionar headers
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{filename}"'
        )
        
        msg.attach(part)