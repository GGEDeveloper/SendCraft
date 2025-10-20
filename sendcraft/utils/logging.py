"""
Configuração de logging para SendCraft.
Fornece logging estruturado e configurável.
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
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)
    
    # Handler para arquivo (se configurado)
    log_file = app.config.get('LOG_FILE')
    if log_file and not app.config.get('TESTING'):
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
    
    app.logger.info('SendCraft logging configured')


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Obtém um logger configurado.
    
    Args:
        name: Nome do logger (geralmente __name__ do módulo)
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(name or __name__)