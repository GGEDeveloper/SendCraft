# 🔧 SendCraft Phase 16: Prompt para Agente Local

Você é um engenheiro DevOps/QA responsável por validar, testar e melhorar a **Phase 15 (API de Envio de Emails)** do SendCraft. Sua missão é garantir que a API esteja pronta para produção através de testes rigorosos e correções necessárias.

## 🎯 OBJETIVO PRINCIPAL
**Transformar a Phase 15 de "funciona" para "production-ready"** através de:
- Testes abrangentes com conta real
- Correção de inconsistências identificadas  
- Hardening de segurança e validações
- Documentação 100% precisa

## 📂 CONTEXTO ATUAL
- **Branch:** main (Phase 15 implementada)
- **Blueprint:** `sendcraft/routes/email_api.py` com 3 endpoints
- **Serviços:** `attachment_service.py`, `email_queue.py`  
- **Conta de Teste:** geral@artnshine.pt (password: 6+r&0io.ThlW2)
- **Problemas:** Rotas desalinhadas, TODOs no código, validações não testadas

## 🚨 PROBLEMAS CRÍTICOS IDENTIFICADOS

### 1. **Inconsistência de Rotas** 🔴 ALTA PRIORIDADE
```
❌ Documentação: POST /api/v1/send
✅ Implementação: POST /api/v1/emails/send
```
**AÇÃO:** Escolher um padrão e alinhar tudo

### 2. **Attachments Count Incompleto** 🟡 MÉDIA PRIORIDADE  
```python
# Em get_send_status():
'attachments_count': 0,  # TODO: Implement attachment counting
```
**AÇÃO:** Implementar contagem real de anexos

### 3. **Validações Não Testadas** 🔴 ALTA PRIORIDADE
- Limites de anexos (10MB/ficheiro, 50MB/total)
- Tipos de ficheiros permitidos
- Rate limiting funcional
**AÇÃO:** Testar todos os cenários de validação

## 📋 TAREFAS PRIORITÁRIAS (4 MILESTONES)

### 🎯 MILESTONE 1: Correções Críticas (1 dia)

#### 1.1 Alinhar Rotas da API
```bash
DECISÃO: Usar /api/v1/send (mais simples)
MUDANÇAS:
- email_api.py: url_prefix='/api/v1', routes: /send, /send/<id>/status, /attachments/upload
- OU atualizar toda documentação para /api/v1/emails/...
```

#### 1.2 Implementar attachments_count
```python
# Em get_send_status():
def count_attachments_for_log(log_id):
    # Implementar contagem real baseada em log.variables_used ou nova tabela
    return 0  # Substituir por lógica real
```

#### 1.3 Atualizar api_docs.py
```python
# Adicionar seção completa Phase 15 com:
# - POST /api/v1/send
# - GET /api/v1/send/{id}/status  
# - POST /api/v1/attachments/upload
# - Exemplos de payload e response
```

### 🧪 MILESTONE 2: Testes de Integração (1 dia)

#### 2.1 Configurar Ambiente de Teste
```python
# Criar scripts/test_phase15.py
API_BASE = "http://localhost:5000"
API_KEY = "chave_da_conta_geral_artnshine"
TEST_EMAIL = "geral@artnshine.pt"
```

#### 2.2 Testes Funcionais Obrigatórios
```python
def test_send_simple():
    """POST /api/v1/send - envio básico sem anexos"""
    payload = {
        "to": ["geral@artnshine.pt"],
        "subject": "Teste Phase 16 - Simples", 
        "html": "<h1>Funciona!</h1>",
        "domain": "artnshine.pt",
        "account": "geral"
    }
    # ESPERADO: 200, message_id, status="sent"

def test_send_with_attachment():
    """POST /api/v1/send - com anexo PDF pequeno"""
    # Anexo: PDF de ~100KB em base64
    # ESPERADO: 200, attachments_processed=1

def test_bulk_processing():
    """POST /api/v1/send - bulk com 5 destinatários"""
    payload = {
        "to": ["geral@artnshine.pt"] * 5,
        "bulk": True
    }
    # ESPERADO: 200, status="queued"

def test_attachment_too_large():
    """POST /api/v1/send - anexo >10MB deve falhar"""
    # ESPERADO: 400, "exceeds 10MB limit"

def test_invalid_file_type():
    """POST /api/v1/send - arquivo .exe deve falhar"""  
    # ESPERADO: 400, "file type not allowed"

def test_idempotency():
    """POST /api/v1/send - mesmo idempotency_key"""
    # Enviar 2x com mesmo key
    # ESPERADO: 1º = 200 sent, 2º = 200 duplicate_ignored

def test_status_check():
    """GET /api/v1/send/{id}/status"""
    # ESPERADO: 200, message_id, status, recipients, attachments_count
```

#### 2.3 Testes de Validação
```python
def test_missing_required_fields():
    """Campos obrigatórios ausentes"""
    payloads = [
        {},  # Vazio
        {"to": []},  # to vazio
        {"to": ["test@test.com"]},  # sem subject
        {"to": ["test@test.com"], "subject": "Test"}  # sem domain/account
    ]
    # ESPERADO: 400, validation_failed

def test_rate_limiting():
    """100+ requests em 1 minuto"""  
    # ESPERADO: 429 após limite
```

### 🛡️ MILESTONE 3: Hardening de Segurança (1 dia)

#### 3.1 Validação de Anexos Rigorosa
```python
# Em attachment_service.py verificar:
ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
MAX_SIZE_PER_FILE = 10 * 1024 * 1024  # 10MB
MAX_TOTAL_SIZE = 50 * 1024 * 1024     # 50MB

def validate_attachments(attachments):
    """Validação rigorosa com mensagens claras"""
    # - Verificar content_type está em ALLOWED_TYPES
    # - Verificar tamanho após decode base64
    # - Verificar filename não contém ../ ou caracteres perigosos
    # - Verificar total não excede 50MB
```

#### 3.2 Sanitização de Headers
```python
def sanitize_email_headers(data):
    """Sanitizar campos perigosos"""
    from_name = data.get('from_name', '').strip()
    reply_to = data.get('reply_to', '').strip() 
    
    # Remover caracteres perigosos: \r\n\t<>
    # Validar formato email em reply_to
    # Limitar tamanho de from_name (100 chars)
```

#### 3.3 Melhorar Error Handling
```python
# Padronizar todas as respostas de erro:
{
    "success": false,
    "error": "validation_failed|rate_limit_exceeded|internal_error",
    "message": "Human readable message",
    "details": {
        "field": "specific info",
        "code": "ERROR_CODE"
    }
}
```

### 📚 MILESTONE 4: Documentação Final (0.5 dias)

#### 4.1 Atualizar Exemplos cURL
```bash
# Corrigir todos os exemplos em docs/phase15/api-examples.md
# Usar rotas corretas e payloads testados

# Exemplo corrigido:
curl -X POST http://localhost:5000/api/v1/send \
  -H "Authorization: Bearer sua_chave_api" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["cliente@exemplo.com"],
    "subject": "Teste",
    "html": "<h1>Funciona!</h1>",
    "domain": "artnshine.pt", 
    "account": "geral"
  }'
```

#### 4.2 Criar OpenAPI Spec
```yaml
# Em docs/phase16/openapi.yaml
openapi: 3.0.3
info:
  title: SendCraft Email API
  version: 1.0.0
  description: API para envio de emails com anexos

paths:
  /api/v1/send:
    post:
      summary: Enviar email individual ou bulk
      requestBody: ...
      responses: ...
```

## 🧪 PLANO DE EXECUÇÃO

### DIA 1: Correções Críticas
1. **Manhã (4h):**
   - Decisão sobre rotas (/api/v1/send vs /api/v1/emails/send)
   - Implementar attachments_count no status
   - Atualizar api_docs.py

2. **Tarde (4h):**
   - Configurar ambiente de teste local
   - Executar primeiros testes funcionais
   - Identificar bugs críticos

### DIA 2: Testes Abrangentes  
1. **Manhã (4h):**
   - Suite completa de testes funcionais
   - Testes de validação e edge cases
   - Testes de segurança básicos

2. **Tarde (4h):**
   - Correção de bugs encontrados
   - Testes de performance básicos
   - Validação com conta real

### DIA 3: Hardening e Docs
1. **Manhã (4h):**
   - Hardening de segurança
   - Melhorias de error handling
   - Rate limiting validation

2. **Tarde (4h):**
   - Documentação atualizada
   - OpenAPI spec
   - Exemplos funcionais testados

### DIA 4: Validação Final
1. **Manhã (2h):**
   - Testes de regressão completos
   - Validação de documentação
   - Checklist final

## ✅ CRITÉRIOS DE ACEITAÇÃO

### Funcionais
- [ ] Envio individual funciona (com e sem anexos)
- [ ] Bulk processing funciona (5-10 emails)
- [ ] Status endpoint retorna info correta
- [ ] Upload de anexos funciona
- [ ] Idempotency previne duplicados

### Segurança
- [ ] Anexos >10MB são rejeitados  
- [ ] Tipos proibidos (.exe) são rejeitados
- [ ] Headers são sanitizados
- [ ] Rate limiting funciona
- [ ] Não há path traversal

### Qualidade
- [ ] Sem TODOs no código
- [ ] Mensagens de erro padronizadas  
- [ ] Documentação 100% precisa
- [ ] Exemplos cURL funcionam
- [ ] OpenAPI spec completa

## 🛠️ FERRAMENTAS E RECURSOS

### Para Testes
```python
# requirements-test.txt
pytest==7.4.0
requests==2.31.0
base64==1.0.0
faker==19.3.0  # Para gerar dados de teste
```

### Para Validação
```bash
# Testar localmente
python -m flask run --host=0.0.0.0 --port=5000

# Executar testes
python scripts/test_phase15.py

# Validar API
curl -X GET http://localhost:5000/api/v1/health
```

### Conta de Teste  
```
Email: geral@artnshine.pt
Password: 6+r&0io.ThlW2
SMTP: mail.artnshine.pt:465 (SSL)
Domain: artnshine.pt
Account: geral
```

## 🎯 ENTREGA FINAL

### Código
- `sendcraft/routes/email_api.py` - corrigido e testado
- `sendcraft/services/attachment_service.py` - validação rigorosa
- `sendcraft/routes/api_docs.py` - Phase 15 documentada

### Testes
- `scripts/test_phase15.py` - suite completa
- `docs/phase16/test-results.md` - relatório de testes  
- `docs/phase16/security-audit.md` - checklist de segurança

### Documentação
- `docs/phase15/api-examples.md` - atualizado e testado
- `docs/phase16/openapi.yaml` - spec completa
- `README-phase15.md` - guia de uso

---

**🚀 COMEÇAR POR:** Decidir sobre as rotas (/api/v1/send) e implementar attachments_count no status endpoint.

**⚠️ ATENÇÃO:** Testar TUDO com a conta real geral@artnshine.pt antes de marcar como concluído.

**📊 SUCESSO:** Quando todos os exemplos cURL da documentação funcionarem na primeira tentativa.