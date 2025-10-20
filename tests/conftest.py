"""
Configuração pytest para testes do SendCraft.
Define fixtures e configurações globais de teste.
"""
import os
import sys
import pytest
from typing import Generator

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sendcraft import create_app
from sendcraft.extensions import db


@pytest.fixture
def app():
    """
    Cria instância da aplicação para testes.
    
    Returns:
        Aplicação Flask configurada para testes
    """
    app = create_app('testing')
    
    # Configurações adicionais de teste
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    
    # Criar contexto da aplicação
    with app.app_context():
        # Criar tabelas
        db.create_all()
        
        yield app
        
        # Limpar após testes
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Cria cliente de teste.
    
    Args:
        app: Fixture da aplicação
    
    Returns:
        Cliente de teste Flask
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Cria runner CLI para testes.
    
    Args:
        app: Fixture da aplicação
    
    Returns:
        CLI runner
    """
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """
    Cria sessão de base de dados para testes.
    
    Args:
        app: Fixture da aplicação
    
    Returns:
        Sessão SQLAlchemy
    """
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configure session
        db.session.configure(bind=connection)
        
        yield db.session
        
        # Rollback após teste
        transaction.rollback()
        connection.close()
        db.session.remove()


@pytest.fixture
def api_headers():
    """
    Headers padrão para testes de API.
    
    Returns:
        Dicionário com headers
    """
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-API-Key': 'SC_test_api_key_12345678901234567890'
    }