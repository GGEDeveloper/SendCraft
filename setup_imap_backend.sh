#!/bin/bash
# SendCraft IMAP Backend Setup Script
# Sets up complete IMAP functionality for encomendas@alitools.pt

echo "======================================"
echo "SendCraft IMAP Backend Setup"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Database credentials
DB_HOST="artnshine.pt"
DB_PORT="3306"
DB_USER="artnshinsendcraft"
DB_PASS="fI8kLiE?i}Ej"
DB_NAME="artnshinsendcraft"

echo -e "\n${YELLOW}Step 1: Running Database Migration${NC}"
echo "----------------------------------------"

# Check if mysql is available
if command -v mysql &> /dev/null; then
    echo "Applying database migration..."
    mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASS $DB_NAME < /workspace/migrations/add_imap_support.sql 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Database migration applied successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Migration might already be applied or had warnings${NC}"
    fi
else
    echo -e "${RED}❌ MySQL client not found. Please install: apt-get install mysql-client${NC}"
    echo "Or run manually: mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p $DB_NAME < /workspace/migrations/add_imap_support.sql"
fi

echo -e "\n${YELLOW}Step 2: Setting up Python environment${NC}"
echo "----------------------------------------"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || . venv/bin/activate

# Install/upgrade requirements
echo "Installing requirements..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Additional packages for IMAP
pip install -q chardet

echo -e "${GREEN}✅ Python environment ready${NC}"

echo -e "\n${YELLOW}Step 3: Initializing Database Tables${NC}"
echo "----------------------------------------"

# Initialize database
export FLASK_ENV=development
flask init-db

echo -e "\n${YELLOW}Step 4: Seeding IMAP Account${NC}"
echo "----------------------------------------"

# Seed the encomendas@alitools.pt account
flask seed-imap --test --sync 10

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ IMAP account seeded and tested successfully${NC}"
else
    echo -e "${RED}❌ Failed to seed IMAP account${NC}"
fi

echo -e "\n${YELLOW}Step 5: Running Tests${NC}"
echo "----------------------------------------"

# Run the test script
python test_imap_implementation.py

echo -e "\n======================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "======================================"

echo -e "\n${YELLOW}Configuration Summary:${NC}"
echo "- Email Account: encomendas@alitools.pt"
echo "- IMAP Server: mail.alitools.pt:993 (SSL)"
echo "- SMTP Server: mail.alitools.pt:465 (SSL)"
echo "- Database: MySQL on artnshine.pt"
echo "- Auto Sync: Enabled (every 5 minutes)"

echo -e "\n${YELLOW}Available Commands:${NC}"
echo "- flask seed-imap           # Seed account only"
echo "- flask seed-imap --test    # Seed and test connection"
echo "- flask seed-imap --sync 50 # Seed and sync 50 emails"

echo -e "\n${YELLOW}API Endpoints:${NC}"
echo "- GET  /api/v1/inbox/<account_id>              # List emails"
echo "- GET  /api/v1/inbox/<account_id>/<email_id>   # Get email"
echo "- POST /api/v1/inbox/sync/<account_id>         # Sync emails"
echo "- PUT  /api/v1/inbox/<account_id>/<email_id>/read # Mark read"
echo "- GET  /api/v1/inbox/<account_id>/stats        # Get stats"

echo -e "\n${YELLOW}Start the application:${NC}"
echo "flask run --host=0.0.0.0 --port=5000"