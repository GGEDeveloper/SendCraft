# 🤖 **FASE 1 - AGENTE AI: Estrutura Base e Modelos**

**Repositório:** https://github.com/GGEDeveloper/SendCraft.git  
**Objetivo:** Criar estrutura modular e sistema de base de dados  
**Tecnologia:** Python 3.9+, Flask, SQLAlchemy, SQLite  

---

## 🎯 **INSTRUÇÕES PARA EXECUÇÃO**

Você é um agente AI experiente em Python/Flask. Sua tarefa é implementar a **FASE 1** do SendCraft - Email Manager com arquitetura modular e de alta qualidade.

### **REQUISITOS TÉCNICOS:**
- Código modular e bem documentado
- Type hints em todas as funções
- Docstrings no formato Google Style
- Tratamento de erros robusto
- Logging estruturado
- Configuração flexível via environment/instance config

---

## 🗂️ **ESTRUTURA A CRIAR**

```
sendcraft/
├── app.py                    # Entry point principal
├── requirements.txt          # Dependências
├── config.py                # Configuração base
├── wsgi.py                  # WSGI entry point para produção
├── .env.example             # Template de variáveis ambiente
├── .gitignore               # Git ignore apropriado
├── README.md                # Documentação inicial
│
├── instance/                # Configurações sensíveis (não commitar)
│   └── config.py.example   # Template de config
│
├── sendcraft/               # Package principal
│   ├── __init__.py         # Factory pattern app
│   ├── extensions.py       # Inicialização de extensões
│   ├── cli.py             # Comandos CLI personalizados
│   │
│   ├── models/            # Modelos de dados
│   │   ├── __init__.py
│   │   ├── base.py        # Base model e mixins
│   │   ├── domain.py      # Domain model
│   │   ├── account.py     # EmailAccount model  
│   │   ├── template.py    # EmailTemplate model
│   │   └── log.py         # EmailLog model
│   │
│   ├── services/          # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── smtp_service.py    # Serviço SMTP
│   │   ├── email_service.py   # Serviço de envio
│   │   ├── template_service.py # Serviço de templates
│   │   └── auth_service.py    # Autenticação API
│   │
│   ├── api/               # Endpoints API
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── send.py    # Endpoints de envio
│   │   │   ├── accounts.py # Gestão contas
│   │   │   ├── templates.py # Gestão templates
│   │   │   └── logs.py    # Logs e estatísticas
│   │   └── errors.py      # Error handlers
│   │
│   ├── web/               # Interface web
│   │   ├── __init__.py
│   │   ├── dashboard.py   # Dashboard routes
│   │   ├── domains.py     # Gestão domínios
│   │   └── templates.py   # Gestão templates web
│   │
│   └── utils/             # Utilitários
│       ├── __init__.py
│       ├── crypto.py      # Encriptação/decriptação
│       ├── validators.py  # Validadores
│       ├── logging.py     # Configuração logging
│       └── helpers.py     # Funções auxiliares
│
├── templates/             # Templates Jinja2
│   ├── base.html
│   ├── dashboard.html
│   └── components/
│       ├── navbar.html
│       └── alerts.html
│
├── static/               # Assets estáticos
│   ├── css/
│   │   └── app.css
│   ├── js/
│   │   └── app.js
│   └── img/
│
└── tests/                # Testes unitários
    ├── __init__.py
    ├── conftest.py       # Configuração pytest
    ├── test_models.py
    ├── test_services.py
    └── test_api.py
```

---

## 📝 **TAREFAS ESPECÍFICAS**

### **1. SETUP INICIAL**

Criar repositório e estrutura base:

```bash
# 1. Clonar repositório
git clone https://github.com/GGEDeveloper/SendCraft.git
cd SendCraft

# 2. Criar estrutura de diretórios
mkdir -p sendcraft/{models,services,api/v1,web,utils}
mkdir -p templates/components static/{css,js,img} tests instance

# 3. Inicializar __init__.py files
find sendcraft -type d -exec touch {}/__init__.py \;
find tests -type d -exec touch {}/__init__.py \;
```

### **2. REQUIREMENTS.TXT**

```python
# Core Framework
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Mail==0.9.1
Flask-CORS==4.0.0

# Security & Auth
PyJWT==2.8.0
cryptography==41.0.7
argon2-cffi==23.1.0

# Configuration & Environment
python-dotenv==1.0.0

# Database
alembic==1.12.1

# Utils
click==8.1.7
email-validator==2.1.0

# Development (optional)
pytest==7.4.3
pytest-flask==1.3.0
```

### **3. CONFIG.PY (Base Configuration)**

```python
\"\"\"
Configuração base da aplicação SendCraft.
Hierarquia: config.py → instance/config.py → environment variables
\"\"\"
import os
from typing import Type

class Config:
    \"\"\"Configuração base.\"\"\"
    
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
    \"\"\"Configuração de desenvolvimento.\"\"\"
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    \"\"\"Configuração de produção.\"\"\"
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    \"\"\"Configuração de testes.\"\"\"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config: dict[str, Type[Config]] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

### **4. SENDCRAFT/__INIT__.PY (Application Factory)**

```python
\"\"\"
SendCraft Application Factory.
Implementa o padrão Factory para criação flexível da aplicação Flask.
\"\"\"
from flask import Flask
from typing import Optional

from .extensions import db, mail, cors
from .utils.logging import setup_logging


def create_app(config_name: Optional[str] = None) -> Flask:
    \"\"\"
    Factory function para criar instância da aplicação SendCraft.
    
    Args:
        config_name: Nome da configuração ('development', 'production', 'testing')
    
    Returns:
        Instância configurada da aplicação Flask
    \"\"\"
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    config_name = config_name or app.config.get('ENV', 'default')
    app.config.from_object(f'config.{config_name}')
    
    # Load instance config (secrets)
    try:
        app.config.from_pyfile('config.py')
    except FileNotFoundError:
        app.logger.warning('Instance config file not found. Using defaults.')
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup logging
    setup_logging(app)
    
    # CLI commands
    register_commands(app)
    
    return app


def init_extensions(app: Flask) -> None:
    \"\"\"Inicializa extensões Flask.\"\"\"
    db.init_app(app)
    mail.init_app(app)
    cors.init_app(app)


def register_blueprints(app: Flask) -> None:
    \"\"\"Registra blueprints da aplicação.\"\"\"
    from .api.v1 import api_v1_bp
    from .web import web_bp
    
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    app.register_blueprint(web_bp)


def register_commands(app: Flask) -> None:
    \"\"\"Registra comandos CLI personalizados.\"\"\"
    from .cli import init_db_command, create_admin_command
    
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
```

### **5. EXTENSIONS.PY**

```python
\"\"\"
Inicialização de extensões Flask.
Centraliza a criação de extensões para evitar circular imports.
\"\"\"
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
cors = CORS()
```

---

## 🗄️ **MODELOS DE DADOS**

### **6. MODELS/BASE.PY**

```python
\"\"\"
Modelo base e mixins para SendCraft.
Fornece funcionalidades comuns para todos os modelos.
\"\"\"
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr

from ..extensions import db


class TimestampMixin:
    \"\"\"Mixin para timestamps automáticos.\"\"\"
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BaseModel(db.Model):
    \"\"\"Modelo base para todos os modelos SendCraft.\"\"\"
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    
    def to_dict(self) -> Dict[str, Any]:
        \"\"\"Converte modelo para dicionário.\"\"\"
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        \"\"\"Atualiza modelo a partir de dicionário.\"\"\"
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def create(cls, **kwargs):
        \"\"\"Cria e salva nova instância.\"\"\"
        instance = cls(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def save(self):
        \"\"\"Salva instância atual.\"\"\"
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        \"\"\"Deleta instância atual.\"\"\"
        db.session.delete(self)
        db.session.commit()


def init_db() -> None:
    \"\"\"Inicializa base de dados criando todas as tabelas.\"\"\"
    from . import domain, account, template, log
    db.create_all()
```

### **7. MODELS/DOMAIN.PY**

```python
\"\"\"Modelo de Domínio para SendCraft.\"\"\"
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from typing import List, Optional

from .base import BaseModel, TimestampMixin


class Domain(BaseModel, TimestampMixin):
    \"\"\"
    Representa um domínio de email (ex: alitools.pt).
    
    Attributes:
        name: Nome do domínio
        is_active: Se o domínio está ativo
        description: Descrição opcional
        spf_record: Registro SPF configurado
        dkim_selector: Seletor DKIM
        accounts: Contas de email associadas
        templates: Templates de email associados
    \"\"\"
    
    __tablename__ = 'domains'
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text)
    spf_record = Column(Text)
    dkim_selector = Column(String(50))
    
    # Relationships
    accounts = relationship('EmailAccount', back_populates='domain', lazy='dynamic')
    templates = relationship('EmailTemplate', back_populates='domain', lazy='dynamic')
    
    def __repr__(self) -> str:
        return f'<Domain {self.name}>'
    
    @classmethod
    def get_by_name(cls, name: str) -> Optional['Domain']:
        \"\"\"Busca domínio por nome.\"\"\"
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def get_active_domains(cls) -> List['Domain']:
        \"\"\"Retorna todos os domínios ativos.\"\"\"
        return cls.query.filter_by(is_active=True).all()
    
    def get_active_accounts(self):
        \"\"\"Retorna contas ativas deste domínio.\"\"\"
        return self.accounts.filter_by(is_active=True)
    
    def get_active_templates(self):
        \"\"\"Retorna templates ativos deste domínio.\"\"\"
        return self.templates.filter_by(is_active=True)
```

---

## ⚡ **PONTO DE CONTROLE**

Após implementar esta fase, execute os testes:

```bash
# Testar imports
python -c "from sendcraft import create_app; print('✅ Import OK')"

# Testar criação de app
python -c "from sendcraft import create_app; app = create_app('testing'); print('✅ App creation OK')"

# Testar modelos
python -c "from sendcraft.models.domain import Domain; print('✅ Models OK')"
```

**CRITÉRIOS DE ACEITAÇÃO:**
- [ ] Estrutura de diretórios criada corretamente
- [ ] Imports funcionam sem erros
- [ ] Application factory cria app successfully
- [ ] Modelos importam corretamente
- [ ] Configuração carrega sem erros

---

## 🔄 **PRÓXIMA FASE**

Quando completar esta fase com sucesso:
1. Fazer commit e push para o repositório
2. Criar tag `v0.1-structure`
3. Reportar status de conclusão
4. Aguardar instruções para **FASE 2: Serviços e APIs**

**Foque na modularidade, documentação e qualidade do código!** 🎯