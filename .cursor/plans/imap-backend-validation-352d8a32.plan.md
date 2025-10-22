<!-- 352d8a32-f234-491c-b5d6-7339207accf8 cdc9b69b-1591-41f7-8e8c-42ea7ed18847 -->
# Phase 9.1 - IMAP Backend Validation & Testing

## 1. Checkout Correct Branch & Verify Implementation

**Actions:**

- Fetch all remote branches
- Checkout `cursor/implement-imap-backend-for-email-inbox-dcb3`
- Pull latest changes from origin

**Verification:** Read and validate that these files contain **complete implementations** (not placeholders):

- `sendcraft/models/email_inbox.py` - Full EmailInbox model with fields: `message_id`, `thread_id`, `folder`, `from_address`, `to_addresses`, `subject`, `body_text`, `body_html`, `received_at`, `is_read`, `is_flagged`, `is_deleted`, `has_attachments`, `attachment_count`, indexes on `(account_id, received_at)`, `(account_id, folder)`, `(account_id, is_read)`
- `sendcraft/models/account.py` - IMAP fields added: `imap_server`, `imap_port`, `imap_use_ssl`, `imap_use_tls`, `last_sync`, `auto_sync_enabled`, `sync_interval_minutes`, plus `get_imap_config()` method
- `sendcraft/services/imap_service.py` - Complete IMAPService class with methods: `connect()`, `select_folder()`, `search_emails()`, `fetch_email_by_id()`, `sync_account_emails()`, `mark_email()`, `disconnect()`, full SSL support and email parsing
- `sendcraft/api/v1/emails_inbox.py` - API blueprint with endpoints: list, get, sync, mark_read, flag, delete, move, stats, threads

**Stop Condition:** If any file contains TODO/placeholder code, report immediately and stop execution.

## 2. Install Dependencies

Install required packages:

```bash
pip install chardet pymysql cryptography python-socketio email-validator
```

## 3. Database Migration & Schema Validation

**Generate and apply migration:**

```bash
flask db migrate -m "Phase 9.1: Add IMAP fields + EmailInbox"
flask db upgrade
```

**Validate MySQL schema** on remote database `artnshine.pt:3306/artnshinsendcraft`:

Verify `email_accounts` table has new columns:

- `imap_server`, `imap_port`, `imap_use_ssl`, `imap_use_tls`, `last_sync`, `auto_sync_enabled`, `sync_interval_minutes`

Verify `email_inbox` table exists with:

- All required columns (id, account_id, message_id, thread_id, folder, from_address, to_addresses, cc_addresses, bcc_addresses, reply_to, subject, body_text, body_html, received_at, sent_at, is_read, is_flagged, is_deleted, has_attachments, attachment_count, size_bytes, raw_headers, created_at, updated_at)
- Indexes: `idx_account_received`, `idx_account_folder`, `idx_account_read`, `idx_message_id`, `idx_thread_id`

## 4. Real Account Seeding

Create production account in database:

**Domain:** `alitools.pt`

- Create if not exists
- Fields: `name='alitools.pt'`, `description='AliTools B2B Platform'`, `is_active=True`

**Email Account:** `encomendas@alitools.pt`

- Domain: alitools.pt
- SMTP: `mail.alitools.pt:465` (SSL=True, TLS=False)
- IMAP: `mail.alitools.pt:993` (SSL=True, TLS=False)
- Password: `6f2zniWMN6aUFaD` (encrypted via AESCipher with SECRET_KEY)
- Auto-sync: enabled, interval=5 minutes
- Limits: daily=1000, monthly=10000

**Validation:** Call `account.get_imap_config(SECRET_KEY)` and verify returned config matches expected values.

## 5. Network Connectivity Tests

Test SSL connectivity to mail servers:

```bash
timeout 10 openssl s_client -connect mail.alitools.pt:993 -quiet < /dev/null  # IMAP
timeout 10 openssl s_client -connect mail.alitools.pt:465 -quiet < /dev/null  # SMTP
```

Expected: Both connections succeed with SSL handshake.

## 6. IMAP Service Integration Test

Direct test of `IMAPService` class:

1. Initialize IMAPService with account
2. Get IMAP config via `account.get_imap_config(SECRET_KEY)`
3. **Connect:** `imap_service.connect(config)` → verify returns True
4. **Select folder:** `imap_service.select_folder('INBOX')` → verify success + message count
5. **Search emails:** `imap_service.search_emails('ALL', limit=5)` → verify returns email IDs list
6. **Fetch email:** `imap_service.fetch_email_by_id(email_ids[-1])` → verify returns email dict with subject
7. **Sync to database:** `imap_service.sync_account_emails(account, folder='INBOX', limit=10, since_last_sync=False)` → verify returns synced count > 0
8. **Disconnect:** `imap_service.disconnect()` → clean shutdown

## 7. API Blueprint Registration

Verify that `emails_inbox` blueprint is registered in the Flask app:

- Check `sendcraft/__init__.py` or `sendcraft/api/v1/__init__.py` for blueprint registration
- If not registered, register it before testing endpoints

## 8. Flask API Endpoint Testing

Start development server and test all endpoints:

**Start server:** `python3 rundev.py` (background process)

**Test endpoints:**

1. `GET /api/v1/emails/inbox/{account_id}?per_page=5` → List emails, verify response structure
2. `POST /api/v1/emails/inbox/sync/{account_id}` with body `{"folder":"INBOX","limit":20,"full_sync":true}` → Trigger sync, verify synced count
3. `GET /api/v1/emails/inbox/{account_id}/stats` → Get statistics (total, unread, flagged, with_attachments)
4. `GET /api/v1/emails/inbox/{account_id}/threads?limit=3` → Get email threads

**Cleanup:** Stop Flask server after tests.

## 9. Database Validation

Query database to verify synced data:

1. Get account by email `encomendas@alitools.pt`
2. Verify `last_sync` timestamp is updated
3. Count total emails: `EmailInbox.query.filter_by(account_id=account.id, is_deleted=False).count()`
4. Count unread emails: `EmailInbox.query.filter_by(account_id=account.id, is_read=False, is_deleted=False).count()`
5. Count flagged emails
6. Count emails with attachments
7. Fetch one sample email and display: subject, from_address, received_at

## 10. Final Validation Report

Generate comprehensive report showing:

- ✅ Branch: `cursor/implement-imap-backend-for-email-inbox-dcb3`
- ✅ Domain and account created successfully
- ✅ IMAP configuration verified
- ✅ SSL connectivity successful (IMAP + SMTP)
- ✅ Email sync working
- ✅ Emails stored in database
- 📊 Statistics: total emails, unread count, flagged count, with attachments
- 🎯 Status: COMPLETE - Ready for Phase 9.2 (Frontend Implementation)

## 11. Git Commit & Push

Create validation commit:

```
Phase 9.1 validation: IMAP backend tested and validated

- Database migration applied successfully  
- Real account encomendas@alitools.pt created and configured
- IMAP connectivity tested (mail.alitools.pt:993)
- Email sync working with EmailInbox model
- API endpoints responding correctly
- Ready for frontend implementation
```

Push to origin branch: `cursor/implement-imap-backend-for-email-inbox-dcb3`

### To-dos

- [ ] Checkout cursor/implement-imap-backend-for-email-inbox-dcb3 and verify complete implementations exist
- [ ] Install required Python packages (chardet, pymysql, cryptography, python-socketio, email-validator)
- [ ] Run flask db migrate and upgrade to apply IMAP schema changes
- [ ] Create alitools.pt domain and encomendas@alitools.pt account with real credentials
- [ ] Test SSL connectivity to mail.alitools.pt:993 (IMAP) and :465 (SMTP)
- [ ] Test IMAPService directly (connect, select, search, fetch, sync, disconnect)
- [ ] Start Flask server and test all API endpoints (list, sync, stats, threads)
- [ ] Verify synced emails are stored correctly in database with proper counts
- [ ] Generate comprehensive validation report and commit changes