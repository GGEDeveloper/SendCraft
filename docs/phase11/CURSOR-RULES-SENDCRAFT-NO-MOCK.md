# 🚫 CURSOR RULES - SENDCRAFT ZERO MOCK POLICY

```markdown
# SENDCRAFT DEVELOPMENT RULES - ZERO MOCK DATA POLICY

## 🚫 ABSOLUTE PROHIBITIONS:
- NEVER create, insert, or seed any mock/fake/sample/test/dev data
- NEVER create "improved" services that simulate IMAP with fake data  
- NEVER add fallback mechanisms that generate artificial records
- NEVER create seed scripts, sample emails, or local testing data
- NEVER modify .cpanel.yml to run seeding tasks
- NEVER add mock data generation to run_dev.py or startup scripts

## ✅ REQUIRED BEHAVIORS:
- Use ONLY real data from geral@alitools.pt and encomendas@alitools.pt
- On IMAP timeout/failure: Return error (HTTP 500/504), don't create fake data
- Frontend calls APIs with proper JSON, backend handles real IMAP only
- Preserve encomendas@alitools.pt account (inactive but kept)
- Activate only geral@alitools.pt for primary email management

## 🔍 PRE-COMMIT VALIDATION:
Before any commit/push, run:
```bash
grep -R "local-sample\\|dev-\\|fake-\\|test-\\|mock-\\|sample-" sendcraft/
```
If ANY matches found, ABORT commit and remove all mock references.

## 📧 EMAIL ACCOUNTS POLICY:
- geral@alitools.pt: ACTIVE (primary account)
- encomendas@alitools.pt: INACTIVE (preserved backup)  
- NO other accounts unless explicitly real AliTools emails

## 🎯 SUCCESS CRITERIA:
- Empty database initially (no fake emails)
- Real IMAP sync from mail.alitools.pt when network allows
- Graceful error handling on IMAP timeout (no data creation)
- Professional interface showing only real emails when synced
```