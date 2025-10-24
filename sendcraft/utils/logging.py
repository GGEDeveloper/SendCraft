"""
Configuração de logging para SendCraft.
Fornece logging estruturado e configurável com suporte serverless.
"""
import logging
import logging.handlers
import os
from typing import Optional
from flask import Flask, has_request_context, request


class RequestFormatter(logging.Formatter):
    """Formatter personalizado que inclui informações do request."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata o log incluindo contexto do request se disponível."""
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
        return super().format(record)


def setup_logging(app: Flask) -> None:
    """
    Configura sistema de logging para a aplicação.
    Compatível com ambientes serverless (Vercel, AWS Lambda).
    
    Args:
        app: Instância da aplicação Flask
    """
    # Remove handlers padrão
    app.logger.handlers = []
    
    # Configura nível de log
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    app.logger.setLevel(log_level)
    
    # Formato do log
    formatter = RequestFormatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Handler para console (SEMPRE disponível em todos os ambientes)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)
    
    # ✅ CORREÇÃO SERVERLESS: Handler para arquivo apenas se seguro
    log_file = app.config.get('LOG_FILE')
    
    # Detectar ambiente serverless
    is_serverless = (
        os.environ.get('VERCEL') or 
        os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or
        os.environ.get('GOOGLE_CLOUD_PROJECT') or
        '/var/task' in os.getcwd()  # Vercel/Lambda path detection
    )
    
    if log_file and not app.config.get('TESTING') and not is_serverless:
        try:
            # Criar diretório se não existir
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Rotating file handler (max 10MB, mantém 10 backups)
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(formatter)
            app.logger.addHandler(file_handler)
            app.logger.info(f'File logging enabled: {log_file}')
            
        except (OSError, PermissionError) as e:
            # Graceful fallback para ambientes read-only
            app.logger.warning(f'File logging disabled (read-only filesystem): {e}')
    
    elif is_serverless:
        app.logger.info('Serverless environment detected - using console logging only')
    
    app.logger.info('SendCraft logging configured successfully')


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Obtém um logger configurado.
    
    Args:
        name: Nome do logger (geralmente __name__ do módulo)
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(name or __name__)