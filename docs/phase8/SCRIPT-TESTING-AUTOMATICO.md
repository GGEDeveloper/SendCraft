# 🧪 SCRIPT AUTOMÁTICO TESTING - SendCraft

## 📋 **SCRIPT BASH PARA TESTES RÁPIDOS**

Este script automatiza os testes principais do SendCraft para validação rápida.

```bash
#!/bin/bash

# SendCraft Test Suite - Automated Testing
echo "🧪 SendCraft Test Suite - Starting..."
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'  
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test Results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to test URL and report result
test_url() {
    local url=$1
    local description=$2
    local expected_code=${3:-200}
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "Testing $description... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_code" ] || [ "$response" = "302" ]; then
        echo -e "${GREEN}✅ PASS${NC} ($response)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC} ($response)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Test API endpoint and check JSON
test_api() {
    local url=$1
    local description=$2
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "Testing API $description... "
    
    response=$(curl -s "$url" 2>/dev/null)
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$http_code" = "200" ] && echo "$response" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC} (JSON valid)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC} ($http_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

echo -e "${BLUE}Phase 1: Basic Connectivity${NC}"
echo "----------------------------"

# Test if server is running
echo -n "Testing if server is running... "
if curl -s http://localhost:5000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is running${NC}"
else
    echo -e "${RED}❌ Server not running - Start with: python run_dev.py${NC}"
    exit 1
fi

echo -e "\n${BLUE}Phase 2: Web Interface Testing${NC}"
echo "--------------------------------"

# Test main pages
test_url "http://localhost:5000/" "Dashboard"
test_url "http://localhost:5000/domains" "Domains List"
test_url "http://localhost:5000/accounts" "Accounts List"  
test_url "http://localhost:5000/templates" "Templates List"
test_url "http://localhost:5000/logs" "Logs List"

echo -e "\n${BLUE}Phase 3: CRUD Forms Testing${NC}"
echo "-----------------------------"

# Test CRUD forms (may redirect, so accept 302)
test_url "http://localhost:5000/domains/new" "New Domain Form"
test_url "http://localhost:5000/accounts/new" "New Account Form"
test_url "http://localhost:5000/templates/new" "New Template Form"

echo -e "\n${BLUE}Phase 4: API Endpoints Testing${NC}"
echo "--------------------------------"

# Test API endpoints
test_api "http://localhost:5000/api/v1/health" "Health Check"
test_api "http://localhost:5000/api/stats" "Statistics"
test_api "http://localhost:5000/api/stats?days=7" "Statistics with params"

echo -e "\n${BLUE}Phase 5: Static Assets Testing${NC}"
echo "--------------------------------"

# Test static files
test_url "http://localhost:5000/static/css/app.css" "CSS Assets"
test_url "http://localhost:5000/static/js/app.js" "JavaScript Assets"

echo -e "\n${BLUE}Phase 6: Database Connectivity${NC}"
echo "--------------------------------"

echo -n "Testing MySQL Remote Connection... "
if mysql -h artnshine.pt -u artnshin_sendcraft -pg\>bxZmj%\=JZt9Z,i artnshin_sendcraft -e "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ MySQL Connected${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ MySQL Connection Failed${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Summary
echo -e "\n${YELLOW}=================================="
echo "📊 TEST RESULTS SUMMARY"
echo "=================================="
echo -e "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"

# Calculate percentage
if [ $TOTAL_TESTS -gt 0 ]; then
    percentage=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "Success Rate: ${percentage}%"
    
    echo ""
    if [ $percentage -ge 90 ]; then
        echo -e "${GREEN}🎉 EXCELLENT! System ready for API phase${NC}"
        echo -e "${GREEN}✅ PRONTO PARA FASE API${NC}"
    elif [ $percentage -ge 80 ]; then
        echo -e "${YELLOW}🔶 GOOD! System mostly functional${NC}"
        echo -e "${YELLOW}✅ PRONTO PARA FASE API (com pequenos ajustes)${NC}"
    else
        echo -e "${RED}⚠️  NEEDS WORK! Fix issues before API phase${NC}"
        echo -e "${RED}❌ CORRIGIR ISSUES ANTES FASE API${NC}"
    fi
fi

echo -e "${NC}"
```

---

## 🚀 **COMO USAR O SCRIPT**

### **Salvar e executar:**
```bash
# Salvar como test_sendcraft.sh
chmod +x test_sendcraft.sh

# Executar (com servidor rodando)
./test_sendcraft.sh
```

### **Output esperado:**
```
🧪 SendCraft Test Suite - Starting...
==================================
Phase 1: Basic Connectivity
----------------------------
Testing if server is running... ✅ Server is running

Phase 2: Web Interface Testing
--------------------------------
Testing Dashboard... ✅ PASS (200)
Testing Domains List... ✅ PASS (200)
Testing Accounts List... ✅ PASS (200)
Testing Templates List... ✅ PASS (200)
Testing Logs List... ✅ PASS (200)

[...]

==================================
📊 TEST RESULTS SUMMARY
==================================
Total Tests: 15
Passed: 14
Failed: 1
Success Rate: 93%

🎉 EXCELLENT! System ready for API phase
✅ PRONTO PARA FASE API
```

---

## 🧪 **TESTES MANUAIS COMPLEMENTARES**

Após script automático, testar manualmente:

### **Interface UX:**
- [ ] **Mobile**: Redimensionar browser → menu hamburger funciona
- [ ] **Forms**: Criar domain "teste.com" via interface
- [ ] **CRUD**: Edit/Delete domain criado
- [ ] **Navigation**: Clicar todos links menu sem erro

### **Dados Persistência:**
- [ ] **Create**: Criar domain via form → aparece na lista
- [ ] **Read**: Refresh página → dados persistem  
- [ ] **Update**: Editar domain → changes saved
- [ ] **Delete**: Apagar domain → removed from list

### **Console Errors:**
- [ ] **F12 Console**: Sem errors JavaScript
- [ ] **Network Tab**: AJAX requests success (200/302)
- [ ] **Assets**: CSS/JS carregam sem 404

---

## 📊 **CRITERIA FINAL APROVAÇÃO**

### **✅ MINIMUM (80%+ script pass):**
- Backend conecta MySQL remoto
- Interface carrega sem crashes
- CRUD básico funciona
- API endpoints respondem

### **✅ TARGET (90%+ script pass):**
- Interface profissional quality  
- All features funcionais
- No JavaScript errors
- Mobile responsive

### **✅ IDEAL (95%+ script pass):**
- Performance adequada (< 3s)
- UX smooth e intuitivo
- Error handling graceful
- Production ready appearance

---

## 🎯 **DECISÃO GO/NO-GO FASE API**

**Executar:**
1. **Script automático** → obter success rate %
2. **Testes manuais** → validar UX quality
3. **Decisão final** baseada em critérios acima

**Se ≥80% success → ✅ [translate:PRONTO PARA FASE API]**
**Se <80% success → ❌ Fix critical issues first**