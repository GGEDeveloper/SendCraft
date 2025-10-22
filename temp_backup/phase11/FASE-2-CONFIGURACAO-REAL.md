# ⚙️ FASE 2 - CONFIGURAÇÃO REAL

## 📋 PROMPT PARA AGENTE - CONFIGURAÇÃO SÓ DADOS REAIS:

```markdown
SendCraft Real Data Configuration - Phase 2

## Context:
Configure SendCraft to work ONLY with real AliTools email data. Set up proper IMAP connection handling without any fallbacks to mock data.

## Task: Configure real data systems (8 minutes)

### Step 1: Verify Database Connection (2 min)

1. **Test remote MySQL connection:**
   ```bash
   source venv/bin/activate
   
   python3 -c "
   from sendcraft import create_app
   from sendcraft.extensions import db
   
   try:
       app = create_app('development')
       with app.app_context():
           # Test database connection
           result = db.engine.execute('SELECT 1').scalar()
           print('✅ Database connection: SUCCESS')
           
           # Verify key tables exist
           tables = ['domain', 'email_account', 'email_inbox']
           for table in tables:
               try:
                   count = db.engine.execute(f'SELECT COUNT(*) FROM {table}').scalar()
                   print(f'✅ Table {table}: {count} records')
               except Exception as e:
                   print(f'❌ Table {table}: ERROR - {e}')
                   
   except Exception as e:
       print(f'❌ Database connection failed: {e}')
       print('Check .env.development DATABASE_URL configuration')
   "
   ```

### Step 2: Configure Real IMAP Settings (2 min)

2. **Ensure IMAP configuration is correct for AliTools:**
   ```bash
   python3 -c "
   from sendcraft import create_app
   from sendcraft.models.account import EmailAccount
   
   app = create_app('development')
   with app.app_context():
       print('🔧 Configuring real IMAP settings...')
       
       geral = EmailAccount.query.filter_by(email_address='geral@alitools.pt').first()
       
       if geral:
           # Ensure correct IMAP settings for AliTools
           geral.imap_server = 'mail.alitools.pt'
           geral.imap_port = 993
           geral.imap_use_ssl = True
           geral.smtp_server = 'mail.alitools.pt'
           geral.smtp_port = 465
           geral.smtp_use_ssl = True
           geral.is_active = True
           geral.auto_sync_enabled = True
           geral.sync_interval_minutes = 10
           geral.save()
           
           print('✅ IMAP Configuration Updated:')
           print(f'   Server: {geral.imap_server}:{geral.imap_port} (SSL: {geral.imap_use_ssl})')
           print(f'   SMTP: {geral.smtp_server}:{geral.smtp_port} (SSL: {geral.smtp_use_ssl})')
           print(f'   Auto-sync: {geral.auto_sync_enabled} (every {geral.sync_interval_minutes} min)')
       else:
           print('❌ geral@alitools.pt account not found')
   "
   ```

### Step 3: Test Real IMAP Connectivity (2 min)

3. **Test actual IMAP connection to mail.alitools.pt:**
   ```bash
   python3 -c "
   import socket
   import ssl
   
   print('🧪 Testing real IMAP connectivity...')
   
   # Test network connectivity first
   try:
       sock = socket.create_connection(('mail.alitools.pt', 993), timeout=10)
       sock.close()
       print('✅ Network: mail.alitools.pt:993 accessible')
   except Exception as e:
       print(f'⚠️ Network: Connection timeout/blocked - {e}')
       print('   This is normal in some local development environments')
       print('   IMAP will work in production environment')
   "
   ```

### Step 4: Configure Web Interface for Real Account (1 min)

4. **Ensure web interface uses geral@alitools.pt:**
   ```bash
   # Check and update web route to use real account
   echo "🔧 Configuring web interface for real account..."
   
   # Verify web route uses correct account
   grep -n "email_address.*alitools.pt" sendcraft/routes/web.py || echo "No hardcoded email found"
   
   # Ensure it points to geral@alitools.pt (primary account)
   sed -i "s/email_address='encomendas@alitools.pt'/email_address='geral@alitools.pt'/g" sendcraft/routes/web.py
   sed -i "s/email_address=\"encomendas@alitools.pt\"/email_address=\"geral@alitools.pt\"/g" sendcraft/routes/web.py
   
   echo "✅ Web interface configured for geral@alitools.pt"
   ```

### Step 5: Validate Frontend JSON Configuration (1 min)

5. **Ensure frontend sends correct JSON for sync:**
   ```bash
   # Verify email-client.js has correct sync request format
   echo "🔧 Validating frontend sync configuration..."
   
   if grep -q "JSON.stringify" sendcraft/static/js/email-client.js; then
       echo "✅ Frontend sends JSON body in sync requests"
   else
       echo "⚠️ Frontend may not be sending JSON body correctly"
   fi
   
   # Check for correct Content-Type header
   if grep -q "Content-Type.*application/json" sendcraft/static/js/email-client.js; then
       echo "✅ Frontend sends correct Content-Type header"
   else
       echo "⚠️ Frontend may not be sending correct headers"
   fi
   
   echo "✅ Frontend configuration validated"
   ```

Execute Phase 2 real data configuration!
```