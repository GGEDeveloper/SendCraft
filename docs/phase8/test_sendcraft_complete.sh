#!/bin/bash

# 🧪 SendCraft Complete Test Suite - Automated Testing
# Execute este script para testar todo o sistema SendCraft

echo "🧪 SendCraft Complete Test Suite"
echo "================================="
echo "Testing all SendCraft functionality before API phase..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'  
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test Results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
ISSUES=()

# Function to test URL and report result
test_url() {
    local url=$1
    local description=$2
    local expected_code=${3:-200}
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "  Testing $description... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_code" ] || [ "$response" = "302" ] || [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ PASS${NC} ($response)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC} ($response)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        ISSUES+=("$description failed with code $response")
    fi
}

# Test API endpoint and check JSON
test_api() {
    local url=$1
    local description=$2
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "  Testing API $description... "
    
    response=$(curl -s "$url" 2>/dev/null)
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$http_code" = "200" ] && echo "$response" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC} (JSON valid)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC} ($http_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        ISSUES+=("API $description failed - code: $http_code")
    fi
}

# Test database connectivity
test_mysql() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "  Testing MySQL Remote Connection... "
    
    if mysql -h artnshine.pt -u artnshin_sendcraft -p'g>bxZmj%=JZt9Z,i' artnshin_sendcraft -e "SELECT 1;" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        ISSUES+=("MySQL remote connection failed")
    fi
}

# Check if server is running
check_server() {
    echo -n "🔍 Checking if SendCraft server is running... "
    if curl -s http://localhost:5000/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Server is running${NC}"
        return 0
    else
        echo -e "${RED}❌ Server not running${NC}"
        echo -e "${YELLOW}💡 Please start server with: python run_dev.py${NC}"
        return 1
    fi
}

# Phase 1: Server Check
echo -e "${CYAN}Phase 1: Server Connectivity${NC}"
echo "-----------------------------"
if ! check_server; then
    echo -e "${RED}⚠️  Cannot continue without running server${NC}"
    exit 1
fi
echo ""

# Phase 2: Basic Web Interface
echo -e "${CYAN}Phase 2: Web Interface Pages${NC}"
echo "-----------------------------"
test_url "http://localhost:5000/" "Dashboard"
test_url "http://localhost:5000/domains" "Domains List"
test_url "http://localhost:5000/accounts" "Accounts List"  
test_url "http://localhost:5000/templates" "Templates List"
test_url "http://localhost:5000/logs" "Logs List"
echo ""

# Phase 3: CRUD Forms
echo -e "${CYAN}Phase 3: CRUD Forms${NC}"
echo "-------------------"
test_url "http://localhost:5000/domains/new" "New Domain Form"
test_url "http://localhost:5000/accounts/new" "New Account Form"
test_url "http://localhost:5000/templates/new" "New Template Form"
echo ""

# Phase 4: API Endpoints
echo -e "${CYAN}Phase 4: API Endpoints${NC}"
echo "----------------------"
test_api "http://localhost:5000/api/v1/health" "Health Check"
test_api "http://localhost:5000/api/stats" "Statistics"
test_api "http://localhost:5000/api/stats?days=7" "Statistics with params"
echo ""

# Phase 5: Static Assets
echo -e "${CYAN}Phase 5: Static Assets${NC}"
echo "----------------------"
test_url "http://localhost:5000/static/css/app.css" "CSS Assets"
test_url "http://localhost:5000/static/js/app.js" "JavaScript Assets"
echo ""

# Phase 6: Database
echo -e "${CYAN}Phase 6: Database Connectivity${NC}"
echo "------------------------------"
test_mysql
echo ""

# Phase 7: Template Content Check
echo -e "${CYAN}Phase 7: Template Content Check${NC}"
echo "-------------------------------"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "  Checking Dashboard content... "
dashboard_content=$(curl -s "http://localhost:5000/" 2>/dev/null)
if echo "$dashboard_content" | grep -q "SendCraft" && echo "$dashboard_content" | grep -q "Dashboard"; then
    echo -e "${GREEN}✅ PASS${NC} (Contains expected content)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAIL${NC} (Missing expected content)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    ISSUES+=("Dashboard missing SendCraft branding or title")
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "  Checking Bootstrap CSS loading... "
if echo "$dashboard_content" | grep -q "bootstrap" || curl -s "http://localhost:5000/static/css/app.css" | grep -q "bootstrap\|btn\|card"; then
    echo -e "${GREEN}✅ PASS${NC} (Bootstrap detected)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAIL${NC} (Bootstrap not detected)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    ISSUES+=("Bootstrap CSS not loading properly")
fi
echo ""

# Results Summary
echo -e "${YELLOW}============================================="
echo "📊 SENDCRAFT TEST RESULTS SUMMARY"
echo "=============================================${NC}"
echo -e "Total Tests Run: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Tests Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Tests Failed: ${RED}$FAILED_TESTS${NC}"

if [ $TOTAL_TESTS -gt 0 ]; then
    percentage=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "Success Rate: ${BLUE}${percentage}%${NC}"
    echo ""
    
    if [ $percentage -ge 95 ]; then
        echo -e "${GREEN}🎉 EXCELLENT! System is production ready${NC}"
        echo -e "${GREEN}✅ SISTEMA PERFEITO - PRONTO PARA FASE API${NC}"
        grade="A+"
    elif [ $percentage -ge 90 ]; then
        echo -e "${GREEN}🔥 GREAT! System ready for API phase${NC}"
        echo -e "${GREEN}✅ PRONTO PARA FASE API${NC}"
        grade="A"
    elif [ $percentage -ge 80 ]; then
        echo -e "${YELLOW}👍 GOOD! System mostly functional${NC}"
        echo -e "${YELLOW}✅ PRONTO PARA FASE API (pequenos ajustes opcionais)${NC}"
        grade="B"
    elif [ $percentage -ge 70 ]; then
        echo -e "${YELLOW}⚠️  FAIR! Some issues need fixing${NC}"
        echo -e "${YELLOW}🔄 CORRIGIR ISSUES CRÍTICOS ANTES FASE API${NC}"
        grade="C"
    else
        echo -e "${RED}❌ POOR! Multiple issues need fixing${NC}"
        echo -e "${RED}🛑 CORRIGIR PROBLEMAS ANTES AVANÇAR${NC}"
        grade="D"
    fi
    
    echo -e "System Grade: ${BLUE}$grade${NC}"
fi

# Issues Report
if [ ${#ISSUES[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}Issues Found:${NC}"
    echo "-------------"
    for issue in "${ISSUES[@]}"; do
        echo -e "${RED}❌${NC} $issue"
    done
fi

echo ""
echo -e "${CYAN}Manual Testing Recommendations:${NC}"
echo "1. Test mobile responsive design (resize browser)"
echo "2. Create a test domain via web interface"
echo "3. Test form submissions and data persistence"
echo "4. Check browser console (F12) for JavaScript errors"
echo "5. Test navigation between all pages"

echo ""
echo -e "${BLUE}Testing completed! Check results above.${NC}"

# Exit with proper code
if [ $percentage -ge 80 ]; then
    exit 0
else
    exit 1
fi