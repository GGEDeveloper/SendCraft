"""
Comandos CLI personalizados para SendCraft.
Fornece comandos para gestão da aplicação via terminal.
"""
import click
from flask import current_app
from flask.cli import with_appcontext
from typing import Optional

from .extensions import db
from .utils.logging import get_logger

logger = get_logger(__name__)


@click.command()
@with_appcontext
def init_db_command() -> None:
    """
    Inicializa a base de dados criando todas as tabelas.
    
    Usage:
        flask init-db
    """
    try:
        # Importar modelos para registrar com SQLAlchemy
        from .models import base
        
        # Criar todas as tabelas
        db.create_all()
        
        click.echo('✅ Base de dados inicializada com sucesso!')
        logger.info('Database initialized successfully')
        
    except Exception as e:
        click.echo(f'❌ Erro ao inicializar base de dados: {e}', err=True)
        logger.error(f'Failed to initialize database: {e}')
        raise


@click.command()
@click.option('--domain', prompt='Domain name', help='Nome do domínio (ex: alitools.pt)')
@click.option('--key', prompt='API Key', help='API key para o domínio')
@with_appcontext
def create_admin_command(domain: str, key: str) -> None:
    """
    Cria um domínio inicial com API key.
    
    Usage:
        flask create-admin --domain alitools.pt --key SC_xxxx
    """
    try:
        # Esta funcionalidade será implementada na FASE 2
        click.echo(f'⚠️  Funcionalidade será implementada na FASE 2')
        click.echo(f'Domínio: {domain}')
        click.echo(f'API Key: {key[:10]}...')
        
    except Exception as e:
        click.echo(f'❌ Erro ao criar admin: {e}', err=True)
        logger.error(f'Failed to create admin: {e}')
        raise


@click.command()
@with_appcontext
def test_smtp_command() -> None:
    """
    Testa a configuração SMTP enviando um email de teste.
    
    Usage:
        flask test-smtp
    """
    try:
        from .services.smtp_service import test_smtp_connection
        
        click.echo('🔍 Testando conexão SMTP...')
        
        # Esta funcionalidade será implementada na FASE 3
        click.echo(f'⚠️  Funcionalidade será implementada na FASE 3')
        
    except Exception as e:
        click.echo(f'❌ Erro no teste SMTP: {e}', err=True)
        logger.error(f'SMTP test failed: {e}')
        raise


@click.command()
@click.option('--days', default=30, help='Número de dias para manter logs')
@with_appcontext
def clean_logs_command(days: int) -> None:
    """
    Limpa logs antigos da base de dados.
    
    Usage:
        flask clean-logs --days 30
    """
    try:
        click.echo(f'🧹 Limpando logs com mais de {days} dias...')
        
        # Esta funcionalidade será implementada na FASE 2
        click.echo(f'⚠️  Funcionalidade será implementada na FASE 2')
        
    except Exception as e:
        click.echo(f'❌ Erro ao limpar logs: {e}', err=True)
        logger.error(f'Failed to clean logs: {e}')
        raise