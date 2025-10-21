# 🧪 TEST SUITE COMPLETA - SendCraft Email Manager

## 📋 **VALIDAÇÃO FINAL SISTEMA ANTES FASE API**

Este documento contém **todos os testes necessários** para validar completamente o SendCraft Email Manager antes de avançar para a fase de desenvolvimento da API.

---

## 🚀 **SETUP INICIAL TESTING**

### **Pré-requisitos:**
```bash
# No diretório SendCraft com branch atualizado
git status  # Verificar branch: cursor/implement-modular-config-with-remote-mysql-access-42e8
source venv/bin/activate
pip list | grep -i pymysql  # Deve mostrar PyMySQL 1.0.2
```

### **Verificar MySQL Remoto:**
```bash
# Testar conexão BD (deve funcionar)
mysql -h artnshine.pt -u artnshin_sendcraft -p artnshin_sendcraft -e "SHOW TABLES;"
# Password: g>bxZmj%=JZt9Z,i
```

### **Arrancar Sistema:**
```bash
# Executar desenvolvimento 
python run_dev.py

# Output esperado:
# ✅ Remote MySQL connection OK
# ✅ SendCraft Development Ready!
# 🌐 Web Interface: http://localhost:5000
```

---

## 🌐 **TESTE 1: INTERFACE WEB BÁSICA**

### **1.1 Dashboard Principal**
```bash
# URL: http://localhost:5000/
```

**✅ Validar:**
- [ ] Página carrega sem erro 500
- [ ] Layout Bootstrap profissional 
- [ ] Navigation bar com: Dashboard, Domains, Accounts, Templates, Logs
- [ ] 4 KPI Cards visíveis (mesmo com valores 0)
- [ ] Charts area presente (Chart.js carregado)
- [ ] Footer SendCraft presente
- [ ] Mobile responsive (testar redimensionar)

### **1.2 Navigation Menu**
```bash
# Testar cada link do menu
```

**✅ Validar:**
- [ ] Dashboard link → http://localhost:5000/
- [ ] Domains link → http://localhost:5000/domains  
- [ ] Accounts link → http://localhost:5000/accounts
- [ ] Templates link → http://localhost:5000/templates
- [ ] Logs link → http://localhost:5000/logs
- [ ] Todos carregam sem erro 404/500

---

## 📊 **TESTE 2: CRUD DOMAINS**

### **2.1 Lista Domains**
```bash
# URL: http://localhost:5000/domains
```

**✅ Validar:**
- [ ] Página carrega (pode estar vazia)
- [ ] Tabela Bootstrap com colunas: Name, Description, Active, Actions
- [ ] Botão "Add New Domain" visível
- [ ] Search box presente (mesmo que não funcional)
- [ ] Message "No domains found" se vazio

### **2.2 Criar Domain**
```bash
# Clicar "Add New Domain" → http://localhost:5000/domains/new
```

**✅ Validar:**
- [ ] Form carrega sem erro
- [ ] Campos: Name, Description, Active (checkbox)
- [ ] Botões: Save, Cancel
- [ ] Validation: Name obrigatório
- [ ] **CRIAR DOMAIN TESTE**: "teste.com" + description "Domain para testes"

### **2.3 Editar Domain**
```bash
# Se domain criado, clicar "Edit" 
```

**✅ Validar:**
- [ ] Form carrega com dados preenchidos
- [ ] Campos editáveis
- [ ] Botão Update funcional
- [ ] **EDITAR**: Alterar description para "Domain editado"

### **2.4 Toggle Active**
```bash
# Toggle switch/button domain ativo/inativo
```

**✅ Validar:**
- [ ] Toggle visual muda estado
- [ ] Estado persiste após refresh
- [ ] Badge status atualiza

### **2.5 Delete Domain**
```bash
# Botão Delete → Confirmation modal
```

**✅ Validar:**
- [ ] Modal confirmação aparece
- [ ] Botões: Cancel, Delete
- [ ] **NÃO APAGAR** domain teste ainda (usar para outros testes)

---

## 📧 **TESTE 3: CRUD ACCOUNTS**

### **3.1 Lista Accounts**
```bash
# URL: http://localhost:5000/accounts
```

**✅ Validar:**
- [ ] Tabela: Email, Domain, SMTP Server, Status, Actions
- [ ] Botão "Add New Account"
- [ ] Status badges coloridos

### **3.2 Criar Account**
```bash
# Clicar "Add New Account" → http://localhost:5000/accounts/new
```

**✅ Validar:**
- [ ] Form campos: Email Address, Domain (dropdown), Display Name
- [ ] SMTP settings: Server, Port, Username, Password, Use TLS
- [ ] **CRIAR ACCOUNT TESTE**: "teste@teste.com" com SMTP Gmail

### **3.3 Testar SMTP (se implementado)**
```bash
# Botão "Test SMTP" na lista accounts
```

**✅ Validar:**
- [ ] Loading spinner durante teste
- [ ] Resultado: Success/Error message
- [ ] Toast notification aparece

### **3.4 Editar/Delete Account**
```bash
# Botões Edit/Delete account criada
```

**✅ Validar:**
- [ ] Edit carrega form preenchido
- [ ] Delete pede confirmação

---

## 📝 **TESTE 4: CRUD TEMPLATES**

### **4.1 Lista Templates**
```bash
# URL: http://localhost:5000/templates
```

**✅ Validar:**
- [ ] Tabela: Name, Subject, Type, Created, Actions  
- [ ] Botão "Add New Template"
- [ ] Categories/filters (se implementado)

### **4.2 Criar Template**
```bash
# Clicar "Add New Template"
```

**✅ Validar:**
- [ ] Form campos: Name, Subject, Type (dropdown)
- [ ] HTML content editor (textarea grande)
- [ ] Variables help/info
- [ ] **CRIAR TEMPLATE**: "Welcome Email" com HTML simples

### **4.3 Editor HTML**
```bash
# No form template, área HTML content
```

**✅ Validar:**
- [ ] Textarea grande para HTML
- [ ] Syntax highlighting (se implementado)
- [ ] Preview area (se implementado)
- [ ] Variables placeholders info

### **4.4 Edit/Delete Template**
```bash
# Actions na lista templates
```

**✅ Validar:**
- [ ] Edit preserva conteúdo HTML
- [ ] Delete confirmação modal

---

## 📋 **TESTE 5: LOGS INTERFACE**

### **5.1 Lista Logs**
```bash
# URL: http://localhost:5000/logs
```

**✅ Validar:**
- [ ] Tabela: Date, From, To, Subject, Status, Actions
- [ ] Status badges: Sent (green), Failed (red), etc.
- [ ] Message "No logs found" se vazio
- [ ] Botão "View" para cada log

### **5.2 Log Detail**
```bash
# Clicar "View" num log (se existir)
```

**✅ Validar:**
- [ ] Página detail carrega
- [ ] Info completa log: From, To, Subject, Status, Dates
- [ ] Error message area (se failed)
- [ ] Botão "Back to Logs"

---

## 🔧 **TESTE 6: FUNCIONALIDADES TÉCNICAS**

### **6.1 API Endpoints**
```bash
# Testar endpoints API via curl
curl http://localhost:5000/api/v1/health
curl http://localhost:5000/api/stats
curl http://localhost:5000/api/stats?days=7
```

**✅ Validar:**
- [ ] `/api/v1/health` → status 200, {"status": "healthy"}
- [ ] `/api/stats` → JSON com contadores
- [ ] Headers Content-Type: application/json

### **6.2 Static Files**
```bash
# Verificar assets carregam
curl -I http://localhost:5000/static/css/app.css
curl -I http://localhost:5000/static/js/app.js
```

**✅ Validar:**
- [ ] CSS file: status 200
- [ ] JS file: status 200  
- [ ] No 404 errors console F12

### **6.3 Database Operations**
```bash
# Via MySQL client verificar dados criados
mysql -h artnshine.pt -u artnshin_sendcraft -p artnshin_sendcraft -e "
SELECT COUNT(*) FROM domains;
SELECT COUNT(*) FROM email_accounts;  
SELECT COUNT(*) FROM email_templates;
"
```

**✅ Validar:**
- [ ] Domain teste aparece na BD
- [ ] Account teste aparece na BD
- [ ] Template teste aparece na BD

---

## 🎨 **TESTE 7: UX/UI QUALIDADE**

### **7.1 Design Responsivo**
```bash
# Browser F12 → Device toolbar → Mobile/Tablet views
```

**✅ Validar:**
- [ ] Layout adapta mobile (< 768px)
- [ ] Navigation hamburger menu mobile
- [ ] Tables scroll horizontal mobile
- [ ] Botões tamanho adequado touch
- [ ] Cards dashboard empilham mobile

### **7.2 JavaScript Interactions**
```bash
# F12 Console → verificar erros JavaScript
```

**✅ Validar:**
- [ ] No errors console JavaScript
- [ ] Modals open/close funcionam
- [ ] Form validations client-side
- [ ] AJAX calls success (Network tab)
- [ ] Loading states visíveis

### **7.3 Visual Polish**
```bash
# Avaliar qualidade visual geral
```

**✅ Validar:**
- [ ] Color scheme consistente
- [ ] Icons apropriados
- [ ] Spacing/padding adequados  
- [ ] Typography legível
- [ ] Professional appearance

---

## 🚀 **TESTE 8: PERFORMANCE**

### **8.1 Load Times**
```bash
# F12 Network tab → Hard refresh (Ctrl+Shift+R)
```

**✅ Validar:**
- [ ] Dashboard load < 3 segundos
- [ ] CRUD pages load < 2 segundos
- [ ] MySQL queries < 1 segundo
- [ ] Static assets cache properly

### **8.2 MySQL Remote Performance**
```bash
# Monitor query times
```

**✅ Validar:**
- [ ] Connection pool funcionando
- [ ] No timeout errors
- [ ] Queries efficient (no N+1)
- [ ] Error handling graceful

---

## 🔒 **TESTE 9: SECURITY & RELIABILITY**

### **9.1 Form Security**
```bash
# Testar inputs maliciosos
```

**✅ Validar:**
- [ ] CSRF tokens forms (se implementado)
- [ ] Input sanitization básica  
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] XSS protection templates

### **9.2 Error Handling**
```bash
# Forçar erros para testar handling
```

**✅ Validar:**
- [ ] 404 pages custom (se implementado)
- [ ] 500 errors graceful 
- [ ] MySQL connection errors handled
- [ ] Form validation errors displayed

---

## 📊 **RESUMO FINAL TESTING**

### **✅ COMPLETAR CHECKLIST:**

#### **Backend (Core):**
- [ ] Python run_dev.py arranca sem erro
- [ ] MySQL remoto conecta consistently  
- [ ] Flask routes todas funcionais
- [ ] Models/Database operations OK
- [ ] Config system modular funciona

#### **Frontend (Interface):**
- [ ] Dashboard profissional carrega
- [ ] Navigation 5 páginas funcional
- [ ] CRUD operations todas funcionam  
- [ ] Templates Bootstrap responsive
- [ ] JavaScript sem erros console

#### **Integration (Full Stack):**
- [ ] Forms submetem para backend
- [ ] Database persiste dados via interface
- [ ] API endpoints funcionais
- [ ] Static assets servem correctly
- [ ] Error handling graceful

#### **Quality (Professional):**
- [ ] Visual design professional quality
- [ ] UX intuitivo e smooth
- [ ] Performance adequate (< 3s loads)
- [ ] Mobile responsive
- [ ] No broken links/404s

### **🎯 CRITÉRIOS SUCESSO FINAL:**
- **Mínimo**: 80% checks ✅ (interface funcional básica)
- **Target**: 90% checks ✅ (sistema professional)  
- **Ideal**: 95% checks ✅ (production ready)

---

## 🔄 **AFTER TESTING - PRÓXIMOS PASSOS**

### **Se Testing Pass (>80% ✅):**
→ **Sistema ready para Fase API Development**
→ Confirmar com [translate:✅ PRONTO PARA FASE API]

### **Se Issues Found (<80% ✅):**
→ Documentar issues específicos
→ Quick fixes necessários before API phase

---

## 📝 **TESTING REPORT TEMPLATE**

```markdown
# SendCraft Testing Report - [DATE]

## Overall Results: ✅ [X]/[Y] checks passed ([Z]%)

### ✅ Working Features:
- Dashboard loads and displays correctly
- [lista features funcionais]

### ❌ Issues Found:
1. **[Issue Title]**
   - Problem: [description]
   - Impact: [high/medium/low]
   - Fix needed: [quick/complex]

### 🎯 Recommendation:
[READY FOR API PHASE] / [NEEDS FIXES FIRST]
```

**Execute todos os testes acima e documenta os resultados. Quando tiveres >80% success rate, confirma e avançamos para a fase API!** 🚀