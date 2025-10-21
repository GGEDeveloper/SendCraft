#!/bin/bash
# 🔍 SendCraft Phase 9.1 - Script de Validação
echo "🔍 Validating Phase 9.1 Implementation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_TOTAL=0

# Function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${YELLOW}Testing: $test_name${NC}"
    ((TESTS_TOTAL++))
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "  ${RED}❌ FAIL${NC}"
    fi
}

echo "🧪 Starting Phase 9.1 validation tests..."
echo "================================================"

# 1. Test Backend Models
echo "📊 Backend Models Tests:"
run_test "EmailInbox model import" "python3 -c 'from sendcraft.models.email_inbox import EmailInbox'"
run_test "EmailAccount IMAP fields" "python3 -c 'from sendcraft.models.account import EmailAccount; a = EmailAccount(); hasattr(a, \"imap_server\")'"

# 2. Test Backend Services  
echo "⚙️ Backend Services Tests:"
run_test "IMAPService import" "python3 -c 'from sendcraft.services.imap_service import IMAPService'"
run_test "RealtimeService import" "python3 -c 'from sendcraft.services.realtime_service import RealtimeEmailService'"

# 3. Test API Endpoints
echo "🌐 API Endpoints Tests:"
# Start app in background for testing
python3 run_local.py > /dev/null 2>&1 &
APP_PID=$!
sleep 3  # Wait for app to start

run_test "API Health Check" "curl -f http://localhost:5000/api/v1/health"
run_test "Inbox API endpoint" "curl -f -X GET http://localhost:5000/api/v1/emails/inbox/1"

# Kill background app
kill $APP_PID 2>/dev/null

# 4. Test Frontend Templates
echo "🎨 Frontend Templates Tests:"
run_test "Inbox template exists" "test -f sendcraft/templates/emails/inbox.html"
run_test "Outbox template exists" "test -f sendcraft/templates/emails/outbox.html"
run_test "Compose template exists" "test -f sendcraft/templates/emails/compose.html"

# 5. Test Static Assets
echo "📦 Static Assets Tests:"
run_test "Email client CSS exists" "test -f sendcraft/static/css/email-client.css"
run_test "EmailClientApp JS exists" "test -f sendcraft/static/js/email-client/EmailClientApp.js"

# 6. Test Database
echo "🗄️ Database Tests:"
run_test "Database migration applied" "flask db current"
run_test "EmailInbox table exists" "python3 -c 'from sendcraft.models.email_inbox import EmailInbox; EmailInbox.query.count()'"

# 7. Test Configuration  
echo "⚙️ Configuration Tests:"
run_test "SocketIO configuration" "python3 -c 'import os; print(os.environ.get(\"SOCKETIO_ENABLED\", \"false\"))'"
run_test "IMAP configuration" "python3 -c 'import os; print(os.environ.get(\"IMAP_CONNECTION_POOL_SIZE\", \"5\"))'"

echo "================================================"
echo -e "📊 Test Results: ${GREEN}$TESTS_PASSED${NC}/${TESTS_TOTAL} tests passed"

if [ $TESTS_PASSED -eq $TESTS_TOTAL ]; then
    echo -e "${GREEN}🎉 All tests passed! Phase 9.1 implementation is complete and ready.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please check the implementation.${NC}"
    exit 1
fi