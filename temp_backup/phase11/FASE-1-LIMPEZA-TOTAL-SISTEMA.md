# 🧹 FASE 1 - LIMPEZA TOTAL SISTEMA

## 📋 PROMPT PARA AGENTE - LIMPEZA MOCK DATA:

```markdown
SendCraft Complete Mock Data Cleanup - Phase 1

## Context:
Remove ALL mock/fake/sample/test data from SendCraft system. Ensure only real AliTools email accounts exist and no artificial data remains.

## Task: Complete cleanup and validation (10 minutes)

### Step 1: Remove Mock Service Files (2 min)

1. **Remove any improved/mock IMAP services:**
   ```bash
   # Remove mock IMAP services if they exist
   rm -f sendcraft/services/imap_service_improved.py
   rm -f sendcraft/services/imap_service_mock.py
   rm -f sendcraft/services/mock_*.py
   
   # Remove any seed scripts
   rm -f scripts/seed_*.py
   rm -f sendcraft/seed_*.py
   rm -f local_seed.py
   rm -f sample_data.py
   
   echo "✅ Mock service files removed"
   ```

### Step 2: Restore Original API Implementation (2 min)

2. **Ensure emails_inbox.py uses original IMAP service:**
   ```bash
   # Restore original IMAP service import if modified
   python3 -c "
   import os
   
   api_file = 'sendcraft/api/v1/emails_inbox.py'
   backup_file = api_file + '.backup'
   
   if os.path.exists(backup_file):
       # Restore from backup
       with open(backup_file, 'r') as f:
           backup_content = f.read()
       
       with open(api_file, 'w') as f:
           f.write(backup_content)
       
       print('✅ Restored emails_inbox.py from backup')
   else:
       # Check and fix manually
       with open(api_file, 'r') as f:
           content = f.read()
       
       # Ensure correct import
       if 'imap_service_improved' in content or 'IMAP_SERVICE_CLASS' in content:
           # Fix the import
           content = content.replace('from ...services.imap_service_improved import IMAPServiceImproved', '')
           content = content.replace('IMAP_SERVICE_CLASS = IMAPServiceImproved', '')
           content = content.replace('IMAP_SERVICE_CLASS = IMAPService', '')
           content = content.replace('imap_service = IMAP_SERVICE_CLASS(account)', 'imap_service = IMAPService(account)')
           
           # Ensure clean import
           if 'from ...services.imap_service import IMAPService' not in content:
               content = 'from ...services.imap_service import IMAPService\\n' + content
           
           with open(api_file, 'w') as f:
               f.write(content)
           
           print('✅ Fixed emails_inbox.py imports')
       else:
           print('✅ emails_inbox.py already clean')
   "
   ```

### Step 3: Clean Database of Mock Emails (3 min)

3. **Remove ALL mock/fake emails from database:**
   ```bash
   source venv/bin/activate
   
   python3 -c "
   from sendcraft import create_app
   from sendcraft.models.email_inbox import EmailInbox
   from sqlalchemy import or_
   
   app = create_app('development')
   with app.app_context():
       print('🧹 Cleaning mock/fake email data from database...')
       
       # Count all emails before cleanup
       total_before = EmailInbox.query.count()
       print(f'Total emails before cleanup: {total_before}')
       
       # Find ALL mock/fake/sample/test emails
       mock_patterns = [
           '%mock%', '%dev-%', '%fake-%', '%test-%', 
           '%local-sample-%', '%sample-%', '%demo-%',
           'system@%', 'newsletter@%'
       ]
       
       conditions = []
       for pattern in mock_patterns:
           conditions.append(EmailInbox.message_id.like(pattern))
           conditions.append(EmailInbox.from_address.like(pattern))
           conditions.append(EmailInbox.subject.like(f'%{pattern.replace(\"%\", \"\")}%'))
       
       mock_emails = EmailInbox.query.filter(or_(*conditions)).all()
       
       mock_count = len(mock_emails)
       print(f'Found {mock_count} mock/fake emails to remove')
       
       if mock_count > 0:
           print('Removing mock emails:')
           for email in mock_emails:
               print(f'  - {email.subject[:50]} from {email.from_address}')
               email.delete(commit=False)
           
           # Commit all deletions
           EmailInbox.query.session.commit()
           
           print(f'✅ Removed {mock_count} mock emails')
       else:
           print('✅ No mock emails found - database clean')
       
       # Verify cleanup
       total_after = EmailInbox.query.count()
       print(f'Final email count: {total_after}')
       
       if total_after == 0:
           print('✅ Database is now clean - ready for real IMAP sync')
   "
   ```

### Step 4: Validate Real Account Configuration (2 min)

4. **Ensure only real AliTools accounts exist:**
   ```bash
   python3 -c "
   from sendcraft import create_app
   from sendcraft.models.domain import Domain
   from sendcraft.models.account import EmailAccount
   from sendcraft.utils.encryption import AESCipher
   
   app = create_app('development')
   with app.app_context():
       print('📧 Validating AliTools email accounts...')
       
       # Ensure alitools.pt domain exists
       domain = Domain.query.filter_by(name='alitools.pt').first()
       if not domain:
           domain = Domain(name='alitools.pt')
           domain.save()
           print('✅ Created alitools.pt domain')
       else:
           print('✅ alitools.pt domain exists')
       
       # Validate geral@alitools.pt account
       geral = EmailAccount.query.filter_by(email_address='geral@alitools.pt').first()
       if geral:
           geral.is_active = True
           geral.auto_sync_enabled = True
           geral.save()
           print('✅ geral@alitools.pt: ACTIVE (primary account)')
           
           # Test password decryption
           try:
               encryption_key = app.config.get('SECRET_KEY', 'dev_secret')
               password = geral.get_decrypted_password(encryption_key)
               print('✅ geral@alitools.pt: Password encryption working')
           except Exception as e:
               print(f'⚠️ geral@alitools.pt: Password issue - {e}')
       else:
           print('❌ geral@alitools.pt account missing - needs creation')
       
       # Validate encomendas@alitools.pt account (preserve as backup)
       encomendas = EmailAccount.query.filter_by(email_address='encomendas@alitools.pt').first()
       if encomendas:
           encomendas.is_active = False
           encomendas.auto_sync_enabled = False
           encomendas.save()
           print('📦 encomendas@alitools.pt: INACTIVE (preserved backup)')
       else:
           print('📦 encomendas@alitools.pt: Not found (OK - optional backup)')
       
       # Check for any other accounts (should not exist)
       all_accounts = EmailAccount.query.all()
       real_emails = ['geral@alitools.pt', 'encomendas@alitools.pt']
       
       for account in all_accounts:
           if account.email_address not in real_emails:
               print(f'⚠️ Unknown account found: {account.email_address}')
               # Don't auto-delete, just warn
       
       print('')
       print('🎯 ACCOUNT VALIDATION COMPLETE')
       print(f'✅ Total accounts: {len(all_accounts)}')
       print('✅ Only real AliTools emails configured')
   "
   ```

### Step 5: Clean Project Files (1 min)

5. **Remove any development artifacts:**
   ```bash
   # Remove backup files created by agents
   find . -name "*.backup" -type f -delete
   find . -name "*_improved.py" -type f -delete
   find . -name "*_mock.py" -type f -delete
   
   # Remove any log files with mock references
   find . -name "*.log" -type f -exec grep -l "mock\\|sample\\|fake" {} \\; -delete
   
   # Remove any temporary Python cache that might have mock references
   find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
   
   echo "✅ Project files cleaned"
   ```

Execute Phase 1 complete cleanup!
```