"""
Modelos de dados do SendCraft.
Exporta todos os modelos para fácil importação.
"""
from .base import BaseModel, TimestampMixin, init_db
from .domain import Domain
from .account import EmailAccount
from .template import EmailTemplate
from .log import EmailLog, EmailStatus
from .email_inbox import EmailInbox

__all__ = [
    'BaseModel',
    'TimestampMixin',
    'init_db',
    'Domain',
    'EmailAccount', 
    'EmailTemplate',
    'EmailLog',
    'EmailStatus',
    'EmailInbox'
]