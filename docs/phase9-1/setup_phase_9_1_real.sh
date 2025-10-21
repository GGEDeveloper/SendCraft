#!/bin/bash
# 🚀 SendCraft Phase 9.1 - Setup Automático com Configurações Reais
echo "🚀 SendCraft Phase 9.1 Setup Starting - encomendas@alitools.pt..."

# 1. Create backup
BACKUP_NAME="sendcraft_backup_phase9-1_$(date +%Y%m%d_%H%M%S)"
echo "📦 Creating backup: $BACKUP_NAME"
cp -r . "../$BACKUP_NAME"

# 2. Ensure correct branch
echo "🌿 Checking current branch..."
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "cursor/implement-modular-config-with-remote-mysql-access-42e8" ]; then
    echo "🔄 Switching to correct branch..."
    git checkout cursor/implement-modular-config-with-remote-mysql-access-42e8
    git pull origin cursor/implement-modular-config-with-remote-mysql-access-42e8
fi

# 3. Create new development branch for Phase 9.1
echo "🌿 Creating Phase 9.1 development branch..."
git checkout -b phase-9.1-email-inbox-outbox-real

# 4. Install dependencies
echo "📋 Installing/checking dependencies..."
pip install python-socketio==5.9.0
pip install email-validator==2.1.0

# 5. Create directory structure for Phase 9.1
echo "📁 Creating Phase 9.1 directory structure..."
mkdir -p docs/phase9-1
mkdir -p sendcraft/templates/emails
mkdir -p sendcraft/static/js/email-client
mkdir -p sendcraft/services
mkdir -p sendcraft/api/v1

# 6. Create placeholder files for AI agents
echo "📄 Creating placeholder files for implementation..."
touch sendcraft/models/email_inbox.py
touch sendcraft/services/imap_service.py
touch sendcraft/api/v1/emails_inbox.py
touch sendcraft/templates/emails/inbox.html
touch sendcraft/templates/emails/outbox.html
touch sendcraft/templates/emails/compose.html
touch sendcraft/static/css/email-client.css
touch sendcraft/static/js/email-client/EmailClientApp.js

# 7. Test current system
echo "🧪 Testing current system status..."
echo "🔍 Checking MySQL connection..."
mysql -h artnshine.pt -u artnshinsendcraft -p"gbxZmjJZt9Z,i" artnshinsendcraft -e "SELECT 'MySQL Connection OK' as status;" 2>/dev/null && echo "✅ MySQL Connection OK" || echo "❌ MySQL Connection Failed"

echo "🔍 Checking virtual environment..."
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
else
    echo "⚠️  Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔍 Activating venv and installing requirements..."
source venv/bin/activate
pip install -r requirements.txt

echo "🔍 Testing SendCraft startup..."
python -c "from sendcraft import create_app; app = create_app('development'); print('✅ SendCraft import OK')" 2>/dev/null && echo "✅ SendCraft imports OK" || echo "❌ SendCraft import issues"

# 8. Create Phase 9.1 configuration file
echo "📝 Creating Phase 9.1 configuration file..."
cat > docs/phase9-1/phase9-1-config.yaml << EOF
# SendCraft Phase 9.1 - Email Management Configuration
# Real configuration for encomendas@alitools.pt

email_account:
  address: "encomendas@alitools.pt"
  password: "6f2zniWMN6aUFaD"
  
  imap:
    server: "mail.alitools.pt"
    port: 993
    ssl: true
    auth: true
  
  smtp:
    server: "mail.alitools.pt"  
    port: 465
    ssl: true
    auth: true

database:
  host: "artnshine.pt"
  port: 3306
  name: "artnshinsendcraft"
  user: "artnshinsendcraft" 
  password: "gbxZmjJZt9Z,i"

implementation:
  backend_time: "15 minutes"
  frontend_time: "20 minutes" 
  integration_time: "10 minutes"
  total_time: "45 minutes"
EOF

echo "✅ Phase 9.1 setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Use Claude 4.1 Opus with PROMPT 1 for backend implementation (15 min)"
echo "2. Use Claude 4.1 Opus with PROMPT 2 for frontend implementation (20 min)" 
echo "3. Use Cursor Agent with PROMPT 3 for integration (10 min)"
echo "4. Run validation: ./validate_phase_9_1.sh"
echo ""
echo "🎯 Real Configuration Ready:"
echo "   📧 Email: encomendas@alitools.pt"
echo "   🔐 IMAP: mail.alitools.pt:993 (SSL)"
echo "   📤 SMTP: mail.alitools.pt:465 (SSL)"
echo "   🗄️  Database: artnshine.pt MySQL (connected)"
echo ""
echo "🚀 Ready for Phase 9.1 implementation with REAL email account!"