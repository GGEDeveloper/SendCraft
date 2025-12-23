# 🔗 Guia de Integração: Sistema de Campanhas

## Passo 1: Registrar as Novas Rotas

Edite `sendcraft/__init__.py` e adicione:

```python
from .routes.campaign_routes import campaign_bp

# ...

def create_app():
    # ... código existente ...
    
    # Registrar blueprints
    app.register_blueprint(campaign_bp)
    
    return app
```

## Passo 2: Importar os Modelos

Edite `sendcraft/models/__init__.py`:

```python
from .email_campaign import (
    EmailCampaign,
    CampaignRecipient,
    CampaignMetrics,
    CampaignStatus,
    WarmupPhase
)

__all__ = [
    # ... modelos existentes ...
    'EmailCampaign',
    'CampaignRecipient',
    'CampaignMetrics',
    'CampaignStatus',
    'WarmupPhase'
]
```

## Passo 3: Executar Migração

```bash
# Gerar migração
flask db migrate -m "Add email campaign models"

# Aplicar migração
flask db upgrade
```

## Passo 4: Testar

```bash
# Iniciar servidor em modo dev
python run_dev.py

# Em outro terminal, testar API
curl -X POST http://localhost:5000/api/campaigns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "account_id": 1,
    "name": "Test Campaign",
    "subject": "Test",
    "html_content": "<h1>Test</h1>"
  }'
```

## Passo 5: Configurar no app.py (Opcional)

Se desejar inicializar automaticamente:

```python
# app.py
from sendcraft.services.campaign_service import get_campaign_service

# Na inicialização do app
if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        # Inicializar serviço de campanhas
        service = get_campaign_service(
            encryption_key=app.config.get('SECRET_KEY', '')
        )
    
    app.run()
```

## Arquivos Criados

```
📄 sendcraft/
   📄 models/
      ✨ email_campaign.py        (3 novos modelos)
   📄 services/
      ✨ campaign_service.py      (Serviço principal)
   📄 routes/
      ✨ campaign_routes.py       (9 endpoints)
📄 EMAIL_CAMPAIGN_WARMUP_GUIDE.md  (Documentação completa)
📄 INTEGRATION_GUIDE.md             (Este arquivo)
```

## Estrutura de Banco de Dados

```sql
-- Tabelas criadas:

CREATE TABLE email_campaigns (
  id INTEGER PRIMARY KEY,
  account_id INTEGER NOT NULL,
  name VARCHAR(255),
  subject VARCHAR(255),
  html_content TEXT,
  text_content TEXT,
  status VARCHAR(50),
  warmup_enabled BOOLEAN,
  current_warmup_phase VARCHAR(50),
  delay_between_emails INTEGER,
  batch_size INTEGER,
  total_recipients INTEGER,
  sent_count INTEGER,
  failed_count INTEGER,
  bounced_count INTEGER,
  opened_count INTEGER,
  clicked_count INTEGER,
  complained_count INTEGER,
  today_sent INTEGER,
  today_bounced INTEGER,
  use_tracking_pixel BOOLEAN,
  use_click_tracking BOOLEAN,
  created_at DATETIME,
  updated_at DATETIME,
  FOREIGN KEY(account_id) REFERENCES email_accounts(id)
);

CREATE TABLE campaign_recipients (
  id INTEGER PRIMARY KEY,
  campaign_id INTEGER NOT NULL,
  email VARCHAR(255),
  name VARCHAR(255),
  status VARCHAR(50),
  sent_at DATETIME,
  opened BOOLEAN,
  opened_at DATETIME,
  clicked BOOLEAN,
  clicked_at DATETIME,
  complained BOOLEAN,
  variables JSON,
  created_at DATETIME,
  updated_at DATETIME,
  FOREIGN KEY(campaign_id) REFERENCES email_campaigns(id)
);

CREATE TABLE campaign_metrics (
  id INTEGER PRIMARY KEY,
  campaign_id INTEGER NOT NULL,
  date DATETIME,
  sent INTEGER,
  failed INTEGER,
  bounced INTEGER,
  opened INTEGER,
  clicked INTEGER,
  complained INTEGER,
  bounce_rate FLOAT,
  complaint_rate FLOAT,
  open_rate FLOAT,
  click_rate FLOAT,
  warmup_phase VARCHAR(50),
  daily_limit INTEGER,
  created_at DATETIME,
  updated_at DATETIME,
  FOREIGN KEY(campaign_id) REFERENCES email_campaigns(id)
);
```

## Variações de Implementação

### Opção A: Sem Warm-up (Envio Imediato)

```python
service.create_campaign(
    account_id=1,
    name="Newsletter Agora",
    subject="Assunto",
    html_content="...",
    warmup_enabled=False  # ❌ Desativar warm-up
)
```

Resultado: Todas as fases liberadas, 10000+ emails/dia.

### Opção B: Warm-up Progressivo (Padrão)

```python
service.create_campaign(
    account_id=1,
    name="Newsletter Segura",
    subject="Assunto",
    html_content="...",
    warmup_enabled=True,  # ✅ Ativar warm-up
    delay_between_emails=180  # 3 min entre emails
)
```

Resultado: Inicia em 50/dia, avança automaticamente.

### Opção C: Envio Rápido (Risky)

```python
service.create_campaign(
    account_id=1,
    name="Newsletter Express",
    subject="Assunto",
    html_content="...",
    warmup_enabled=True,
    delay_between_emails=30,  # 30 segundos apenas
    batch_size=100  # 100 por batch
)
```

Resultado: Mais rápido mas maior risco de spam.

## Exemplo Completo: Flask Shell

```bash
flask shell
```

```python
from sendcraft.models import EmailAccount, EmailCampaign, CampaignRecipient
from sendcraft.services.campaign_service import get_campaign_service
from sendcraft.extensions import db

# 1. Obter conta existente
account = EmailAccount.query.filter_by(is_default=True).first()
print(f"Conta: {account.email_address}")

# 2. Criar serviço
service = get_campaign_service()

# 3. Criar campanha
campaign = service.create_campaign(
    account_id=account.id,
    name="Black Friday 2025",
    subject="{{ name }}, vem conferir os descontos!",
    html_content="""
        <h1>Black Friday</h1>
        <p>Olá {{ name }},</p>
        <p>Temos um desconto especial para você!</p>
    """,
    from_name="Black Friday Team",
    warmup_enabled=True
)
print(f"Campanha criada: {campaign.id}")

# 4. Gerar recipients de teste
recipients = [
    {
        "email": f"user{i}@example.com",
        "name": f"User {i}",
        "variables": {"discount": f"{10 + i}%"}
    }
    for i in range(100)
]

# 5. Adicionar
added, dups = service.add_recipients(campaign.id, recipients)
print(f"Adicionados: {added}")

# 6. Iniciar
success = service.start_campaign(campaign.id)
print(f"Iniciada: {success}")

# 7. Monitorar
import time
for _ in range(10):
    stats = service.get_campaign_stats(campaign.id)
    print(f"Enviados: {stats['sent']}/{stats['total_recipients']} - "
          f"Taxa abertura: {stats['open_rate']}")
    time.sleep(10)
```

## Troubleshooting

### ImportError: cannot import name 'EmailCampaign'

**Solução**: Adicione imports ao `__init__.py`

```python
from .email_campaign import EmailCampaign, CampaignRecipient, CampaignMetrics
```

### ModuleNotFoundError: No module named 'sendcraft.routes.campaign_routes'

**Solução**: Verifique se o arquivo foi criado no caminho correto

```bash
ls -la sendcraft/routes/campaign_routes.py
```

### Flask migrate error

**Solução**: Limpar e recriar migrações

```bash
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Endpoint retorna 404

**Solução**: Verifique se o blueprint foi registrado

```python
# app.py
from .routes.campaign_routes import campaign_bp
app.register_blueprint(campaign_bp)
```

## Próximo: Implementar Webhook para Bounces/Complaints

Veja: `WEBHOOK_INTEGRATION.md` (em progresso)
