#!/usr/bin/env python3
"""
Test script for SendCraft IMAP implementation.
Tests all IMAP backend functionality.
"""
import os
import sys
import json
import requests
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment
os.environ['FLASK_ENV'] = 'development'

from sendcraft import create_app
from sendcraft.models import EmailAccount, EmailInbox, Domain
from sendcraft.services.imap_service import IMAPService
from sendcraft.extensions import db

# Create app context
app = create_app('development')


def test_database_migration():
    """Test that database migration was applied correctly."""
    print("\n" + "="*50)
    print("1. Testing Database Migration")
    print("="*50)
    
    with app.app_context():
        try:
            # Check if IMAP columns exist in email_accounts
            from sqlalchemy import inspect
            
            inspector = inspect(db.engine)
            
            # Check email_accounts columns
            account_columns = [col['name'] for col in inspector.get_columns('email_accounts')]
            required_columns = [
                'imap_server', 'imap_port', 'imap_use_ssl', 
                'imap_use_tls', 'last_sync', 'auto_sync_enabled', 
                'sync_interval_minutes'
            ]
            
            missing_columns = [col for col in required_columns if col not in account_columns]
            if missing_columns:
                print(f"❌ Missing columns in email_accounts: {missing_columns}")
                print("   Run: mysql < /workspace/migrations/add_imap_support.sql")
                return False
            else:
                print("✅ All IMAP columns exist in email_accounts table")
            
            # Check if email_inbox table exists
            if 'email_inbox' not in inspector.get_table_names():
                print("❌ email_inbox table does not exist")
                print("   Run: mysql < /workspace/migrations/add_imap_support.sql")
                return False
            else:
                print("✅ email_inbox table exists")
                
                # Check email_inbox columns
                inbox_columns = [col['name'] for col in inspector.get_columns('email_inbox')]
                required_inbox_columns = [
                    'id', 'account_id', 'message_id', 'from_address',
                    'subject', 'body_text', 'received_at', 'is_read'
                ]
                
                missing_inbox_columns = [col for col in required_inbox_columns if col not in inbox_columns]
                if missing_inbox_columns:
                    print(f"❌ Missing columns in email_inbox: {missing_inbox_columns}")
                    return False
                else:
                    print("✅ All required columns exist in email_inbox table")
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking database: {e}")
            return False


def test_seed_account():
    """Test seeding the encomendas@alitools.pt account."""
    print("\n" + "="*50)
    print("2. Testing Account Seeding")
    print("="*50)
    
    with app.app_context():
        try:
            from sendcraft.cli.seed_imap_account import seed_alitools_imap_account
            
            # Seed account
            account = seed_alitools_imap_account(force=False)
            
            if account:
                print(f"✅ Account seeded: {account.email_address}")
                print(f"   SMTP: {account.smtp_server}:{account.smtp_port}")
                print(f"   IMAP: {account.imap_server}:{account.imap_port}")
                print(f"   Auto Sync: {account.auto_sync_enabled}")
                return account
            else:
                print("❌ Failed to seed account")
                return None
                
        except Exception as e:
            print(f"❌ Error seeding account: {e}")
            return None


def test_imap_connection(account):
    """Test IMAP connection."""
    print("\n" + "="*50)
    print("3. Testing IMAP Connection")
    print("="*50)
    
    with app.app_context():
        try:
            imap_service = IMAPService(account)
            
            # Get config
            encryption_key = app.config.get('SECRET_KEY', '')
            config = account.get_imap_config(encryption_key)
            
            # Connect
            print(f"Connecting to {config['server']}:{config['port']}...")
            if imap_service.connect(config):
                print("✅ Successfully connected to IMAP server")
                
                # List folders
                folders = imap_service.list_folders()
                print(f"✅ Available folders: {folders[:5]}...")  # Show first 5
                
                # Select INBOX
                success, num_messages = imap_service.select_folder('INBOX')
                if success:
                    print(f"✅ INBOX has {num_messages} messages")
                
                # Fetch a few emails
                recent_emails = imap_service.fetch_recent_emails(limit=3)
                print(f"✅ Fetched {len(recent_emails)} recent emails:")
                for email in recent_emails:
                    print(f"   - {email.get('from_address')}: {email.get('subject', '(no subject)')[:50]}")
                
                # Disconnect
                imap_service.disconnect()
                return True
            else:
                print("❌ Failed to connect to IMAP server")
                return False
                
        except Exception as e:
            print(f"❌ Error testing IMAP connection: {e}")
            return False


def test_email_sync(account):
    """Test email synchronization."""
    print("\n" + "="*50)
    print("4. Testing Email Synchronization")
    print("="*50)
    
    with app.app_context():
        try:
            imap_service = IMAPService(account)
            
            print("Syncing emails from IMAP server...")
            synced_count = imap_service.sync_account_emails(
                account=account,
                folder='INBOX',
                limit=10,
                since_last_sync=False
            )
            
            print(f"✅ Synced {synced_count} emails to database")
            
            # Check database
            total_emails = EmailInbox.query.filter_by(account_id=account.id).count()
            unread_emails = EmailInbox.query.filter_by(
                account_id=account.id,
                is_read=False
            ).count()
            
            print(f"✅ Database stats:")
            print(f"   - Total emails: {total_emails}")
            print(f"   - Unread emails: {unread_emails}")
            print(f"   - Last sync: {account.last_sync}")
            
            return synced_count > 0
            
        except Exception as e:
            print(f"❌ Error syncing emails: {e}")
            return False


def test_api_endpoints(account_id):
    """Test API endpoints."""
    print("\n" + "="*50)
    print("5. Testing API Endpoints")
    print("="*50)
    
    # Start test server in background
    import threading
    import time
    
    def run_server():
        app.run(port=5000, debug=False, use_reloader=False)
    
    # Start server thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # Wait for server to start
    
    base_url = "http://localhost:5000/api/v1"
    
    tests = [
        {
            "name": "List inbox emails",
            "method": "GET",
            "url": f"{base_url}/inbox/{account_id}",
            "params": {"page": 1, "per_page": 10}
        },
        {
            "name": "Get inbox stats",
            "method": "GET",
            "url": f"{base_url}/inbox/{account_id}/stats"
        },
        {
            "name": "Sync emails",
            "method": "POST",
            "url": f"{base_url}/inbox/sync/{account_id}",
            "json": {"limit": 5}
        }
    ]
    
    all_passed = True
    
    for test in tests:
        try:
            if test["method"] == "GET":
                response = requests.get(
                    test["url"], 
                    params=test.get("params", {})
                )
            else:
                response = requests.post(
                    test["url"],
                    json=test.get("json", {})
                )
            
            if response.status_code == 200:
                print(f"✅ {test['name']}: OK")
                # Show sample response
                data = response.json()
                if 'emails' in data and data['emails']:
                    print(f"   Found {len(data['emails'])} emails")
                elif 'stats' in data:
                    print(f"   Stats: {data['stats']}")
            else:
                print(f"❌ {test['name']}: {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {test['name']}: {e}")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("SendCraft IMAP Implementation Test Suite")
    print("="*50)
    
    # Test 1: Database Migration
    if not test_database_migration():
        print("\n⚠️  Please run the database migration first:")
        print("mysql -h artnshine.pt -P 3306 -u artnshinsendcraft -p artnshinsendcraft < /workspace/migrations/add_imap_support.sql")
        return
    
    # Test 2: Seed Account
    account = test_seed_account()
    if not account:
        print("\n❌ Account seeding failed. Cannot continue tests.")
        return
    
    # Test 3: IMAP Connection
    if not test_imap_connection(account):
        print("\n❌ IMAP connection failed. Check credentials and server settings.")
        return
    
    # Test 4: Email Sync
    if not test_email_sync(account):
        print("\n⚠️  Email sync had issues but continuing...")
    
    # Test 5: API Endpoints
    with app.app_context():
        if test_api_endpoints(account.id):
            print("\n✅ All API endpoints working")
        else:
            print("\n⚠️  Some API endpoints had issues")
    
    print("\n" + "="*50)
    print("✅ IMAP Implementation Test Complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Run the migration if not done: mysql < /workspace/migrations/add_imap_support.sql")
    print("2. Use Flask CLI: flask seed-imap --test --sync 50")
    print("3. Test API: curl http://localhost:5000/api/v1/inbox/1")


if __name__ == '__main__':
    main()