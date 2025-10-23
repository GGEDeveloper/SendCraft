"""
Serviço de Queue de Emails para SendCraft Phase 15
Processamento assíncrono de emails em lote
"""
import threading
import time
import queue
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum

from ..models import EmailAccount, EmailLog
from ..models.log import EmailStatus
from ..services.smtp_service import SMTPService
from ..services.attachment_service import AttachmentService
from ..extensions import db
from ..utils.logging import get_logger

logger = get_logger(__name__)


class QueueStatus(str, Enum):
    """Status da queue de emails."""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'


class EmailQueueItem:
    """Item da queue de emails."""
    
    def __init__(self, 
                 account: EmailAccount,
                 recipients: List[str],
                 subject: str,
                 html_content: Optional[str] = None,
                 text_content: Optional[str] = None,
                 attachments: Optional[List[Dict[str, Any]]] = None,
                 from_name: Optional[str] = None,
                 reply_to: Optional[str] = None,
                 cc: Optional[List[str]] = None,
                 bcc: Optional[List[str]] = None,
                 idempotency_key: Optional[str] = None,
                 variables: Optional[Dict[str, Any]] = None):
        """
        Inicializa item da queue.
        
        Args:
            account: Conta de email para envio
            recipients: Lista de destinatários
            subject: Assunto do email
            html_content: Conteúdo HTML
            text_content: Conteúdo texto
            attachments: Lista de anexos
            from_name: Nome do remetente
            reply_to: Email de resposta
            cc: Lista CC
            bcc: Lista BCC
            idempotency_key: Chave de idempotência
            variables: Variáveis para templates
        """
        self.account = account
        self.recipients = recipients
        self.subject = subject
        self.html_content = html_content
        self.text_content = text_content
        self.attachments = attachments or []
        self.from_name = from_name
        self.reply_to = reply_to
        self.cc = cc
        self.bcc = bcc
        self.idempotency_key = idempotency_key
        self.variables = variables or {}
        
        # Metadados
        self.created_at = datetime.utcnow()
        self.status = QueueStatus.PENDING
        self.processed_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.results = []
        self.error_message = None


class EmailQueue:
    """Queue simples para processamento de emails em lote."""
    
    def __init__(self, max_workers: int = 2):
        """
        Inicializa queue de emails.
        
        Args:
            max_workers: Número máximo de workers
        """
        self.max_workers = max_workers
        self.queue = queue.Queue()
        self.workers = []
        self.running = False
        self.attachment_service = AttachmentService()
        
        # Estatísticas
        self.stats = {
            'total_processed': 0,
            'total_success': 0,
            'total_failed': 0,
            'active_workers': 0
        }
    
    def start(self) -> None:
        """Inicia workers da queue."""
        if self.running:
            logger.warning("Email queue is already running")
            return
        
        self.running = True
        
        # Criar workers
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"EmailWorker-{i+1}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Email queue started with {self.max_workers} workers")
    
    def stop(self) -> None:
        """Para workers da queue."""
        if not self.running:
            return
        
        self.running = False
        
        # Aguardar workers terminarem
        for worker in self.workers:
            worker.join(timeout=5)
        
        self.workers.clear()
        logger.info("Email queue stopped")
    
    def add_email(self, queue_item: EmailQueueItem) -> str:
        """
        Adiciona email à queue.
        
        Args:
            queue_item: Item da queue
            
        Returns:
            ID do item (timestamp)
        """
        item_id = f"QUEUE-{int(queue_item.created_at.timestamp())}"
        self.queue.put((item_id, queue_item))
        
        logger.info(f"Email added to queue: {item_id} ({len(queue_item.recipients)} recipients)")
        return item_id
    
    def get_queue_size(self) -> int:
        """
        Retorna tamanho atual da queue.
        
        Returns:
            Número de itens na queue
        """
        return self.queue.qsize()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da queue.
        
        Returns:
            Dict com estatísticas
        """
        return {
            **self.stats,
            'queue_size': self.get_queue_size(),
            'running': self.running,
            'active_workers': len([w for w in self.workers if w.is_alive()])
        }
    
    def _worker_loop(self) -> None:
        """Loop principal do worker."""
        logger.info(f"Email worker {threading.current_thread().name} started")
        
        while self.running:
            try:
                # Tentar obter item da queue (timeout 1s)
                item_id, queue_item = self.queue.get(timeout=1)
                
                # Processar item
                self._process_queue_item(item_id, queue_item)
                
                # Marcar como concluído
                self.queue.task_done()
                
            except queue.Empty:
                # Timeout - continuar loop
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
        
        logger.info(f"Email worker {threading.current_thread().name} stopped")
    
    def _process_queue_item(self, item_id: str, queue_item: EmailQueueItem) -> None:
        """
        Processa item da queue.
        
        Args:
            item_id: ID do item
            queue_item: Item da queue
        """
        try:
            logger.info(f"Processing queue item: {item_id}")
            queue_item.status = QueueStatus.PROCESSING
            
            # Preparar anexos
            smtp_attachments = self.attachment_service.prepare_attachments_for_smtp(
                queue_item.attachments
            )
            
            # Processar cada destinatário
            for recipient in queue_item.recipients:
                try:
                    # Criar log de email
                    log = EmailLog(
                        account_id=queue_item.account.id,
                        recipient_email=recipient,
                        sender_email=queue_item.account.email_address,
                        subject=queue_item.subject,
                        status=EmailStatus.PENDING,
                        variables_used={
                            'idempotency_key': queue_item.idempotency_key,
                            'queue_item_id': item_id,
                            **queue_item.variables
                        }
                    )
                    db.session.add(log)
                    db.session.commit()
                    
                    # Marcar como enviando
                    log.mark_sending()
                    
                    # Enviar email
                    encryption_key = db.app.config.get('SECRET_KEY', '')
                    smtp_service = SMTPService(encryption_key)
                    
                    success, message, message_id = smtp_service.send_email(
                        account=queue_item.account,
                        to_email=recipient,
                        subject=queue_item.subject,
                        html_content=queue_item.html_content,
                        text_content=queue_item.text_content,
                        from_name=queue_item.from_name,
                        reply_to=queue_item.reply_to,
                        cc=queue_item.cc,
                        bcc=queue_item.bcc,
                        attachments=smtp_attachments if smtp_attachments else None
                    )
                    
                    # Atualizar log
                    if success:
                        log.mark_sent(message_id or '', message)
                        queue_item.success_count += 1
                        queue_item.results.append({
                            'email': recipient,
                            'status': 'sent',
                            'message_id': message_id,
                            'log_id': log.id
                        })
                    else:
                        log.mark_failed(message)
                        queue_item.failed_count += 1
                        queue_item.results.append({
                            'email': recipient,
                            'status': 'failed',
                            'error': message,
                            'log_id': log.id
                        })
                    
                    queue_item.processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process recipient {recipient}: {e}")
                    queue_item.failed_count += 1
                    queue_item.results.append({
                        'email': recipient,
                        'status': 'failed',
                        'error': str(e)
                    })
                    queue_item.processed_count += 1
            
            # Marcar como concluído
            queue_item.status = QueueStatus.COMPLETED
            
            # Atualizar estatísticas
            self.stats['total_processed'] += queue_item.processed_count
            self.stats['total_success'] += queue_item.success_count
            self.stats['total_failed'] += queue_item.failed_count
            
            logger.info(f"Queue item completed: {item_id} - {queue_item.success_count} sent, {queue_item.failed_count} failed")
            
        except Exception as e:
            logger.error(f"Queue item processing failed: {item_id} - {e}", exc_info=True)
            queue_item.status = QueueStatus.FAILED
            queue_item.error_message = str(e)
    
    def process_bulk_email(self, 
                          account: EmailAccount,
                          recipients: List[str],
                          subject: str,
                          html_content: Optional[str] = None,
                          text_content: Optional[str] = None,
                          attachments: Optional[List[Dict[str, Any]]] = None,
                          from_name: Optional[str] = None,
                          reply_to: Optional[str] = None,
                          cc: Optional[List[str]] = None,
                          bcc: Optional[List[str]] = None,
                          idempotency_key: Optional[str] = None,
                          variables: Optional[Dict[str, Any]] = None) -> str:
        """
        Processa email em lote.
        
        Args:
            account: Conta de email
            recipients: Lista de destinatários
            subject: Assunto
            html_content: Conteúdo HTML
            text_content: Conteúdo texto
            attachments: Anexos
            from_name: Nome do remetente
            reply_to: Email de resposta
            cc: Lista CC
            bcc: Lista BCC
            idempotency_key: Chave de idempotência
            variables: Variáveis
            
        Returns:
            ID do item da queue
        """
        # Criar item da queue
        queue_item = EmailQueueItem(
            account=account,
            recipients=recipients,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            attachments=attachments,
            from_name=from_name,
            reply_to=reply_to,
            cc=cc,
            bcc=bcc,
            idempotency_key=idempotency_key,
            variables=variables
        )
        
        # Adicionar à queue
        return self.add_email(queue_item)


# Instância global da queue
email_queue = EmailQueue(max_workers=2)


def start_email_queue() -> None:
    """Inicia a queue global de emails."""
    email_queue.start()


def stop_email_queue() -> None:
    """Para a queue global de emails."""
    email_queue.stop()


def get_email_queue() -> EmailQueue:
    """
    Retorna instância da queue global.
    
    Returns:
        Instância da EmailQueue
    """
    return email_queue
