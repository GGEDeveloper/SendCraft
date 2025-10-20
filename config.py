"""
Configuração base da aplicação SendCraft.
Hierarquia: config.py → instance/config.py → environment variables
"""
import os
from typing import Type


class Config:
    """Configuração base."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-me'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///sendcraft.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # SendCraft
    DEFAULT_FROM_NAME = os.environ.get('DEFAULT_FROM_NAME') or 'SendCraft'
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'dev-encryption-key'
    
    # API
    API_KEYS = {}  # Populated from instance config
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT') or '100/hour'
    
    # Email
    DEFAULT_SMTP_SERVER = os.environ.get('DEFAULT_SMTP_SERVER') or 'localhost'
    DEFAULT_SMTP_PORT = int(os.environ.get('DEFAULT_SMTP_PORT') or 587)
    DEFAULT_USE_TLS = os.environ.get('DEFAULT_USE_TLS', 'true').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'sendcraft.log'


class DevelopmentConfig(Config):
    """Configuração de desenvolvimento."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configuração de produção."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Configuração de testes."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config: dict[str, Type[Config]] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}