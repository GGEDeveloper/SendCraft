# 🤖 SendCraft Agent Testing Prompt - Automated Validation

## 🎯 Copy-Paste Prompt para Agent Local

```markdown
SendCraft Phase 13 Enterprise Complete Testing - Browser MCP Automation

## Context:
SendCraft email management system has completed Phase 13A (rich email viewer), Phase 13B (attachments & security), and Phase 13C (external API). System is enterprise-grade with multi-account support, professional interface, and real IMAP synchronization working. Need comprehensive automated testing using browser MCP tools.

## Current System Status:
- ✅ Clean server startup without encryption errors
- ✅ Multi-account switching: geral@alitools.pt (ID 2) + geral@artnshine.pt (ID 3) 
- ✅ Real IMAP sync working: 7 emails in geral@artnshine.pt
- ✅ Database-driven email display (EmailInbox model)
- ✅ Professional three-pane interface implemented
- ✅ External API with Bearer authentication ready

## Task: Execute comprehensive browser testing with document creation (20 minutes)

### Prerequisites Verification:
```bash
# Verify server running:
ps aux | grep python  # Should show run_dev.py process
netstat -tlnp | grep :5000  # Should show Flask listening
curl -s http://localhost:5000 | grep -q "SendCraft" && echo "Server OK" || echo "Server DOWN"
```

### Phase 1: Create Test Documents for Attachment Testing (5 minutes)

Create comprehensive test documents in ~/Downloads/SendCraft-Testing/:

#### 1. SendCraft-Test-Report.pdf
```
SENDCRAFT ENTERPRISE EMAIL MANAGEMENT SYSTEM
Phase 13 Complete - Professional Testing Report

Generated: October 23, 2025, 13:30 WEST
Version: Enterprise Grade Complete
Status: Production Ready

SYSTEM CAPABILITIES IMPLEMENTED:
✅ Multi-Account Email Management Interface
✅ Rich HTML Email Rendering with Security Sanitization
✅ Professional Three-Pane Layout (Gmail/Outlook Style)
✅ Functional Attachment Download System
✅ Remote Image Privacy Controls (Blocked by Default)
✅ External REST API for Third-Party Integrations
✅ Real IMAP Email Synchronization with Database Storage
✅ Bearer Token Authentication for API Access
✅ Interactive API Documentation at /api/docs
✅ Enterprise-Grade Security and Performance

ACCOUNTS CONFIGURED AND OPERATIONAL:
- geral@alitools.pt (Account ID: 2, Status: Active)
- geral@artnshine.pt (Account ID: 3, Status: Active, Primary Test Account)

TECHNICAL ARCHITECTURE:
- Backend: Python Flask with SQLAlchemy ORM
- Database: MySQL Remote (dominios.pt) with optimized indexing
- Frontend: Bootstrap 5 + Custom CSS/JavaScript
- Email Services: IMAP/SMTP with cPanel VBS compatibility
- Security: HTML sanitization, API authentication, encrypted storage
- API: RESTful endpoints with comprehensive documentation

TESTING PURPOSE:
This PDF document serves as test attachment for validating
SendCraft Enterprise attachment download and file type detection
functionality. Expected to display with document icon and
download capability.

File Type: PDF
Expected Icon: Document/PDF icon
Expected Size: 2-4KB
Download Test: Should stream with proper Content-Disposition headers
```

#### 2. SendCraft-Feature-Summary.docx
Create Microsoft Word document with:
```
SendCraft Enterprise - Complete Feature Documentation

EMAIL CLIENT PROFESSIONAL FEATURES:
• Multi-account interface with seamless switching between accounts
• Professional three-pane layout inspired by Gmail and Outlook
• Rich HTML email rendering with comprehensive security sanitization
• Attachment handling with intelligent file type detection and icons
• Remote image privacy controls with user consent requirements
• Relative date formatting in Portuguese with full timestamp hover
• Email threading and conversation grouping capabilities
• Advanced search functionality with real-time filtering
• Professional email actions (reply, forward, flag, delete)
• Mobile responsive design with adaptive three-pane layout
• Email signature detection and enhanced formatting
• Quote text handling with proper indentation

BACKEND ARCHITECTURE & SERVICES:
• Modular Flask application with enterprise-grade structure
• SQLAlchemy ORM with MySQL database and optimized queries
• IMAPService for real email synchronization with duplicate detection
• SMTPService for reliable outbound email delivery
• Template system with dynamic variable substitution
• Comprehensive logging with structured error handling
• Database migrations and model relationships
• Security middleware and authentication layers

EXTERNAL API INTEGRATION CAPABILITIES:
• RESTful endpoints designed for third-party application integration
• Bearer token authentication system with API key management
• Template-based automated email sending for e-commerce workflows
• Direct email sending with full HTML and plain text support
• Account and template management endpoints for external apps
• Comprehensive rate limiting and access control mechanisms
• Interactive API documentation with live testing capabilities
• CORS support for web-based integrations and applications

SECURITY & PERFORMANCE FEATURES:
• HTML content sanitization preventing XSS and script injection
• API key authentication with request logging and monitoring
• Remote image blocking for privacy protection by default
• Encrypted password storage with environment-specific keys
• Database indexing for optimal query performance
• Efficient IMAP synchronization with minimal server impact
• Error handling with secure failure modes

Test document for Microsoft Word format attachment validation.
Expected Icon: Word document icon
Expected Size: 3-5KB
Download Test: Should preserve formatting and open in Word applications
```

#### 3. SendCraft-Test-Data.xlsx
Create Excel spreadsheet with 4 sheets:

**Sheet 1 - Account Configuration:**
| Account | Domain | Status | IMAP Server | Last Sync | Message Count |
|---------|--------|--------|-------------|-----------|---------------|
| geral@alitools.pt | alitools.pt | Active | mail.alitools.pt | 2025-10-23 | 0 |
| geral@artnshine.pt | artnshine.pt | Active | mail.artnshine.pt | 2025-10-23 | 7 |

**Sheet 2 - Email Statistics:**
| Metric | Count | Period | Last Updated |
|--------|-------|--------|-------------|
| Total Emails | 7 | All Time | 2025-10-23 13:30 |
| Unread Emails | 0 | Current | 2025-10-23 13:30 |
| Flagged Emails | 0 | Current | 2025-10-23 13:30 |
| With Attachments | 0 | Current | 2025-10-23 13:30 |

**Sheet 3 - Feature Test Results:**
| Feature | Status | Notes | Test Date |
|---------|--------|-------|----------|
| Multi-Account Switching | PASS | Seamless transitions | 2025-10-23 |
| Rich HTML Rendering | PASS | Professional styling | 2025-10-23 |
| Attachment Downloads | PENDING | Awaiting test attachments | 2025-10-23 |
| Remote Image Toggle | PASS | Privacy controls working | 2025-10-23 |
| Email Search | PASS | Real-time filtering | 2025-10-23 |

**Sheet 4 - Performance Metrics:**
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Homepage Load Time | <2s | <3s | PASS |
| Email Client Load | <3s | <5s | PASS |
| Email Selection Speed | <500ms | <1s | PASS |
| IMAP Sync Duration | <10s | <15s | PASS |
| Database Query Time | <100ms | <200ms | PASS |

#### 4. SendCraft-Interface-Screenshot.png
- Navigate to http://localhost:5000/emails/inbox/3
- Take high-quality screenshot showing:
  - Three-pane layout with email selected
  - Account switcher dropdown
  - Email content with rich formatting
  - Professional styling throughout
- Save as PNG format

#### 5. SendCraft-Logo.jpg
- Create or capture SendCraft branding image
- Professional logo/header representation
- JPEG format for broad compatibility
- Dimensions: 800x400 or similar professional ratio

#### 6. SendCraft-Test-Archive.zip
- Create ZIP file containing all above documents
- Include README.txt:
  ```
  SendCraft Enterprise Test Documents
  
  Contents:
  - SendCraft-Test-Report.pdf (System documentation)
  - SendCraft-Feature-Summary.docx (Feature overview)
  - SendCraft-Test-Data.xlsx (Statistics and metrics)
  - SendCraft-Interface-Screenshot.png (Interface capture)
  - SendCraft-Logo.jpg (Branding image)
  - README.txt (This file)
  
  Purpose: Test attachment functionality in SendCraft Enterprise
  Created: October 23, 2025
  Version: Phase 13 Complete
  ```

### Phase 2: Homepage & Navigation Testing (3 minutes)

1. **Navigate to http://localhost:5000**
   - Verify dashboard loads without errors
   - Check browser console for JavaScript errors
   - Validate statistics widgets show data

2. **Dashboard Content Verification:**
   - Domain count should show 2 domains (alitools.pt, artnshine.pt)
   - Account count should show 2 active accounts
   - Recent logs section present (may be empty)
   - Email statistics for last 24h

3. **Navigation Menu Testing:**
   - Click "Accounts" → verify /accounts loads with account list
   - Click "Domains" → verify /domains shows domain management
   - Click "Templates" → verify /templates loads (may be empty)
   - Click "Logs" → verify /logs interface loads
   - All navigation should be smooth without errors

4. **Responsive Design Check:**
   - Resize browser window to different sizes
   - Verify layout adapts appropriately
   - Test mobile view (width <768px)

5. **Take screenshot of homepage for documentation**

### Phase 3: Email Client Comprehensive Testing (10 minutes)

#### Multi-Account Interface Validation:
1. **Navigate to http://localhost:5000/emails/inbox**
   - Should default to first active account
   - Verify three-pane layout displays correctly
   - Check account switcher dropdown in header

2. **Account Switching Testing:**
   - Dropdown should show:
     - "geral@alitools.pt" 
     - "geral@artnshine.pt"
   - Click geral@alitools.pt → URL should change to /emails/inbox/2
   - Click geral@artnshine.pt → URL should change to /emails/inbox/3
   - Account info in left sidebar should update dynamically
   - Email list should refresh for selected account

3. **Email List Functionality:**
   - For geral@artnshine.pt (should have 7 emails from previous sync)
   - Email items should display in middle pane
   - Each email should show: sender, subject, date, status icons
   - Unread emails should have visual distinction
   - Emails with attachments should show paperclip icon
   - Click on email should highlight and load content in right pane

#### Rich Email Content Display (Phase 13A Validation):
1. **Select various email types:**
   - Click on HTML-formatted email (if available)
   - Verify rich rendering with preserved styling
   - Check that images show "Imagem bloqueada" placeholder
   - Select plain text email
   - Verify proper text formatting and line breaks

2. **Date Formatting Validation:**
   - Check emails show relative dates ("há X horas", "ontem", etc.)
   - Hover over date → should show full timestamp tooltip
   - Verify Portuguese language formatting

3. **Content Quality Check:**
   - HTML emails should preserve safe styling
   - Links should be styled but safe (no automatic opening)
   - Tables, lists, and formatting should render correctly
   - Email signatures should be visually distinct
   - Quote text (lines starting with ">") should be indented

#### Enhanced Email Actions (Phase 13B Validation):
1. **Email Synchronization:**
   - Click "Sincronizar" button in header
   - Watch browser network tab for API call to /api/v1/emails/inbox/sync/3
   - Should see toast notification about sync status
   - If no new emails: "No new emails" message expected
   - If new emails: "Synced X new emails" message

2. **Attachment Functionality:**
   - Find email with attachments (if any exist)
   - Verify attachment list shows below email content
   - Check file type icons display correctly
   - Verify file size formatting (KB, MB)
   - Click download buttons (may show API endpoint errors if not fully implemented)

3. **Email Action Buttons:**
   - Click "View Original" → should trigger download of .eml file
   - Click "Print" → should open browser print dialog with formatted email
   - Look for "Show Headers" button (may be placeholder)
   - Verify all buttons are styled consistently

4. **Remote Image Security:**
   - Find HTML email with embedded images (if available)
   - Images should show "Imagem bloqueada" placeholder by default
   - Click "Bloquear Imagens" button
   - Button text should toggle to "Ocultar Imagens Remotas"
   - Should see toast notification about image loading state

#### Navigation & Filtering Systems:
1. **Folder Navigation:**
   - Click different folders in left sidebar:
     - "Caixa de Entrada" (Inbox) - should be active
     - "Enviados" (Sent) - may be empty
     - "Rascunhos" (Drafts) - may be empty  
     - "Lixeira" (Trash) - may be empty
   - Verify folder highlighting and email count updates

2. **Filter Tab Testing:**
   - Click filter tabs above email list:
     - "Todos" (All) - should show all emails
     - "Não Lidos" (Unread) - filter to unread emails
     - "Marcados" (Flagged) - filter to flagged emails
     - "Com Anexos" (With Attachments) - filter to emails with attachments
   - Verify badge counts update appropriately
   - Check active filter highlighting

3. **Search Functionality:**
   - Click in search box at top of email list
   - Type partial email subject or sender name
   - Verify email list filters in real-time
   - Clear search → verify list returns to full view
   - Test search across different fields (subject, sender, content)

### Phase 4: API Documentation Testing (1 minute)
1. **Navigate to http://localhost:5000/api/docs**
   - Verify interactive documentation page loads
   - Check that endpoints are listed with examples
   - Look for authentication guide
   - Verify request/response format examples present
   - Take screenshot for documentation

### Phase 5: Test Email Preparation (1 minute)
1. **Prepare outbound test email:**
   - Recipient: mmelo.deb@gmail.com
   - Subject: "SendCraft Enterprise Validation Test - [current timestamp]"
   - HTML Content: 
     ```html
     <h1>✅ SendCraft Enterprise Email Management System</h1>
     <h2>Phase 13 Complete - All Features Operational</h2>
     
     <p><strong>System Status:</strong> Fully Functional ✅</p>
     
     <h3>Features Successfully Implemented:</h3>
     <ul>
         <li>✅ Multi-account email management interface</li>
         <li>✅ Rich HTML email rendering with security</li>
         <li>✅ Professional three-pane layout</li>
         <li>✅ Attachment download system</li>
         <li>✅ Remote image privacy controls</li>
         <li>✅ External API for integrations</li>
         <li>✅ Real IMAP synchronization</li>
     </ul>
     
     <h3>Testing Request:</h3>
     <p>Please reply to this email and attach the following test documents:</p>
     <ul>
         <li>PDF document (for document icon testing)</li>
         <li>Image file (JPG/PNG for image icon testing)</li>  
         <li>ZIP archive (for archive icon testing)</li>
         <li>Any other file types available</li>
     </ul>
     
     <p>This will enable validation of the complete attachment download and
     file type detection system in the SendCraft inbox interface.</p>
     
     <p><strong>Reply Subject Suggestion:</strong><br>
     "Re: SendCraft Enterprise Test - Attachment Response"</p>
     
     <hr>
     <p style="color: #666; font-size: 12px;">
     SendCraft Enterprise Email Management System<br>
     Generated: [timestamp]<br>
     Test Environment: Development (localhost:5000)
     </p>
     ```
   - Text Version: Plain text equivalent of above

2. **Note:** If compose interface not available, document for manual sending

### Success Criteria Validation:

✅ All test documents created successfully (PDF, DOCX, XLSX, PNG, JPG, ZIP)
✅ Homepage dashboard loads with real statistics and no errors
✅ Navigation between all sections (accounts, domains, templates, logs) functional
✅ Multi-account email client interface fully operational
✅ Account switching works smoothly between both accounts
✅ Email list displays stored database emails correctly
✅ Rich HTML email rendering from Phase 13A visible and working
✅ Attachment display system from Phase 13B shows icons and download buttons
✅ Remote image security toggle functional with state changes
✅ All folder navigation (Inbox, Sent, Drafts, Trash) working
✅ Filter tabs (Todos, Não Lidos, Marcados, Com Anexos) functional
✅ Search functionality provides real-time email filtering
✅ Email synchronization process functional with server logs
✅ API documentation accessible at /api/docs
✅ Test email prepared for mmelo.deb@gmail.com (if sending possible)
✅ No JavaScript console errors throughout testing
✅ Mobile responsive design adapts appropriately
✅ Professional appearance and user experience throughout

### Error Documentation Required:
If any issues found, document:
- Specific error messages or unexpected behavior
- Browser console errors (copy exact messages)
- UI elements that don't respond correctly
- Performance issues or slow loading
- Mobile responsiveness problems
- API endpoints that return errors
- Any functionality that doesn't work as expected

### Final Deliverables Expected:
1. ✅ Complete test document set created and saved
2. ✅ Screenshots of key interfaces (homepage, email client, mobile view)
3. ✅ Validation report with pass/fail status for each feature
4. ✅ Any issues identified with detailed descriptions
5. ✅ Performance observations and metrics
6. ✅ Test email sent to mmelo.deb@gmail.com (if possible)

Execute comprehensive SendCraft Enterprise testing with complete validation.
```

## 📋 Post-Testing Actions

### ✅ If All Tests Pass:
1. **Mark Phase 13 as validated**
2. **Prepare production deployment**
3. **Update project status to "Enterprise Ready"
4. **Plan AliTools integration timeline**
5. **Archive test results for reference**

### ❌ If Issues Found:
1. **Document all issues with details**
2. **Prioritize fixes by severity**
3. **Create GitHub issues for tracking**
4. **Plan resolution timeline**
5. **Schedule re-testing after fixes**

## 🚀 Next Steps After Validation

### Production Deployment
- **Deploy email.artnshine.pt** with validated code
- **Configure production API keys** for AliTools
- **Setup SSL certificates** and security
- **Performance monitoring** and logging

### AliTools Integration
- **API key generation** for AliTools.pt
- **Template creation** for order confirmations
- **Integration testing** with real orders
- **Production monitoring** setup

**Testing protocol ensures SendCraft Enterprise quality and reliability.**