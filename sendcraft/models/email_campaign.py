"""
Modelo de Campanha de Email para SendCraft Phase 15
Gerenciamento de campanhas de envio em massa com warm-up
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any, List

from .base import TimestampMixin
from ..extensions import db


class CampaignStatus(str, Enum):
    """Status da campanha de email."""
    DRAFT = 'draft'
    SCHEDULED = 'scheduled'
    RUNNING = 'running'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    FAILED = 'failed'


class WarmupPhase(str, Enum):
    """Fases de warm-up de reputação."""
    PHASE_1 = 'phase_1'  # 50 emails/dia
    PHASE_2 = 'phase_2'  # 150 emails/dia
    PHASE_3 = 'phase_3'  # 400 emails/dia
    PHASE_4 = 'phase_4'  # 600 emails/dia
    PHASE_5 = 'phase_5'  # 1000+ emails/dia (sem limite)


class EmailCampaign(TimestampMixin, db.Model):
    """Modelo para campanhas de envio em massa."""
    __tablename__ = 'email_campaigns'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('email_accounts.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Conteúdo
    subject = db.Column(db.String(255), nullable=False)
    html_content = db.Column(db.Text)
    text_content = db.Column(db.Text)
    from_name = db.Column(db.String(255))
    reply_to = db.Column(db.String(255))
    
    # Status e controle
    status = db.Column(db.String(50), default=CampaignStatus.DRAFT)
    warmup_enabled = db.Column(db.Boolean, default=True)
    current_warmup_phase = db.Column(db.String(50), default=WarmupPhase.PHASE_1)
    
    # Agendamento
    scheduled_start = db.Column(db.DateTime)
    scheduled_end = db.Column(db.DateTime)
    actual_start = db.Column(db.DateTime)
    actual_end = db.Column(db.DateTime)
    
    # Configurações de envio
    delay_between_emails = db.Column(db.Integer, default=180)  # segundos (3 min padrão)
    batch_size = db.Column(db.Integer, default=10)  # emails por batch
    max_daily_limit = db.Column(db.Integer, default=50)  # configurável por fase
    
    # Estatísticas
    total_recipients = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    bounced_count = db.Column(db.Integer, default=0)
    opened_count = db.Column(db.Integer, default=0)
    clicked_count = db.Column(db.Integer, default=0)
    complained_count = db.Column(db.Integer, default=0)
    
    # Métricas diárias
    today_sent = db.Column(db.Integer, default=0)
    today_bounced = db.Column(db.Integer, default=0)
    last_date_reset = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Configurações avançadas
    use_tracking_pixel = db.Column(db.Boolean, default=True)
    use_click_tracking = db.Column(db.Boolean, default=True)
    allow_unsubscribe = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    account = db.relationship('EmailAccount', backref='campaigns')
    recipients = db.relationship('CampaignRecipient', backref='campaign', cascade='all, delete-orphan')
    logs = db.relationship('EmailLog', backref='campaign', lazy='dynamic')
    
    def __repr__(self):
        return f'<EmailCampaign {self.id}: {self.name}>'
    
    def get_warmup_daily_limit(self) -> int:
        """Retorna limite diário baseado na fase atual."""
        limits = {
            WarmupPhase.PHASE_1: 50,
            WarmupPhase.PHASE_2: 150,
            WarmupPhase.PHASE_3: 400,
            WarmupPhase.PHASE_4: 600,
            WarmupPhase.PHASE_5: 10000,  # Essencialmente ilimitado
        }
        return limits.get(self.current_warmup_phase, 50)
    
    def get_bounce_rate(self) -> float:
        """Calcula taxa de bounce."""
        if self.sent_count == 0:
            return 0.0
        return (self.bounced_count / self.sent_count) * 100
    
    def get_complaint_rate(self) -> float:
        """Calcula taxa de reclamações."""
        if self.sent_count == 0:
            return 0.0
        return (self.complained_count / self.sent_count) * 100
    
    def get_open_rate(self) -> float:
        """Calcula taxa de abertura."""
        if self.sent_count == 0:
            return 0.0
        return (self.opened_count / self.sent_count) * 100
    
    def get_click_rate(self) -> float:
        """Calcula taxa de cliques."""
        if self.sent_count == 0:
            return 0.0
        return (self.clicked_count / self.sent_count) * 100
    
    def can_send_today(self) -> bool:
        """Verifica se pode enviar mais emails hoje."""
        # Reset contadores se mudou de dia
        self._check_and_reset_daily_counters()
        
        if not self.warmup_enabled:
            return True
        
        daily_limit = self.get_warmup_daily_limit()
        return self.today_sent < daily_limit
    
    def get_remaining_today(self) -> int:
        """Retorna quantos emails podem ser enviados hoje."""
        self._check_and_reset_daily_counters()
        
        if not self.warmup_enabled:
            return 999999  # Essencialmente ilimitado
        
        daily_limit = self.get_warmup_daily_limit()
        remaining = daily_limit - self.today_sent
        return max(0, remaining)
    
    def increment_sent(self, count: int = 1) -> None:
        """Incrementa contadores de envio."""
        self._check_and_reset_daily_counters()
        self.sent_count += count
        self.today_sent += count
        db.session.commit()
    
    def increment_failed(self, count: int = 1) -> None:
        """Incrementa contadores de falha."""
        self.failed_count += count
        db.session.commit()
    
    def increment_bounced(self, count: int = 1) -> None:
        """Incrementa contadores de bounce."""
        self._check_and_reset_daily_counters()
        self.bounced_count += count
        self.today_bounced += count
        db.session.commit()
    
    def should_advance_warmup_phase(self) -> bool:
        """
        Avalia se deve avançar para próxima fase de warm-up.
        Critérios:
        - Mínimo 2 dias na fase atual
        - Taxa de bounce < 2%
        - Taxa de reclamações < 0.1%
        """
        if not self.warmup_enabled or self.current_warmup_phase == WarmupPhase.PHASE_5:
            return False
        
        # Verificar antigüidade na fase
        if not self.actual_start:
            return False
        
        days_in_phase = (datetime.utcnow() - self.actual_start).days
        if days_in_phase < 2:
            return False
        
        # Verificar métricas
        bounce_rate = self.get_bounce_rate()
        complaint_rate = self.get_complaint_rate()
        
        return bounce_rate < 2.0 and complaint_rate < 0.1
    
    def advance_warmup_phase(self) -> bool:
        """Avança para próxima fase de warm-up."""
        phases = [
            WarmupPhase.PHASE_1,
            WarmupPhase.PHASE_2,
            WarmupPhase.PHASE_3,
            WarmupPhase.PHASE_4,
            WarmupPhase.PHASE_5,
        ]
        
        try:
            current_index = phases.index(self.current_warmup_phase)
            if current_index < len(phases) - 1:
                self.current_warmup_phase = phases[current_index + 1]
                db.session.commit()
                return True
        except (ValueError, IndexError):
            pass
        
        return False
    
    def _check_and_reset_daily_counters(self) -> None:
        """Reseta contadores diários se mudou de dia."""
        if not self.last_date_reset:
            self.last_date_reset = datetime.utcnow()
            return
        
        # Se passou de 24 horas, resetar contadores
        if datetime.utcnow() - self.last_date_reset >= timedelta(days=1):
            self.today_sent = 0
            self.today_bounced = 0
            self.last_date_reset = datetime.utcnow()
            db.session.commit()


class CampaignRecipient(TimestampMixin, db.Model):
    """Modelo para destinatários de campanha."""
    __tablename__ = 'campaign_recipients'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('email_campaigns.id'), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    
    # Status de envio
    status = db.Column(db.String(50), default='pending')  # pending, sent, failed, bounced
    sent_at = db.Column(db.DateTime)
    failed_reason = db.Column(db.Text)
    
    # Métricas individuais
    opened = db.Column(db.Boolean, default=False)
    opened_at = db.Column(db.DateTime)
    clicked = db.Column(db.Boolean, default=False)
    clicked_at = db.Column(db.DateTime)
    complained = db.Column(db.Boolean, default=False)
    complained_at = db.Column(db.DateTime)
    
    # Controle
    bounce_type = db.Column(db.String(50))  # 'hard' ou 'soft'
    retry_count = db.Column(db.Integer, default=0)
    
    # Dados customizados
    variables = db.Column(db.JSON, default={})
    
    def __repr__(self):
        return f'<CampaignRecipient {self.id}: {self.email}>'


class CampaignMetrics(TimestampMixin, db.Model):
    """Histórico de métricas de campanha."""
    __tablename__ = 'campaign_metrics'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('email_campaigns.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Contadores do dia
    sent = db.Column(db.Integer, default=0)
    failed = db.Column(db.Integer, default=0)
    bounced = db.Column(db.Integer, default=0)
    opened = db.Column(db.Integer, default=0)
    clicked = db.Column(db.Integer, default=0)
    complained = db.Column(db.Integer, default=0)
    
    # Taxas
    bounce_rate = db.Column(db.Float, default=0.0)
    complaint_rate = db.Column(db.Float, default=0.0)
    open_rate = db.Column(db.Float, default=0.0)
    click_rate = db.Column(db.Float, default=0.0)
    
    # Fase de warm-up neste dia
    warmup_phase = db.Column(db.String(50))
    daily_limit = db.Column(db.Integer)
    
    campaign = db.relationship('EmailCampaign', backref='metrics')
    
    def __repr__(self):
        return f'<CampaignMetrics {self.campaign_id}: {self.date.date()}>'
