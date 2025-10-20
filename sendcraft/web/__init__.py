"""
Web Interface Blueprint.
Define as rotas para a interface web do SendCraft.
"""
from flask import Blueprint

# Criar blueprint
web_bp = Blueprint('web', __name__)

# Importar rotas
from . import dashboard, domains, templates_routes, accounts, logs