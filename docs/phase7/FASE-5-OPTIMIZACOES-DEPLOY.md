# 🎯 FASE 5: OPTIMIZAÇÕES E DEPLOY

## 📋 **OBJETIVO**
Finalizar optimizações performance, criar modo production e preparar deploy no servidor dominios.pt.

---

## 🔧 **AÇÕES DO UTILIZADOR**

### **5.1. Optimizações Performance Local**
```bash
# Testar performance development mode
# Verificar tempos resposta MySQL remoto
# Identificar queries lentas ou N+1 problems

# Executar com logging SQL ativo:
python3 -c "
import os
os.environ['SQLALCHEMY_ECHO'] = 'True'
exec(open('run_dev.py').read())
"
```

### **5.2. Criar .env.production Completo**
```bash
# Criar ficheiro production config
cat > .env.production << 'EOF'
# SendCraft - Configuração Production (Servidor dominios.pt)
FLASK_ENV=production
SECRET_KEY=sendcraft-production-secret-key-super-secure-change-this-2024
DEBUG=False

# MySQL local no servidor (localhost quando em dominios.pt)
MYSQL_URL=mysql+pymysql://artnshin_sendcraft:g>bxZmj%25=JZt9Z%2Ci@localhost:3306/artnshin_sendcraft

# SendCraft Settings
DEFAULT_FROM_NAME=SendCraft Email Manager
ENCRYPTION_KEY=sendcraft-production-32-chars-key-very-secure!!
ENCRYPTION_ALGORITHM=AES

# API Production
API_RATE_LIMIT=1000/hour
API_KEY_REQUIRED=false

# Security Production
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
WTF_CSRF_ENABLED=true

# Logging Production
LOG_LEVEL=WARNING
LOG_FILE=/tmp/sendcraft_production.log

# Performance
SQLALCHEMY_POOL_SIZE=5
SQLALCHEMY_POOL_TIMEOUT=30
SQLALCHEMY_POOL_RECYCLE=3600
EOF
```

### **5.3. Criar Script Production**
```bash
# Criar run_production.py
cat > run_production.py << 'EOF'
#!/usr/bin/env python3
"""SendCraft Production Mode"""
import os
import sys

def main():
    print("🚀 SendCraft Production Mode (MySQL localhost)")
    print("=" * 50)
    
    os.environ['FLASK_ENV'] = 'production'
    
    # Validar ambiente production
    required_vars = ['SECRET_KEY', 'ENCRYPTION_KEY', 'MYSQL_URL']
    for var in required_vars:
        if not os.environ.get(var):
            print(f"❌ Missing required env var: {var}")
            sys.exit(1)
    
    print("✅ Production environment validated")
    
    from sendcraft import create_app
    app = create_app('production')
    
    print("✅ SendCraft Production Ready!")
    print("🌐 Interface: http://email.artnshine.pt:9000")
    print("🗄️ Database: MySQL localhost")
    print("=" * 50)
    
    # Production server (Gunicorn recommended)
    app.run(host='0.0.0.0', port=9000, debug=False)

if __name__ == '__main__':
    main()
EOF

chmod +x run_production.py
```

---

## 🚀 **DEPLOY NO SERVIDOR DOMINIOS.PT**

### **5.1. Upload Código para Servidor**
```bash
# Via git (recomendado)
# No servidor dominios.pt:
cd ~/public_html/
git clone https://github.com/GGEDeveloper/SendCraft.git sendcraft
cd sendcraft
git checkout cursor/implement-modular-config-with-remote-mysql-access-42e8
```

### **5.2. Setup Ambiente Servidor**
```bash
# No servidor dominios.pt (via terminal cPanel)
cd ~/public_html/sendcraft

# Criar virtual environment Python
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### **5.3. Configurar Production**
```bash
# Copiar .env.production para servidor
# Ou criar diretamente no servidor:
nano .env.production
# (colar conteúdo do ficheiro .env.production criado)

# Verificar conexão MySQL local servidor
mysql -h localhost -u artnshin_sendcraft -p artnshin_sendcraft -e "SHOW TABLES;"
```

### **5.4. Testar Production**
```bash
# Teste inicial produção
python run_production.py

# Se funciona, aceder: http://email.artnshine.pt:9000
```

---

## 🤖 **PROMPT AGENTE AI - OPTIMIZAÇÕES FINAIS**

```
# SendCraft - Optimizações Performance e Production

## Contexto:
- Repo: https://github.com/GGEDeveloper/SendCraft
- Branch: cursor/implement-modular-config-with-remote-mysql-access-42e8
- Status: Interface funcional, deploy ready
- Objetivo: Optimizar performance + production hardening

## Tarefas Optimização:

### 1. DATABASE PERFORMANCE
- Index optimization models (domain.name, account.email_address)
- Connection pooling ajustar para production
- Query optimization (eager loading relacionamentos)
- Database migrations sistema (flask db commands)

### 2. CACHING LAYER
- Flask-Caching implementation
- Cache dashboard stats (TTL 5 minutos)
- Cache template rendering
- Cache SMTP test results temporarily

### 3. SECURITY HARDENING
- Input sanitization all forms
- CSRF protection todas routes
- SQL injection prevention (já SQLAlchemy ORM)
- XSS prevention templates
- Rate limiting API endpoints

### 4. LOGGING & MONITORING
- Structured logging (JSON format)
- Error tracking (email notifications)
- Performance monitoring (slow queries log)
- Health check endpoint detalhado

### 5. PRODUCTION DEPLOYMENT
- Gunicorn WSGI server config
- Nginx reverse proxy config (se disponível)
- Systemd service file SendCraft
- Backup/restore scripts database

### 6. TESTING SUITE
- Unit tests models básicos
- Integration tests API endpoints
- Functional tests interface web
- pytest configuration

## Prioridade:
1. Database indexes (CRÍTICO performance)
2. Security hardening (CRÍTICO segurança)  
3. Caching dashboard (melhoria UX)
4. Logging structured (debugging)
5. Production deployment (deploy)
6. Testing suite (qualidade)

## Critério Sucesso:
✅ Dashboard load time < 2 segundos
✅ Forms submission < 1 segundo
✅ All inputs sanitized
✅ Production deploy funcional
✅ Error handling graceful
✅ Basic tests coverage 60%+
```

---

## 📊 **VALIDAÇÃO FINAL**

### **Performance Benchmarks:**
```bash
# Teste carga dashboard (local)
time curl -s http://localhost:5000/ > /dev/null

# Teste CRUD operations
time curl -s -X POST http://localhost:5000/api/v1/domains \
  -H "Content-Type: application/json" \
  -d '{"name":"test.com","description":"Test"}'

# Resultado esperado: < 2s responses
```

### **Security Check:**
```bash
# Verificar HTTPS headers (production)
curl -I http://email.artnshine.pt:9000/

# Verificar CSRF protection
# Tentar POST sem CSRF token deve falhar
```

---

## ✅ **CRITÉRIOS SUCESSO FASE 5**
- ✅ Performance optimizada (< 2s page loads)
- ✅ Production mode funcional
- ✅ Deploy servidor dominios.pt OK
- ✅ Security hardening implementado
- ✅ Monitoring/logging ativo
- ✅ Basic testing suite

---

## 🎉 **FASE FINAL**
Sistema SendCraft completo e em produção!

### **URLs Finais:**
- **Development**: http://localhost:5000 (MySQL remoto)
- **Production**: http://email.artnshine.pt:9000 (MySQL local)

### **Comandos Execução:**
- Local Development: `python run_dev.py`
- Production Server: `python run_production.py`