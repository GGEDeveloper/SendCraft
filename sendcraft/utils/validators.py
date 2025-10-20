"""
Validadores para SendCraft.
Fornece funções de validação para diversos tipos de dados.
"""
import re
from typing import Dict, Any, List, Optional, Tuple


class ValidationError(Exception):
    """Exceção para erros de validação."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        """
        Inicializa erro de validação.
        
        Args:
            message: Mensagem de erro
            field: Campo que causou o erro
        """
        self.message = message
        self.field = field
        super().__init__(message)


def validate_email(email: str, allow_empty: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Valida endereço de email.
    
    Args:
        email: Email para validar
        allow_empty: Se permite email vazio
    
    Returns:
        Tupla (válido, mensagem_erro)
    """
    if not email:
        if allow_empty:
            return True, None
        return False, "Email is required"
    
    # Padrão RFC 5322 simplificado
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    # Verificar comprimento
    if len(email) > 254:
        return False, "Email too long (max 254 characters)"
    
    return True, None


def validate_domain(domain: str) -> Tuple[bool, Optional[str]]:
    """
    Valida nome de domínio.
    
    Args:
        domain: Domínio para validar
    
    Returns:
        Tupla (válido, mensagem_erro)
    """
    if not domain:
        return False, "Domain is required"
    
    # Padrão para domínio válido
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    
    if not re.match(pattern, domain):
        return False, "Invalid domain format"
    
    # Verificar comprimento
    if len(domain) > 253:
        return False, "Domain too long (max 253 characters)"
    
    return True, None


def validate_api_key(api_key: str) -> Tuple[bool, Optional[str]]:
    """
    Valida formato de API key.
    
    Args:
        api_key: API key para validar
    
    Returns:
        Tupla (válido, mensagem_erro)
    """
    if not api_key:
        return False, "API key is required"
    
    # Verificar prefixo
    if not api_key.startswith('SC_'):
        return False, "API key must start with 'SC_'"
    
    # Verificar comprimento
    if len(api_key) < 20:
        return False, "API key too short"
    
    # Verificar caracteres válidos
    pattern = r'^SC_[a-zA-Z0-9]+$'
    if not re.match(pattern, api_key):
        return False, "API key contains invalid characters"
    
    return True, None


def validate_smtp_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida configuração SMTP.
    
    Args:
        config: Dicionário com configuração SMTP
    
    Returns:
        Tupla (válido, lista_erros)
    """
    errors = []
    
    # Verificar campos obrigatórios
    required_fields = ['server', 'port', 'username', 'password']
    for field in required_fields:
        if field not in config or not config[field]:
            errors.append(f"Field '{field}' is required")
    
    # Validar servidor
    if 'server' in config and config['server']:
        valid, error = validate_domain(config['server'])
        if not valid:
            errors.append(f"Invalid SMTP server: {error}")
    
    # Validar porta
    if 'port' in config:
        try:
            port = int(config['port'])
            if port < 1 or port > 65535:
                errors.append("SMTP port must be between 1 and 65535")
        except (ValueError, TypeError):
            errors.append("SMTP port must be a number")
    
    # Validar email do remetente
    if 'from_email' in config and config['from_email']:
        valid, error = validate_email(config['from_email'])
        if not valid:
            errors.append(f"Invalid from_email: {error}")
    
    return len(errors) == 0, errors


def validate_template_variables(template: str, variables: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida variáveis de template.
    
    Args:
        template: String do template com placeholders
        variables: Dicionário de variáveis
    
    Returns:
        Tupla (válido, lista_erros)
    """
    errors = []
    
    # Encontrar todos os placeholders no template
    placeholders = re.findall(r'\{\{([^}]+)\}\}', template)
    
    # Verificar se todas as variáveis necessárias estão presentes
    for placeholder in placeholders:
        var_name = placeholder.strip()
        if var_name not in variables:
            errors.append(f"Missing required variable: {var_name}")
    
    return len(errors) == 0, errors


def validate_password(password: str, min_length: int = 8) -> Tuple[bool, Optional[str]]:
    """
    Valida força de senha.
    
    Args:
        password: Senha para validar
        min_length: Comprimento mínimo
    
    Returns:
        Tupla (válido, mensagem_erro)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    # Verificar complexidade
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and numbers"
    
    return True, None


def validate_request_data(data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> Tuple[bool, Dict[str, str]]:
    """
    Valida dados de request contra schema.
    
    Args:
        data: Dados para validar
        schema: Schema de validação
    
    Returns:
        Tupla (válido, dicionário_erros)
    """
    errors = {}
    
    for field, rules in schema.items():
        # Verificar se campo é obrigatório
        required = rules.get('required', False)
        value = data.get(field)
        
        if required and not value:
            errors[field] = f"{field} is required"
            continue
        
        if not value:
            continue
        
        # Validar tipo
        expected_type = rules.get('type')
        if expected_type and not isinstance(value, expected_type):
            errors[field] = f"{field} must be of type {expected_type.__name__}"
            continue
        
        # Validar comprimento para strings
        if isinstance(value, str):
            min_length = rules.get('min_length')
            max_length = rules.get('max_length')
            
            if min_length and len(value) < min_length:
                errors[field] = f"{field} must be at least {min_length} characters"
            elif max_length and len(value) > max_length:
                errors[field] = f"{field} must be at most {max_length} characters"
        
        # Validar range para números
        if isinstance(value, (int, float)):
            min_value = rules.get('min_value')
            max_value = rules.get('max_value')
            
            if min_value is not None and value < min_value:
                errors[field] = f"{field} must be at least {min_value}"
            elif max_value is not None and value > max_value:
                errors[field] = f"{field} must be at most {max_value}"
        
        # Validar valores permitidos
        allowed_values = rules.get('allowed_values')
        if allowed_values and value not in allowed_values:
            errors[field] = f"{field} must be one of: {', '.join(map(str, allowed_values))}"
        
        # Validar com função customizada
        custom_validator = rules.get('validator')
        if custom_validator:
            valid, error_msg = custom_validator(value)
            if not valid:
                errors[field] = error_msg
    
    return len(errors) == 0, errors