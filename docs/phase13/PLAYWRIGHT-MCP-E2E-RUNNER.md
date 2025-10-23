# 🎭 SendCraft Playwright MCP E2E Testing Runner

## 🎯 Objectivo
Prompt completo para execução automatizada de testes end-to-end no browser usando Playwright MCP Server, incluindo criação de documentos de teste, screenshots, e relatório comprehensive.

## 🤖 COPY-PASTE PROMPT AGENT (Playwright MCP Active)

```markdown
SendCraft Phase 13 Complete E2E Testing - Playwright MCP Automation

## Context:
Execute comprehensive end-to-end browser testing for SendCraft email management system using Playwright MCP Server. System has Phase 13A (rich email viewer), 13B (attachments & security), and 13C (external API) implemented. Need full UI validation with document creation for attachment testing.

## Prerequisites:
- Playwright MCP Server active and connected
- SendCraft running on http://localhost:5000
- Two email accounts: geral@alitools.pt (ID 2), geral@artnshine.pt (ID 3)
- Development mode with remote MySQL (dominios.pt)

## Task: Execute comprehensive browser E2E testing (25 minutes)

### Phase 1: Environment Setup & Document Creation (8 minutes)

#### Browser Setup:
- Launch Chromium in headed mode
- Set viewport to 1440x900 (desktop)
- Create output directory: ~/Downloads/SendCraft-Testing/
- Create screenshots subdirectory: ~/Downloads/SendCraft-Testing/screenshots/

#### Test Documents Creation:
Create attachment test files in ~/Downloads/SendCraft-Testing/:

1. **SendCraft-Test-Report.pdf** (or .txt equivalent):
```
SENDCRAFT ENTERPRISE EMAIL MANAGEMENT SYSTEM
Phase 13 Complete - E2E Testing Report

Generated: [current timestamp]
Version: Enterprise Grade
Status: Production Ready

SYSTEM CAPABILITIES VALIDATED:
✅ Multi-Account Email Management Interface
✅ Rich HTML Email Rendering with Security Sanitization
✅ Professional Three-Pane Layout (Gmail/Outlook Style)
✅ Attachment Download System with File Type Detection
✅ Remote Image Privacy Controls (Blocked by Default)
✅ Real IMAP Email Synchronization with Database Storage
✅ External REST API with Bearer Authentication
✅ Interactive Documentation and Testing Interface

ACCOUNTS CONFIGURED:
- geral@alitools.pt (Account ID: 2, Status: Active)
- geral@artnshine.pt (Account ID: 3, Status: Active, 7 emails synced)

TECHNICAL STACK:
- Backend: Python Flask + SQLAlchemy ORM
- Database: MySQL Remote (dominios.pt)
- Frontend: Bootstrap 5 + Custom JavaScript
- Email: IMAP/SMTP with cPanel compatibility
- Security: HTML sanitization + API authentication

This PDF serves as test attachment for download functionality validation.
File Type: PDF | Expected Icon: Document | Expected Size: 2-4KB
```

2. **SendCraft-Feature-Summary.docx** (or .txt):
Complete feature documentation for Word format testing

3. **SendCraft-Test-Data.xlsx** (or .csv):
Spreadsheet with account data, statistics, and test metrics

4. **README.txt**:
```
SendCraft Enterprise Test Documents
Created: [timestamp]
Purpose: Attachment functionality validation

Files:
- SendCraft-Test-Report.pdf: System documentation
- SendCraft-Feature-Summary.docx: Feature overview
- SendCraft-Test-Data.xlsx: Metrics and statistics
- SendCraft-Interface-Screenshot.jpg: UI capture
- SendCraft-Test-Archive.tar.gz: Complete test bundle
```

5. **SendCraft-Test-Archive.tar.gz**: Compressed archive of all test files

### Phase 2: Homepage & Navigation Testing (5 minutes)

1. **Navigate to http://localhost:5000**
   - Wait for page load
   - Take screenshot: `homepage.png`
   - Check for dashboard statistics (selectors: .card, .stats-container)
   - Record any console errors

2. **Navigation Menu Testing:**
   - Click navigation links and verify pages load:
     - /accounts → screenshot: `accounts.png`
     - /domains → screenshot: `domains.png`
     - /templates → screenshot: `templates.png`
     - /logs → screenshot: `logs.png`
   - Record page load times and any errors

3. **Responsive Design Check:**
   - Resize window to 768px width
   - Verify layout adapts
   - Take screenshot: `homepage-tablet.png`
   - Return to 1440x900

### Phase 3: Email Client Core Testing (10 minutes)

#### Multi-Account Interface:
1. **Navigate to /emails/inbox**
   - Wait for complete page load
   - Take screenshot: `inbox-initial.png`
   - Verify three-pane layout structure:
     - Left sidebar (#emailSidebar)
     - Middle email list (#emailListPane)
     - Right content pane (#emailContentPane)

2. **Account Switcher Testing:**
   - Locate account dropdown (#accountSwitcher)
   - Take screenshot showing dropdown: `account-switcher.png`
   - Select geral@alitools.pt → verify URL changes to /emails/inbox/2
   - Take screenshot: `account-switch-id2.png`
   - Select geral@artnshine.pt → verify URL changes to /emails/inbox/3
   - Take screenshot: `account-switch-id3.png`

#### Email List & Content Testing:
1. **Email List Validation:**
   - Wait for email list to load (#emailItems)
   - Verify email items display (.email-item)
   - Count visible emails (should be 7 for geral@artnshine.pt)
   - Take screenshot: `email-list-loaded.png`

2. **Email Selection & Content:**
   - Click first email in list
   - Wait for content to load in right pane
   - Verify elements populated:
     - Subject (#emailSubject)
     - Sender info (#senderName, #senderEmail)
     - Date (#emailDate)
     - Email body (#emailBody)
   - Take screenshot: `email-opened.png`

### Phase 4: Advanced Features Testing (Phase 13A+B) (7 minutes)

#### Rich Content Display (13A):
1. **HTML Rendering Test:**
   - Select HTML-formatted email (if available)
   - Verify content renders with styling
   - Check images show "Imagem bloqueada" placeholder
   - Take screenshot: `html-email-rendering.png`

2. **Date Formatting Test:**
   - Check email dates in list show relative format
   - Hover over date to verify timestamp tooltip
   - Record if dates show "Invalid Date" or "há NaN anos" (bug)

#### Security & Actions Testing (13B):
1. **Remote Image Toggle:**
   - Locate toggle button (may be #toggleImagesBtn or similar)
   - Click toggle button
   - Verify state change and toast notification
   - Take screenshot: `remote-images-toggle.png`

2. **Email Actions:**
   - Test "Sincronizar" button (#syncEmailsBtn)
   - Wait for sync completion and toast
   - Take screenshot: `email-sync.png`
   - Test "View Original" button (if present)
   - Test "Print" button (if present)

3. **Attachment Display:**
   - Find email with attachments (if any)
   - Verify attachment list displays (#emailAttachments)
   - Check file type icons and download buttons
   - Take screenshot: `email-attachments.png`

#### Filter & Search Testing:
1. **Filter Tabs:**
   - Test filter tabs: Todos, Não Lidos, Marcados, Com Anexos
   - Click "Com Anexos" → verify filter applies correctly
   - Record if filtering works or shows all emails (potential bug)
   - Take screenshot: `email-filters.png`

2. **Search Functionality:**
   - Use search box (#searchInput)
   - Enter partial email subject or sender
   - Verify email list filters in real-time
   - Clear search and verify list returns to full
   - Take screenshot: `email-search.png`

### Phase 5: Mobile & Responsive Testing (3 minutes)

1. **Mobile Viewport:**
   - Change viewport to 390x844 (iPhone-like)
   - Navigate to /emails/inbox/3
   - Verify mobile layout adaptation
   - Test sidebar toggle/collapse (if available)
   - Take screenshot: `inbox-mobile.png`

2. **Touch Interactions:**
   - Test email selection on mobile
   - Verify content pane behavior
   - Take screenshot: `mobile-email-open.png`

3. **Return to Desktop:**
   - Reset viewport to 1440x900

### Phase 6: Documentation & Reporting (2 minutes)

#### Final Screenshots:
1. **Interface Showcase:**
   - Open best-looking email with content
   - Take high-quality screenshot: `SendCraft-Interface-Screenshot.jpg`
   - Replace placeholder file created earlier

#### Comprehensive Report:
Create `SendCraft-Phase13-UI-E2E-Report.md` with:

```markdown
# SendCraft Phase 13 E2E Testing Report

## Test Environment
- Date: [timestamp]
- Browser: Chromium (Playwright)
- Viewport: 1440x900 → 390x844 (mobile)
- URL: http://localhost:5000
- Accounts: geral@alitools.pt (ID 2), geral@artnshine.pt (ID 3)

## Test Results Summary
- Total Tests: 24
- Passed: [count]
- Failed: [count]
- Pass Rate: [percentage]%

## Detailed Results

### Homepage & Navigation
- [ ] Homepage loads with statistics
- [ ] Navigation menu functional (/accounts, /domains, /templates, /logs)
- [ ] Responsive design working
- [ ] No critical console errors

### Email Client Interface  
- [ ] Three-pane layout displays correctly
- [ ] Account switcher shows both accounts
- [ ] Account switching changes URLs (ID 2 ↔ ID 3)
- [ ] Email list loads with stored emails (7 for artnshine.pt)
- [ ] Email selection shows content in right pane

### Phase 13A Features
- [ ] HTML email rendering with sanitization
- [ ] Date formatting (relative Portuguese dates)
- [ ] Email content styling professional
- [ ] Typography and layout enhanced

### Phase 13B Features
- [ ] Remote image toggle functional
- [ ] Attachment display with file type icons
- [ ] Email sync button working with toast notifications
- [ ] View Original and Print buttons functional
- [ ] Security controls active (images blocked by default)

### Advanced Functionality
- [ ] Email filtering (Todos, Não Lidos, Marcados, Com Anexos)
- [ ] Search functionality with real-time filtering
- [ ] Folder navigation (Inbox, Sent, Drafts, Trash)
- [ ] Mobile responsive design (390x844)

## Issues Identified
[List any bugs or problems found]

## Performance Observations
[Note page load times, interaction responsiveness]

## Console Messages
[List any JavaScript errors or warnings]

## Network Activity
[Summary of API calls and response times]

## Screenshots Index
[List all screenshots taken with descriptions]

## Recommendations
[Suggestions for improvements or fixes needed]

## Conclusion
[Overall assessment of system readiness]
```

#### Evidence Collection:
1. **Console Messages:**
   - Collect all console errors, warnings, and logs
   - Include in report with timestamps

2. **Network Activity:**
   - Record API calls made during testing
   - Note response times and status codes
   - Include successful /api/v1/emails/inbox/* calls

3. **Performance Metrics:**
   - Page load times
   - JavaScript interaction response times
   - Email list loading speed
   - Account switching speed

### Success Criteria:

✅ All test documents created successfully
✅ Homepage and navigation fully functional (no critical errors)
✅ Multi-account email client operational with switching
✅ Email list displays stored emails correctly
✅ Email content renders with proper formatting
✅ Phase 13A features working (rich rendering, dates)
✅ Phase 13B features working (attachments, security toggles)
✅ Filter and search functionality operational
✅ Mobile responsive design adapts appropriately
✅ No critical JavaScript console errors
✅ Professional appearance maintained throughout
✅ Screenshots captured for all key interfaces
✅ Comprehensive report generated with findings

### Expected Deliverables:

1. **Test Documents:** PDF/DOCX/XLSX or text equivalents for attachment testing
2. **Screenshots:** 15+ images documenting interface and functionality
3. **Test Report:** Detailed Markdown report with pass/fail results
4. **Console Logs:** JavaScript errors and warnings collected
5. **Performance Data:** Load times and interaction metrics
6. **Mobile Validation:** Responsive design verification
7. **Issue Documentation:** Any bugs or problems identified with details

Execute comprehensive SendCraft Phase 13 E2E testing with Playwright MCP automation.
```

---

## 📋 **EXECUTION INSTRUCTIONS**

### **STEP 1: Run Playwright E2E Testing**
1. Ensure SendCraft running: `python run_dev.py`
2. Copy prompt above and paste in agent with Playwright MCP
3. Wait for completion (~25 minutes)
4. Review results in ~/Downloads/SendCraft-Testing/

### **STEP 2: Critical Fixes (if needed)**
Based on E2E results, apply fixes for:
- Date parsing issues ("Invalid Date" → Portuguese relatives)
- Filter logic issues ("Com Anexos" not filtering)

### **STEP 3: Re-validation**
- Run E2E testing again after fixes
- Achieve 100% pass rate (24/24 tests)

**Comprehensive automated testing protocol for SendCraft Enterprise ready!**