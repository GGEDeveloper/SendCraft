# 🚀 **FILES-TO-CREATE.md**

## 📁 **Ficheiros Obrigatórios Phase 12**

### **Criar todos estes ficheiros com conteúdo exacto:**

---

## 1️⃣ **app.py** (root do projeto)

```python
#!/usr/bin/env python3
"""
SendCraft Production Entry Point
cPanel Python App entry point for email.artnshine.pt
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def application(environ, start_response):
    """WSGI application entry point for cPanel Passenger"""
    from sendcraft import create_app
    
    # Force production environment
    os.environ['FLASK_ENV'] = 'production'
    
    # Create Flask app in production mode
    app = create_app('production')
    
    return app(environ, start_response)

if __name__ == '__main__':
    """Direct run for testing (não usar em produção)"""
    from sendcraft import create_app
    
    os.environ['FLASK_ENV'] = 'production'
    app = create_app('production')
    
    print("🚀 SendCraft Production Mode")
    print("🌐 Running on https://email.artnshine.pt")
    
    # Run on all interfaces for cPanel
    app.run(host='0.0.0.0', port=5000, debug=False)
```

---

## 2️⃣ **passenger_wsgi.py** (root do projeto)

```python
#!/usr/bin/env python3
"""
SendCraft Passenger WSGI Entry Point
Auto-generated entry point for cPanel Passenger WSGI
Compatible with cPanel Python App deployment
"""
import os
import sys
from pathlib import Path

# Add project to Python path for imports
project_path = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_path))

# Set production environment
os.environ['FLASK_ENV'] = 'production'

# Import WSGI application from app.py
from app import application

# Passenger WSGI expects 'application' callable
# This is automatically used by cPanel Passenger

# Optional: Direct run for debugging
if __name__ == '__main__':
    """Test WSGI application locally (debug only)"""
    from sendcraft import create_app
    
    app = create_app('production')
    print("🧪 Testing Passenger WSGI...")
    print("🌐 Production: https://email.artnshine.pt")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
```

---

## 3️⃣ **instance/config.py** (nova pasta)

```python
"""
SendCraft Instance Configuration
Production secrets and sensitive settings
NÃO COMMITIR SENHAS REAIS - este é template
"""

# Production Security Keys (MUDAR EM PRODUÇÃO!)
SECRET_KEY = 'sendcraft-production-secret-key-32-characters-change-this!'
ENCRYPTION_KEY = 'sendcraft-encrypt-key-32-chars-change-production!'

# API Authentication (se necessário)
API_KEY_REQUIRED = True
API_KEYS = {
    'admin': 'sendcraft-admin-api-key-2024-change-me',
    'service': 'sendcraft-service-api-key-2024-change-me',
    'sync': 'sendcraft-sync-api-key-2024-change-me'
}

# Production MySQL Override (opcional - usa config.py default se não definido)
# MYSQL_URL = 'mysql+pymysql://artnshin_sendcraft:SENHA_REAL@localhost:3306/artnshin_sendcraft'

# Email Configuration Production
DEFAULT_FROM_NAME = 'SendCraft Email Manager'  
DEFAULT_FROM_EMAIL = 'noreply@artnshine.pt'
ADMIN_EMAIL = 'admin@artnshine.pt'

# Production Feature Flags
FEATURE_REAL_SMTP_ENABLED = True
FEATURE_AUTO_SYNC_ENABLED = True
FEATURE_LOGGING_ENHANCED = True

# Rate Limiting Production
API_RATE_LIMIT = '2000/hour'  # Mais permissivo em produção
WEB_RATE_LIMIT = '500/hour'

# Security Production
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True  
SESSION_COOKIE_SAMESITE = 'Lax'
WTF_CSRF_ENABLED = True

# Logging Production
LOG_LEVEL = 'INFO'
LOG_FILE = '/home/artnshin/logs/sendcraft.log'

# Custom Production Settings
PRODUCTION_MODE = True
DEBUG_TOOLBAR = False
SQLALCHEMY_ECHO = False  # Não mostrar SQL em produção
```

---

## 4️⃣ **.cpanel.yml** (substituir o existente)

```yaml
---
deployment:
  tasks:
    # Deploy files
    - export DEPLOYPATH=/home/artnshin/public_html/sendcraft
    - /bin/cp -R * $DEPLOYPATH
    
    # Install dependencies
    - cd $DEPLOYPATH
    - /home/artnshin/virtualenv/public_html/sendcraft/3.9/bin/pip install -r requirements.txt
    
    # Set permissions  
    - chmod +x $DEPLOYPATH/app.py
    - chmod +x $DEPLOYPATH/passenger_wsgi.py
    
    # Create logs directory
    - mkdir -p /home/artnshin/logs
    
    # Restart Python app (opcional)
    - touch $DEPLOYPATH/tmp/restart.txt
```

---

## 5️⃣ **requirements.txt** (substituir o existente)

```txt
# Flask Core
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Mail==0.9.1
Flask-CORS==4.0.0
Flask-Migrate==4.0.5
Werkzeug==2.3.7

# Security & Auth
PyJWT==2.8.0
cryptography==41.0.7

# Configuration
python-dotenv==1.0.0

# Database
alembic==1.12.1
PyMySQL==1.0.2

# Utilities
click==8.1.7
email-validator==2.1.0
chardet==5.2.0

# WebSocket (se necessário)
python-socketio==5.10.0

# Testing (development only)
pytest==7.4.3
pytest-flask==1.3.0

# Production WSGI (adicionar se necessário)
# gunicorn==20.1.0
```

---

## 6️⃣ **Alteração em run_dev.py** (manter compatibilidade)

**ADICIONAR no início do ficheiro (após imports):**

```python
# Compatibility check - only run if not in production
if os.environ.get('FLASK_ENV') == 'production':
    print("❌ run_dev.py não deve ser usado em produção!")
    print("✅ Use app.py ou passenger_wsgi.py para produção")
    sys.exit(1)
```

---

## ✅ **Validação dos Ficheiros:**

### **Teste Local (antes commit):**
```bash
# Verificar ficheiros criados
ls -la app.py passenger_wsgi.py
ls -la instance/config.py  
ls -la .cpanel.yml

# Teste importação
python3 -c "from app import application; print('✅ app.py OK')"
python3 -c "from passenger_wsgi import application; print('✅ passenger_wsgi.py OK')"

# Teste configuração
python3 -c "
import os
os.environ['FLASK_ENV'] = 'production'
from sendcraft import create_app
app = create_app('production')
print('✅ Production config OK')
"
```

### **Estrutura Final:**
```
SendCraft/
├── ✅ app.py              # Production entry point
├── ✅ passenger_wsgi.py   # WSGI entry point
├── ✅ instance/
│   └── ✅ config.py       # Production secrets
├── ✅ .cpanel.yml         # Complete deployment
├── ✅ requirements.txt    # All dependencies  
├── ✅ run_dev.py          # Development (unchanged)
└── ✅ sendcraft/...       # Existing code
```

---

## 🚀 **Próximos Passos:**

1. **Criar todos ficheiros** com conteúdo exacto acima
2. **Testar localmente** antes commit
3. **Git commit + push** 
4. **Seguir** `DEPLOY-INSTRUCTIONS.md`

**Todos estes ficheiros são obrigatórios para deploy produção funcionar!** ✅