# 🧪 SendCraft Phase 16: Testing & Quality Assurance

## 🎯 Objetivo
Validar e melhorar a Phase 15 (API de Envio de Emails) através de testes abrangentes, correções de inconsistências e hardening de segurança.

## 📋 Estado Atual
- ✅ Phase 15 implementada na main
- ✅ Blueprint: `sendcraft/routes/email_api.py` 
- ✅ Serviços: `attachment_service.py`, `email_queue.py`
- ❌ Rotas não testadas com conta real
- ❌ Documentação desalinhada com implementação
- ❌ Validações podem ter gaps

## 🔍 Problemas Identificados

### 1. Inconsistência de Rotas
**Problema:** Documentação usa `/api/v1/send` mas implementação usa `/api/v1/emails/...`
**Impacto:** Exemplos cURL não funcionam
**Prioridade:** 🔴 Alta

### 2. Attachments Count
**Problema:** `GET /status` retorna `attachments_count: 0` (TODO)
**Impacto:** Informação incompleta para cliente
**Prioridade:** 🟡 Média

### 3. Validação de Anexos
**Problema:** Limites podem não estar configurados corretamente
**Impacto:** Segurança e performance
**Prioridade:** 🔴 Alta

### 4. Idempotency
**Problema:** Implementação atual pode ter colisões
**Impacto:** Emails duplicados
**Prioridade:** 🟡 Média

## 🚀 Tarefas Phase 16

### Milestone 1: Correção de Inconsistências (1 dia)
- [ ] **1.1** Alinhar rotas: escolher `/api/v1/send` ou `/api/v1/emails/send`
- [ ] **1.2** Atualizar `api_docs.py` com endpoints Phase 15
- [ ] **1.3** Corrigir exemplos cURL na documentação
- [ ] **1.4** Implementar `attachments_count` no status

### Milestone 2: Testes de Integração (1 dia)
- [ ] **2.1** Teste envio individual sem anexos
- [ ] **2.2** Teste envio individual com anexo PDF
- [ ] **2.3** Teste bulk com 10 destinatários
- [ ] **2.4** Teste upload de anexos grandes (>10MB) - deve falhar
- [ ] **2.5** Teste idempotency - mesmo key não duplica
- [ ] **2.6** Teste rate limiting com muitas requisições

### Milestone 3: Hardening (1 dia)
- [ ] **3.1** Validar limites de anexos (10MB/ficheiro, 50MB/total)
- [ ] **3.2** Sanitizar headers (Reply-To, From-Name)
- [ ] **3.3** Melhorar mensagens de erro padronizadas
- [ ] **3.4** Implementar logging estruturado

### Milestone 4: Documentação Final (0.5 dias)
- [ ] **4.1** OpenAPI spec completa
- [ ] **4.2** Exemplos Node.js e PHP atualizados
- [ ] **4.3** Guia de troubleshooting
- [ ] **4.4** README de deployment

## 🧪 Plano de Testes Detalhado

### Testes Funcionais

#### 1. Envio Individual
```bash
# Teste 1.1: Envio básico sem anexos
POST /api/v1/emails/send
{
  "to": ["teste@exemplo.com"],
  "subject": "Teste Básico",
  "html": "<h1>Funcionou!</h1>",
  "domain": "alitools.pt",
  "account": "teste"
}
# Esperado: 200, message_id, status="sent"

# Teste 1.2: Envio com anexo PDF
POST /api/v1/emails/send
{
  "to": ["teste@exemplo.com"],
  "subject": "Teste com PDF",
  "html": "<h1>PDF anexo</h1>",
  "attachments": [{"filename": "test.pdf", "content_type": "application/pdf", "content": "JVBERi0xLjQ..."}],
  "domain": "alitools.pt",
  "account": "teste"
}
# Esperado: 200, attachments_processed=1
```

#### 2. Validações
```bash
# Teste 2.1: Anexo muito grande (deve falhar)
POST /api/v1/emails/send
{
  "attachments": [{"filename": "huge.pdf", "content": "base64_15MB_content"}]
}
# Esperado: 400, "exceeds 10MB limit"

# Teste 2.2: Tipo não permitido (deve falhar)  
POST /api/v1/emails/send
{
  "attachments": [{"filename": "virus.exe", "content_type": "application/exe", "content": "..."}]
}
# Esperado: 400, "file type not allowed"
```

#### 3. Bulk Processing
```bash
# Teste 3.1: Bulk pequeno (10 emails)
POST /api/v1/emails/send
{
  "to": ["user1@test.com", "user2@test.com", ...], // 10 emails
  "bulk": true
}
# Esperado: 200, status="queued"

# Teste 3.2: Bulk muito grande (deve falhar)
POST /api/v1/emails/send
{
  "to": ["user1@test.com", ...], // 150 emails
  "bulk": true
}
# Esperado: 400, "limited to 100 recipients"
```

#### 4. Status Check
```bash
# Teste 4.1: Status válido
GET /api/v1/emails/send/MSG-123456/status
# Esperado: 200, message_id, status, recipients

# Teste 4.2: Status inválido
GET /api/v1/emails/send/INVALID/status  
# Esperado: 400, "invalid message ID"
```

### Testes de Segurança

#### 1. Input Validation
- Headers maliciosos (XSS em From-Name)
- Anexos com nomes perigosos (`../../../etc/passwd`)
- Recipients com formato inválido
- Content muito grande (DOS)

#### 2. Rate Limiting
- Muitas requisições por minuto
- Bulk requests consecutivas
- API key abuse

### Testes de Performance
- Envio 100 emails individuais
- Upload anexo 50MB (limite)
- Processamento queue bulk
- Memória durante operação

## 🛠️ Checklist de Qualidade

### Código
- [ ] Type hints em todos os métodos
- [ ] Docstrings completas
- [ ] Error handling consistente
- [ ] Logging estruturado
- [ ] Não há TODOs no código

### API
- [ ] Respostas JSON padronizadas
- [ ] HTTP status codes corretos
- [ ] Headers de rate limiting
- [ ] Validation messages claras
- [ ] Idempotency funcional

### Segurança
- [ ] Input sanitization
- [ ] File type validation
- [ ] Size limits enforced
- [ ] No path traversal
- [ ] API key validation

### Performance  
- [ ] Attachment processing eficiente
- [ ] Queue não bloqueia requests
- [ ] Memory leaks verificados
- [ ] Database queries otimizadas

## 📊 Métricas de Sucesso

### Funcionais
- ✅ 100% testes funcionais passam
- ✅ Envio com anexo <5s
- ✅ Bulk 100 emails <30s
- ✅ Zero emails duplicados com idempotency

### Qualidade
- ✅ Zero warnings de linting
- ✅ 90%+ test coverage nos serviços
- ✅ Documentação 100% atualizada
- ✅ Zero TODOs/FIXMEs no código

### Segurança
- ✅ Arquivos perigosos bloqueados
- ✅ Rate limiting funcional
- ✅ Input validation 100%
- ✅ Não vaza informação sensível

## 🎯 Entregáveis Phase 16

### Código
1. **Correções no `email_api.py`**
   - Rotas consistentes
   - Attachments count implementado
   - Error handling melhorado

2. **Melhorias nos Serviços**
   - `AttachmentService` com validação rigorosa
   - `EmailQueue` com metrics básicas
   - Logging estruturado

3. **Testes**
   - Suite de testes de integração
   - Scripts de validação
   - Performance benchmarks

### Documentação
1. **API Docs Atualizada**
   - OpenAPI spec completa
   - Exemplos funcionais
   - Error codes documentados

2. **Guias de Uso**
   - Node.js integration
   - PHP integration  
   - cURL examples

3. **Operations Guide**
   - Deployment checklist
   - Monitoring guide
   - Troubleshooting

## ⚡ Quick Start

### Para começar Phase 16:
```bash
# 1. Validar estado atual
curl -H "Authorization: Bearer {key}" https://sendcraft.dominios.pt/api/v1/emails/send

# 2. Executar testes básicos
python scripts/test_email_api.py

# 3. Validar documentação
open docs/phase16/test-results.md
```

---
**Phase 16 Duration:** 3-4 dias  
**Priority:** 🔴 Alta - necessária para produção  
**Dependencies:** Phase 15 completa