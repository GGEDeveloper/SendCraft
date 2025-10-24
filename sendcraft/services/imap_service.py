"""Serviço IMAP para SendCraft - Implementação Completa."""
import imaplib
import email
import ssl
import re
import hashlib
import json
import chardet
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime, parseaddr
from email.message import EmailMessage

from ..models import EmailAccount, EmailInbox
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)


class IMAPService:
    """Serviço completo para operações IMAP."""
    
    def __init__(self, account: EmailAccount = None):
        """
        Inicializa serviço IMAP.
        
        Args:
            account: Conta de email para operações
        """
        self.account = account
        self.connection = None
        self.is_connected = False
        self.selected_folder = None
    
    def connect(self, config: Dict[str, Any] = None) -> bool:
        """
        Conecta ao servidor IMAP usando configuração cPanel VBS (60s timeout + socket options).
        
        Args:
            config: Configuração IMAP (opcional, usa account se não fornecido)
            
        Returns:
            True se conectou com sucesso
        """
        import socket
        
        try:
            # Usar config fornecido ou do account
            if not config and self.account:
                from flask import current_app
                encryption_key = current_app.config.get('SECRET_KEY', '')
                config = self.account.get_imap_config(encryption_key)
            
            if not config:
                logger.error("No IMAP configuration provided")
                return False
            
            server = config.get('server', 'mail.localhost')
            port = config.get('port', 993)
            username = config.get('username')
            password = config.get('password')
            use_ssl = config.get('use_ssl', True)
            use_tls = config.get('use_tls', False)
            
            logger.info(f"🔗 Connecting to {server}:{port} as {username} (cPanel VBS mode)")
            
            # PRIMARY: SSL/TLS connection (993 from cPanel VBS)
            if use_ssl:
                try:
                    # Criar contexto SSL seguro (cPanel compatible)
                    ssl_context = ssl.create_default_context()
                    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
                    ssl_context.check_hostname = True
                    ssl_context.verify_mode = ssl.CERT_REQUIRED
                    
                    # Create SSL connection
                    self.connection = imaplib.IMAP4_SSL(server, port, ssl_context=ssl_context)
                    
                    # CRITICAL: Apply cPanel timeout (60 seconds from VBS: 0000003c hex)
                    self.connection.sock.settimeout(60)
                    
                    # CRITICAL: Apply cPanel socket options (Windows Live Mail settings)
                    self.connection.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    if hasattr(socket, 'TCP_NODELAY'):
                        self.connection.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    
                    # Authenticate
                    result = self.connection.login(username, password)
                    
                    if result[0] == 'OK':
                        self.is_connected = True
                        logger.info("✅ IMAP connected with cPanel VBS settings (SSL 60s timeout)")
                        return True
                        
                except (socket.timeout, ssl.SSLError, ConnectionResetError) as e:
                    logger.warning(f"SSL connection failed: {e}")
                    logger.info("🔄 Trying cPanel STARTTLS fallback (port 143)...")
                    
                    # FALLBACK: STARTTLS configuration (from non-SSL VBS file)
                    return self._connect_starttls_cpanel(server, username, password)
                    
            else:
                # Non-SSL connection with STARTTLS
                return self._connect_starttls_cpanel(server, username, password)
            
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP error during connection: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            self.is_connected = False
            return False
    
    def _connect_starttls_cpanel(self, server: str, username: str, password: str) -> bool:
        """
        Fallback to STARTTLS using cPanel non-SSL VBS settings (port 143).
        
        Args:
            server: IMAP server hostname
            username: Username for authentication
            password: Password for authentication
            
        Returns:
            True if connection successful
        """
        import socket
        
        try:
            logger.info("📡 Connecting via STARTTLS (port 143)...")
            
            # Connect to port 143 (non-SSL from VBS)
            self.connection = imaplib.IMAP4(server, 143)
            
            # Apply same 60s timeout as SSL version
            self.connection.sock.settimeout(60)
            self.connection.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            if hasattr(socket, 'TCP_NODELAY'):
                self.connection.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            # Start TLS
            self.connection.starttls()
            
            # Login
            result = self.connection.login(username, password)
            
            if result[0] == 'OK':
                self.is_connected = True
                logger.info("✅ IMAP connected via STARTTLS (143) with cPanel settings")
                return True
                
        except Exception as e:
            logger.error(f"STARTTLS fallback failed: {e}")
            
        return False
    
    def disconnect(self) -> None:
        """Desconecta do servidor IMAP."""
        try:
            if self.connection and self.is_connected:
                try:
                    self.connection.close()
                except:
                    pass
                self.connection.logout()
                logger.info("Disconnected from IMAP server")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
        finally:
            self.connection = None
            self.is_connected = False
            self.selected_folder = None
    
    def select_folder(self, folder: str = 'INBOX') -> Tuple[bool, int]:
        """
        Seleciona pasta IMAP.
        
        Args:
            folder: Nome da pasta
            
        Returns:
            Tuple (sucesso, número de mensagens)
        """
        if not self.is_connected:
            logger.error("Not connected to IMAP server")
            return False, 0
        
        try:
            # Selecionar pasta
            result, data = self.connection.select(folder)
            
            if result == 'OK':
                self.selected_folder = folder
                # Extrair número de mensagens
                num_messages = int(data[0]) if data and data[0] else 0
                logger.info(f"Selected folder '{folder}' with {num_messages} messages")
                return True, num_messages
            else:
                logger.error(f"Failed to select folder '{folder}': {result}")
                return False, 0
                
        except Exception as e:
            logger.error(f"Error selecting folder '{folder}': {e}")
            return False, 0
    
    def list_folders(self) -> List[str]:
        """
        Lista todas as pastas IMAP.
        
        Returns:
            Lista de nomes de pastas
        """
        if not self.is_connected:
            logger.error("Not connected to IMAP server")
            return []
        
        try:
            result, data = self.connection.list()
            
            if result == 'OK':
                folders = []
                for item in data:
                    if isinstance(item, bytes):
                        # Parse folder line
                        try:
                            # Decodificar e extrair nome da pasta
                            folder_line = item.decode('utf-8', errors='ignore')
                            # Procurar nome da pasta entre aspas
                            match = re.search(r'"([^"]+)"$', folder_line)
                            if match:
                                folders.append(match.group(1))
                            else:
                                # Tentar pegar última palavra
                                parts = folder_line.split()
                                if parts:
                                    folders.append(parts[-1].strip('"'))
                        except:
                            continue
                return folders
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error listing folders: {e}")
            return []
    
    def search_emails(
        self, 
        criteria: str = 'ALL',
        limit: int = 50,
        since_date: Optional[datetime] = None
    ) -> List[str]:
        """
        Busca emails baseado em critério IMAP.
        
        Args:
            criteria: Critério de busca IMAP
            limit: Limite de resultados
            since_date: Buscar apenas após esta data
            
        Returns:
            Lista de IDs de email
        """
        if not self.is_connected or not self.selected_folder:
            logger.error("Not connected or no folder selected")
            return []
        
        try:
            # Construir critério com data se fornecida
            if since_date:
                date_str = since_date.strftime("%d-%b-%Y")
                if criteria == 'ALL':
                    criteria = f'SINCE {date_str}'
                else:
                    criteria = f'({criteria}) SINCE {date_str}'
            
            # Buscar emails
            result, data = self.connection.search(None, criteria)
            
            if result == 'OK':
                message_ids = data[0].split() if data[0] else []
                
                # Aplicar limite (pegar os mais recentes)
                if len(message_ids) > limit:
                    message_ids = message_ids[-limit:]
                
                logger.info(f"Found {len(message_ids)} emails matching criteria")
                return [id.decode('utf-8') if isinstance(id, bytes) else str(id) for id in message_ids]
            else:
                logger.error(f"Search failed: {result}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []
    
    def fetch_email_by_id(self, email_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca email específico por ID.
        
        Args:
            email_id: ID do email no servidor IMAP
            
        Returns:
            Dados do email ou None
        """
        if not self.is_connected or not self.selected_folder:
            logger.error("Not connected or no folder selected")
            return None
        
        try:
            # Buscar email completo (RFC822)
            result, data = self.connection.fetch(email_id, '(RFC822 FLAGS)')
            
            if result == 'OK' and data and data[0]:
                # Extrair email e flags
                if isinstance(data[0], tuple):
                    raw_email = data[0][1]
                    # Extrair flags se disponíveis
                    flags_match = re.search(rb'FLAGS \(([^)]*)\)', data[0][0])
                    flags = flags_match.group(1).decode() if flags_match else ''
                else:
                    raw_email = data[0]
                    flags = ''
                
                # Parse email
                email_data = self.parse_email_message(raw_email, email_id)
                
                # Adicionar flags
                if email_data and flags:
                    email_data['is_read'] = '\\Seen' in flags
                    email_data['is_flagged'] = '\\Flagged' in flags
                    email_data['is_answered'] = '\\Answered' in flags
                    email_data['is_draft'] = '\\Draft' in flags
                
                return email_data
            else:
                logger.error(f"Failed to fetch email {email_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching email {email_id}: {e}")
            return None
    
    def parse_email_message(self, raw_email: bytes, email_id: str = None) -> Dict[str, Any]:
        """
        Parseia mensagem de email raw (RFC822 completo).
        
        Args:
            raw_email: Email raw em bytes
            email_id: ID do email no servidor
            
        Returns:
            Dicionário com dados do email parseados
        """
        try:
            # Parse email RFC822
            msg = email.message_from_bytes(raw_email)
            
            # Extrair Message-ID
            message_id = msg.get('Message-ID', '')
            if message_id:
                message_id = message_id.strip('<>')
            else:
                # Gerar Message-ID único se não existir
                message_id = hashlib.md5(raw_email[:1000]).hexdigest() + '@local'
            
            # Extrair e decodificar subject
            subject = self._decode_header(msg.get('Subject', ''))
            
            # Extrair e parsear endereços
            from_header = msg.get('From', '')
            from_name, from_address = parseaddr(from_header)
            from_name = self._decode_header(from_name) if from_name else from_address
            
            # To, CC, BCC
            to_header = msg.get('To', '')
            cc_header = msg.get('Cc', '')
            bcc_header = msg.get('Bcc', '')
            reply_to = msg.get('Reply-To', '')
            
            # Data de recebimento
            date_header = msg.get('Date', '')
            received_at = None
            if date_header:
                try:
                    received_at = parsedate_to_datetime(date_header)
                except:
                    received_at = datetime.utcnow()
            else:
                received_at = datetime.utcnow()
            
            # Extrair corpo e anexos
            body_text = ''
            body_html = ''
            attachments = []
            
            # Processar todas as partes do email
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition', ''))
                
                # Pular containers multipart
                if part.get_content_maintype() == 'multipart':
                    continue
                
                # Verificar se é anexo
                if 'attachment' in content_disposition or 'inline' in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        filename = self._decode_header(filename)
                        payload = part.get_payload(decode=True)
                        attachments.append({
                            'filename': filename,
                            'content_type': content_type,
                            'size': len(payload) if payload else 0,
                            'content_id': part.get('Content-ID', '').strip('<>')
                        })
                    continue
                
                # Processar corpo do email
                if content_type == 'text/plain' and not body_text:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset()
                        if not charset:
                            # Detectar charset automaticamente
                            detected = chardet.detect(payload)
                            charset = detected.get('encoding', 'utf-8')
                        try:
                            body_text = payload.decode(charset, errors='replace')
                        except:
                            body_text = payload.decode('utf-8', errors='replace')
                
                elif content_type == 'text/html' and not body_html:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset()
                        if not charset:
                            detected = chardet.detect(payload)
                            charset = detected.get('encoding', 'utf-8')
                        try:
                            body_html = payload.decode(charset, errors='replace')
                        except:
                            body_html = payload.decode('utf-8', errors='replace')
            
            # Threading information
            in_reply_to = msg.get('In-Reply-To', '').strip('<>')
            references = msg.get('References', '')
            
            # Gerar thread_id baseado em subject e referências
            thread_id = self._generate_thread_id(subject, in_reply_to, references)
            
            # Prioridade
            priority = 3  # Normal
            x_priority = msg.get('X-Priority', '3')
            if x_priority:
                try:
                    priority = int(x_priority[0])
                except:
                    priority = 3
            
            # Criar dicionário com todos os dados
            return {
                'uid': email_id,
                'message_id': message_id,
                'from_address': from_address,
                'from_name': from_name,
                'to_address': to_header,
                'cc_addresses': cc_header,
                'bcc_addresses': bcc_header,
                'reply_to': reply_to,
                'subject': subject,
                'body_text': body_text.strip(),
                'body_html': body_html.strip(),
                'received_at': received_at,
                'has_attachments': len(attachments) > 0,
                'attachments': attachments,
                'attachment_count': len(attachments),
                'in_reply_to': in_reply_to,
                'references': references,
                'thread_id': thread_id,
                'is_read': False,  # Será atualizado com FLAGS
                'is_flagged': False,
                'is_answered': False,
                'is_draft': False,
                'priority': priority,
                'size_bytes': len(raw_email),
                'raw_headers': str(msg.items())[:2000]  # Limitar tamanho
            }
            
        except Exception as e:
            logger.error(f"Error parsing email: {e}")
            return None
    
    def fetch_recent_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca emails recentes do servidor.
        
        Args:
            limit: Número máximo de emails
            
        Returns:
            Lista de emails parseados
        """
        if not self.is_connected:
            logger.error("Not connected to IMAP server")
            return []
        
        try:
            # Selecionar INBOX se não estiver selecionado
            if not self.selected_folder:
                success, _ = self.select_folder('INBOX')
                if not success:
                    return []
            
            # Buscar IDs de emails recentes
            email_ids = self.search_emails('ALL', limit=limit)
            
            if not email_ids:
                logger.info("No emails found")
                return []
            
            emails = []
            for email_id in reversed(email_ids):  # Mais recente primeiro
                email_data = self.fetch_email_by_id(email_id)
                if email_data:
                    email_data['folder'] = self.selected_folder
                    emails.append(email_data)
            
            logger.info(f"Fetched {len(emails)} emails")
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching recent emails: {e}")
            return []
    
    def sync_account_emails(
        self, 
        account: EmailAccount = None,
        folder: str = 'INBOX',
        limit: int = 50,
        since_last_sync: bool = True
    ) -> int:
        """
        Sincroniza emails da conta com banco de dados.
        
        Args:
            account: Conta para sincronizar
            folder: Pasta IMAP
            limit: Limite de emails
            since_last_sync: Se deve sincronizar apenas desde última sync
            
        Returns:
            Número de emails sincronizados
        """
        account = account or self.account
        if not account:
            logger.error("No account provided for sync")
            return 0
        
        try:
            # Conectar se necessário
            if not self.is_connected:
                from flask import current_app
                encryption_key = current_app.config.get('SECRET_KEY', '')
                config = account.get_imap_config(encryption_key)
                if not self.connect(config):
                    return 0
            
            # Selecionar pasta
            success, _ = self.select_folder(folder)
            if not success:
                return 0
            
            # Determinar data de busca
            since_date = None
            if since_last_sync and account.last_sync:
                since_date = account.last_sync
            
            # Buscar emails
            email_ids = self.search_emails('ALL', limit=limit, since_date=since_date)
            
            if not email_ids:
                logger.info(f"No new emails for account {account.email_address}")
                account.update_last_sync()
                return 0
            
            synced_count = 0
            
            for email_id in email_ids:
                try:
                    # Buscar dados do email
                    email_data = self.fetch_email_by_id(email_id)
                    if not email_data:
                        continue
                    
                    # Verificar se já existe no banco
                    existing = EmailInbox.get_by_message_id(
                        account.id, 
                        email_data['message_id']
                    )
                    
                    if existing:
                        # Atualizar flags se mudaram
                        updated = False
                        if existing.is_read != email_data.get('is_read', False):
                            existing.is_read = email_data['is_read']
                            updated = True
                        if existing.is_flagged != email_data.get('is_flagged', False):
                            existing.is_flagged = email_data['is_flagged']
                            updated = True
                        if existing.uid != email_id:
                            existing.uid = email_id
                            updated = True
                        
                        if updated:
                            existing.save(commit=False)
                        continue
                    
                    # Criar novo registro
                    email_data['account_id'] = account.id
                    email_data['folder'] = folder
                    
                    # Converter attachments para JSON
                    if 'attachments' in email_data:
                        email_data['attachments_json'] = json.dumps(email_data['attachments'])
                        del email_data['attachments']
                    
                    inbox_email = EmailInbox(**email_data)
                    db.session.add(inbox_email)
                    synced_count += 1
                    
                    logger.debug(f"Synced email: {email_data.get('subject', 'No subject')[:50]}")
                    
                except Exception as e:
                    logger.error(f"Error syncing email {email_id}: {e}")
                    continue
            
            # Commit todas as mudanças
            if synced_count > 0:
                db.session.commit()
                logger.info(f"Synced {synced_count} new emails for {account.email_address}")
            
            # Atualizar última sincronização
            account.update_last_sync()
            
            return synced_count
            
        except Exception as e:
            logger.error(f"Error during email sync for {account.email_address}: {e}")
            db.session.rollback()
            return 0
    
    def mark_as_read(self, email_id: str, mark_read: bool = True) -> bool:
        """
        Marca email como lido/não lido no servidor IMAP.
        
        Args:
            email_id: ID do email
            mark_read: True para marcar como lido
            
        Returns:
            True se sucesso
        """
        if not self.is_connected:
            return False
        
        try:
            flag_command = '+FLAGS' if mark_read else '-FLAGS'
            result, _ = self.connection.store(email_id, flag_command, '\\Seen')
            return result == 'OK'
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
            return False
    
    def mark_as_flagged(self, email_id: str, flagged: bool = True) -> bool:
        """
        Marca email como favorito/importante.
        
        Args:
            email_id: ID do email
            flagged: True para marcar
            
        Returns:
            True se sucesso
        """
        if not self.is_connected:
            return False
        
        try:
            flag_command = '+FLAGS' if flagged else '-FLAGS'
            result, _ = self.connection.store(email_id, flag_command, '\\Flagged')
            return result == 'OK'
        except Exception as e:
            logger.error(f"Error flagging email: {e}")
            return False
    
    def delete_email(self, email_id: str, expunge: bool = False) -> bool:
        """
        Marca email para deleção.
        
        Args:
            email_id: ID do email
            expunge: Se deve expurgar imediatamente
            
        Returns:
            True se sucesso
        """
        if not self.is_connected:
            return False
        
        try:
            # Marcar como deletado
            result, _ = self.connection.store(email_id, '+FLAGS', '\\Deleted')
            
            if result == 'OK' and expunge:
                # Expurgar emails deletados
                self.connection.expunge()
            
            return result == 'OK'
        except Exception as e:
            logger.error(f"Error deleting email: {e}")
            return False
    
    def move_email(self, email_id: str, target_folder: str) -> bool:
        """
        Move email para outra pasta.
        
        Args:
            email_id: ID do email
            target_folder: Pasta de destino
            
        Returns:
            True se sucesso
        """
        if not self.is_connected:
            return False
        
        try:
            # Copiar para nova pasta
            result, _ = self.connection.copy(email_id, target_folder)
            
            if result == 'OK':
                # Marcar como deletado na pasta atual
                self.delete_email(email_id, expunge=True)
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error moving email: {e}")
            return False
    
    def _decode_header(self, header_value: str) -> str:
        """
        Decodifica cabeçalho de email corretamente.
        
        Args:
            header_value: Valor do cabeçalho
            
        Returns:
            Valor decodificado
        """
        if not header_value:
            return ''
        
        try:
            # Decodificar partes do cabeçalho
            decoded_parts = decode_header(header_value)
            decoded_str = ''
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        try:
                            decoded_str += part.decode(encoding, errors='replace')
                        except:
                            decoded_str += part.decode('utf-8', errors='replace')
                    else:
                        decoded_str += part.decode('utf-8', errors='replace')
                else:
                    decoded_str += str(part)
            
            return decoded_str.strip()
        except Exception as e:
            logger.debug(f"Error decoding header: {e}")
            return str(header_value)
    
    def _generate_thread_id(self, subject: str, in_reply_to: str, references: str) -> str:
        """
        Gera ID único para thread de email.
        
        Args:
            subject: Assunto do email
            in_reply_to: Message-ID respondido
            references: Referências
            
        Returns:
            Thread ID ou None
        """
        # Normalizar subject removendo prefixos comuns
        normalized_subject = re.sub(
            r'^(Re:|Fwd?:|Fw:|Res:|Enc:|RES:)\s*', 
            '', 
            subject or '', 
            flags=re.IGNORECASE
        ).strip()
        
        # Se tem referências, usar primeira como base
        if references:
            ref_ids = references.split()
            if ref_ids:
                # Pegar primeira referência e gerar hash
                base_ref = ref_ids[0].strip('<>')
                return hashlib.md5(base_ref.encode()).hexdigest()
        
        # Se tem in_reply_to, usar como base
        if in_reply_to:
            return hashlib.md5(in_reply_to.encode()).hexdigest()
        
        # Gerar baseado no subject normalizado
        if normalized_subject:
            return hashlib.md5(normalized_subject.encode()).hexdigest()
        
        return None
    
    def get_folder_status(self, folder: str = 'INBOX') -> Dict[str, Any]:
        """
        Obtém status de uma pasta IMAP.
        
        Args:
            folder: Nome da pasta
            
        Returns:
            Dicionário com informações da pasta
        """
        if not self.is_connected:
            return {}
        
        try:
            # STATUS command para obter informações
            result, data = self.connection.status(
                folder, 
                '(MESSAGES RECENT UNSEEN)'
            )
            
            if result == 'OK' and data:
                # Parse response
                status_str = data[0].decode() if isinstance(data[0], bytes) else data[0]
                
                # Extrair valores
                messages = re.search(r'MESSAGES (\d+)', status_str)
                recent = re.search(r'RECENT (\d+)', status_str)
                unseen = re.search(r'UNSEEN (\d+)', status_str)
                
                return {
                    'folder': folder,
                    'total_messages': int(messages.group(1)) if messages else 0,
                    'recent_messages': int(recent.group(1)) if recent else 0,
                    'unseen_messages': int(unseen.group(1)) if unseen else 0
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting folder status: {e}")
            return {}
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()