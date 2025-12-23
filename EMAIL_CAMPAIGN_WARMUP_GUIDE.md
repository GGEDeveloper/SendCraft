# 📧 Guia Completo: Envio em Massa com Warm-up no SendCraft

## 📋 Índice
1. [Visão Geral](#vis%C3%A3o-geral)
2. [Arquitetura](#arquitetura)
3. [Modelos de Dados](#modelos-de-dados)
4. [Sistema de Warm-up](#sistema-de-warm-up)
5. [API REST](#api-rest)
6. [Exemplos de Uso](#exemplos-de-uso)
7. [Monitoramento](#monitoramento)
8. [Troubleshooting](#troubleshooting)

---

## Visão Geral

O SendCraft agora suporta **envio em massa de emails com aquecimento progressivo de reputação** (warm-up). Este sistema permite:

✅ Enviar emails em grande escala (100k+)  
✅ Construir reputacião do domínio gradualmente  
✅ Reduzir taxa de bounce e spam complaints  
✅ Rastrear métricas em tempo real  
✅ Pausar/retomar campanhas  
✅ Templates com variáveis personalizadas  

---

## Arquitetura

### Componentes

```
┌─────────────────────────────────────┐
│  API REST (campaign_routes.py)      │
│  POST /api/campaigns                │
│  POST /api/campaigns/{id}/recipients│
│  POST /api/campaigns/{id}/start     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Campaign Service                   │
│  - create_campaign()                │
│  - add_recipients()                 │
│  - start_campaign()                 │
│  - _process_campaign_worker()       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Database Models                    │
│  - EmailCampaign                    │
│  - CampaignRecipient                │
│  - CampaignMetrics                  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  SMTP Service                       │
│  - send_email()                     │
│  - handle_bounces()                 │
└─────────────────────────────────────┘
```

### Fluxo de Execução

1. **Criar Campanha** → Draft status
2. **Adicionar Recipientes** → Lista de destinatários (CSV, JSON, API)
3. **Iniciar Campanha** → Running status
4. **Worker processa** → Ença emails com:
   - Rate limiting por fase
   - Delays entre emails
   - Rastreamento de métricas
5. **Avalia warm-up** → Avança de fase se critérios met
6. **Conclui** → Completed status

---

## Modelos de Dados

### EmailCampaign

Armazena configuração e estado da campanha.

```python
class EmailCampaign(db.Model):
    id                      # ID único
    account_id              # Conta SMTP associada
    name                    # Nome da campanha
    subject                 # Assunto template
    html_content            # Conteúdo HTML
    text_content            # Versão texto (opcional)
    from_name               # Nome do remetente
    reply_to                # Email de resposta
    
    # Status e Controle
    status                  # draft, scheduled, running, paused, completed, failed
    warmup_enabled          # Ativar aquecimento
    current_warmup_phase    # phase_1 a phase_5
    
    # Configurações
    delay_between_emails    # Segundos entre emails (padrão: 180 = 3 min)
    batch_size              # Emails por batch (padrão: 10)
    max_daily_limit         # Limite diário (auto-ajustado por fase)
    
    # Estatísticas
    total_recipients        # Total de destinatários
    sent_count              # Emails enviados
    failed_count            # Falhas de envio
    bounced_count           # Hard bounces
    opened_count            # Aberturas rastreadas
    clicked_count           # Cliques rastreados
    complained_count        # Spam complaints
    
    # Diárias
    today_sent              # Enviados hoje
    today_bounced           # Bounces hoje
    last_date_reset         # Último reset do dia
    
    # Rastreamento
    use_tracking_pixel      # Pixel de abertura
    use_click_tracking      # Rastreamento de cliques
    allow_unsubscribe       # Link de unsubscribe
```

### CampaignRecipient

Armazena dados de cada destinatário.

```python
class CampaignRecipient(db.Model):
    id                      # ID único
    campaign_id             # Relação com campanha
    email                   # Email do destinatário
    name                    # Nome
    
    # Status
    status                  # pending, sent, failed, bounced
    sent_at                 # Timestamp de envio
    failed_reason           # Motivo da falha
    
    # Métricas
    opened                  # Se abriu
    opened_at               # Quando abriu
    clicked                 # Se clicou
    clicked_at              # Quando clicou
    complained              # Se reclamou (spam)
    complained_at           # Quando reclamou
    
    # Controle
    bounce_type             # hard ou soft
    retry_count             # Número de tentativas
    variables               # Dados personalizados (JSON)
```

### CampaignMetrics

Histórico diário de métricas.

```python
class CampaignMetrics(db.Model):
    id
    campaign_id
    date                    # Data do snapshot
    
    # Contadores
    sent                    # Enviados no dia
    failed                  # Falhas no dia
    bounced                 # Bounces no dia
    opened                  # Aberturas no dia
    clicked                 # Cliques no dia
    complained              # Complaints no dia
    
    # Taxas
    bounce_rate             # Porcentagem
    complaint_rate          # Porcentagem
    open_rate               # Porcentagem
    click_rate              # Porcentagem
    
    # Contexto
    warmup_phase            # Fase naquele dia
    daily_limit             # Limite naquele dia
```

---

## Sistema de Warm-up

### Fases Progressivas

| Fase | Emails/Dia | Duração Min | Objetivo |
|------|-----------|------------|----------|
| **Phase 1** | 50 | 2 dias | Validar configuração SMTP |
| **Phase 2** | 150 | 3-5 dias | Testar taxa de abertura |
| **Phase 3** | 400 | 5-7 dias | Construir histório positivo |
| **Phase 4** | 600 | 7-10 dias | Aumentar volume |
| **Phase 5** | 10000+ | Ilimitado | Escala completa |

### Critérios de Avanço

Uma campanha avança de fase automaticamente quando:

```python
✓ Mínimo 2 dias na fase atual
✓ Taxa de bounce < 2%
✓ Taxa de complaints < 0.1%
```

Exemplo:
```
Fase 1 (2 dias) → 50 emails/dia = 100 emails
  - 98 entregues ✓ (98% delivery)
  - 1 bounce (1%)
  - 0 complaints (0%)
  → AVANÇAR para Fase 2

Fase 2 (3-5 dias) → 150 emails/dia = até 750 emails
  - 730 entregues
  - 12 bounces (1.6%)
  - 0 complaints
  → AVANÇAR para Fase 3
```

### Delay Entre Emails

Por padrão: **180 segundos (3 minutos)** entre cada email.

**Configurável por campanha:**
```python
# Muito rápido (risky)
delay_between_emails=30  # 30 segundos

# Recomendado
delay_between_emails=180  # 3 minutos

# Muito lento
delay_between_emails=300  # 5 minutos
```

### Rate Limiting

O sistema respeita limites diários:

```python
# Verifica antes de cada email
if not campaign.can_send_today():
    # Aguarda até próximo dia
    time.sleep(3600)  # 1 hora
    # Tenta novamente
```

---

## API REST

### 1. Criar Campanha

**POST** `/api/campaigns`

```bash
curl -X POST http://localhost:5000/api/campaigns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "account_id": 1,
    "name": "Newsletter Dezembro",
    "subject": "Olá {{ name }}, venha conferir as novidades!",
    "html_content": "<h1>Bem-vindo!</h1><p>Olá {{ name }},</p>...",
    "text_content": "Bem-vindo!\nOlá {{ name }},...",
    "from_name": "Newsletter Team",
    "reply_to": "support@example.com",
    "warmup_enabled": true,
    "delay_between_emails": 180,
    "batch_size": 10,
    "use_tracking_pixel": true,
    "use_click_tracking": true
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "Newsletter Dezembro",
  "status": "draft",
  "created_at": "2025-12-23T00:45:00Z"
}
```

### 2. Adicionar Recipientes (JSON)

**POST** `/api/campaigns/1/recipients`

```bash
curl -X POST http://localhost:5000/api/campaigns/1/recipients \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "recipients": [
      {
        "email": "user1@example.com",
        "name": "User One",
        "variables": {
          "coupon_code": "SAVE20",
          "discount_percent": "20"
        }
      },
      {
        "email": "user2@example.com",
        "name": "User Two",
        "variables": {
          "coupon_code": "SAVE10",
          "discount_percent": "10"
        }
      }
    ]
  }'
```

**Response:**
```json
{
  "added": 2,
  "duplicates": 0,
  "total_recipients": 2
}
```

### 3. Adicionar Recipientes (CSV)

**POST** `/api/campaigns/1/recipients/bulk?skip_duplicates=true`

**CSV (recipients.csv):**
```csv
email,name,coupon_code
user1@example.com,User One,SAVE20
user2@example.com,User Two,SAVE10
user3@example.com,User Three,SAVE15
```

```bash
curl -X POST http://localhost:5000/api/campaigns/1/recipients/bulk \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@recipients.csv"
```

### 4. Iniciar Campanha

**POST** `/api/campaigns/1/start`

```bash
curl -X POST http://localhost:5000/api/campaigns/1/start \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "message": "Campaign started",
  "campaign_id": 1,
  "status": "running"
}
```

### 5. Obter Estatísticas

**GET** `/api/campaigns/1/stats`

```bash
curl -X GET http://localhost:5000/api/campaigns/1/stats \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "name": "Newsletter Dezembro",
  "status": "running",
  "total_recipients": 1000,
  "sent": 150,
  "failed": 2,
  "bounced": 0,
  "opened": 45,
  "clicked": 12,
  "complained": 0,
  "today_sent": 150,
  "remaining_today": 0,
  "bounce_rate": "0.00%",
  "complaint_rate": "0.00%",
  "open_rate": "30.00%",
  "click_rate": "8.00%",
  "warmup_enabled": true,
  "warmup_phase": "phase_1",
  "daily_limit": 150
}
```

### 6. Pausar Campanha

**POST** `/api/campaigns/1/pause`

```bash
curl -X POST http://localhost:5000/api/campaigns/1/pause \
  -H "Authorization: Bearer TOKEN"
```

### 7. Retomar Campanha

**POST** `/api/campaigns/1/resume`

```bash
curl -X POST http://localhost:5000/api/campaigns/1/resume \
  -H "Authorization: Bearer TOKEN"
```

### 8. Listar Recipientes

**GET** `/api/campaigns/1/recipients?status=sent&limit=50&offset=0`

```bash
curl "http://localhost:5000/api/campaigns/1/recipients?status=sent&limit=50" \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "total": 150,
  "limit": 50,
  "offset": 0,
  "recipients": [
    {
      "id": 1,
      "email": "user1@example.com",
      "name": "User One",
      "status": "sent",
      "sent_at": "2025-12-23T01:00:00Z",
      "opened": true,
      "clicked": true,
      "complained": false
    },
    ...
  ]
}
```

### 9. Listar Campanhas

**GET** `/api/campaigns?account_id=1&status=running&limit=50`

```bash
curl "http://localhost:5000/api/campaigns?account_id=1&status=running" \
  -H "Authorization: Bearer TOKEN"
```

---

## Exemplos de Uso

### Python (requests)

```python
import requests
import json

BASE_URL = "http://localhost:5000"
TOKEN = "your-auth-token"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# 1. Criar campanha
campaign_data = {
    "account_id": 1,
    "name": "Campanha Natal 2025",
    "subject": "Feliz Natal, {{ name }}!",
    "html_content": "<h1>Festas Especiais</h1>...",
    "warmup_enabled": True,
    "delay_between_emails": 180
}

resp = requests.post(
    f"{BASE_URL}/api/campaigns",
    json=campaign_data,
    headers=HEADERS
)
campaign_id = resp.json()["id"]
print(f"Campanha criada: {campaign_id}")

# 2. Adicionar recipients
recipients = [
    {
        "email": f"user{i}@example.com",
        "name": f"User {i}",
        "variables": {"discount": "15%"}
    }
    for i in range(1, 101)
]

resp = requests.post(
    f"{BASE_URL}/api/campaigns/{campaign_id}/recipients",
    json={"recipients": recipients},
    headers=HEADERS
)
print(f"Adicionados: {resp.json()['added']} recipients")

# 3. Iniciar campanha
resp = requests.post(
    f"{BASE_URL}/api/campaigns/{campaign_id}/start",
    headers=HEADERS
)
print(f"Status: {resp.json()['status']}")

# 4. Monitorar progresso
import time
while True:
    resp = requests.get(
        f"{BASE_URL}/api/campaigns/{campaign_id}/stats",
        headers=HEADERS
    )
    stats = resp.json()
    print(f"Enviados: {stats['sent']}/{stats['total_recipients']} "
          f"(Aberturas: {stats['open_rate']})")
    
    if stats['status'] == 'completed':
        break
    
    time.sleep(30)  # Verificar a cada 30 segundos
```

### JavaScript (fetch)

```javascript
const BASE_URL = 'http://localhost:5000';
const TOKEN = 'your-auth-token';

const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${TOKEN}`
};

// 1. Criar campanha
async function createCampaign() {
  const campaignData = {
    account_id: 1,
    name: 'Campanha Natal 2025',
    subject: 'Feliz Natal, {{ name }}!',
    html_content: '<h1>Festas Especiais</h1>...',
    warmup_enabled: true
  };

  const resp = await fetch(`${BASE_URL}/api/campaigns`, {
    method: 'POST',
    headers,
    body: JSON.stringify(campaignData)
  });

  const data = await resp.json();
  return data.id;
}

// 2. Adicionar recipients
async function addRecipients(campaignId) {
  const recipients = Array.from({length: 100}, (_, i) => ({
    email: `user${i+1}@example.com`,
    name: `User ${i+1}`,
    variables: {discount: '15%'}
  }));

  const resp = await fetch(
    `${BASE_URL}/api/campaigns/${campaignId}/recipients`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify({recipients})
    }
  );

  const data = await resp.json();
  console.log(`Adicionados: ${data.added} recipients`);
}

// 3. Iniciar campanha
async function startCampaign(campaignId) {
  const resp = await fetch(
    `${BASE_URL}/api/campaigns/${campaignId}/start`,
    {method: 'POST', headers}
  );

  const data = await resp.json();
  console.log(`Status: ${data.status}`);
}

// 4. Monitorar
async function monitorCampaign(campaignId) {
  while (true) {
    const resp = await fetch(
      `${BASE_URL}/api/campaigns/${campaignId}/stats`,
      {headers}
    );

    const stats = await resp.json();
    console.log(`Enviados: ${stats.sent}/${stats.total_recipients} (${stats.open_rate})`);

    if (stats.status === 'completed') break;
    await new Promise(r => setTimeout(r, 30000));
  }
}

// Executar
(async () => {
  const campaignId = await createCampaign();
  await addRecipients(campaignId);
  await startCampaign(campaignId);
  await monitorCampaign(campaignId);
})();
```

---

## Monitoramento

### Métricas Principais

**Taxa de Entrega (Delivery Rate)**
```
(Total Enviados - Bounces) / Total Enviados × 100
Objetivo: > 95%
```

**Taxa de Bounce**
```
(Hard Bounces + Soft Bounces) / Total Enviados × 100
Crítico: < 2%
Bom: < 0.5%
```

**Taxa de Reclamações**
```
Complaints / Total Enviados × 100
Crítico: > 0.1%
Bom: < 0.01%
```

**Taxa de Abertura**
```
Aberturas / Total Entregue × 100
Bom: 20-30%
Excelente: > 40%
```

**Taxa de Clique**
```
Cliques / Total Entregue × 100
Bom: 5-10%
Excelente: > 15%
```

### Dashboard em Tempo Real

Monitore através do painel web:
```
/dashboard/campaigns/{campaign_id}
```

Mostra:
- Progresso de envio
- Curva de aberturas
- Cliques por hora
- Fases de warm-up
- Alertas de anomalias

### Webhooks (Opcional)

Configure para receber notificações:
```python
# Bounce
POST /webhooks/bounce
{
  "campaign_id": 1,
  "recipient_email": "user@example.com",
  "bounce_type": "hard",
  "reason": "Invalid email"
}

# Complaint
POST /webhooks/complaint
{
  "campaign_id": 1,
  "recipient_email": "user@example.com"
}

# Open
POST /webhooks/open
{
  "campaign_id": 1,
  "recipient_id": 1,
  "timestamp": "2025-12-23T01:00:00Z"
}
```

---

## Troubleshooting

### Problema: Campanha não inicia

**Causa**: Não há recipients pendentes

**Solução**:
```bash
# Verificar recipients
curl "http://localhost:5000/api/campaigns/1/recipients?status=pending" \
  -H "Authorization: Bearer TOKEN"

# Se vazio, adicionar mais
curl -X POST http://localhost:5000/api/campaigns/1/recipients \
  -H "Authorization: Bearer TOKEN" \
  -d '{"recipients": [...]'
```

### Problema: Emails marcados como spam

**Causas comuns**:
- Falta de SPF/DKIM/DMARC
- Taxa de envio muito alta
- Conteúdo duplicado
- Links suspeitos

**Soluções**:
```bash
# 1. Verificar registros SPF/DKIM
dig TXT example.com
dig TXT selector._domainkey.example.com

# 2. Reduzir delay entre emails
PATCH /api/campaigns/1
{"delay_between_emails": 300}  # 5 min

# 3. Usar warm-up agressivamente
{"warmup_enabled": true}  # Inicia em 50/dia

# 4. Monitorar bounce rate
GET /api/campaigns/1/stats
```

### Problema: Taxa de bounce alta

**Causas**:
- Email inválido na lista
- Servidor recipient offline
- Filtros de spam

**Solução**:
```python
# Validar emails antes de enviar
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Filtrar recipients inválidos
valid_recipients = [
    r for r in recipients 
    if validate_email(r['email'])
]
```

### Problema: Warm-up não avança

**Verificar critérios**:
```bash
GET /api/campaigns/1/stats

# Deve ter:
# - bounce_rate < 2%
# - complaint_rate < 0.1%
# - 2+ dias na fase atual
```

**Debug**:
```python
from sendcraft.models import EmailCampaign

campaign = EmailCampaign.query.get(1)
print(f"Bounce rate: {campaign.get_bounce_rate()}%")
print(f"Complaint rate: {campaign.get_complaint_rate()}%")
print(f"Days in phase: {(datetime.utcnow() - campaign.actual_start).days}")
print(f"Should advance: {campaign.should_advance_warmup_phase()}")
```

### Problema: Performance lenta

**Otimizações**:
```python
# 1. Aumentar batch size
{"batch_size": 50}  # Padrão: 10

# 2. Reduzir delay
{"delay_between_emails": 60}  # Padrão: 180

# 3. Usar índices no banco
db.session.execute('''
    CREATE INDEX idx_campaign_recipients 
    ON campaign_recipients(campaign_id, status);
''')

# 4. Limpar histórico antigo
db.session.query(CampaignMetrics).filter(
    CampaignMetrics.date < datetime.utcnow() - timedelta(days=90)
).delete()
db.session.commit()
```

---

## Próximos Passos

✅ **Implementado**: Modelos, serviço, API  
⏳ **Em progresso**: Dashboard web  
📅 **Planejado**: 
- Integração com Webhook para bounces/complaints
- Análises avançadas (cohort analysis)
- A/B testing automático
- Segmentação inteligente

---

## Suporte

Dúvidas? Abra uma issue no repositório.
