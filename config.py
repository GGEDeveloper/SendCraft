"""
SendCraft - Sistema de Configurações Modulares
Suporta: local (SQLite), development (Remote MySQL), production (MySQL local)
"""
import os
from typing import Type, Dict, Any


class BaseConfig:
    """Configuração base comum a todos os ambientes"""
    
    # Flask Core
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sendcraft-production-key-change-me-32-chars'
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'sendcraft-encryption-key-change-32c'
    
    # SendCraft Core  
    DEFAULT_FROM_NAME = os.environ.get('DEFAULT_FROM_NAME') or 'SendCraft Email Manager'
    
    # ❌ REMOVER TODOS ESTES (não são mais usados):
    # DEFAULT_SMTP_SERVER = ...
    # DEFAULT_SMTP_PORT = ...
    # MAIL_SERVER = ...
    # MAIL_PORT = ...
    # MAIL_USE_TLS = ...
    # MAIL_USE_SSL = ...
    # MAIL_USERNAME = ...
    # MAIL_PASSWORD = ...
    # DEFAULT_SENDER = ...
    
    # API Configuration
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT') or '1000/hour'
    API_KEY_REQUIRED = os.environ.get('API_KEY_REQUIRED', 'false').lower() == 'true'
    API_KEYS = {}  # Populated from instance config
    
    # Database Base Settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'pool_timeout': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Pagination
    PAGINATION_PER_PAGE = 20
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE')  # ✅ CORREÇÃO: Sem default, fica None para Vercel
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class LocalConfig(BaseConfig):
    """Configuração para desenvolvimento local (SQLite)"""
    
    DEBUG = True
    TESTING = False
    FLASK_ENV = 'local'
    
    # SQLite local - sem MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///sendcraft_local.db'
    
    # Logging detalhado
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'sendcraft_local.log'  # ✅ OK para local
    SQLALCHEMY_ECHO = True  # Ver SQL queries
    
    # SMTP Mock (sem envios reais)
    SMTP_TESTING_MODE = True
    
    # Security relaxed para desenvolvimento
    WTF_CSRF_ENABLED = False


class DevelopmentConfig(BaseConfig):
    """Configuração para desenvolvimento remoto (Remote MySQL direto → dominios.pt)"""
    
    DEBUG = True
    TESTING = False
    FLASK_ENV = 'development'
    
    # MySQL remoto direto (sem SSH tunnel)
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_URL') or \
        'mysql+pymysql://artnshin_sendcraft:g>bxZmj%25=JZt9Z%2Ci@artnshine.pt:3306/artnshin_sendcraft'
    
    # Remote MySQL Configuration (sem SSH)
    MYSQL_REMOTE_HOST = 'artnshine.pt'
    MYSQL_REMOTE_PORT = 3306
    
    # Connection settings para MySQL remoto
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 3,  # Menos conexões para remoto
        'pool_timeout': 30,
        'pool_recycle': 1800,  # Reciclar mais frequentemente
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 20,  # Timeout maior para conexão remota
            'read_timeout': 20,
            'write_timeout': 20
        }
    }
    
    # Logging moderado
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'sendcraft_dev.log'  # ✅ OK para development
    SQLALCHEMY_ECHO = False


class ProductionConfig(BaseConfig):
    """Configuração para produção (Vercel Serverless)"""
    
    DEBUG = False
    TESTING = False
    FLASK_ENV = 'production'
    
    # MySQL via connection string (Vercel environment variable)
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_URL') or \
        os.environ.get('DATABASE_URL')
    
    # Production Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # ✅ CORREÇÃO CRÍTICA VERCEL: Serverless-optimized
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 1,  # Serverless = 1 connection
        'pool_timeout': 10,
        'pool_recycle': 300,  # 5 minutes
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 5,
            'read_timeout': 30,
            'write_timeout': 30
        }
    }
    
    # ✅ CORREÇÃO: Logging sem ficheiro (Vercel read-only filesystem)
    LOG_LEVEL = 'INFO'  # Visível no Vercel dashboard
    LOG_FILE = None  # ✅ CRITICAL: Desabilita file logging para Vercel
    SQLALCHEMY_ECHO = False


class TestingConfig(BaseConfig):
    """Configuração para testes"""
    
    DEBUG = True
    TESTING = True
    FLASK_ENV = 'testing'
    
    # SQLite em memória para testes rápidos
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable external connections for testing
    WTF_CSRF_ENABLED = False
    SMTP_TESTING_MODE = True
    LOG_FILE = None  # Sem logs para testes


# Registry de configurações
config: Dict[str, Type[BaseConfig]] = {
    'local': LocalConfig,
    'development': DevelopmentConfig, 
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': LocalConfig  # Default para development local
}


def get_config(config_name: str = None) -> Type[BaseConfig]:
    """
    Retorna configuração baseada no ambiente.
    
    Args:
        config_name: Nome da configuração (local|development|production|testing)
        
    Returns:
        Classe de configuração apropriada
    """
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'local')
    
    return config.get(config_name, config['default'])