"""
Modelos de dados do SendCraft.
Exporta todos os modelos para fácil importação.
"""
from .base import BaseModel, TimestampMixin, init_db

# Modelos serão importados na FASE 2
# from .domain import Domain
# from .account import EmailAccount
# from .template import EmailTemplate
# from .log import EmailLog

__all__ = [
    'BaseModel',
    'TimestampMixin',
    'init_db',
    # 'Domain',
    # 'EmailAccount', 
    # 'EmailTemplate',
    # 'EmailLog'
]