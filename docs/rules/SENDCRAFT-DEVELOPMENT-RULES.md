# 🎯 SENDCRAFT DEVELOPMENT RULES - AGENTE WORKFLOW

## 📋 REGRAS GERAIS DESENVOLVIMENTO AGENTE

### 🚫 **ABSOLUTE PROHIBITIONS:**
- **NEVER create ANY mock/fake/sample/test data** in ANY environment
- **NEVER create improved/mock services** that simulate real functionality
- **NEVER add fallback mechanisms** that generate artificial data
- **NEVER modify database** to add sample/demo/test records
- **NEVER create seed scripts** or data generation utilities
- **NEVER simulate API responses** with fake data
- **NEVER add "for testing purposes" data** to any environment

### ✅ **REQUIRED BEHAVIORS:**
- **Use ONLY real data** from geral@alitools.pt and encomendas@alitools.pt
- **On errors/timeouts**: Return proper HTTP errors (500/504), don't create fake data
- **Frontend validation**: Test interface loading and structure, don't check for data
- **API testing**: Verify endpoints respond correctly, empty results are valid
- **Database operations**: Only work with real accounts and real email data
- **Code validation**: Check file existence and structure, not content simulation

### 🔍 **VALIDATION APPROACH:**
- **Test interface structure** (HTML elements, CSS classes, JS functions) not data
- **Test API responses** (HTTP codes, JSON structure) not specific content
- **Test connectivity** (server starts, endpoints accessible) not mock scenarios
- **Test configuration** (settings correct, accounts configured) not artificial data

### 📝 **REPORTING RULES:**
- **Report what exists** (files, structure, configuration) not what could be simulated
- **Report empty results** as success when no real data available
- **Report errors properly** when real connections fail
- **Report validation** based on system readiness, not mock scenarios

---

## 🔧 **WORKFLOW ESPECÍFICO SENDCRAFT**

### 📧 **EMAIL ACCOUNTS POLICY:**
- **geral@alitools.pt**: PRIMARY account (always ACTIVE)
- **encomendas@alitools.pt**: BACKUP account (INACTIVE but preserved)
- **NO other accounts** unless explicitly real AliTools emails
- **Account testing**: Verify configuration exists, don't simulate usage

### 🗄️ **DATABASE POLICY:**
- **Empty email_inbox table** = SUCCESS (ready for real sync)
- **Only real accounts** in email_account table
- **Domain alitools.pt** must exist
- **No sample/demo/test records** ever

### 🌐 **WEB INTERFACE TESTING:**
- **Test HTML structure** loads correctly
- **Test CSS/JS assets** are accessible
- **Test account display** shows configured account
- **DON'T test with mock emails** or simulate user interactions
- **Empty interface** = SUCCESS (ready for real data)

### 🔗 **API TESTING APPROACH:**
- **Test HTTP 200 responses** on GET endpoints
- **Test JSON structure** in responses (empty arrays OK)
- **Test POST endpoints** accept correct headers/body
- **DON'T create test data** to validate functionality
- **Timeout/errors** = Expected behavior in local development

### 🏗️ **FRONTEND VALIDATION:**
- **Check file existence**: HTML, CSS, JS files present
- **Check structure**: Classes, IDs, functions defined
- **Check configuration**: API endpoints, account settings
- **DON'T check data rendering** or simulate interactions

---

## 🎯 **TASK EXECUTION RULES**

### 📋 **QUANDO TESTAR FUNCIONALIDADE:**
- **Verify files exist** and have correct structure
- **Verify server starts** without errors  
- **Verify endpoints respond** with correct HTTP codes
- **Verify configuration** is properly set
- **DON'T generate data** to test functionality

### ⚠️ **QUANDO REPORTAR SUCCESS:**
- **Empty email list** = SUCCESS (no mock data)
- **IMAP timeout** = EXPECTED (local development limitation)
- **Interface loads** = SUCCESS (even without emails)
- **APIs respond** = SUCCESS (even with empty results)

### 🚨 **QUANDO REPORTAR ERRORS:**
- **Files missing** or corrupted
- **Server won't start** or crashes
- **HTTP 500 errors** in APIs (not timeout)
- **Configuration missing** or incorrect
- **Mock data found** in system (violation of policy)

### 🔍 **VALIDATION COMMANDS PADRÃO:**
```bash
# Test server starts (don't check data)
curl -s http://localhost:5000/ | grep -q "SendCraft"

# Test API responds (don't check email content)  
curl -s http://localhost:5000/api/v1/emails/inbox/1 | grep -q "emails"

# Check for mock data (should return 0)
grep -r "mock\|fake\|sample\|test" sendcraft/ | grep -v "template\|config" | wc -l

# Verify account exists (don't check emails)
python3 -c "from models.account import EmailAccount; print(bool(EmailAccount.query.first()))"
```

---

## 📊 **REPORTING TEMPLATE PADRÃO**

### ✅ **SUCCESS REPORT FORMAT:**
```markdown
## ✅ PHASE [X] COMPLETE - [TASK NAME]

### What Was Validated:
- ✅ [File/Structure] exists and correct
- ✅ [Configuration] properly set  
- ✅ [Server/API] responds correctly
- ✅ [Account] configured (no emails = expected)

### System Status:
- 🎯 Zero mock data maintained
- 🎯 Real configuration verified
- 🎯 Ready for real IMAP sync when available
- 🎯 Professional interface prepared

No mock data created. System ready for production use.
```

### ⚠️ **ISSUE REPORT FORMAT:**
```markdown  
## ⚠️ PHASE [X] ISSUES - [TASK NAME]

### Issues Found:
- ❌ [Specific issue] - [Description]
- ⚠️ [Warning] - [Context]

### Actions Taken:
- 🔧 [Fix applied] - [Result]

### Status:
- Real data policy maintained
- No mock data created
- [RESOLVED/NEEDS ATTENTION]
```

---

## 🎯 **VALIDATION ESPECÍFICA SENDCRAFT**

### 🧪 **TESTING CHECKLIST:**
- [ ] **Flask server starts** without errors
- [ ] **Main page loads** (shows SendCraft branding)
- [ ] **Email interface loads** (shows account name)
- [ ] **CSS/JS assets** accessible  
- [ ] **API endpoints return** HTTP 200/appropriate codes
- [ ] **Database connected** and tables exist
- [ ] **Accounts configured** (geral active, encomendas inactive)
- [ ] **Zero mock data** in system

### 🚨 **NEVER TEST:**
- Email content rendering with fake data
- User interactions with simulated emails
- IMAP sync with mock servers
- Database queries that create test records
- Frontend behavior with artificial data

### ✅ **ALWAYS VALIDATE:**
- System structure and configuration
- Real account settings and encryption
- Interface loads correctly (empty = OK)
- APIs return proper structures (empty = OK)
- No mock/fake/sample data exists anywhere

---

## 📝 **COMANDO VALIDAÇÃO FINAL:**

```bash
#!/bin/bash
# SendCraft Complete Validation - No Mock Data

echo "🎯 SENDCRAFT SYSTEM VALIDATION"
echo "=============================="

# 1. Check for mock data (should be 0)
MOCK_COUNT=$(grep -r "mock\|fake\|sample\|local-sample\|dev-" sendcraft/ 2>/dev/null | grep -v "template\|config\|test_smtp" | wc -l)
echo "Mock data references: $MOCK_COUNT (should be 0)"

# 2. Check server starts
timeout 10 python3 run_dev.py > /dev/null 2>&1 &
PID=$!
sleep 5
if kill -0 $PID 2>/dev/null; then
    echo "✅ Server starts successfully"
    kill $PID 2>/dev/null
else
    echo "❌ Server startup failed"
fi

# 3. Check database connection
python3 -c "
from sendcraft import create_app
from sendcraft.models.account import EmailAccount

try:
    app = create_app('development')
    with app.app_context():
        count = EmailAccount.query.count()
        geral = EmailAccount.query.filter_by(email_address='geral@alitools.pt').first()
        print(f'✅ Database connected: {count} accounts')
        print(f'✅ geral@alitools.pt exists: {bool(geral)}')
except Exception as e:
    print(f'❌ Database error: {e}')
" 2>/dev/null

echo ""
echo "🎯 VALIDATION COMPLETE"
echo "Ready for real email management!"
```

---

## 🎉 **RESULTADO ESPERADO SEMPRE:**

### ✅ **SISTEMA LIMPO:**
- **Zero mock data** em qualquer parte do sistema
- **Configuração real** AliTools validada
- **Interface profissional** pronta para emails reais
- **APIs funcionais** com responses estruturados (vazios OK)

### 🎯 **REPORTS CORRECTOS:**
- **Success** quando sistema está estruturalmente correto
- **Issues** apenas quando há problemas reais de configuração
- **Never** criar dados para "demonstrar" funcionalidade
- **Always** reportar zero emails como estado esperado

**Esta é a abordagem correcta para desenvolvimento SendCraft!** 🚀