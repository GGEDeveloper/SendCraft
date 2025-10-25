# 🚀 PROMPT CLAUDE 4.1 OPUS MAX - FRONTEND COMPLETE

SendCraft Phase 9.2 - Modern Three-Pane Email Client Interface

## Context:
I have a fully functional IMAP backend for SendCraft with:
- EmailInbox model with all fields (message_id, from_address, subject, body_text, body_html, etc.)
- Working API endpoints at /api/v1/emails/inbox/ 
- Account configured: encomendas@alitools.pt
- Database ready with email sync capability

**Current Project Structure:**
- Flask app with Jinja2 templates
- Bootstrap 5 design system already integrated
- Existing CSS: sendcraft/static/css/main.css
- JavaScript patterns established
- Portuguese language interface

**Available API Endpoints:**
- GET /api/v1/emails/inbox/{account_id} - List emails (pagination, filters)
- POST /api/v1/emails/inbox/sync/{account_id} - Trigger email sync
- GET /api/v1/emails/inbox/{account_id}/stats - Email statistics
- PUT /api/v1/emails/inbox/{account_id}/{email_id}/read - Mark as read
- DELETE /api/v1/emails/inbox/{account_id}/{email_id} - Delete email

## Task: Create Complete Three-Pane Email Client

### 1. MAIN TEMPLATE: sendcraft/templates/emails/inbox.html

Create modern three-pane Gmail-style interface with:
- LEFT SIDEBAR: Account info, sync button, email stats, folders (Inbox/Sent/Trash)
- MIDDLE PANE: Email list with search, filters (All/Unread/Flagged/Attachments), pagination
- RIGHT PANE: Email content viewer with actions (read/flag/delete)

Requirements:
- Bootstrap 5 responsive design
- Portuguese language
- Loading states and error handling
- Empty states for no emails
- Mobile-responsive collapsible panes

### 2. CSS STYLING: sendcraft/static/css/email-client.css

Create complete responsive CSS for:
- Three-pane layout using flexbox
- Professional business email appearance
- Hover states and animations
- Mobile responsive breakpoints
- Email item states (read/unread/flagged)
- Modern design matching SendCraft theme

### 3. JAVASCRIPT CLIENT: sendcraft/static/js/email-client.js

Create complete EmailClient class with:
- AJAX integration with all API endpoints
- Real-time email loading and pagination
- Email selection and content display
- Sync functionality with progress indicators
- Email actions (mark read, flag, delete)
- Search and filtering
- Auto-sync every 5 minutes
- Error handling and notifications
- Mobile touch support

Key methods needed:
- loadEmailList(), selectEmail(), syncEmails()
- markAsRead(), toggleFlag(), deleteEmail()
- setupEventListeners(), renderEmailContent()

### 4. WEB ROUTE: Add to sendcraft/routes/web.py

Add route for email inbox page:
```python
@web_bp.route('/emails/inbox')
def emails_inbox():
    from ..models.account import EmailAccount
    account = EmailAccount.query.filter_by(
        email_address='encomendas@alitools.pt',
        is_active=True
    ).first()
    
    if not account:
        flash('Nenhuma conta de email configurada.', 'warning')
        return redirect(url_for('web.dashboard'))
    
    return render_template('emails/inbox.html', 
                         account=account,
                         page_title=f'Email Inbox - {account.email_address}')
```

### 5. NAVIGATION UPDATE: In sendcraft/templates/base.html

Add email client link to existing navigation menu.

## Implementation Requirements:

- Follow existing SendCraft Bootstrap 5 design patterns
- Portuguese language interface throughout
- Responsive three-pane layout (sidebar + list + content)
- Real-time email functionality via AJAX
- Professional business email client appearance
- Error handling and loading states for all operations
- Integration with existing navigation system
- Mobile-responsive design
- Toast notifications for user feedback

Create a complete, modern email client interface that integrates seamlessly with the existing SendCraft system and provides full email management functionality for the encomendas@alitools.pt account.