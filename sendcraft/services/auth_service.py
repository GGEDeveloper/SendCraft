"""Serviço de autenticação para APIs SendCraft."""
from functools import wraps
from flask import request, jsonify, current_app, g
from typing import Optional, Callable, Any, Tuple
import logging

from ..utils.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """Serviço de autenticação por API Key."""
    
    @staticmethod
    def get_api_keys() -> dict:
        """
        Retorna API keys configuradas.
        
        Returns:
            Dicionário com API keys
        """
        return current_app.config.get('API_KEYS', {})
    
    @staticmethod
    def validate_api_key(api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Valida API key.
        
        Args:
            api_key: Chave da API
            
        Returns:
            Tuple (is_valid, key_name)
        """
        if not api_key:
            return False, None
            
        api_keys = AuthService.get_api_keys()
        
        # Procurar chave válida
        for key_name, valid_key in api_keys.items():
            if api_key == valid_key:
                logger.debug(f"API key validated for: {key_name}")
                return True, key_name
        
        logger.debug(f"Invalid API key attempted: {api_key[:10]}...")
        return False, None
    
    @staticmethod
    def extract_api_key_from_request() -> Optional[str]:
        """
        Extrai API key do request atual.
        
        Returns:
            API key ou None
        """
        # Tentar header Authorization: Bearer <key>
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:].strip()
        
        # Tentar header X-API-Key
        if request.headers.get('X-API-Key'):
            return request.headers.get('X-API-Key')
        
        # Tentar query parameter
        return request.args.get('api_key')


def require_api_key(f: Callable) -> Callable:
    """
    Decorator para exigir autenticação por API key.
    
    Usage:
        @require_api_key
        def protected_route():
            return jsonify({"message": "Access granted"})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs) -> Any:
        api_key = AuthService.extract_api_key_from_request()
        
        if not api_key:
            logger.warning(f"API access attempt without key from {request.remote_addr}")
            return jsonify({
                'error': 'API key required',
                'message': 'Include API key in Authorization header: Bearer <key>'
            }), 401
        
        is_valid, key_name = AuthService.validate_api_key(api_key)
        
        if not is_valid:
            logger.warning(f"Invalid API key attempt from {request.remote_addr}: {api_key[:10]}...")
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }), 401
        
        # Store auth info for use in route
        g.api_key_name = key_name
        g.api_key = api_key
        g.authenticated = True
        
        logger.info(f"API access granted to {key_name} from {request.remote_addr}")
        return f(*args, **kwargs)
    
    return decorated_function


def optional_api_key(f: Callable) -> Callable:
    """
    Decorator para autenticação opcional por API key.
    Útil para endpoints que podem ter funcionalidades extras com auth.
    
    Usage:
        @optional_api_key
        def public_route():
            if g.authenticated:
                # Extra features for authenticated users
                pass
            return jsonify({"message": "Public content"})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs) -> Any:
        api_key = AuthService.extract_api_key_from_request()
        
        if api_key:
            is_valid, key_name = AuthService.validate_api_key(api_key)
            if is_valid:
                g.api_key_name = key_name
                g.api_key = api_key
                g.authenticated = True
                logger.debug(f"Optional auth: {key_name} authenticated")
            else:
                g.authenticated = False
                logger.debug(f"Optional auth: invalid key provided")
        else:
            g.authenticated = False
            logger.debug("Optional auth: no key provided")
        
        return f(*args, **kwargs)
    
    return decorated_function