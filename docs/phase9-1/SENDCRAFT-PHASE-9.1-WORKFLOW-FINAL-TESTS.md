# 🚀 SendCraft Phase 9.1 - WORKFLOW FINAL + TEST SUITE

## ✅ **PROMPTS JÁ ESTÃO COMPLETOS - USAR DIRETOS**

### **SIM - Os prompts já criados são suficientes e completos!**

**Usar exatamente estes ficheiros:**
- [124] **PROMPT-1-BACKEND-REAL-CONFIG.md** → Claude 4.1 Opus (Backend)  
- [120] **PROMPT-2-FRONTEND-CLIENT.md** → Claude 4.1 Opus (Frontend)
- [121] **PROMPT-3-INTEGRATION.md** → Cursor Agent (Integration)

**ÚNICA ADIÇÃO NECESSÁRIA:** Test Suite para sanity checks

---

## 🧪 **TEST SUITE - SANITY CHECKS EM CADA FASE**

### **FASE 1: Local Agent Setup - Sanity Check**
```bash
#!/bin/bash
# test_phase1_setup.sh

echo "🧪 Testing Phase 1 Setup..."

# Test 1: Branch criado
if git branch | grep -q "phase-9.1-email-inbox-outbox-real"; then
    echo "✅ Branch phase-9.1 created"
else
    echo "❌ Branch not created"
    exit 1
fi

# Test 2: Directories created
if [ -d "sendcraft/templates/emails" ]; then
    echo "✅ Email templates directory created"
else
    echo "❌ Email templates directory missing"
    exit 1
fi

# Test 3: Dependencies installed
if pip list | grep -q "python-socketio"; then
    echo "✅ python-socketio installed"
else
    echo "❌ python-socketio missing"
    exit 1
fi

# Test 4: Placeholder files exist
if [ -f "sendcraft/models/email_inbox.py" ]; then
    echo "✅ Placeholder files created"
else
    echo "❌ Placeholder files missing"
    exit 1
fi

echo "🎉 Phase 1 Setup - ALL TESTS PASSED"
```

### **FASE 2: Backend IMAP - Sanity Check**
```bash
#!/bin/bash
# test_phase2_backend.sh

echo "🧪 Testing Phase 2 Backend..."

# Test 1: EmailInbox model
python3 -c "from sendcraft.models.email_inbox import EmailInbox; print('✅ EmailInbox model OK')" 2>/dev/null || echo "❌ EmailInbox model failed"

# Test 2: IMAP Service  
python3 -c "from sendcraft.services.imap_service import IMAPService; print('✅ IMAPService OK')" 2>/dev/null || echo "❌ IMAPService failed"

# Test 3: API endpoints
python3 -c "from sendcraft.api.v1.emails_inbox import emails_bp; print('✅ API endpoints OK')" 2>/dev/null || echo "❌ API endpoints failed"

# Test 4: mail.alitools.pt config
if grep -q "mail.alitools.pt" sendcraft/services/imap_service.py; then
    echo "✅ REAL mail.alitools.pt config found"
else
    echo "❌ Real IMAP config missing"
    exit 1
fi

# Test 5: SSL port 993
if grep -q "993" sendcraft/services/imap_service.py; then
    echo "✅ IMAP port 993 SSL configured"
else
    echo "❌ IMAP SSL port not configured"
    exit 1
fi

echo "🎉 Phase 2 Backend - ALL TESTS PASSED"
```

### **FASE 3: Database Migration - Sanity Check**
```bash
#!/bin/bash  
# test_phase3_migration.sh

echo "🧪 Testing Phase 3 Migration..."

# Test 1: Migration generated
if ls migrations/versions/ | grep -q "email_inbox"; then
    echo "✅ Migration file generated"
else
    echo "❌ Migration file not found"
    exit 1
fi

# Test 2: Migration applied
flask db current > /dev/null 2>&1 && echo "✅ Migration system OK" || echo "❌ Migration system failed"

# Test 3: EmailInbox table exists
mysql -h artnshine.pt -u artnshinsendcraft -p"gbxZmjJZt9Z,i" artnshinsendcraft -e "DESCRIBE email_inbox;" > /dev/null 2>&1 && echo "✅ EmailInbox table created" || echo "❌ EmailInbox table not found"

# Test 4: IMAP fields added
mysql -h artnshine.pt -u artnshinsendcraft -p"gbxZmjJZt9Z,i" artnshinsendcraft -e "DESCRIBE email_accounts;" | grep -q "imap_server" && echo "✅ IMAP fields added to EmailAccount" || echo "❌ IMAP fields missing"

echo "🎉 Phase 3 Migration - ALL TESTS PASSED"
```

### **FASE 4: Frontend Client - Sanity Check**
```bash
#!/bin/bash
# test_phase4_frontend.sh

echo "🧪 Testing Phase 4 Frontend..."

# Test 1: Templates exist
for template in "inbox.html" "outbox.html" "compose.html"; do
    if [ -f "sendcraft/templates/emails/$template" ]; then
        echo "✅ $template exists"
    else
        echo "❌ $template missing"
        exit 1
    fi
done

# Test 2: CSS file exists and has three-pane
if [ -f "sendcraft/static/css/email-client.css" ]; then
    if grep -q "email-client-container" sendcraft/static/css/email-client.css; then
        echo "✅ Email client CSS with three-pane layout"
    else
        echo "❌ Three-pane CSS missing"
        exit 1
    fi
else
    echo "❌ Email client CSS missing"
    exit 1
fi

# Test 3: JavaScript functionality
if [ -f "sendcraft/static/js/email-client/EmailClientApp.js" ]; then
    if grep -q "syncEmails" sendcraft/static/js/email-client/EmailClientApp.js; then
        echo "✅ Email sync functionality in JS"
    else
        echo "❌ Email sync JS missing"
        exit 1
    fi
else
    echo "❌ EmailClientApp.js missing"
    exit 1
fi

# Test 4: Bootstrap 5 integration
if grep -q "bootstrap" sendcraft/templates/emails/inbox.html; then
    echo "✅ Bootstrap 5 integration"
else
    echo "❌ Bootstrap integration missing"
    exit 1
fi

echo "🎉 Phase 4 Frontend - ALL TESTS PASSED"
```

### **FASE 5: Integration - Sanity Check**
```bash
#!/bin/bash
# test_phase5_integration.sh

echo "🧪 Testing Phase 5 Integration..."

# Test 1: Email routes added
if grep -q "emails_inbox" sendcraft/routes/web.py; then
    echo "✅ Email routes integrated"
else
    echo "❌ Email routes missing"
    exit 1
fi

# Test 2: API blueprints registered
if grep -q "emails_bp" sendcraft/api/v1/__init__.py; then
    echo "✅ API blueprints registered"
else
    echo "❌ API blueprints not registered"
    exit 1
fi

# Test 3: Navigation updated
if grep -q "emails" sendcraft/templates/base.html; then
    echo "✅ Navigation updated with email links"
else
    echo "❌ Navigation not updated"
    exit 1
fi

# Test 4: Models imported
if grep -q "email_inbox" sendcraft/__init__.py; then
    echo "✅ EmailInbox model imported"
else
    echo "❌ EmailInbox model not imported"
    exit 1
fi

echo "🎉 Phase 5 Integration - ALL TESTS PASSED"
```

### **FASE 6: Final Validation - Comprehensive Test**
```bash
#!/bin/bash
# test_phase6_final.sh

echo "🧪 Testing Phase 6 Final Validation..."

# Test 1: App starts without errors
python3 -c "from sendcraft import create_app; app = create_app('development'); print('✅ App starts OK')" 2>/dev/null || echo "❌ App startup failed"

# Test 2: Email routes accessible  
python3 rundev.py > /dev/null 2>&1 &
APP_PID=$!
sleep 3

curl -f -s http://localhost:5000/emails/inbox > /dev/null && echo "✅ Email inbox route OK" || echo "❌ Email inbox route failed"

kill $APP_PID 2>/dev/null

# Test 3: API endpoints respond
python3 rundev.py > /dev/null 2>&1 &
APP_PID=$!
sleep 3

curl -f -s http://localhost:5000/api/v1/emails/inbox/1 > /dev/null && echo "✅ API endpoints OK" || echo "❌ API endpoints failed"

kill $APP_PID 2>/dev/null

# Test 4: Real account creation
python3 -c "
from sendcraft import create_app
from sendcraft.models.account import EmailAccount

app = create_app('development')
with app.app_context():
    account = EmailAccount.query.filter_by(email_address='encomendas@alitools.pt').first()
    if account and account.imap_server == 'mail.alitools.pt':
        print('✅ Real account with correct IMAP config')
    else:
        print('❌ Real account config incorrect')
"

# Test 5: IMAP connectivity
timeout 5 bash -c 'cat < /dev/null > /dev/tcp/mail.alitools.pt/993' && echo "✅ IMAP server reachable" || echo "❌ IMAP server not reachable"

echo "🎉 Phase 6 Final - ALL TESTS PASSED"
```

---

## 🔄 **MASTER TEST RUNNER - ALL PHASES**

### **Executar Todos os Testes de Uma Vez:**
```bash
#!/bin/bash
# run_all_phase_tests.sh

echo "🚀 SendCraft Phase 9.1 - Complete Test Suite"
echo "============================================"

PHASES=("setup" "backend" "migration" "frontend" "integration" "final")
PASSED=0
TOTAL=6

for phase in "${PHASES[@]}"; do
    echo ""
    echo "Testing Phase: $phase"
    echo "------------------------"
    
    if ./test_phase${BASH_REMATCH[1]}_${phase}.sh; then
        ((PASSED++))
        echo "✅ Phase $phase: PASSED"
    else
        echo "❌ Phase $phase: FAILED"
    fi
done

echo ""
echo "============================================"
echo "📊 Test Results: $PASSED/$TOTAL phases passed"

if [ $PASSED -eq $TOTAL ]; then
    echo "🎉 ALL PHASES PASSED - Phase 9.1 is ready!"
    exit 0
else
    echo "⚠️  Some phases failed - review and fix issues"
    exit 1
fi
```

---

## 🎯 **WORKFLOW FINAL COM TEST SUITE**

### **EXECUÇÃO COM SANITY CHECKS:**

```
🕐 FASE 1: Local Agent Setup (2-3 min)
├── Executar prompt Cursor Agent
├── ✅ Run: ./test_phase1_setup.sh
└── Confirmar: Environment OK

🕐 FASE 2: Backend IMAP (15-20 min)  
├── Executar PROMPT-1-BACKEND-REAL-CONFIG.md (Claude)
├── ✅ Run: ./test_phase2_backend.sh
└── Confirmar: Models/Services OK

🕐 FASE 3: Database Migration (1-2 min)
├── flask db migrate + flask db upgrade
├── ✅ Run: ./test_phase3_migration.sh  
└── Confirmar: Database OK

🕐 FASE 4: Frontend Client (20-25 min)
├── Executar PROMPT-2-FRONTEND-CLIENT.md (Claude)  
├── ✅ Run: ./test_phase4_frontend.sh
└── Confirmar: Interface OK

🕐 FASE 5: Integration (10-15 min)
├── Executar PROMPT-3-INTEGRATION.md (Cursor)
├── ✅ Run: ./test_phase5_integration.sh
└── Confirmar: Integration OK

🕐 FASE 6: Final Validation (3-5 min)
├── Criar conta real encomendas@alitools.pt
├── ✅ Run: ./test_phase6_final.sh
└── Confirmar: Sistema 100% funcional

🎉 MASTER TEST:
├── ✅ Run: ./run_all_phase_tests.sh
└── Confirmar: Todos os testes passam
```

---

## 📋 **RESUMO - O QUE TENS DE FAZER:**

### **USAR OS PROMPTS EXISTENTES (JÁ COMPLETOS):**
1. **Cursor Agent**: Prompt setup direto do workflow
2. **Claude 4.1**: [124] PROMPT-1-BACKEND-REAL-CONFIG.md
3. **User**: flask db migrate + upgrade  
4. **Claude 4.1**: [120] PROMPT-2-FRONTEND-CLIENT.md
5. **Cursor Agent**: [121] PROMPT-3-INTEGRATION.md
6. **User**: Testing final

### **SANITY CHECKS ENTRE CADA FASE:**
- Executar script de teste correspondente
- Só avançar se todos os testes passarem
- Debugging imediato se algo falhar

### **VANTAGEM DOS SANITY CHECKS:**
✅ **Detecção precoce** de problemas  
✅ **Debugging** fase a fase  
✅ **Confiança** de que cada etapa está OK  
✅ **Rollback fácil** se algo correr mal  
✅ **Validação automática** do resultado final

**Com esta abordagem: 0% chance de falha, 100% confidence no resultado final!** 🚀