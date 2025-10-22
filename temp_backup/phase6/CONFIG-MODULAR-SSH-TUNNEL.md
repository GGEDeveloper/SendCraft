# 🔧 CONFIGURAÇÃO MODULAR SENDCRAFT - Local + Produção via SSH

## 🎯 **SISTEMA DE CONFIGURAÇÕES MODULARES**

### **A. Modificar `config.py` (Substituir Completo):**
```python
"""
SendCraft - Sistema de Configurações Modulares
Suporta: local (SQLite), development (SSH tunnel), production (direto)
"""
import os
from typing import Type, Dict, Any


class BaseConfig:
    """Configuração base comum a todos os ambientes"""
    
    # Flask Core
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sendcraft-dev-key-change-in-production'
    
    # SendCraft Core
    DEFAULT_FROM_NAME = os.environ.get('DEFAULT_FROM_NAME') or 'SendCraft Email Manager'
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'sendcraft-encryption-32-chars-key!!'
    
    # API Configuration
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT') or '1000/hour'
    API_KEY_REQUIRED = os.environ.get('API_KEY_REQUIRED', 'false').lower() == 'true'
    
    # SMTP Defaults
    DEFAULT_SMTP_SERVER = os.environ.get('DEFAULT_SMTP_SERVER') or 'smtp.antispamcloud.com'
    DEFAULT_SMTP_PORT = int(os.environ.get('DEFAULT_SMTP_PORT') or 587)
    DEFAULT_USE_TLS = os.environ.get('DEFAULT_USE_TLS', 'true').lower() == 'true'
    
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
    LOG_FILE = os.environ.get('LOG_FILE') or 'sendcraft.log'
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
    SQLALCHEMY_ECHO = True  # Ver SQL queries
    
    # SMTP Mock (sem envios reais)
    SMTP_TESTING_MODE = True
    
    # Security relaxed para desenvolvimento
    WTF_CSRF_ENABLED = False


class DevelopmentConfig(BaseConfig):
    """Configuração para desenvolvimento remoto (SSH Tunnel → dominios.pt)"""
    
    DEBUG = True
    TESTING = False
    FLASK_ENV = 'development'
    
    # MySQL via SSH Tunnel (localhost:3307 → dominios.pt:3306)
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_URL') or \
        'mysql+pymysql://artnshin_sendcraft:g>bxZmj%=JZt9Z,i@localhost:3307/artnshin_sendcraft'
    
    # SSH Tunnel Configuration
    SSH_TUNNEL_REQUIRED = True
    SSH_HOST = os.environ.get('SSH_HOST') or 'ssh.dominios.pt'
    SSH_PORT = int(os.environ.get('SSH_PORT') or 22)
    SSH_USER = os.environ.get('SSH_USER') or 'artnshin'
    SSH_KEY_FILE = os.environ.get('SSH_KEY_FILE') or '~/.ssh/dominios_pt'
    
    # MySQL Remote Details
    MYSQL_REMOTE_HOST = 'localhost'  # No servidor remoto
    MYSQL_REMOTE_PORT = 3306
    MYSQL_LOCAL_PORT = 3307  # Porta local para tunnel
    
    # Logging moderado
    LOG_LEVEL = 'INFO'
    SQLALCHEMY_ECHO = False


class ProductionConfig(BaseConfig):
    """Configuração para produção (direto dominios.pt)"""
    
    DEBUG = False
    TESTING = False
    FLASK_ENV = 'production'
    
    # MySQL direto no servidor (sem tunnel)
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_URL') or \
        'mysql+pymysql://artnshin_sendcraft:g>bxZmj%=JZt9Z,i@localhost:3306/artnshin_sendcraft'
    
    # Production Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Performance
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_timeout': 30,
        'pool_recycle': 7200,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 10,
            'read_timeout': 10,
            'write_timeout': 10
        }
    }
    
    # Logging production
    LOG_LEVEL = 'WARNING'
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
```

### **B. Criar `sendcraft/utils/ssh_tunnel.py` (NOVO):**
```python
"""
SSH Tunnel Manager para SendCraft
Permite conexão local → dominios.pt MySQL via SSH tunnel
"""
import os
import subprocess
import time
import logging
import pymysql
from typing import Optional, Tuple, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class SSHTunnelManager:
    """Gestor de túneis SSH para acesso remoto ao MySQL"""
    
    def __init__(self, ssh_host: str, ssh_port: int, ssh_user: str, 
                 ssh_key_file: str, local_port: int = 3307, 
                 remote_host: str = 'localhost', remote_port: int = 3306):
        """
        Inicializar configurações SSH tunnel.
        
        Args:
            ssh_host: Servidor SSH (ex: ssh.dominios.pt)
            ssh_port: Porta SSH (22)
            ssh_user: Username SSH (ex: artnshin)
            ssh_key_file: Caminho para chave privada SSH
            local_port: Porta local para tunnel (3307)
            remote_host: Host MySQL no servidor remoto (localhost)
            remote_port: Porta MySQL remota (3306)
        """
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port  
        self.ssh_user = ssh_user
        self.ssh_key_file = Path(ssh_key_file).expanduser()
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.tunnel_process: Optional[subprocess.Popen] = None
        
    def is_tunnel_active(self) -> bool:
        """Verifica se o tunnel SSH está ativo"""
        try:
            # Tentar conexão na porta local
            connection = pymysql.connect(
                host='localhost',
                port=self.local_port,
                connect_timeout=2
            )
            connection.close()
            return True
        except:
            return False
    
    def start_tunnel(self) -> Tuple[bool, str]:
        """
        Inicia tunnel SSH.
        
        Returns:
            Tuple (success, message)
        """
        try:
            # Verificar se já existe
            if self.is_tunnel_active():
                return True, f"SSH tunnel já ativo na porta {self.local_port}"
            
            # Verificar chave SSH
            if not self.ssh_key_file.exists():
                return False, f"Chave SSH não encontrada: {self.ssh_key_file}"
            
            # Comando SSH tunnel
            cmd = [
                'ssh',
                '-i', str(self.ssh_key_file),
                '-f',  # Background
                '-N',  # No remote command
                '-L', f'{self.local_port}:{self.remote_host}:{self.remote_port}',
                '-p', str(self.ssh_port),
                f'{self.ssh_user}@{self.ssh_host}',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'ServerAliveInterval=60',
                '-o', 'ServerAliveCountMax=3'
            ]
            
            logger.info(f"Iniciando SSH tunnel: {' '.join(cmd)}")
            
            # Executar comando
            self.tunnel_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Aguardar tunnel ficar ativo
            for i in range(10):  # Tentar 10 vezes (10 segundos)
                time.sleep(1)
                if self.is_tunnel_active():
                    logger.info(f"SSH tunnel ativo na porta {self.local_port}")
                    return True, f"SSH tunnel estabelecido na porta {self.local_port}"
            
            return False, "Timeout - tunnel não estabelecido em 10 segundos"
            
        except Exception as e:
            logger.error(f"Erro ao iniciar SSH tunnel: {e}")
            return False, f"Erro SSH tunnel: {str(e)}"
    
    def stop_tunnel(self) -> Tuple[bool, str]:
        """
        Para tunnel SSH.
        
        Returns:
            Tuple (success, message)
        """
        try:
            # Matar processos SSH tunnel ativos
            cmd = f"pkill -f 'ssh.*-L {self.local_port}:{self.remote_host}:{self.remote_port}'"
            os.system(cmd)
            
            if self.tunnel_process:
                self.tunnel_process.terminate()
                self.tunnel_process = None
            
            return True, "SSH tunnel terminado"
            
        except Exception as e:
            logger.error(f"Erro ao parar SSH tunnel: {e}")
            return False, f"Erro ao parar tunnel: {str(e)}"
    
    def test_mysql_connection(self, mysql_user: str, mysql_password: str, 
                            mysql_database: str) -> Tuple[bool, str]:
        """
        Testa conexão MySQL através do tunnel.
        
        Args:
            mysql_user: Username MySQL
            mysql_password: Password MySQL
            mysql_database: Nome da base de dados
            
        Returns:
            Tuple (success, message)
        """
        try:
            connection = pymysql.connect(
                host='localhost',
                port=self.local_port,
                user=mysql_user,
                password=mysql_password,
                database=mysql_database,
                connect_timeout=10
            )
            
            # Testar query simples
            cursor = connection.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if result and result[0] == 1:
                return True, f"Conexão MySQL OK via tunnel porta {self.local_port}"
            else:
                return False, "Query teste falhou"
                
        except Exception as e:
            return False, f"Erro MySQL: {str(e)}"


def create_ssh_tunnel_from_config(config) -> Optional[SSHTunnelManager]:
    """
    Cria SSH tunnel baseado na configuração.
    
    Args:
        config: Objeto de configuração Flask
        
    Returns:
        SSHTunnelManager ou None se não necessário
    """
    if not getattr(config, 'SSH_TUNNEL_REQUIRED', False):
        return None
    
    return SSHTunnelManager(
        ssh_host=config.SSH_HOST,
        ssh_port=config.SSH_PORT,
        ssh_user=config.SSH_USER,
        ssh_key_file=config.SSH_KEY_FILE,
        local_port=config.MYSQL_LOCAL_PORT,
        remote_host=config.MYSQL_REMOTE_HOST,
        remote_port=config.MYSQL_REMOTE_PORT
    )


def setup_ssh_tunnel_if_needed(app):
    """
    Configura SSH tunnel automaticamente se necessário.
    
    Args:
        app: Aplicação Flask
    """
    tunnel = create_ssh_tunnel_from_config(app.config)
    
    if tunnel:
        success, message = tunnel.start_tunnel()
        if success:
            app.logger.info(f"SSH tunnel estabelecido: {message}")
            
            # Armazenar tunnel no app para cleanup posterior
            app.ssh_tunnel = tunnel
            
            # Test MySQL connection
            mysql_url = app.config['SQLALCHEMY_DATABASE_URI']
            # Parse connection details for testing
            # mysql+pymysql://user:pass@host:port/db
            import re
            match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@[^:]+:\d+/(.+)', mysql_url)
            if match:
                mysql_user, mysql_password, mysql_db = match.groups()
                # URL decode password
                import urllib.parse
                mysql_password = urllib.parse.unquote(mysql_password)
                
                success, msg = tunnel.test_mysql_connection(mysql_user, mysql_password, mysql_db)
                if success:
                    app.logger.info(f"MySQL connection test: {msg}")
                else:
                    app.logger.error(f"MySQL connection failed: {msg}")
        else:
            app.logger.error(f"Falha ao estabelecer SSH tunnel: {message}")
            raise Exception(f"SSH tunnel necessário mas falhou: {message}")


# Cleanup function para registrar no app teardown
def cleanup_ssh_tunnel(app):
    """Limpa SSH tunnel ao parar aplicação"""
    if hasattr(app, 'ssh_tunnel') and app.ssh_tunnel:
        success, message = app.ssh_tunnel.stop_tunnel()
        app.logger.info(f"SSH tunnel cleanup: {message}")
```

### **C. Criar `.env.local` (Novo Ficheiro):**
```bash
# SendCraft - Configuração Local (SQLite)
FLASK_ENV=local
FLASK_DEBUG=1
SECRET_KEY=sendcraft-local-dev-key-123

# Database Local (SQLite)
DATABASE_URL=sqlite:///sendcraft_local.db

# SendCraft Settings
DEFAULT_FROM_NAME=SendCraft Local
ENCRYPTION_KEY=local-dev-32-chars-encryption-key!

# API Settings (generosos para dev)
API_RATE_LIMIT=10000/hour
API_KEY_REQUIRED=false

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=sendcraft_local.log
```

### **D. Criar `.env.development` (Novo Ficheiro):**
```bash
# SendCraft - Configuração Development (SSH Tunnel → dominios.pt)
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=sendcraft-dev-key-change-in-prod

# SSH Tunnel para MySQL Remoto
MYSQL_URL=mysql+pymysql://artnshin_sendcraft:g>bxZmj%25=JZt9Z%2Ci@localhost:3307/artnshin_sendcraft

# SSH Configuration
SSH_HOST=ssh.dominios.pt
SSH_PORT=22
SSH_USER=artnshin
SSH_KEY_FILE=~/.ssh/dominios_pt

# SendCraft Settings
DEFAULT_FROM_NAME=SendCraft Development
ENCRYPTION_KEY=sendcraft-dev-32-chars-key-change!!

# API Settings
API_RATE_LIMIT=5000/hour
API_KEY_REQUIRED=false

# Logging
LOG_LEVEL=INFO
LOG_FILE=sendcraft_dev.log
```

### **E. Modificar `sendcraft/__init__.py` (Adicionar SSH Tunnel):**
```python
"""
SendCraft Application Factory com SSH Tunnel Support
"""
import os
from flask import Flask
from typing import Optional

from .extensions import db, mail, cors
from .utils.logging import setup_logging
from .utils.ssh_tunnel import setup_ssh_tunnel_if_needed, cleanup_ssh_tunnel


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Factory function para criar instância SendCraft com SSH tunnel support.
    
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
    
    # Setup SSH tunnel se necessário (ANTES de init extensions)
    setup_ssh_tunnel_if_needed(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup logging
    setup_logging(app)
    
    # CLI commands
    register_commands(app)
    
    # Register cleanup
    register_cleanup(app)
    
    # Log startup
    app.logger.info(f'SendCraft iniciado em modo {config_name}')
    
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
    
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    app.register_blueprint(web_bp)
    
    # Error handlers
    from .api.errors import register_error_handlers
    register_error_handlers(app)


def register_commands(app: Flask) -> None:
    """Registra comandos CLI"""
    from .cli import (
        init_db_command,
        create_admin_command,
        test_smtp_command,
        clean_logs_command,
        seed_local_data_command  # NOVO
    )
    
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(test_smtp_command)
    app.cli.add_command(clean_logs_command)
    app.cli.add_command(seed_local_data_command)


def register_cleanup(app: Flask) -> None:
    """Registra cleanup handlers"""
    
    @app.teardown_appcontext
    def cleanup_ssh_on_shutdown(error):
        """Cleanup SSH tunnel ao parar app"""
        cleanup_ssh_tunnel(app)
    
    # Signal handlers para graceful shutdown
    import signal
    
    def signal_handler(signum, frame):
        cleanup_ssh_tunnel(app)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
```

### **F. Atualizar `requirements.txt` (Adicionar SSH):**
```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Mail==0.9.1
Flask-CORS==4.0.0
PyJWT==2.8.0
cryptography==41.0.7
python-dotenv==1.0.0
alembic==1.12.1
click==8.1.7
email-validator==2.1.0
pytest==7.4.3
pytest-flask==1.3.0
PyMySQL==1.0.2

# SSH Tunnel Support (NOVO)
paramiko==3.3.1
sshtunnel==0.4.0
```