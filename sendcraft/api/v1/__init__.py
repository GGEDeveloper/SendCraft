"""
API v1 Blueprint.
Define os endpoints da API RESTful versão 1.
"""
from flask import Blueprint

# Criar blueprint
api_v1_bp = Blueprint('api_v1', __name__)

# Importar rotas (serão implementadas na FASE 3)
# from . import send, accounts, templates, logs