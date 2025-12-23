"""
Serviço de Campanha de Email para SendCraft Phase 15
Gerenciam todas as operações de envio em massa com warm-up
"""
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

from ..models import EmailAccount, EmailCampaign, CampaignRecipient, CampaignMetrics, EmailLog
from ..models.email_campaign import CampaignStatus, WarmupPhase
from ..models.log import EmailStatus
from ..extensions import db
from ..utils.logging import get_logger
from .email_queue import EmailQueue, EmailQueueItem
from .smtp_service import SMTPService
from .attachment_service import AttachmentService

logger = get_logger(__name__)


class CampaignService:
    """Serviço para gerenciar campanhas de email."""

    def __init__(self, encryption_key: str = ''):
        """
        Inicializa o serviço.
        
        Args:
            encryption_key: Chave de criptografia para contas
        """
        self.encryption_key = encryption_key
        self.smtp_service = SMTPService(encryption_key)
        self.attachment_service = AttachmentService()
        self.active_campaigns = {}  # Campanhas em execução
        self.campaign_lock = threading.Lock()

    def create_campaign(self,
                       account_id: int,
                       name: str,
                       subject: str,
                       html_content: str,
                       description: Optional[str] = None,
                       text_content: Optional[str] = None,
                       from_name: Optional[str] = None,
                       reply_to: Optional[str] = None,
                       warmup_enabled: bool = True,
                       delay_between_emails: int = 180,
                       batch_size: int = 10,
                       use_tracking_pixel: bool = True,
                       use_click_tracking: bool = True) -> EmailCampaign:
        """
        Cria nova campanha de email.
        
        Args:
            account_id: ID da conta de email
            name: Nome da campanha
            subject: Assunto
            html_content: Conteúdo HTML
            description: Descrição
            text_content: Versão texto
            from_name: Nome do remetente
            reply_to: Email de resposta
            warmup_enabled: Ativar warm-up
            delay_between_emails: Delay entre emails (segundos)
            batch_size: Tamanho do batch
            use_tracking_pixel: Usar pixel de rastreamento
            use_click_tracking: Rastrear cliques
            
        Returns:
            Campanha criada
        """
        try:
            campaign = EmailCampaign(
                account_id=account_id,
                name=name,
                subject=subject,
                html_content=html_content,
                description=description,
                text_content=text_content,
                from_name=from_name,
                reply_to=reply_to,
                warmup_enabled=warmup_enabled,
                delay_between_emails=delay_between_emails,
                batch_size=batch_size,
                current_warmup_phase=WarmupPhase.PHASE_1 if warmup_enabled else WarmupPhase.PHASE_5,
                use_tracking_pixel=use_tracking_pixel,
                use_click_tracking=use_click_tracking,
                status=CampaignStatus.DRAFT
            )
            
            db.session.add(campaign)
            db.session.commit()
            
            logger.info(f"Campaign created: {campaign.id} - {name}")
            return campaign
            
        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            db.session.rollback()
            raise

    def add_recipients(self,
                      campaign_id: int,
                      recipients: List[Dict[str, Any]],
                      skip_duplicates: bool = True) -> Tuple[int, int]:
        """
        Adiciona destinatários à campanha.
        
        Args:
            campaign_id: ID da campanha
            recipients: Lista de dicts com 'email', 'name', 'variables'
            skip_duplicates: Pular emails duplicados
            
        Returns:
            Tuple (adicionados, duplicados)
        """
        try:
            campaign = EmailCampaign.query.get(campaign_id)
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            added = 0
            duplicates = 0
            
            # Buscar emails existentes
            existing_emails = set(db.session.query(CampaignRecipient.email)
                                 .filter_by(campaign_id=campaign_id)
                                 .all())
            existing_emails = {email[0] for email in existing_emails}
            
            for recipient in recipients:
                email = recipient.get('email', '').strip().lower()
                
                if not email or not self._is_valid_email(email):
                    continue
                
                # Verificar duplicata
                if email in existing_emails:
                    if skip_duplicates:
                        duplicates += 1
                        continue
                    else:
                        # Atualizar existente
                        existing = CampaignRecipient.query.filter_by(
                            campaign_id=campaign_id,
                            email=email
                        ).first()
                        if existing:
                            existing.name = recipient.get('name')
                            existing.variables = recipient.get('variables', {})
                            db.session.commit()
                            continue
                
                # Criar novo recipient
                recipient_obj = CampaignRecipient(
                    campaign_id=campaign_id,
                    email=email,
                    name=recipient.get('name'),
                    variables=recipient.get('variables', {})
                )
                db.session.add(recipient_obj)
                existing_emails.add(email)
                added += 1
                
                # Commit em batches para performance
                if added % 1000 == 0:
                    db.session.commit()
            
            # Commit final
            db.session.commit()
            
            # Atualizar total de recipients
            total = CampaignRecipient.query.filter_by(
                campaign_id=campaign_id,
                status='pending'
            ).count()
            campaign.total_recipients = total
            db.session.commit()
            
            logger.info(f"Campaign {campaign_id}: {added} recipients added, {duplicates} duplicates")
            return added, duplicates
            
        except Exception as e:
            logger.error(f"Error adding recipients: {e}")
            db.session.rollback()
            raise

    def start_campaign(self, campaign_id: int) -> bool:
        """
        Inicia execução da campanha.
        
        Args:
            campaign_id: ID da campanha
            
        Returns:
            True se iniciada com sucesso
        """
        try:
            campaign = EmailCampaign.query.get(campaign_id)
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            if campaign.status != CampaignStatus.DRAFT:
                logger.warning(f"Campaign {campaign_id} is not in DRAFT status")
                return False
            
            # Validar recipients
            pending_count = CampaignRecipient.query.filter_by(
                campaign_id=campaign_id,
                status='pending'
            ).count()
            
            if pending_count == 0:
                logger.error(f"Campaign {campaign_id} has no pending recipients")
                return False
            
            # Atualizar status
            campaign.status = CampaignStatus.RUNNING
            campaign.actual_start = datetime.utcnow()
            campaign.today_sent = 0
            campaign.today_bounced = 0
            campaign.last_date_reset = datetime.utcnow()
            db.session.commit()
            
            # Iniciar thread de processamento
            with self.campaign_lock:
                self.active_campaigns[campaign_id] = True
            
            worker = threading.Thread(
                target=self._process_campaign_worker,
                args=(campaign_id,),
                name=f"CampaignWorker-{campaign_id}",
                daemon=True
            )
            worker.start()
            
            logger.info(f"Campaign {campaign_id} started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting campaign: {e}")
            return False

    def pause_campaign(self, campaign_id: int) -> bool:
        """
        Pausa execução da campanha.
        
        Args:
            campaign_id: ID da campanha
            
        Returns:
            True se pausada com sucesso
        """
        try:
            campaign = EmailCampaign.query.get(campaign_id)
            if not campaign:
                return False
            
            campaign.status = CampaignStatus.PAUSED
            db.session.commit()
            
            with self.campaign_lock:
                if campaign_id in self.active_campaigns:
                    del self.active_campaigns[campaign_id]
            
            logger.info(f"Campaign {campaign_id} paused")
            return True
            
        except Exception as e:
            logger.error(f"Error pausing campaign: {e}")
            return False

    def resume_campaign(self, campaign_id: int) -> bool:
        """
        Retoma execução da campanha pausada.
        
        Args:
            campaign_id: ID da campanha
            
        Returns:
            True se retomada com sucesso
        """
        try:
            campaign = EmailCampaign.query.get(campaign_id)
            if not campaign:
                return False
            
            if campaign.status != CampaignStatus.PAUSED:
                logger.warning(f"Campaign {campaign_id} is not paused")
                return False
            
            campaign.status = CampaignStatus.RUNNING
            db.session.commit()
            
            # Reiniciar worker
            with self.campaign_lock:
                self.active_campaigns[campaign_id] = True
            
            worker = threading.Thread(
                target=self._process_campaign_worker,
                args=(campaign_id,),
                name=f"CampaignWorker-{campaign_id}",
                daemon=True
            )
            worker.start()
            
            logger.info(f"Campaign {campaign_id} resumed")
            return True
            
        except Exception as e:
            logger.error(f"Error resuming campaign: {e}")
            return False

    def _process_campaign_worker(self, campaign_id: int) -> None:
        """
        Worker thread para processar campanha.
        
        Args:
            campaign_id: ID da campanha
        """
        logger.info(f"Campaign worker started for campaign {campaign_id}")
        
        try:
            while True:
                with self.campaign_lock:
                    if campaign_id not in self.active_campaigns:
                        logger.info(f"Campaign {campaign_id} worker exiting")
                        break
                
                campaign = EmailCampaign.query.get(campaign_id)
                if not campaign or campaign.status != CampaignStatus.RUNNING:
                    break
                
                # Processar um batch
                success = self._process_campaign_batch(campaign_id)
                
                if not success:
                    # Nenhum recipient para processar
                    campaign.status = CampaignStatus.COMPLETED
                    campaign.actual_end = datetime.utcnow()
                    db.session.commit()
                    break
                
                # Aguardar um pouco entre batches
                time.sleep(5)
        
        except Exception as e:
            logger.error(f"Campaign {campaign_id} worker error: {e}", exc_info=True)
            campaign = EmailCampaign.query.get(campaign_id)
            if campaign:
                campaign.status = CampaignStatus.FAILED
                db.session.commit()
        
        finally:
            with self.campaign_lock:
                if campaign_id in self.active_campaigns:
                    del self.active_campaigns[campaign_id]

    def _process_campaign_batch(self, campaign_id: int) -> bool:
        """
        Processa um batch de recipients pendentes.
        
        Args:
            campaign_id: ID da campanha
            
        Returns:
            True se processou algum recipient
        """
        campaign = EmailCampaign.query.get(campaign_id)
        if not campaign:
            return False
        
        # Verificar limite diário
        if not campaign.can_send_today():
            logger.info(f"Campaign {campaign_id} hit daily limit, waiting")
            # Aguardar 1 hora
            time.sleep(3600)
            return True
        
        # Obter recipients pendentes
        recipients = CampaignRecipient.query.filter_by(
            campaign_id=campaign_id,
            status='pending'
        ).limit(campaign.batch_size).all()
        
        if not recipients:
            return False
        
        account = EmailAccount.query.get(campaign.account_id)
        if not account:
            logger.error(f"Account {campaign.account_id} not found")
            return False
        
        # Enviar emails do batch
        for recipient in recipients:
            if not campaign.can_send_today():
                break
            
            try:
                # Preparar conteúdo com variáveis do recipient
                subject = self._render_template(campaign.subject, recipient.variables)
                html_content = self._render_template(campaign.html_content, recipient.variables)
                text_content = self._render_template(campaign.text_content, recipient.variables) if campaign.text_content else None
                
                # Adicionar tracking pixel se habilitado
                if campaign.use_tracking_pixel and html_content:
                    tracking_pixel = f'<img src="/track/pixel/{campaign.id}/{recipient.id}" width="1" height="1" />'
                    html_content += tracking_pixel
                
                # Enviar email
                success, message, message_id = self.smtp_service.send_email(
                    account=account,
                    to_email=recipient.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    from_name=campaign.from_name,
                    reply_to=campaign.reply_to
                )
                
                if success:
                    recipient.status = 'sent'
                    recipient.sent_at = datetime.utcnow()
                    campaign.increment_sent()
                    logger.debug(f"Email sent to {recipient.email}")
                else:
                    recipient.status = 'failed'
                    recipient.failed_reason = message
                    campaign.increment_failed()
                    logger.warning(f"Failed to send to {recipient.email}: {message}")
                
                db.session.commit()
                
                # Delay entre emails
                time.sleep(campaign.delay_between_emails)
            
            except Exception as e:
                logger.error(f"Error sending to {recipient.email}: {e}")
                recipient.status = 'failed'
                recipient.failed_reason = str(e)
                campaign.increment_failed()
                db.session.commit()
        
        # Evaluar warm-up advancement
        if campaign.should_advance_warmup_phase():
            if campaign.advance_warmup_phase():
                logger.info(f"Campaign {campaign_id} advanced to {campaign.current_warmup_phase}")
        
        return True

    def get_campaign_stats(self, campaign_id: int) -> Dict[str, Any]:
        """
        Retorna estatísticas da campanha.
        
        Args:
            campaign_id: ID da campanha
            
        Returns:
            Dict com estatísticas
        """
        campaign = EmailCampaign.query.get(campaign_id)
        if not campaign:
            return {}
        
        return {
            'id': campaign.id,
            'name': campaign.name,
            'status': campaign.status,
            'total_recipients': campaign.total_recipients,
            'sent': campaign.sent_count,
            'failed': campaign.failed_count,
            'bounced': campaign.bounced_count,
            'opened': campaign.opened_count,
            'clicked': campaign.clicked_count,
            'complained': campaign.complained_count,
            'today_sent': campaign.today_sent,
            'remaining_today': campaign.get_remaining_today(),
            'bounce_rate': f"{campaign.get_bounce_rate():.2f}%",
            'complaint_rate': f"{campaign.get_complaint_rate():.2f}%",
            'open_rate': f"{campaign.get_open_rate():.2f}%",
            'click_rate': f"{campaign.get_click_rate():.2f}%",
            'warmup_enabled': campaign.warmup_enabled,
            'warmup_phase': campaign.current_warmup_phase,
            'daily_limit': campaign.get_warmup_daily_limit(),
        }

    def _render_template(self, template: Optional[str], variables: Dict[str, Any]) -> Optional[str]:
        """
        Renderiza template com variáveis.
        
        Args:
            template: Template string
            variables: Dicionário de variáveis
            
        Returns:
            Template renderizado
        """
        if not template:
            return None
        
        try:
            # Substituição simples de variáveis
            result = template
            for key, value in variables.items():
                result = result.replace(f"{{{{ {key} }}}}", str(value))
            return result
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return template

    def _is_valid_email(self, email: str) -> bool:
        """
        Valida formato de email.
        
        Args:
            email: Email para validar
            
        Returns:
            True se válido
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


# Instância global do serviço
def get_campaign_service(encryption_key: str = '') -> CampaignService:
    """
    Retorna instância do serviço de campanha.
    
    Args:
        encryption_key: Chave de criptografia
        
    Returns:
        Instância do CampaignService
    """
    return CampaignService(encryption_key)
