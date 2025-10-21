-- SendCraft IMAP Support Migration
-- Adds IMAP fields to email_accounts and creates email_inbox table
-- Date: 2025-10-21

-- Add IMAP configuration columns to email_accounts table
ALTER TABLE email_accounts 
ADD COLUMN imap_server VARCHAR(200) DEFAULT 'mail.alitools.pt',
ADD COLUMN imap_port INT DEFAULT 993,
ADD COLUMN imap_use_ssl BOOLEAN DEFAULT TRUE,
ADD COLUMN imap_use_tls BOOLEAN DEFAULT FALSE,
ADD COLUMN last_sync DATETIME NULL,
ADD COLUMN auto_sync_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN sync_interval_minutes INT DEFAULT 5;

-- Create email_inbox table for storing received emails
CREATE TABLE IF NOT EXISTS email_inbox (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Account relationship
    account_id INT NOT NULL,
    
    -- Unique identifiers
    message_id VARCHAR(500),
    uid VARCHAR(100),
    
    -- Email addresses
    from_address VARCHAR(200) NOT NULL,
    from_name VARCHAR(200),
    to_address TEXT,
    cc_addresses TEXT,
    bcc_addresses TEXT,
    reply_to VARCHAR(200),
    
    -- Content
    subject VARCHAR(500),
    body_text LONGTEXT,
    body_html LONGTEXT,
    
    -- Timestamps
    received_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Status flags
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    is_flagged BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    is_answered BOOLEAN NOT NULL DEFAULT FALSE,
    is_draft BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Attachments
    has_attachments BOOLEAN NOT NULL DEFAULT FALSE,
    attachments_json TEXT,
    attachment_count INT DEFAULT 0,
    
    -- Metadata
    raw_headers TEXT,
    size_bytes INT DEFAULT 0,
    
    -- Threading
    thread_id VARCHAR(200),
    in_reply_to VARCHAR(500),
    `references` TEXT,
    
    -- Organization
    folder VARCHAR(100) DEFAULT 'INBOX',
    labels TEXT,
    priority INT DEFAULT 3,
    
    -- Foreign key constraint
    FOREIGN KEY (account_id) REFERENCES email_accounts(id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_message_id (message_id),
    INDEX idx_from_address (from_address),
    INDEX idx_subject (subject),
    INDEX idx_received_at (received_at),
    INDEX idx_is_read (is_read),
    INDEX idx_has_attachments (has_attachments),
    INDEX idx_thread_id (thread_id),
    INDEX idx_folder (folder)
);

-- Create composite indexes for better performance
CREATE INDEX idx_account_received ON email_inbox(account_id, received_at);
CREATE INDEX idx_account_folder ON email_inbox(account_id, folder);
CREATE INDEX idx_account_read ON email_inbox(account_id, is_read);
CREATE INDEX idx_account_thread ON email_inbox(account_id, thread_id);
CREATE UNIQUE INDEX idx_message_unique ON email_inbox(account_id, message_id);

-- Update existing encomendas@alitools.pt account if exists
UPDATE email_accounts 
SET imap_server = 'mail.alitools.pt',
    imap_port = 993,
    imap_use_ssl = TRUE,
    imap_use_tls = FALSE,
    auto_sync_enabled = TRUE,
    sync_interval_minutes = 5
WHERE email_address = 'encomendas@alitools.pt';