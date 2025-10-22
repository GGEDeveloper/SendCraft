#!/usr/bin/env python3
"""Test direct IMAP connection to mail.alitools.pt"""
import imaplib
import ssl
import email
from email.header import decode_header

def test_imap_connection():
    """Test IMAP connection directly"""
    
    # Configuration
    server = 'mail.alitools.pt'
    port = 993
    username = 'encomendas@alitools.pt'
    password = '6f2zniWMN6aUFaD'
    
    print(f"🔌 Connecting to {server}:{port}...")
    
    try:
        # Create SSL context
        ssl_context = ssl.create_default_context()
        
        # Connect via SSL
        imap = imaplib.IMAP4_SSL(server, port, ssl_context=ssl_context)
        print("✅ SSL connection established")
        
        # Login
        imap.login(username, password)
        print(f"✅ Logged in as {username}")
        
        # List folders
        result, folders = imap.list()
        if result == 'OK':
            print("\n📁 Available folders:")
            for folder in folders[:5]:  # Show first 5
                print(f"  - {folder.decode()}")
        
        # Select INBOX
        result, data = imap.select('INBOX')
        if result == 'OK':
            num_messages = int(data[0])
            print(f"\n📧 INBOX has {num_messages} messages")
        
        # Search for recent emails
        result, data = imap.search(None, 'ALL')
        if result == 'OK':
            message_ids = data[0].split()
            print(f"📨 Found {len(message_ids)} emails")
            
            # Fetch last 3 emails
            for msg_id in message_ids[-3:]:
                result, data = imap.fetch(msg_id, '(RFC822)')
                if result == 'OK':
                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Decode subject
                    subject = msg.get('Subject', '')
                    decoded_subject = ''
                    if subject:
                        decoded_parts = decode_header(subject)
                        for part, encoding in decoded_parts:
                            if isinstance(part, bytes):
                                if encoding:
                                    decoded_subject += part.decode(encoding, errors='replace')
                                else:
                                    decoded_subject += part.decode('utf-8', errors='replace')
                            else:
                                decoded_subject += str(part)
                    
                    from_addr = msg.get('From', 'Unknown')
                    print(f"\n  Email #{msg_id.decode()}:")
                    print(f"    From: {from_addr}")
                    print(f"    Subject: {decoded_subject[:60]}")
        
        # Logout
        imap.logout()
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == '__main__':
    test_imap_connection()