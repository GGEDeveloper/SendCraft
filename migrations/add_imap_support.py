"""Add IMAP support to SendCraft

This migration adds IMAP fields to email_accounts table and creates the email_inbox table.

Revision ID: add_imap_support_001
Create Date: 2025-10-21
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


def upgrade():
    """Add IMAP support tables and columns."""
    
    # Add IMAP columns to email_accounts table
    with op.batch_alter_table('email_accounts') as batch_op:
        batch_op.add_column(sa.Column('imap_server', sa.String(200), server_default='mail.alitools.pt'))
        batch_op.add_column(sa.Column('imap_port', sa.Integer(), server_default='993'))
        batch_op.add_column(sa.Column('imap_use_ssl', sa.Boolean(), server_default=sa.true()))
        batch_op.add_column(sa.Column('imap_use_tls', sa.Boolean(), server_default=sa.false()))
        batch_op.add_column(sa.Column('last_sync', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('auto_sync_enabled', sa.Boolean(), server_default=sa.true()))
        batch_op.add_column(sa.Column('sync_interval_minutes', sa.Integer(), server_default='5'))
    
    # Create email_inbox table
    op.create_table('email_inbox',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow),
        
        # Relacionamento com conta
        sa.Column('account_id', sa.Integer(), sa.ForeignKey('email_accounts.id'), nullable=False),
        
        # Identificadores únicos
        sa.Column('message_id', sa.String(500), index=True),
        sa.Column('uid', sa.String(100)),
        
        # Endereços
        sa.Column('from_address', sa.String(200), nullable=False, index=True),
        sa.Column('from_name', sa.String(200)),
        sa.Column('to_address', sa.Text()),
        sa.Column('cc_addresses', sa.Text()),
        sa.Column('bcc_addresses', sa.Text()),
        sa.Column('reply_to', sa.String(200)),
        
        # Conteúdo
        sa.Column('subject', sa.String(500), index=True),
        sa.Column('body_text', sa.Text()),
        sa.Column('body_html', sa.Text()),
        
        # Timestamps
        sa.Column('received_at', sa.DateTime(), nullable=False, index=True, default=datetime.utcnow),
        
        # Status
        sa.Column('is_read', sa.Boolean(), nullable=False, default=False, index=True),
        sa.Column('is_flagged', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_answered', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_draft', sa.Boolean(), nullable=False, default=False),
        
        # Anexos
        sa.Column('has_attachments', sa.Boolean(), nullable=False, default=False, index=True),
        sa.Column('attachments_json', sa.Text()),
        sa.Column('attachment_count', sa.Integer(), default=0),
        
        # Metadados
        sa.Column('raw_headers', sa.Text()),
        sa.Column('size_bytes', sa.Integer(), default=0),
        
        # Threading
        sa.Column('thread_id', sa.String(200), index=True),
        sa.Column('in_reply_to', sa.String(500)),
        sa.Column('references', sa.Text()),
        
        # Organização
        sa.Column('folder', sa.String(100), default='INBOX', index=True),
        sa.Column('labels', sa.Text()),
        sa.Column('priority', sa.Integer(), default=3)
    )
    
    # Create composite indexes for performance
    op.create_index('idx_account_received', 'email_inbox', ['account_id', 'received_at'])
    op.create_index('idx_account_folder', 'email_inbox', ['account_id', 'folder'])
    op.create_index('idx_account_read', 'email_inbox', ['account_id', 'is_read'])
    op.create_index('idx_account_thread', 'email_inbox', ['account_id', 'thread_id'])
    op.create_index('idx_message_unique', 'email_inbox', ['account_id', 'message_id'], unique=True)


def downgrade():
    """Remove IMAP support."""
    
    # Drop email_inbox table and indexes
    op.drop_index('idx_message_unique', 'email_inbox')
    op.drop_index('idx_account_thread', 'email_inbox')
    op.drop_index('idx_account_read', 'email_inbox')
    op.drop_index('idx_account_folder', 'email_inbox')
    op.drop_index('idx_account_received', 'email_inbox')
    op.drop_table('email_inbox')
    
    # Remove IMAP columns from email_accounts table
    with op.batch_alter_table('email_accounts') as batch_op:
        batch_op.drop_column('imap_server')
        batch_op.drop_column('imap_port')
        batch_op.drop_column('imap_use_ssl')
        batch_op.drop_column('imap_use_tls')
        batch_op.drop_column('last_sync')
        batch_op.drop_column('auto_sync_enabled')
        batch_op.drop_column('sync_interval_minutes')