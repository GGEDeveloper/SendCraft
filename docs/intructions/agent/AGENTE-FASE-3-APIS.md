# 🤖 **FASE 3 - AGENTE AI: APIs e Autenticação**

**Continuação das FASES 1-2**  
**Repositório:** https://github.com/GGEDeveloper/SendCraft.git  
**Objetivo:** Implementar API RESTful completa com autenticação  

---

## 🎯 **PRÉ-REQUISITOS**

- FASES 1-2 completadas
- Modelos e serviços implementados
- Tag `v0.2-models-services` criada

---

## 🔐 **SISTEMA DE AUTENTICAÇÃO**

### **1. SERVICES/AUTH_SERVICE.PY**

```python
\"\"\"Serviço de autenticação para APIs SendCraft.\"\"\"
from functools import wraps
from flask import request, jsonify, current_app, g
from typing import Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)


class AuthService:
    \"\"\"Serviço de autenticação por API Key.\"\"\"
    
    @staticmethod
    def get_api_keys() -> dict:
        \"\"\"Retorna API keys configuradas.\"\"\"
        return current_app.config.get('API_KEYS', {})
    
    @staticmethod
    def validate_api_key(api_key: str) -> tuple[bool, Optional[str]]:
        \"\"\"
        Valida API key.
        
        Args:
            api_key: Chave da API
            
        Returns:
            Tuple (is_valid, key_name)
        \"\"\"
        if not api_key:
            return False, None
            
        api_keys = AuthService.get_api_keys()
        
        for key_name, valid_key in api_keys.items():
            if api_key == valid_key:
                return True, key_name
                
        return False, None
    
    @staticmethod
    def extract_api_key_from_request() -> Optional[str]:
        \"\"\"Extrai API key do request atual.\"\"\"
        # Header Authorization: Bearer <key>
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:].strip()
        
        # Query parameter
        return request.args.get('api_key')


def require_api_key(f: Callable) -> Callable:
    \"\"\"
    Decorator para exigir autenticação por API key.
    
    Usage:
        @require_api_key
        def protected_route():
            return jsonify({\"message\": \"Access granted\"})
    \"\"\"
    @wraps(f)
    def decorated_function(*args, **kwargs) -> Any:
        api_key = AuthService.extract_api_key_from_request()
        
        if not api_key:
            logger.warning(f\"API access attempt without key from {request.remote_addr}\")
            return jsonify({
                'error': 'API key required',
                'message': 'Include API key in Authorization header: Bearer <key>'
            }), 401
        
        is_valid, key_name = AuthService.validate_api_key(api_key)
        
        if not is_valid:
            logger.warning(f\"Invalid API key attempt from {request.remote_addr}: {api_key[:10]}...\")
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }), 401
        
        # Store auth info for use in route
        g.api_key_name = key_name
        g.api_key = api_key
        
        logger.info(f\"API access granted to {key_name} from {request.remote_addr}\")
        return f(*args, **kwargs)
    
    return decorated_function


def optional_api_key(f: Callable) -> Callable:
    \"\"\"
    Decorator para autenticação opcional por API key.
    Útil para endpoints que podem ter funcionalidades extras com auth.
    \"\"\"
    @wraps(f)
    def decorated_function(*args, **kwargs) -> Any:
        api_key = AuthService.extract_api_key_from_request()
        
        if api_key:
            is_valid, key_name = AuthService.validate_api_key(api_key)
            if is_valid:
                g.api_key_name = key_name
                g.api_key = api_key
                g.authenticated = True
            else:
                g.authenticated = False
        else:
            g.authenticated = False
        
        return f(*args, **kwargs)
    
    return decorated_function
```

---

## 🌐 **ENDPOINTS API V1**

### **2. API/V1/__INIT__.PY**

```python
\"\"\"Inicialização da API v1.\"\"\"
from flask import Blueprint

# Criar blueprint principal
api_v1_bp = Blueprint('api_v1', __name__)

# Importar e registrar sub-blueprints
from . import send, accounts, templates, logs, health

# Registrar rotas
api_v1_bp.register_blueprint(send.bp)
api_v1_bp.register_blueprint(accounts.bp)
api_v1_bp.register_blueprint(templates.bp)
api_v1_bp.register_blueprint(logs.bp)
api_v1_bp.register_blueprint(health.bp)
```

### **3. API/V1/SEND.PY**

```python
\"\"\"Endpoints de envio de email.\"\"\"
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any
import logging

from ...models.domain import Domain
from ...models.account import EmailAccount
from ...models.template import EmailTemplate
from ...models.log import EmailLog
from ...services.smtp_service import SMTPService
from ...services.auth_service import require_api_key
from ...extensions import db

bp = Blueprint('send', __name__, url_prefix='/send')
logger = logging.getLogger(__name__)


@bp.route('', methods=['POST'])
@require_api_key
def send_email():
    \"\"\"
    Envia email usando template.
    
    JSON Body:
    {
        \"domain\": \"alitools.pt\",
        \"account\": \"encomendas\",
        \"to\": \"cliente@exemplo.com\",
        \"template_key\": \"order_confirmation\",
        \"variables\": {
            \"customer_name\": \"João Silva\",
            \"order_number\": \"#12345\"
        },
        \"from_name\": \"ALITOOLS\" (opcional)
    }
    \"\"\"
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        # Validar campos obrigatórios
        required_fields = ['domain', 'account', 'to', 'template_key']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields
            }), 400
        
        # Buscar domínio
        domain = Domain.get_by_name(data['domain'])
        if not domain or not domain.is_active:
            return jsonify({'error': f\"Domain '{data['domain']}' not found or inactive\"}), 404
        
        # Buscar conta
        account_email = f\"{data['account']}@{data['domain']}\"
        account = EmailAccount.get_by_email(account_email)
        if not account or not account.is_active:
            return jsonify({'error': f\"Account '{account_email}' not found or inactive\"}), 404
        
        # Buscar template
        template = EmailTemplate.get_by_key(domain.id, data['template_key'])
        if not template:
            return jsonify({'error': f\"Template '{data['template_key']}' not found for domain '{data['domain']}'\"}), 404
        
        # Validar variáveis do template
        variables = data.get('variables', {})
        is_valid, missing_vars = template.validate_variables(variables)
        
        if not is_valid:
            return jsonify({
                'error': 'Missing required template variables',
                'missing_variables': missing_vars,
                'required_variables': template.variables_required
            }), 400
        
        # Criar log inicial
        log = EmailLog(
            account_id=account.id,
            template_id=template.id,
            recipient_email=data['to'],
            sender_email=account.email_address,
            subject=template.render_subject(variables),
            status='pending',
            variables_used=variables,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(log)
        db.session.commit()
        
        # Renderizar conteúdo
        subject = template.render_subject(variables)
        html_content = template.render_html(variables)
        text_content = template.render_text(variables)
        
        # Enviar email
        smtp_service = SMTPService(current_app.config['ENCRYPTION_KEY'])
        success, message, message_id = smtp_service.send_email(
            account=account,
            to_email=data['to'],
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            from_name=data.get('from_name')
        )
        
        # Atualizar log
        if success:
            log.mark_sent(message_id or '', message)
        else:
            log.mark_failed(message)
        
        # Retornar resultado
        return jsonify({
            'success': success,
            'log_id': log.id,
            'message': message,
            'message_id': message_id,
            'template_used': template.template_key,
            'variables_count': len(variables)
        }), 200 if success else 500
        
    except ValueError as e:
        logger.error(f\"Template rendering error: {e}\")
        return jsonify({
            'error': 'Template rendering error',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f\"Send email error: {e}\", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500


@bp.route('/direct', methods=['POST'])
@require_api_key
def send_direct():
    \"\"\"
    Envia email direto sem template.
    
    JSON Body:
    {
        \"domain\": \"alitools.pt\",
        \"account\": \"encomendas\",
        \"to\": \"cliente@exemplo.com\",
        \"subject\": \"Assunto do email\",
        \"html_content\": \"<h1>HTML content</h1>\" (opcional),
        \"text_content\": \"Text content\" (opcional),
        \"from_name\": \"ALITOOLS\" (opcional)
    }
    \"\"\"
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        # Validar campos obrigatórios
        required_fields = ['domain', 'account', 'to', 'subject']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields
            }), 400
        
        # Validar que há pelo menos um conteúdo
        if not data.get('html_content') and not data.get('text_content'):
            return jsonify({
                'error': 'At least one content type required',
                'message': 'Provide html_content or text_content'
            }), 400
        
        # Buscar domínio
        domain = Domain.get_by_name(data['domain'])
        if not domain or not domain.is_active:
            return jsonify({'error': f\"Domain '{data['domain']}' not found or inactive\"}), 404
        
        # Buscar conta
        account_email = f\"{data['account']}@{data['domain']}\"
        account = EmailAccount.get_by_email(account_email)
        if not account or not account.is_active:
            return jsonify({'error': f\"Account '{account_email}' not found or inactive\"}), 404
        
        # Criar log
        log = EmailLog(
            account_id=account.id,
            recipient_email=data['to'],
            sender_email=account.email_address,
            subject=data['subject'],
            status='pending',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        db.session.add(log)
        db.session.commit()
        
        # Enviar email
        smtp_service = SMTPService(current_app.config['ENCRYPTION_KEY'])
        success, message, message_id = smtp_service.send_email(
            account=account,
            to_email=data['to'],
            subject=data['subject'],
            html_content=data.get('html_content'),
            text_content=data.get('text_content'),
            from_name=data.get('from_name')
        )
        
        # Atualizar log
        if success:
            log.mark_sent(message_id or '', message)
        else:
            log.mark_failed(message)
        
        return jsonify({
            'success': success,
            'log_id': log.id,
            'message': message,
            'message_id': message_id
        }), 200 if success else 500
        
    except Exception as e:
        logger.error(f\"Send direct email error: {e}\", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500


@bp.route('/test/<domain>/<account>', methods=['POST'])
@require_api_key
def test_smtp_connection(domain: str, account: str):
    \"\"\"Testa conexão SMTP de uma conta.\"\"\"
    try:
        # Buscar domínio
        domain_obj = Domain.get_by_name(domain)
        if not domain_obj:
            return jsonify({'error': f\"Domain '{domain}' not found\"}), 404
        
        # Buscar conta
        account_email = f\"{account}@{domain}\"
        account_obj = EmailAccount.get_by_email(account_email)
        if not account_obj:
            return jsonify({'error': f\"Account '{account_email}' not found\"}), 404
        
        # Testar conexão
        smtp_service = SMTPService(current_app.config['ENCRYPTION_KEY'])
        success, message = smtp_service.test_connection(account_obj)
        
        return jsonify({
            'success': success,
            'message': message,
            'account': account_email,
            'smtp_server': account_obj.smtp_server,
            'smtp_port': account_obj.smtp_port
        }), 200 if success else 500
        
    except Exception as e:
        logger.error(f\"SMTP test error: {e}\", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500
```

### **4. API/V1/HEALTH.PY**

```python
\"\"\"Endpoints de health check.\"\"\"
from flask import Blueprint, jsonify, current_app
from datetime import datetime
import sys

from ...extensions import db
from ...services.auth_service import optional_api_key

bp = Blueprint('health', __name__)


@bp.route('/health', methods=['GET'])
@optional_api_key
def health_check():
    \"\"\"Health check básico.\"\"\"
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'service': 'SendCraft Email Manager'
    })


@bp.route('/status', methods=['GET'])
@optional_api_key  
def detailed_status():
    \"\"\"Status detalhado do sistema.\"\"\"
    try:
        # Testar database
        try:
            db.session.execute('SELECT 1')
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        # Info do sistema
        status_info = {
            'status': 'healthy' if db_status == 'connected' else 'degraded',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'service': 'SendCraft Email Manager',
            'python_version': sys.version,
            'database_status': db_status,
            'config': {
                'debug': current_app.debug,
                'testing': current_app.testing,
                'env': current_app.config.get('ENV', 'unknown')
            }
        }
        
        # Info adicional se autenticado
        if hasattr(g, 'authenticated') and g.authenticated:
            from ...models.domain import Domain
            from ...models.account import EmailAccount
            from ...models.template import EmailTemplate
            from ...models.log import EmailLog
            
            status_info['statistics'] = {
                'domains': Domain.query.count(),
                'active_domains': Domain.query.filter_by(is_active=True).count(),
                'accounts': EmailAccount.query.count(),
                'active_accounts': EmailAccount.query.filter_by(is_active=True).count(),
                'templates': EmailTemplate.query.count(),
                'active_templates': EmailTemplate.query.filter_by(is_active=True).count(),
                'total_logs': EmailLog.query.count()
            }
        
        return jsonify(status_info)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500
```

---

## 📊 **ENDPOINTS DE DADOS**

### **5. API/V1/ACCOUNTS.PY**

```python
\"\"\"Endpoints de gestão de contas.\"\"\"
from flask import Blueprint, jsonify, request, current_app
from typing import Dict, Any

from ...models.domain import Domain
from ...models.account import EmailAccount
from ...services.auth_service import require_api_key
from ...extensions import db

bp = Blueprint('accounts', __name__, url_prefix='/accounts')


@bp.route('/<domain>', methods=['GET'])
@require_api_key
def list_accounts(domain: str):
    \"\"\"Lista contas de um domínio.\"\"\"
    domain_obj = Domain.get_by_name(domain)
    if not domain_obj:
        return jsonify({
            'error': f\"Domain '{domain}' not found\",
            'accounts': []
        }), 404
    
    accounts = EmailAccount.query.filter_by(domain_id=domain_obj.id).all()
    
    return jsonify({
        'domain': domain,
        'accounts': [{
            'id': acc.id,
            'local_part': acc.local_part,
            'email_address': acc.email_address,
            'display_name': acc.display_name,
            'is_active': acc.is_active,
            'smtp_server': acc.smtp_server,
            'smtp_port': acc.smtp_port,
            'use_tls': acc.use_tls,
            'daily_limit': acc.daily_limit,
            'monthly_limit': acc.monthly_limit,
            'created_at': acc.created_at.isoformat(),
            'updated_at': acc.updated_at.isoformat()
        } for acc in accounts]
    })


@bp.route('/<domain>/<local_part>', methods=['GET'])
@require_api_key
def get_account(domain: str, local_part: str):
    \"\"\"Obtém detalhes de uma conta específica.\"\"\"
    email_address = f\"{local_part}@{domain}\"
    account = EmailAccount.get_by_email(email_address)
    
    if not account:
        return jsonify({'error': f\"Account '{email_address}' not found\"}), 404
    
    return jsonify({
        'id': account.id,
        'local_part': account.local_part,
        'email_address': account.email_address,
        'display_name': account.display_name,
        'is_active': account.is_active,
        'smtp_server': account.smtp_server,
        'smtp_port': account.smtp_port,
        'use_tls': account.use_tls,
        'use_ssl': account.use_ssl,
        'daily_limit': account.daily_limit,
        'monthly_limit': account.monthly_limit,
        'domain': {
            'id': account.domain.id,
            'name': account.domain.name,
            'is_active': account.domain.is_active
        },
        'created_at': account.created_at.isoformat(),
        'updated_at': account.updated_at.isoformat()
    })
```

### **6. API/V1/TEMPLATES.PY**

```python
\"\"\"Endpoints de gestão de templates.\"\"\"
from flask import Blueprint, jsonify

from ...models.domain import Domain
from ...models.template import EmailTemplate
from ...services.auth_service import require_api_key

bp = Blueprint('templates', __name__, url_prefix='/templates')


@bp.route('/<domain>', methods=['GET'])
@require_api_key
def list_templates(domain: str):
    \"\"\"Lista templates de um domínio.\"\"\"
    domain_obj = Domain.get_by_name(domain)
    if not domain_obj:
        return jsonify({
            'error': f\"Domain '{domain}' not found\",
            'templates': []
        }), 404
    
    templates = EmailTemplate.query.filter_by(domain_id=domain_obj.id).all()
    
    return jsonify({
        'domain': domain,
        'templates': [{
            'id': tpl.id,
            'template_key': tpl.template_key,
            'template_name': tpl.template_name,
            'description': tpl.description,
            'category': tpl.category,
            'version': tpl.version,
            'is_active': tpl.is_active,
            'variables_required': tpl.variables_required,
            'variables_optional': tpl.variables_optional,
            'created_at': tpl.created_at.isoformat(),
            'updated_at': tpl.updated_at.isoformat()
        } for tpl in templates]
    })


@bp.route('/<domain>/<template_key>', methods=['GET'])
@require_api_key  
def get_template(domain: str, template_key: str):
    \"\"\"Obtém detalhes de um template específico.\"\"\"
    domain_obj = Domain.get_by_name(domain)
    if not domain_obj:
        return jsonify({'error': f\"Domain '{domain}' not found\"}), 404
    
    template = EmailTemplate.get_by_key(domain_obj.id, template_key)
    if not template:
        return jsonify({'error': f\"Template '{template_key}' not found for domain '{domain}'\"}), 404
    
    return jsonify({
        'id': template.id,
        'template_key': template.template_key,
        'template_name': template.template_name,
        'description': template.description,
        'category': template.category,
        'version': template.version,
        'subject_template': template.subject_template,
        'html_template': template.html_template,
        'text_template': template.text_template,
        'variables_required': template.variables_required,
        'variables_optional': template.variables_optional,
        'is_active': template.is_active,
        'domain': {
            'id': template.domain.id,
            'name': template.domain.name
        },
        'created_at': template.created_at.isoformat(),
        'updated_at': template.updated_at.isoformat()
    })
```

---

## ⚡ **PONTO DE CONTROLE FASE 3**

Testar APIs implementadas:

```bash
# Testar imports
python -c "from sendcraft.api.v1 import api_v1_bp; print('✅ API Blueprint OK')"

# Testar auth service
python -c "from sendcraft.services.auth_service import AuthService; print('✅ Auth Service OK')"

# Testar endpoints (após inicializar app)
# curl -H \"Authorization: Bearer test_key\" http://localhost:5000/api/v1/health
```

**CRITÉRIOS DE ACEITAÇÃO:**
- [ ] API Blueprint registra corretamente
- [ ] Auth service valida API keys
- [ ] Health endpoints respondem
- [ ] Send endpoints implementados
- [ ] Error handling robusto

---

## 🔄 **PRÓXIMA FASE**

Tag: `v0.3-api-complete`  
**Próxima:** **FASE 4: Interface Web e CLI**

**APIs funcionais e seguras!** 🔐