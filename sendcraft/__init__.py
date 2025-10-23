"""
SendCraft Application Factory com suporte a múltiplos ambientes.
"""
import os
import sys
from flask import Flask
from typing import Optional

from .extensions import db, mail, cors, migrate
from .utils.logging import setup_logging


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Factory function para criar instância SendCraft com configuração modular.
    
    Args:
        config_name: Nome da configuração (local|development|production|testing)
    
    Returns:
        Instância configurada da aplicação Flask
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Garantir diretório instance
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'local')
    
    # Load environment file baseado no config_name
    load_environment_file(config_name)
    
    # Importar e aplicar configuração
    from config import get_config
    app.config.from_object(get_config(config_name))
    
    # Load instance config (secrets locais)
    try:
        app.config.from_pyfile('config.py', silent=True)
    except Exception:
        app.logger.debug('No instance config file found')
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup logging
    setup_logging(app)
    
    # CLI commands
    register_commands(app)
    
    # Log startup
    app.logger.info(f'SendCraft iniciado em modo {config_name}')
    
    # Mostrar informações de configuração
    if config_name == 'local':
        app.logger.info('📊 Usando SQLite local (modo offline)')
    elif config_name == 'development':
        app.logger.info('🌐 Conectando ao MySQL remoto (dominios.pt)')
    elif config_name == 'production':
        app.logger.info('🚀 Usando MySQL local (produção)')
    
    return app


def load_environment_file(config_name: str) -> None:
    """
    Carrega ficheiro .env específico do ambiente.
    
    Args:
        config_name: Nome da configuração
    """
    from dotenv import load_dotenv
    
    env_files = [
        f'.env.{config_name}',
        '.env.local',  # Fallback
        '.env'         # Fallback geral
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(env_file, override=True)
            print(f"✅ Loaded environment from {env_file}")
            break
    else:
        print("⚠️ No environment file found, using system ENV vars")


def init_extensions(app: Flask) -> None:
    """Inicializa extensões Flask"""
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "X-API-Key", "Authorization"]
        }
    })
    
    # Criar tabelas se necessário (SQLite)
    with app.app_context():
        if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite'):
            db.create_all()
            app.logger.info("SQLite database initialized")


def register_blueprints(app: Flask) -> None:
    """Registra blueprints da aplicação"""
    from .api.v1 import api_v1_bp
    from .routes.web import web_bp
    from .routes.external_api import external_api_bp
    from .routes.api_docs import docs_bp
    
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    app.register_blueprint(web_bp)
    app.register_blueprint(external_api_bp)  # External API for AliTools integration
    app.register_blueprint(docs_bp)  # API documentation
    
    # Error handlers
    from .api.errors import register_error_handlers
    register_error_handlers(app)


def register_commands(app: Flask) -> None:
    """Registra comandos CLI"""
    # Importar comandos do arquivo commands.py
    from .commands import (
        init_db_command,
        create_admin_command,
        test_smtp_command,
        clean_logs_command,
        seed_imap_command
    )
    
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(test_smtp_command)
    app.cli.add_command(clean_logs_command)
    app.cli.add_command(seed_imap_command)
    
    # Adicionar comando seed-local-data se disponível
    try:
        from .cli.seed_data import seed_local_data
        app.cli.add_command(seed_local_data)
    except ImportError:
        app.logger.debug("Seed data command not available")