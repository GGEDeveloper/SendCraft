"""Error handlers para API SendCraft."""
from flask import jsonify, request
from werkzeug.exceptions import HTTPException
from typing import Tuple, Dict, Any
import logging

from ..utils.logging import get_logger

logger = get_logger(__name__)


# Custom Exception Classes
class APIError(Exception):
    """Base exception for API errors."""
    status_code = 500
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class BadRequest(APIError):
    """Exception for Bad Request (400)."""
    status_code = 400


class NotFound(APIError):
    """Exception for Not Found (404)."""
    status_code = 404


class ServerError(APIError):
    """Exception for Internal Server Error (500)."""
    status_code = 500


def register_error_handlers(app):
    """
    Registra error handlers na aplicação.
    
    Args:
        app: Instância Flask
    """
    
    @app.errorhandler(400)
    def bad_request(error) -> Tuple[Dict[str, Any], int]:
        """Handler para Bad Request (400)."""
        logger.warning(f"Bad request from {request.remote_addr}: {error}")
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'The request was invalid or cannot be processed',
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error) -> Tuple[Dict[str, Any], int]:
        """Handler para Unauthorized (401)."""
        logger.warning(f"Unauthorized access attempt from {request.remote_addr}")
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource',
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error) -> Tuple[Dict[str, Any], int]:
        """Handler para Forbidden (403)."""
        logger.warning(f"Forbidden access attempt from {request.remote_addr}: {error}")
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource',
            'status_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error) -> Tuple[Dict[str, Any], int]:
        """Handler para Not Found (404)."""
        logger.info(f"Resource not found: {request.url}")
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error) -> Tuple[Dict[str, Any], int]:
        """Handler para Method Not Allowed (405)."""
        logger.warning(f"Method not allowed: {request.method} on {request.url}")
        return jsonify({
            'error': 'Method Not Allowed',
            'message': f'The method {request.method} is not allowed for this resource',
            'status_code': 405
        }), 405
    
    @app.errorhandler(422)
    def unprocessable_entity(error) -> Tuple[Dict[str, Any], int]:
        """Handler para Unprocessable Entity (422)."""
        logger.warning(f"Unprocessable entity from {request.remote_addr}: {error}")
        return jsonify({
            'error': 'Unprocessable Entity',
            'message': 'The request was well-formed but contains semantic errors',
            'status_code': 422
        }), 422
    
    @app.errorhandler(429)
    def too_many_requests(error) -> Tuple[Dict[str, Any], int]:
        """Handler para Too Many Requests (429)."""
        logger.warning(f"Rate limit exceeded from {request.remote_addr}")
        return jsonify({
            'error': 'Too Many Requests',
            'message': 'Rate limit exceeded. Please try again later',
            'status_code': 429
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error) -> Tuple[Dict[str, Any], int]:
        """Handler para Internal Server Error (500)."""
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later',
            'status_code': 500
        }), 500
    
    @app.errorhandler(503)
    def service_unavailable(error) -> Tuple[Dict[str, Any], int]:
        """Handler para Service Unavailable (503)."""
        logger.error(f"Service unavailable: {error}")
        return jsonify({
            'error': 'Service Unavailable',
            'message': 'The service is temporarily unavailable. Please try again later',
            'status_code': 503
        }), 503
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException) -> Tuple[Dict[str, Any], int]:
        """Handler genérico para exceções HTTP."""
        logger.warning(f"HTTP exception {error.code}: {error.description}")
        return jsonify({
            'error': error.name,
            'message': error.description,
            'status_code': error.code
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception) -> Tuple[Dict[str, Any], int]:
        """Handler para erros não esperados."""
        logger.error(f"Unexpected error: {error}", exc_info=True)
        
        # Em produção, não expor detalhes do erro
        if app.config.get('DEBUG', False):
            message = str(error)
        else:
            message = 'An unexpected error occurred'
        
        return jsonify({
            'error': 'Internal Server Error',
            'message': message,
            'status_code': 500
        }), 500