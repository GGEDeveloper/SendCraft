"""
Migration: Add API fields to email_accounts table
Date: 2025-10-23
Phase: 14C
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sendcraft import create_app
from sendcraft.extensions import db
from sqlalchemy import text, inspect

def upgrade():
    """Add API fields to email_accounts table"""
    app = create_app()
    
    with app.app_context():
        # Check if columns already exist
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('email_accounts')]
        
        conn = db.engine.connect()
        
        try:
            if 'api_enabled' not in columns:
                conn.execute(text('ALTER TABLE email_accounts ADD COLUMN api_enabled BOOLEAN DEFAULT FALSE NOT NULL'))
                print('✅ Added api_enabled column')
            
            if 'api_key_hash' not in columns:
                conn.execute(text('ALTER TABLE email_accounts ADD COLUMN api_key_hash VARCHAR(128)'))
                print('✅ Added api_key_hash column')
            
            if 'api_created_at' not in columns:
                conn.execute(text('ALTER TABLE email_accounts ADD COLUMN api_created_at DATETIME'))
                print('✅ Added api_created_at column')
            
            if 'api_last_used_at' not in columns:
                conn.execute(text('ALTER TABLE email_accounts ADD COLUMN api_last_used_at DATETIME'))
                print('✅ Added api_last_used_at column')
            
            conn.commit()
            print('✅ Migration completed successfully')
            
        except Exception as e:
            conn.rollback()
            print(f'❌ Migration error: {e}')
            raise
        finally:
            conn.close()

if __name__ == '__main__':
    upgrade()

