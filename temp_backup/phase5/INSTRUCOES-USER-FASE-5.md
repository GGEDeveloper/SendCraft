# 📋 Instruções para o Utilizador - SendCraft Fase 5

## 🎯 **PREPARAÇÃO PRÉ-DESENVOLVIMENTO**

### **1. Verificar Estado Atual do Repositório (5min)**
```bash
# Conectar ao cPanel:
source /home/artnshin/virtualenv/public_html/sendcraft/3.9/bin/activate
cd /home/artnshin/public_html/sendcraft

# Verificar interface existente:
ls -la templates/
ls -la static/

# Verificar se web routes existem:
find . -name "*web*" -o -name "*routes*"

# Testar interface atual (deve dar 404):
curl -s http://localhost:9000/ | head -20
```

### **2. Pull Latest Changes do GitHub (2min)**
```bash
# Verificar remote:
git remote -v

# Pull latest:
git pull origin main

# Verificar templates existentes:
ls -la templates/base.html templates/dashboard.html
```

### **3. Verificar SendCraft Running (1min)**
```bash
# Confirmar processo ativo:
ps aux | grep "app.run.*9000"

# Health check:
curl -s http://localhost:9000/api/v1/health

# Se não estiver a correr:
export FLASK_ENV=production
export MYSQL_URL="mysql+pymysql://artnshin_sendcraft:g>bxZmj%=JZt9Z,i@localhost:3306/artnshin_sendcraft"
nohup python -c "from app import app; app.run(host='0.0.0.0', port=9000)" > sendcraft.log 2>&1 &
```

---

## 🚀 **EXECUÇÃO FASE 5**

### **PASSO 1: Setup Agent AI (2min)**
1. Abrir agent AI (Claude/ChatGPT/Cursor)
2. Usar prompt do ficheiro `PROMPT-AGENT-AI-FASE-5.md`
3. Fornecer contexto do repositório GitHub

### **PASSO 2: Implementação Sequencial (4h)**

#### **Sessão 1: Flask Routes (1.5h)**
- Agent implementa `sendcraft/routes/web.py`
- Testa rotas básicas
- Verifica integração com services

#### **Sessão 2: Templates CRUD (1.5h)**  
- Agent cria templates domínios
- Agent cria templates accounts  
- Agent cria templates templates/logs
- Testa navegação completa

#### **Sessão 3: JavaScript Avançado (1h)**
- Agent expande `static/js/app.js`
- Implementa CRUD via HTMX
- Testa funcionalidades interativas

### **PASSO 3: Testing & Deploy (30min)**
```bash
# Push changes para GitHub:
git add .
git commit -m "feat(phase5): complete web interface implementation"
git push origin main

# Restart SendCraft:
pkill -f "app.run.*9000"
export FLASK_ENV=production
nohup python -c "from app import app; app.run(host='0.0.0.0', port=9000)" > sendcraft.log 2>&1 &

# Testar interface completa:
sleep 5
curl -s http://localhost:9000/ | head -20
echo "🌐 Abrir browser: http://email.artnshine.pt:9000"
```

---

## 🧪 **VALIDAÇÃO PÓS-IMPLEMENTAÇÃO**

### **Checklist Interface Web**
- [ ] Dashboard carrega com dados reais
- [ ] Navegação funciona (sem 404s)
- [ ] Página domínios lista dados MySQL
- [ ] CRUD domínios funciona (criar/editar/eliminar)
- [ ] Página contas lista dados MySQL  
- [ ] CRUD contas funciona
- [ ] Templates editor carrega
- [ ] Logs interface mostra dados
- [ ] Mobile responsive OK
- [ ] Toast notifications funcionam
- [ ] HTMX operations sem erros

### **Comandos de Teste**
```bash
# Testar cada página:
curl -s http://localhost:9000/ | grep "Dashboard"
curl -s http://localhost:9000/domains | grep "Domínios"
curl -s http://localhost:9000/accounts | grep "Contas" 
curl -s http://localhost:9000/templates | grep "Templates"
curl -s http://localhost:9000/logs | grep "Logs"
```

---

## 📋 **PÓS-FASE 5 (OPCIONAIS)**

### **Se Tempo Disponível - Implementar Fases 6-8:**

#### **Fase 6: UX Enhancements (1.5h)**
- Search avançado
- Bulk operations  
- Export functionality
- Real-time features

#### **Fase 7: Design Polish (1h)**
- SendCraft branding refinado
- Dark mode completo
- Custom components
- Animation enhancements

#### **Fase 8: Production Hardening (1h)**
- Error pages customizadas
- Security enhancements
- Performance optimizations
- Monitoring interface

---

## ⚠️ **TROUBLESHOOTING**

### **Se Interface não Carrega**
```bash
# Verificar logs:
tail -20 sendcraft.log

# Verificar imports Python:
python -c "from sendcraft.routes.web import web_bp; print('Web routes OK')"

# Verificar templates:
python -c "from flask import Flask; app = Flask(__name__); app.template_folder = 'templates'; print('Templates OK')"
```

### **Se APIs não Respondem**
```bash
# Restart SendCraft:
pkill -f python.*9000
sleep 2
export FLASK_ENV=production
nohup python -c "from app import app; app.run(host='0.0.0.0', port=9000)" > sendcraft.log 2>&1 &
```

### **Se 404 Errors**
```bash
# Verificar blueprint registration:
grep -r "register_blueprint.*web" sendcraft/

# Verificar route patterns:
grep -r "@web_bp.route" sendcraft/
```

---

## 🎉 **RESULTADO ESPERADO**

Após Fase 5, terás:

**SendCraft Email Manager com interface web enterprise completa:**
- 🏠 Dashboard com KPIs real-time
- 🌐 Gestão de domínios (CRUD completo)
- 📧 Gestão de contas email (CRUD + SMTP test)
- 📝 Editor de templates HTML
- 📊 Interface de logs e estatísticas  
- 📱 Completamente responsivo
- 🎨 Design moderno matching AliTools standards

**URLs Finais:**
- Dashboard: `http://email.artnshine.pt:9000/`
- Domínios: `http://email.artnshine.pt:9000/domains`
- Contas: `http://email.artnshine.pt:9000/accounts`
- Templates: `http://email.artnshine.pt:9000/templates`
- Logs: `http://email.artnshine.pt:9000/logs`

**A plataforma SendCraft estará 100% completa e enterprise-ready! 🚀**