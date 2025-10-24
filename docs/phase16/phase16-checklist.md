# 📋 SendCraft Phase 16: Checklist de Execução

## 🎯 Guia de Execução para o Agente Local

### 🚀 Setup Inicial

#### 1. Preparar Estrutura
```bash
# No repositório SendCraft
mkdir -p docs/phase16
mkdir -p scripts
touch docs/phase16/.gitkeep
touch scripts/.gitkeep
```

#### 2. Copiar Scripts
- Copiar conteúdo de `phase16-test-scripts.md` para os arquivos:
  - `scripts/test_phase15.py`
  - `scripts/validate_api.py` 
  - `scripts/generate_test_data.py`
  - `Makefile` (na raiz)

#### 3. Configurar API Key
```python
# Em scripts/test_phase15.py, linha ~15:
API_KEY = "SUA_CHAVE_API_REAL_AQUI"

# Para obter a chave:
# 1. Acessar SendCraft web interface
# 2. Ir para conta geral@artnshine.pt
# 3. Copiar API key
```

---

## 📋 Execução por Milestone

### 🎯 MILESTONE 1: Correções Críticas (Dia 1)

#### ✅ Task 1.1: Decidir Rotas
**Problema:** `/api/v1/send` vs `/api/v1/emails/send`

**Opções:**
1. **Mudar blueprint para /api/v1/send** (recomendado)
2. **Atualizar documentação para /api/v1/emails/**

**Ação:**
```python
# Em sendcraft/routes/email_api.py, linha ~25:
# OPÇÃO 1 (recomendada):
email_api_bp = Blueprint('email_api', __name__, url_prefix='/api/v1')

# E atualizar rotas:
@email_api_bp.route('/send', methods=['POST'])
@email_api_bp.route('/send/<message_id>/status', methods=['GET'])  
@email_api_bp.route('/attachments/upload', methods=['POST'])
```

#### ✅ Task 1.2: Implementar attachments_count
**Problema:** Status endpoint retorna `attachments_count: 0` (TODO)

**Ação:**
```python
# Em sendcraft/routes/email_api.py, função get_send_status():

# Substituir:
'attachments_count': 0,  # TODO: Implement attachment counting

# Por:
'attachments_count': len(log.variables_used.get('attachments', [])) if log.variables_used else 0,

# OU implementar método no EmailLog:
def count_attachments(self):
    if self.variables_used and 'attachments' in self.variables_used:
        return len(self.variables_used['attachments'])
    return 0
```

#### ✅ Task 1.3: Atualizar api_docs.py
```python
# Em sendcraft/routes/api_docs.py, adicionar seção:

<!-- Phase 15 Email Sending API -->
<h2 class="mt-5">📧 Email Sending API (Phase 15)</h2>

<!-- Endpoint /send -->
<div class="endpoint-card card">
    <div class="card-header">
        <span class="method-badge method-post">POST</span>
        <strong>/api/v1/send</strong>
    </div>
    <div class="card-body">
        <p>Send individual or bulk emails with attachments.</p>
        <!-- Adicionar exemplos completos -->
    </div>
</div>

<!-- Outros endpoints... -->
```

#### ✅ Task 1.4: Teste Inicial
```bash
# Executar validação básica
cd SendCraft
python scripts/validate_api.py

# Se OK, testar primeiro envio
python scripts/test_phase15.py
```

---

### 🧪 MILESTONE 2: Testes Completos (Dia 2)

#### ✅ Task 2.1: Configurar Testes
```bash
# Instalar dependências
pip install requests pytest faker

# Gerar dados de teste
python scripts/generate_test_data.py

# Verificar arquivos criados
ls docs/phase16/test-*.json
```

#### ✅ Task 2.2: Executar Suite Completa
```bash
# Teste completo
make test-full

# OU manualmente:
python scripts/validate_api.py
python scripts/generate_test_data.py  
python scripts/test_phase15.py
```

#### ✅ Task 2.3: Analisar Resultados
```bash
# Ver resultados
cat docs/phase16/test-results.json

# Contar passes/fails
grep "PASS\|FAIL" docs/phase16/test-results.json | wc -l
```

#### ✅ Task 2.4: Corrigir Falhas
**Para cada teste que falhar:**
1. Identificar causa no código
2. Implementar correção  
3. Re-executar teste específico
4. Validar correção

---

### 🛡️ MILESTONE 3: Hardening (Dia 3)

#### ✅ Task 3.1: Validação de Anexos
```python
# Em sendcraft/services/attachment_service.py:

ALLOWED_TYPES = [
    'application/pdf',
    'image/jpeg', 
    'image/png',
    'text/plain',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

MAX_SIZE_PER_FILE = 10 * 1024 * 1024  # 10MB
MAX_TOTAL_SIZE = 50 * 1024 * 1024     # 50MB

def validate_attachments(self, attachments):
    """Validação rigorosa"""
    errors = []
    total_size = 0
    
    for i, att in enumerate(attachments):
        # Validar content_type
        if att['content_type'] not in ALLOWED_TYPES:
            errors.append(f"Attachment {i}: type '{att['content_type']}' not allowed")
        
        # Validar tamanho
        content_size = len(att['content']) * 3 / 4  # base64 to bytes
        if content_size > MAX_SIZE_PER_FILE:
            errors.append(f"Attachment {i}: size {content_size/1024/1024:.1f}MB exceeds 10MB limit")
        
        total_size += content_size
    
    if total_size > MAX_TOTAL_SIZE:
        errors.append(f"Total attachments size {total_size/1024/1024:.1f}MB exceeds 50MB limit")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'total_size_mb': total_size / 1024 / 1024
    }
```

#### ✅ Task 3.2: Sanitização Headers
```python
# Em sendcraft/routes/email_api.py, função send_email():

def sanitize_email_data(data):
    """Sanitizar campos perigosos"""
    
    # Sanitizar from_name
    if 'from_name' in data:
        data['from_name'] = data['from_name'][:100].strip()
        # Remover caracteres perigosos
        data['from_name'] = re.sub(r'[\r\n\t<>"]', '', data['from_name'])
    
    # Validar reply_to
    if 'reply_to' in data:
        reply_to = data['reply_to'].strip()
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', reply_to):
            raise ValueError("Invalid reply_to email format")
        data['reply_to'] = reply_to
    
    # Sanitizar recipients
    for field in ['to', 'cc', 'bcc']:
        if field in data and data[field]:
            sanitized = []
            for email in data[field]:
                email = email.strip().lower()
                if re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                    sanitized.append(email)
            data[field] = sanitized
    
    return data

# Aplicar antes de processar:
data = sanitize_email_data(data)
```

#### ✅ Task 3.3: Melhorar Error Handling
```python
# Padronizar respostas de erro:

def error_response(error_type, message, details=None, status_code=400):
    """Resposta de erro padronizada"""
    response = {
        'success': False,
        'error': error_type,
        'message': message
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code

# Usar em vez de:
# return jsonify({'error': 'something'}), 400

# Usar:  
# return error_response('validation_failed', 'Missing required fields', {'missing': ['to', 'subject']})
```

---

### 📚 MILESTONE 4: Documentação (Dia 4)

#### ✅ Task 4.1: Exemplos Atualizados
```bash
# Atualizar docs/phase15/api-examples.md com rotas corretas
# Testar todos os exemplos cURL

# Exemplo correto:
curl -X POST http://localhost:5000/api/v1/send \
  -H "Authorization: Bearer sua_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["cliente@exemplo.com"],
    "subject": "Teste",
    "html": "<h1>Funciona!</h1>",
    "domain": "artnshine.pt",
    "account": "geral"
  }'
```

#### ✅ Task 4.2: OpenAPI Spec
```yaml
# Criar docs/phase16/openapi.yaml
openapi: 3.0.3
info:
  title: SendCraft Email API
  version: 1.0.0
  description: API para envio de emails com anexos

paths:
  /api/v1/send:
    post:
      summary: Send Email
      description: Send individual or bulk emails with optional attachments
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SendEmailRequest'
      responses:
        '200':
          description: Email sent successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SendEmailResponse'
        '400':
          description: Validation error
        '401':
          description: Authentication required
        '404':
          description: Domain or account not found
        '429':
          description: Rate limit exceeded

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      
  schemas:
    SendEmailRequest:
      type: object
      required: [to, subject, domain, account]
      properties:
        to:
          type: array
          items:
            type: string
            format: email
          example: ["cliente@exemplo.com"]
        subject:
          type: string
          example: "Confirmação de Encomenda"
        html:
          type: string
          example: "<h1>Obrigado!</h1>"
        # ... outros campos
```

---

## ✅ Checklist Final

### Código
- [ ] Rotas consistentes (/api/v1/send)
- [ ] attachments_count implementado
- [ ] Validação de anexos rigorosa
- [ ] Headers sanitizados
- [ ] Error handling padronizado
- [ ] Sem TODOs no código

### Testes  
- [ ] Envio simples: ✅ PASS
- [ ] Com anexo PDF: ✅ PASS  
- [ ] Bulk processing: ✅ PASS
- [ ] Anexo >10MB: ✅ FAIL (esperado)
- [ ] Arquivo .exe: ✅ FAIL (esperado)
- [ ] Status endpoint: ✅ PASS
- [ ] Validações: ✅ PASS
- [ ] Idempotency: ✅ PASS

### Documentação
- [ ] api_docs.py atualizada
- [ ] Exemplos cURL funcionais
- [ ] OpenAPI spec completa
- [ ] README atualizado

### Segurança
- [ ] Tipos de arquivo validados
- [ ] Tamanhos respeitados
- [ ] Headers sanitizados  
- [ ] Rate limiting testado

---

## 🎯 Critério de Sucesso

**Phase 16 está COMPLETA quando:**

```bash
# Este comando retorna 100% success rate:
python scripts/test_phase15.py

# E este exemplo cURL funciona na primeira tentativa:
curl -X POST http://localhost:5000/api/v1/send \
  -H "Authorization: Bearer $(cat .api_key)" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["geral@artnshine.pt"],
    "subject": "Phase 16 Complete! 🚀",
    "html": "<h1>✅ SendCraft Phase 16 funcionou perfeitamente!</h1>",
    "domain": "artnshine.pt",
    "account": "geral"
  }'

# Resposta esperada:
# {
#   "success": true,
#   "message_id": "MSG-123456",
#   "status": "sent",
#   "recipients_processed": 1,
#   "recipients_success": ["geral@artnshine.pt"],
#   "recipients_failed": [],
#   "attachments_processed": 0,
#   "total_size_mb": 0.0,
#   "processing_time_ms": 850
# }
```

**🏆 Phase 16 = Production Ready API! 🚀**