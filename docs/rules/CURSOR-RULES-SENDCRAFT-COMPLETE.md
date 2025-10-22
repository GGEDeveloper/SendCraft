# 🎯 CURSOR RULES - SENDCRAFT PROJECT

## CORE SENDCRAFT POLICIES

### ZERO MOCK DATA POLICY
- NEVER create ANY mock/fake/sample/test/dev data in ANY environment
- NEVER create improved/mock services that simulate real functionality  
- NEVER add fallback mechanisms that generate artificial records
- NEVER create seed scripts, sample emails, or local testing data
- NEVER modify .cpanel.yml to run seeding tasks
- NEVER add mock data generation to startup scripts

### REAL DATA ONLY
- Use ONLY real data from geral@alitools.pt and encomendas@alitools.pt
- On IMAP timeout/failure: Return error (HTTP 500/504), don't create fake data
- Frontend calls APIs with proper JSON, backend handles real IMAP only
- Preserve encomendas@alitools.pt account (inactive but kept)
- Activate only geral@alitools.pt for primary email management

### EMAIL ACCOUNTS POLICY
- geral@alitools.pt: ACTIVE (primary account)
- encomendas@alitools.pt: INACTIVE (preserved backup)
- NO other accounts unless explicitly real AliTools emails

## TESTING AND VALIDATION RULES

### WHAT TO TEST
- Test interface structure (HTML elements, CSS classes, JS functions) not data
- Test API responses (HTTP codes, JSON structure) not specific content  
- Test connectivity (server starts, endpoints accessible) not mock scenarios
- Test configuration (settings correct, accounts configured) not artificial data
- Verify files exist and have correct structure

### WHAT NOT TO TEST
- Email content rendering with fake data
- User interactions with simulated emails
- IMAP sync with mock servers
- Database queries that create test records
- Frontend behavior with artificial data

### SUCCESS CRITERIA
- Empty email list = SUCCESS (no mock data)
- IMAP timeout = EXPECTED (local development limitation)
- Interface loads = SUCCESS (even without emails)
- APIs respond = SUCCESS (even with empty results)
- Zero emails in database = SUCCESS (ready for real sync)

## DEVELOPMENT WORKFLOW

### VALIDATION APPROACH
- Report what exists (files, structure, configuration) not what could be simulated
- Report empty results as success when no real data available
- Report errors properly when real connections fail
- Report validation based on system readiness, not mock scenarios

### PRE-COMMIT VALIDATION
Before any commit/push, run:
```bash
grep -R "local-sample\\|dev-\\|fake-\\|test-\\|mock-\\|sample-" sendcraft/
```
If ANY matches found, ABORT commit and remove all mock references.

### DATABASE POLICY
- Empty email_inbox table = SUCCESS (ready for real sync)
- Only real accounts in email_account table
- Domain alitools.pt must exist
- No sample/demo/test records ever

## ERROR HANDLING

### WHEN TO REPORT SUCCESS
- Empty email list (no mock data)
- IMAP timeout (expected in local development)
- Interface loads correctly (even without data)
- APIs return proper structure (empty arrays OK)
- Server starts without errors

### WHEN TO REPORT ERRORS
- Files missing or corrupted
- Server won't start or crashes
- HTTP 500 errors in APIs (not timeout)
- Configuration missing or incorrect
- Mock data found in system (violation of policy)

## SENDCRAFT SPECIFICS

### WEB INTERFACE TESTING
- Test HTML structure loads correctly
- Test CSS/JS assets are accessible
- Test account display shows configured account
- DON'T test with mock emails or simulate interactions
- Empty interface = SUCCESS (ready for real data)

### API TESTING APPROACH
- Test HTTP 200 responses on GET endpoints
- Test JSON structure in responses (empty arrays OK)
- Test POST endpoints accept correct headers/body
- DON'T create test data to validate functionality
- Timeout/errors = Expected behavior in local development

### FRONTEND VALIDATION
- Check file existence: HTML, CSS, JS files present
- Check structure: Classes, IDs, functions defined
- Check configuration: API endpoints, account settings
- DON'T check data rendering or simulate interactions