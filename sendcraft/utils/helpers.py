"""
Funções auxiliares para SendCraft.
Utilitários diversos usados em toda a aplicação.
"""
import re
import string
import secrets
from typing import Optional, Dict, Any
from datetime import datetime


def generate_api_key(prefix: str = 'SC_', length: int = 64) -> str:
    """
    Gera uma API key segura.
    
    Args:
        prefix: Prefixo da API key
        length: Comprimento total da key (incluindo prefixo)
    
    Returns:
        API key gerada
    """
    # Calcular comprimento necessário
    key_length = length - len(prefix)
    
    # Caracteres permitidos
    alphabet = string.ascii_letters + string.digits
    
    # Gerar key aleatória
    key = ''.join(secrets.choice(alphabet) for _ in range(key_length))
    
    return f'{prefix}{key}'


def is_valid_email(email: str) -> bool:
    """
    Valida formato de email.
    
    Args:
        email: Email para validar
    
    Returns:
        True se o email é válido
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_domain(domain: str) -> bool:
    """
    Valida formato de domínio.
    
    Args:
        domain: Domínio para validar
    
    Returns:
        True se o domínio é válido
    """
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    return bool(re.match(pattern, domain))


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nome de ficheiro removendo caracteres perigosos.
    
    Args:
        filename: Nome do ficheiro
    
    Returns:
        Nome sanitizado
    """
    # Remover caracteres perigosos
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Remover múltiplos underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remover underscore no início e fim
    sanitized = sanitized.strip('_')
    
    return sanitized or 'unnamed'


def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Trunca string para comprimento máximo.
    
    Args:
        text: Texto para truncar
        max_length: Comprimento máximo
        suffix: Sufixo para adicionar se truncado
    
    Returns:
        String truncada
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_bytes(num_bytes: int) -> str:
    """
    Formata bytes para formato legível.
    
    Args:
        num_bytes: Número de bytes
    
    Returns:
        String formatada (ex: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    
    return f"{num_bytes:.1f} PB"


def get_client_ip(request) -> str:
    """
    Obtém IP real do cliente considerando proxies.
    
    Args:
        request: Flask request object
    
    Returns:
        IP do cliente
    """
    # Verificar headers de proxy
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    elif request.environ.get('HTTP_X_REAL_IP'):
        return request.environ['HTTP_X_REAL_IP']
    else:
        return request.environ.get('REMOTE_ADDR', 'unknown')


def parse_bool(value: Any) -> bool:
    """
    Parse de valor para boolean.
    
    Args:
        value: Valor para converter
    
    Returns:
        Boolean parseado
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on')
    
    return bool(value)


def safe_get_nested(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Obtém valor nested de dicionário de forma segura.
    
    Args:
        data: Dicionário de dados
        path: Caminho separado por pontos (ex: "user.profile.name")
        default: Valor padrão se não encontrado
    
    Returns:
        Valor encontrado ou default
    """
    keys = path.split('.')
    result = data
    
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
    
    return result


def datetime_to_string(dt: Optional[datetime], format: str = '%Y-%m-%d %H:%M:%S') -> Optional[str]:
    """
    Converte datetime para string.
    
    Args:
        dt: Datetime para converter
        format: Formato da string
    
    Returns:
        String formatada ou None
    """
    if dt is None:
        return None
    
    return dt.strftime(format)


def string_to_datetime(date_string: Optional[str], format: str = '%Y-%m-%d %H:%M:%S') -> Optional[datetime]:
    """
    Converte string para datetime.
    
    Args:
        date_string: String para converter
        format: Formato da string
    
    Returns:
        Datetime ou None
    """
    if not date_string:
        return None
    
    try:
        return datetime.strptime(date_string, format)
    except (ValueError, TypeError):
        return None