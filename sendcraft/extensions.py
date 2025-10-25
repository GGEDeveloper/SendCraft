"""
Inicialização de extensões Flask.
Centraliza a criação de extensões para evitar circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_cors import CORS
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
cors = CORS()
migrate = Migrate()