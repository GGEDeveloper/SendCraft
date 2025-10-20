"""
Configuração base da aplicação SendCraft.
MySQL/MariaDB único para desenvolvimento e produção.
"""
import os
from typing import Type


class Config:
    """Configuração base."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-me'
    
    # Database - MySQL único
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_URL') or 'mysql://sendcraft:password@localhost:3306/sendcraft'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # MySQL Connection Pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'pool_timeout': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # SendCraft
    DEFAULT_FROM_NAME = os.environ.get('DEFAULT_FROM_NAME') or 'SendCraft'
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'dev-encryption-key'
    
    # API
    API_KEYS = {}  # Populated from instance config
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT') or '100/hour'
    
    # Email
    DEFAULT_SMTP_SERVER = os.environ.get('DEFAULT_SMTP_SERVER') or 'smtp.antispamcloud.com'
    DEFAULT_SMTP_PORT = int(os.environ.get('DEFAULT_SMTP_PORT') or 587)
    DEFAULT_USE_TLS = os.environ.get('DEFAULT_USE_TLS', 'true').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'sendcraft.log'


class DevelopmentConfig(Config):
    """Configuração de desenvolvimento."""
    DEBUG = True


class ProductionConfig(Config):
    """Configuração de produção."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Configuração de testes."""
    TESTING = True
    # Usar mesmo MySQL para testes, base diferente
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_TEST_URL') or 'mysql://sendcraft:password@localhost:3306/sendcraft_test'


config: dict[str, Type[Config]] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
