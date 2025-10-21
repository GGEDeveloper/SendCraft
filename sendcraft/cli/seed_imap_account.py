"""Seed function para conta IMAP encomendas@alitools.pt."""
import click
from flask import current_app
from sqlalchemy import text

from ..models import Domain, EmailAccount
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Configuração real da conta encomendas@alitools.pt
ALITOOLS_IMAP_CONFIG = {
    'domain': 'alitools.pt',
    'email': 'encomendas@alitools.pt',
    'password': '6f2zniWMN6aUFaD',
    'smtp_server': 'mail.alitools.pt',
    'smtp_port': 465,
    'smtp_use_ssl': True,
    'smtp_use_tls': False,
    'imap_server': 'mail.alitools.pt', 
    'imap_port': 993,
    'imap_use_ssl': True,
    'imap_use_tls': False,
    'display_name': 'AliTools Encomendas',
    'daily_limit': 5000,
    'monthly_limit': 100000,
    'auto_sync_enabled': True,
    'sync_interval_minutes': 5
}


def seed_alitools_imap_account(force: bool = False):
    """
    Seed da conta IMAP encomendas@alitools.pt.
    
    Args:
        force: Se True, recria a conta mesmo se já existir
    """
    try:
        logger.info("Starting AliTools IMAP account seeding...")
        
        # Verificar se o domínio existe
        domain = Domain.query.filter_by(name=ALITOOLS_IMAP_CONFIG['domain']).first()
        
        if not domain:
            # Criar domínio
            domain = Domain.create(
                name=ALITOOLS_IMAP_CONFIG['domain'],
                is_active=True,
                description='AliTools - Domain for order management'
            )
            logger.info(f"Created domain: {domain.name}")
        else:
            logger.info(f"Domain already exists: {domain.name}")
        
        # Verificar se a conta existe
        account = EmailAccount.get_by_email(ALITOOLS_IMAP_CONFIG['email'])
        
        if account and not force:
            logger.info(f"Account already exists: {account.email_address}")
            
            # Atualizar configurações IMAP se necessário
            updated = False
            
            if account.imap_server != ALITOOLS_IMAP_CONFIG['imap_server']:
                account.imap_server = ALITOOLS_IMAP_CONFIG['imap_server']
                updated = True
            
            if account.imap_port != ALITOOLS_IMAP_CONFIG['imap_port']:
                account.imap_port = ALITOOLS_IMAP_CONFIG['imap_port']
                updated = True
            
            if account.imap_use_ssl != ALITOOLS_IMAP_CONFIG['imap_use_ssl']:
                account.imap_use_ssl = ALITOOLS_IMAP_CONFIG['imap_use_ssl']
                updated = True
            
            if account.auto_sync_enabled != ALITOOLS_IMAP_CONFIG['auto_sync_enabled']:
                account.auto_sync_enabled = ALITOOLS_IMAP_CONFIG['auto_sync_enabled']
                updated = True
            
            if account.sync_interval_minutes != ALITOOLS_IMAP_CONFIG['sync_interval_minutes']:
                account.sync_interval_minutes = ALITOOLS_IMAP_CONFIG['sync_interval_minutes']
                updated = True
            
            if updated:
                account.save()
                logger.info("Updated IMAP configuration for existing account")
            
            return account
        
        elif account and force:
            # Deletar conta existente
            account.delete()
            logger.info(f"Deleted existing account: {account.email_address}")
        
        # Criar nova conta
        account = EmailAccount.create(
            domain_id=domain.id,
            local_part='encomendas',
            email_address=ALITOOLS_IMAP_CONFIG['email'],
            display_name=ALITOOLS_IMAP_CONFIG['display_name'],
            
            # SMTP Configuration
            smtp_server=ALITOOLS_IMAP_CONFIG['smtp_server'],
            smtp_port=ALITOOLS_IMAP_CONFIG['smtp_port'],
            smtp_username=ALITOOLS_IMAP_CONFIG['email'],
            use_ssl=ALITOOLS_IMAP_CONFIG['smtp_use_ssl'],
            use_tls=ALITOOLS_IMAP_CONFIG['smtp_use_tls'],
            
            # IMAP Configuration
            imap_server=ALITOOLS_IMAP_CONFIG['imap_server'],
            imap_port=ALITOOLS_IMAP_CONFIG['imap_port'],
            imap_use_ssl=ALITOOLS_IMAP_CONFIG['imap_use_ssl'],
            imap_use_tls=ALITOOLS_IMAP_CONFIG['imap_use_tls'],
            auto_sync_enabled=ALITOOLS_IMAP_CONFIG['auto_sync_enabled'],
            sync_interval_minutes=ALITOOLS_IMAP_CONFIG['sync_interval_minutes'],
            
            # Limits
            daily_limit=ALITOOLS_IMAP_CONFIG['daily_limit'],
            monthly_limit=ALITOOLS_IMAP_CONFIG['monthly_limit'],
            
            is_active=True
        )
        
        # Set encrypted password
        encryption_key = current_app.config.get('SECRET_KEY', '')
        account.set_password(ALITOOLS_IMAP_CONFIG['password'], encryption_key)
        account.save()
        
        logger.info(f"""
        ✅ Successfully seeded AliTools IMAP account:
        - Email: {account.email_address}
        - SMTP Server: {account.smtp_server}:{account.smtp_port}
        - IMAP Server: {account.imap_server}:{account.imap_port}
        - Auto Sync: {account.auto_sync_enabled}
        - Sync Interval: {account.sync_interval_minutes} minutes
        """)
        
        return account
        
    except Exception as e:
        logger.error(f"Error seeding AliTools IMAP account: {e}")
        db.session.rollback()
        raise


def test_imap_connection(account: EmailAccount = None):
    """
    Testa conexão IMAP da conta.
    
    Args:
        account: Conta para testar (busca encomendas@alitools.pt se não fornecida)
    """
    try:
        if not account:
            account = EmailAccount.get_by_email(ALITOOLS_IMAP_CONFIG['email'])
        
        if not account:
            logger.error("Account not found. Run seed_alitools_imap_account() first.")
            return False
        
        from ..services.imap_service import IMAPService
        
        logger.info(f"Testing IMAP connection for {account.email_address}...")
        
        # Criar serviço IMAP
        imap_service = IMAPService(account)
        
        # Obter configuração
        encryption_key = current_app.config.get('SECRET_KEY', '')
        config = account.get_imap_config(encryption_key)
        
        # Conectar
        if not imap_service.connect(config):
            logger.error("Failed to connect to IMAP server")
            return False
        
        # Listar pastas
        folders = imap_service.list_folders()
        logger.info(f"Available folders: {folders}")
        
        # Selecionar INBOX
        success, num_messages = imap_service.select_folder('INBOX')
        if success:
            logger.info(f"INBOX has {num_messages} messages")
        
        # Buscar alguns emails recentes
        recent_emails = imap_service.fetch_recent_emails(limit=5)
        logger.info(f"Fetched {len(recent_emails)} recent emails")
        
        for email in recent_emails:
            logger.info(f"  - From: {email.get('from_address')} | Subject: {email.get('subject', '(no subject)')}")
        
        # Desconectar
        imap_service.disconnect()
        
        logger.info("✅ IMAP connection test successful!")
        return True
        
    except Exception as e:
        logger.error(f"IMAP connection test failed: {e}")
        return False


def sync_initial_emails(limit: int = 50):
    """
    Sincroniza emails iniciais da conta encomendas@alitools.pt.
    
    Args:
        limit: Número de emails para sincronizar
    """
    try:
        # Buscar conta
        account = EmailAccount.get_by_email(ALITOOLS_IMAP_CONFIG['email'])
        
        if not account:
            logger.error("Account not found. Run seed_alitools_imap_account() first.")
            return 0
        
        from ..services.imap_service import IMAPService
        
        logger.info(f"Starting initial sync for {account.email_address}...")
        
        # Criar serviço IMAP
        imap_service = IMAPService(account)
        
        # Sincronizar emails
        synced_count = imap_service.sync_account_emails(
            account=account,
            folder='INBOX',
            limit=limit,
            since_last_sync=False  # Full sync
        )
        
        logger.info(f"✅ Successfully synced {synced_count} emails")
        
        # Mostrar estatísticas
        from ..models import EmailInbox
        
        total_emails = EmailInbox.query.filter_by(account_id=account.id).count()
        unread_emails = EmailInbox.query.filter_by(
            account_id=account.id,
            is_read=False
        ).count()
        
        logger.info(f"""
        📊 Inbox Statistics:
        - Total Emails: {total_emails}
        - Unread Emails: {unread_emails}
        - Last Sync: {account.last_sync}
        """)
        
        return synced_count
        
    except Exception as e:
        logger.error(f"Initial sync failed: {e}")
        return 0


@click.command('seed-imap')
@click.option('--force', is_flag=True, help='Force recreate account if exists')
@click.option('--test', is_flag=True, help='Test IMAP connection')
@click.option('--sync', type=int, default=0, help='Sync initial emails (specify limit)')
def seed_imap_command(force: bool, test: bool, sync: int):
    """Seed AliTools IMAP account with real configuration."""
    try:
        # Seed account
        account = seed_alitools_imap_account(force=force)
        
        # Test connection if requested
        if test:
            test_imap_connection(account)
        
        # Sync emails if requested
        if sync > 0:
            sync_initial_emails(limit=sync)
        
        click.echo("✅ IMAP account seeding completed successfully!")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


# Function to be called from Python code
def setup_imap_account():
    """
    Setup completo da conta IMAP encomendas@alitools.pt.
    Pode ser chamada diretamente do código Python.
    """
    try:
        # 1. Seed account
        account = seed_alitools_imap_account(force=False)
        
        # 2. Test connection
        if test_imap_connection(account):
            # 3. Sync initial emails
            sync_initial_emails(limit=50)
        
        return account
        
    except Exception as e:
        logger.error(f"Failed to setup IMAP account: {e}")
        return None