"""
SendCraft Application Factory.
Implementa o padrão Factory para criação flexível da aplicação Flask.
"""
import os
from flask import Flask
from typing import Optional

from .extensions import db, mail, cors
from .utils.logging import setup_logging


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Factory function para criar instância da aplicação SendCraft.
    
    Args:
        config_name: Nome da configuração ('development', 'production', 'testing')
    
    Returns:
        Instância configurada da aplicação Flask
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Garantir que o diretório instance existe
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    
    # Importar configurações
    from config import config
    app.config.from_object(config.get(config_name, config['default']))
    
    # Load instance config (secrets) se existir
    config_file = os.path.join(app.instance_path, 'config.py')
    if os.path.exists(config_file):
        app.config.from_pyfile('config.py')
    else:
        app.logger.warning('Instance config file not found. Using defaults.')
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup logging
    setup_logging(app)
    
    # CLI commands
    register_commands(app)
    
    # Log startup
    app.logger.info(f'SendCraft started in {config_name} mode')
    
    return app


def init_extensions(app: Flask) -> None:
    """
    Inicializa extensões Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    db.init_app(app)
    mail.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "X-API-Key"]
        }
    })
    
    # Criar tabelas no contexto da aplicação (para SQLite)
    with app.app_context():
        if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite'):
            db.create_all()


def register_blueprints(app: Flask) -> None:
    """
    Registra blueprints da aplicação.
    
    Args:
        app: Instância da aplicação Flask
    """
    from .api.v1 import api_v1_bp
    from .web import web_bp
    
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    app.register_blueprint(web_bp)
    
    # Registrar error handlers
    from .api.errors import register_error_handlers
    register_error_handlers(app)


def register_commands(app: Flask) -> None:
    """
    Registra comandos CLI personalizados.
    
    Args:
        app: Instância da aplicação Flask
    """
    from .cli import (
        init_db_command,
        create_admin_command,
        test_smtp_command,
        clean_logs_command
    )
    
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(test_smtp_command)
    app.cli.add_command(clean_logs_command)