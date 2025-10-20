# 🤖 **FASE 2 - AGENTE AI: Modelos Completos e Serviços**

**Continuação da FASE 1**  
**Repositório:** https://github.com/GGEDeveloper/SendCraft.git  
**Objetivo:** Completar modelos de dados e implementar serviços core  

---

## 🎯 **PRÉ-REQUISITOS**

- FASE 1 completada com sucesso
- Estrutura base criada e testada
- Repositório atualizado com tag `v0.1-structure`

---

## 📊 **MODELOS RESTANTES**

### **1. MODELS/ACCOUNT.PY**

```python
\"\"\"Modelo de Conta de Email para SendCraft.\"\"\"
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from typing import Optional, Dict, Any
from email_validator import validate_email, EmailNotValidError

from .base import BaseModel, TimestampMixin
from ..utils.crypto import AESCipher


class EmailAccount(BaseModel, TimestampMixin):
    \"\"\"
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
    \"\"\"
    
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
    
    # Relationships
    logs = relationship('EmailLog', back_populates='account', lazy='dynamic')
    
    def __repr__(self) -> str:
        return f'<EmailAccount {self.email_address}>'
    
    def __init__(self, **kwargs):
        # Auto-generate email_address from local_part and domain
        if 'local_part' in kwargs and 'domain_id' in kwargs and 'email_address' not in kwargs:
            from .domain import Domain
            domain = Domain.query.get(kwargs['domain_id'])
            if domain:
                kwargs['email_address'] = f\"{kwargs['local_part']}@{domain.name}\"
        
        super().__init__(**kwargs)
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['EmailAccount']:
        \"\"\"Busca conta por email.\"\"\"
        return cls.query.filter_by(email_address=email).first()
    
    @classmethod
    def get_active_accounts(cls):
        \"\"\"Retorna todas as contas ativas.\"\"\"
        return cls.query.filter_by(is_active=True).all()
    
    def set_password(self, password: str, encryption_key: str) -> None:
        \"\"\"Define password encriptada.\"\"\"
        cipher = AESCipher(encryption_key)
        self.smtp_password = cipher.encrypt(password)
    
    def get_password(self, encryption_key: str) -> str:
        \"\"\"Retorna password decriptada.\"\"\"
        if not self.smtp_password:
            return ''
        cipher = AESCipher(encryption_key)
        return cipher.decrypt(self.smtp_password)
    
    def validate_email(self) -> bool:
        \"\"\"Valida formato do email.\"\"\"
        try:
            validate_email(self.email_address)
            return True
        except EmailNotValidError:
            return False
    
    def get_smtp_config(self, encryption_key: str) -> Dict[str, Any]:
        \"\"\"Retorna configuração SMTP para uso.\"\"\"
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
```

### **2. MODELS/TEMPLATE.PY**

```python
\"\"\"Modelo de Template de Email para SendCraft.\"\"\"
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from typing import Optional, List, Dict, Any
import json
from jinja2 import Template, TemplateError

from .base import BaseModel, TimestampMixin


class EmailTemplate(BaseModel, TimestampMixin):
    \"\"\"
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
    \"\"\"
    
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
        return f'<EmailTemplate {self.template_key}@{self.domain.name if self.domain else \"unknown\"}>'
    
    @classmethod
    def get_by_key(cls, domain_id: int, template_key: str) -> Optional['EmailTemplate']:
        \"\"\"Busca template por chave e domínio.\"\"\"
        return cls.query.filter_by(
            domain_id=domain_id,
            template_key=template_key,
            is_active=True
        ).first()
    
    @classmethod
    def get_active_templates(cls, domain_id: Optional[int] = None):
        \"\"\"Retorna templates ativos, opcionalmente filtrados por domínio.\"\"\"
        query = cls.query.filter_by(is_active=True)
        if domain_id:
            query = query.filter_by(domain_id=domain_id)
        return query.all()
    
    def validate_variables(self, variables: Dict[str, Any]) -> tuple[bool, List[str]]:
        \"\"\"
        Valida se as variáveis fornecidas atendem aos requisitos.
        
        Returns:
            Tuple (is_valid, missing_variables)
        \"\"\"
        required = self.variables_required or []
        missing = [var for var in required if var not in variables]
        return len(missing) == 0, missing
    
    def render_subject(self, variables: Dict[str, Any]) -> str:
        \"\"\"Renderiza o assunto do email.\"\"\"
        try:
            template = Template(self.subject_template)
            return template.render(**variables)
        except TemplateError as e:
            raise ValueError(f\"Erro ao renderizar assunto: {e}\")
    
    def render_html(self, variables: Dict[str, Any]) -> Optional[str]:
        \"\"\"Renderiza o corpo HTML do email.\"\"\"
        if not self.html_template:
            return None
        try:
            template = Template(self.html_template)
            return template.render(**variables)
        except TemplateError as e:
            raise ValueError(f\"Erro ao renderizar HTML: {e}\")
    
    def render_text(self, variables: Dict[str, Any]) -> Optional[str]:
        \"\"\"Renderiza o corpo texto do email.\"\"\"
        if not self.text_template:
            return None
        try:
            template = Template(self.text_template)
            return template.render(**variables)
        except TemplateError as e:
            raise ValueError(f\"Erro ao renderizar texto: {e}\")
    
    def get_all_variables(self) -> List[str]:
        \"\"\"Retorna todas as variáveis (obrigatórias + opcionais).\"\"\"
        required = self.variables_required or []
        optional = self.variables_optional or []
        return list(set(required + optional))
```

### **3. MODELS/LOG.PY**

```python
\"\"\"Modelo de Log de Email para SendCraft.\"\"\"
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from .base import BaseModel


class EmailStatus(str, Enum):
    \"\"\"Status possíveis de um email.\"\"\"
    PENDING = 'pending'
    SENDING = 'sending'
    SENT = 'sent'
    FAILED = 'failed'
    BOUNCED = 'bounced'
    DELIVERED = 'delivered'
    OPENED = 'opened'
    CLICKED = 'clicked'


class EmailLog(BaseModel):
    \"\"\"
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
    \"\"\"
    
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
    status = Column(String(20), nullable=False, default=EmailStatus.PENDING, index=True)
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
        \"\"\"Retorna logs recentes.\"\"\"
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_logs_by_account(cls, account_id: int, limit: int = 100) -> List['EmailLog']:
        \"\"\"Retorna logs de uma conta específica.\"\"\"
        return cls.query.filter_by(account_id=account_id)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_logs_by_status(cls, status: EmailStatus, limit: int = 100) -> List['EmailLog']:
        \"\"\"Retorna logs por status.\"\"\"
        return cls.query.filter_by(status=status)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_stats_by_account(cls, account_id: int, days: int = 30) -> Dict[str, int]:
        \"\"\"Retorna estatísticas de uma conta.\"\"\"
        from sqlalchemy import func
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)
        
        stats = cls.query.filter(
            cls.account_id == account_id,
            cls.created_at >= cutoff_date
        ).with_entities(
            cls.status,
            func.count(cls.id).label('count')
        ).group_by(cls.status).all()
        
        return {stat.status: stat.count for stat in stats}
    
    def mark_sent(self, message_id: str, smtp_response: str = None) -> None:
        \"\"\"Marca email como enviado.\"\"\"
        self.status = EmailStatus.SENT
        self.message_id = message_id
        self.smtp_response = smtp_response
        self.sent_at = datetime.utcnow()
        self.save()
    
    def mark_failed(self, error_message: str) -> None:
        \"\"\"Marca email como falhou.\"\"\"
        self.status = EmailStatus.FAILED
        self.error_message = error_message
        self.save()
    
    def mark_delivered(self) -> None:
        \"\"\"Marca email como entregue.\"\"\"
        self.status = EmailStatus.DELIVERED
        self.delivered_at = datetime.utcnow()
        self.save()
```

---

## 🛠️ **SERVIÇOS CORE**

### **4. UTILS/CRYPTO.PY**

```python
\"\"\"Utilitários de criptografia para SendCraft.\"\"\"
from cryptography.fernet import Fernet
import base64
import hashlib
import secrets
from typing import str


class AESCipher:
    \"\"\"Cipher AES-256 para encriptação simétrica.\"\"\"
    
    def __init__(self, key: str):
        \"\"\"
        Inicializa cipher com chave.
        
        Args:
            key: Chave de encriptação (será derivada para 32 bytes)
        \"\"\"
        # Deriva chave de 32 bytes usando SHA-256
        key_bytes = key.encode('utf-8')
        digest = hashlib.sha256(key_bytes).digest()
        self.fernet = Fernet(base64.urlsafe_b64encode(digest))
    
    def encrypt(self, plaintext: str) -> str:
        \"\"\"
        Encripta texto plano.
        
        Args:
            plaintext: Texto a encriptar
            
        Returns:
            Texto encriptado em base64
        \"\"\"
        if not plaintext:
            return ''
        
        plaintext_bytes = plaintext.encode('utf-8')
        encrypted_bytes = self.fernet.encrypt(plaintext_bytes)
        return encrypted_bytes.decode('utf-8')
    
    def decrypt(self, ciphertext: str) -> str:
        \"\"\"
        Decripta texto encriptado.
        
        Args:
            ciphertext: Texto encriptado em base64
            
        Returns:
            Texto plano decriptado
            
        Raises:
            ValueError: Se não conseguir decriptar
        \"\"\"
        if not ciphertext:
            return ''
        
        try:
            ciphertext_bytes = ciphertext.encode('utf-8')
            decrypted_bytes = self.fernet.decrypt(ciphertext_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f\"Erro ao decriptar: {e}\")

    @classmethod
    def generate_key(cls) -> str:
        \"\"\"Gera chave aleatória segura.\"\"\"
        return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    \"\"\"
    Cria hash seguro de API key.
    
    Args:
        api_key: API key em texto plano
        
    Returns:
        Hash SHA-256 da chave
    \"\"\"
    return hashlib.sha256(api_key.encode('utf-8')).hexdigest()


def generate_api_key(prefix: str = 'SC') -> str:
    \"\"\"
    Gera API key segura.
    
    Args:
        prefix: Prefixo da chave
        
    Returns:
        API key formatada
    \"\"\"
    random_part = secrets.token_urlsafe(32)
    return f\"{prefix}_{random_part}\"
```

### **5. SERVICES/SMTP_SERVICE.PY**

```python
\"\"\"Serviço SMTP para SendCraft.\"\"\"
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional, List
import logging

from ..models.account import EmailAccount
from ..utils.crypto import AESCipher


logger = logging.getLogger(__name__)


class SMTPService:
    \"\"\"Serviço para envio de emails via SMTP.\"\"\"
    
    def __init__(self, encryption_key: str):
        \"\"\"
        Inicializa serviço SMTP.
        
        Args:
            encryption_key: Chave para decriptar passwords
        \"\"\"
        self.encryption_key = encryption_key
        self.cipher = AESCipher(encryption_key)
    
    def test_connection(self, account: EmailAccount) -> tuple[bool, str]:
        \"\"\"
        Testa conexão SMTP com uma conta.
        
        Args:
            account: Conta de email para testar
            
        Returns:
            Tuple (success, message)
        \"\"\"
        try:
            config = account.get_smtp_config(self.encryption_key)
            
            with self._create_smtp_connection(config) as server:
                # Se chegou aqui, a conexão foi bem-sucedida
                return True, \"Conexão SMTP estabelecida com sucesso\"
                
        except Exception as e:
            error_msg = f\"Erro na conexão SMTP: {str(e)}\"
            logger.error(error_msg)
            return False, error_msg
    
    def send_email(
        self,
        account: EmailAccount,
        to_email: str,
        subject: str,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> tuple[bool, str, Optional[str]]:
        \"\"\"
        Envia email usando conta especificada.
        
        Args:
            account: Conta de email para envio
            to_email: Email do destinatário
            subject: Assunto do email
            html_content: Conteúdo HTML
            text_content: Conteúdo texto plano
            from_name: Nome do remetente (opcional)
            
        Returns:
            Tuple (success, message, message_id)
        \"\"\"
        try:
            config = account.get_smtp_config(self.encryption_key)
            
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self._format_from_address(config, from_name)
            msg['To'] = to_email
            
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
            
            # Enviar
            with self._create_smtp_connection(config) as server:
                server.send_message(msg)
                message_id = msg.get('Message-ID', '')
                
                success_msg = f\"Email enviado com sucesso para {to_email}\"
                logger.info(success_msg)
                return True, success_msg, message_id
                
        except Exception as e:
            error_msg = f\"Erro ao enviar email: {str(e)}\"
            logger.error(error_msg)
            return False, error_msg, None
    
    def _create_smtp_connection(self, config: Dict[str, Any]):
        \"\"\"
        Cria conexão SMTP configurada.
        
        Args:
            config: Configuração SMTP da conta
            
        Returns:
            Objeto SMTP conectado e autenticado
        \"\"\"
        server = config['server']
        port = config['port']
        username = config['username']
        password = config['password']
        use_tls = config['use_tls']
        use_ssl = config['use_ssl']
        
        # Criar conexão
        if use_ssl:
            context = ssl.create_default_context()
            smtp = smtplib.SMTP_SSL(server, port, context=context)
        else:
            smtp = smtplib.SMTP(server, port)
            
        # Ativar TLS se necessário
        if use_tls and not use_ssl:
            context = ssl.create_default_context()
            smtp.starttls(context=context)
        
        # Autenticar
        if username and password:
            smtp.login(username, password)
        
        return smtp
    
    def _format_from_address(self, config: Dict[str, Any], from_name: Optional[str] = None) -> str:
        \"\"\"
        Formata endereço de remetente.
        
        Args:
            config: Configuração da conta
            from_name: Nome do remetente
            
        Returns:
            Endereço formatado
        \"\"\"
        email = config['from_email']
        name = from_name or config.get('from_name', '')
        
        if name:
            return f\"{name} <{email}>\"
        return email
```

---

## ⚡ **PONTO DE CONTROLE FASE 2**

Após implementar esta fase, execute os testes:

```bash
# Testar modelos completos
python -c "from sendcraft.models import Domain, EmailAccount, EmailTemplate, EmailLog; print('✅ All models OK')"

# Testar crypto
python -c "from sendcraft.utils.crypto import AESCipher; c = AESCipher('test'); encrypted = c.encrypt('hello'); decrypted = c.decrypt(encrypted); print('✅ Crypto OK' if decrypted == 'hello' else '❌ Crypto FAIL')"

# Testar SMTP service
python -c "from sendcraft.services.smtp_service import SMTPService; s = SMTPService('test'); print('✅ SMTP Service OK')"
```

**CRITÉRIOS DE ACEITAÇÃO:**
- [ ] Todos os modelos implementados e funcionais
- [ ] Crypto service encrypts/decrypts corretamente
- [ ] SMTP service instancia sem erros
- [ ] Relationships entre modelos funcionam
- [ ] Métodos de classe e instância testados

---

## 🔄 **PRÓXIMA FASE**

Quando completar esta fase:
1. Commit e push com tag `v0.2-models-services`
2. Reportar conclusão
3. Aguardar **FASE 3: APIs e Endpoints**

**Continue focado na qualidade e modularidade!** 🎯