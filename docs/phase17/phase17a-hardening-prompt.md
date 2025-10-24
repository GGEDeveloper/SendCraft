# 🚀 SendCraft Phase 17A: Hardening & Documentação

**Você é um engenheiro sênior responsável por consolidar e documentar a API SendCraft e UI de gestão que já existe. Sua missão é aplicar ajustes mínimos, padronizar respostas e criar documentação definitiva.**

## 🎯 OBJETIVO PHASE 17A
- ✅ **Documentar API v1** com referência completa
- ✅ **Melhorar UX API Keys** na interface web  
- ✅ **Padronizar respostas JSON** dos endpoints
- ✅ **Validar limites de anexos** e mensagens consistentes
- ✅ **Criar guia da UI** para utilizadores finais

## 📂 CONTEXTO
- **Repositório:** SendCraft na main branch
- **API:** Funcional em `/api/v1/send`, `/api/v1/send/{id}/status`, `/api/v1/attachments/upload`
- **UI:** Web interface completa em `/` com gestão de domínios, contas, API keys, templates, logs, inbox
- **Conta de teste:** geral@artnshine.pt (configurada e ativa)

---

## 📋 EXECUÇÃO PHASE 17A

### 🛠️ **TAREFA 1: Atualizar UI de API Keys (30 min)**

#### 1.1 Localizar Template
```bash
# Arquivo: sendcraft/templates/accounts/api_access.html
# Verificar se existe e qual a estrutura atual
```

#### 1.2 Melhorar UX da API Key
No template `accounts/api_access.html`, adicionar:

```html
<!-- Quando new_api_key está disponível (após gerar/rotacionar) -->
{% if new_api_key %}
<div class="alert alert-success alert-dismissible fade show" role="alert">
    <h5 class="alert-heading">✅ API Key Gerada com Sucesso!</h5>
    <p><strong>IMPORTANTE:</strong> Esta chave será mostrada apenas uma vez. Guarde-a em local seguro.</p>
    
    <div class="input-group mb-3">
        <input type="text" class="form-control font-monospace" 
               id="newApiKey" 
               value="{{ new_api_key }}" 
               readonly>
        <button class="btn btn-outline-secondary" 
                type="button" 
                onclick="copyToClipboard('newApiKey')">
            <i class="bi bi-clipboard"></i> Copiar
        </button>
    </div>
    
    <small class="text-muted">
        Use esta chave no cabeçalho: <code>Authorization: Bearer {{ new_api_key }}</code>
    </small>
    
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>

<script>
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    element.select();
    element.setSelectionRange(0, 99999); // Para mobile
    document.execCommand('copy');
    
    // Feedback visual
    const btn = element.nextElementSibling;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-check"></i> Copiado!';
    btn.classList.replace('btn-outline-secondary', 'btn-success');
    
    setTimeout(() => {
        btn.innerHTML = originalText;
        btn.classList.replace('btn-success', 'btn-outline-secondary');
    }, 2000);
}
</script>
{% endif %}
```

#### 1.3 Melhorar Estado da Chave Existente
Adicionar indicador visual mais claro:

```html
<!-- Estado atual da API Key -->
<div class="row mb-3">
    <div class="col-md-6">
        <label class="form-label">Status da API</label>
        <div>
            {% if api_data.is_enabled %}
                <span class="badge bg-success">
                    <i class="bi bi-check-circle"></i> Ativa
                </span>
            {% else %}
                <span class="badge bg-secondary">
                    <i class="bi bi-x-circle"></i> Desativada
                </span>
            {% endif %}
        </div>
    </div>
    
    <div class="col-md-6">
        <label class="form-label">Chave API</label>
        <div>
            {% if api_data.has_key %}
                <code class="text-muted">{{ api_data.key_display }}</code>
                <small class="d-block text-muted">
                    Criada: {{ api_data.created_at.strftime('%d/%m/%Y %H:%M') if api_data.created_at }}
                </small>
            {% else %}
                <em class="text-muted">Nenhuma chave gerada</em>
            {% endif %}
        </div>
    </div>
</div>
```

### 🛠️ **TAREFA 2: Padronizar Respostas JSON (45 min)**

#### 2.1 Revisar Email API
Arquivo: `sendcraft/routes/email_api.py`

Garantir que todas as respostas de erro seguem o padrão:
```python
# Padrão consistente para TODOS os endpoints
{
    "success": False,  # ou True
    "error": "error_code",  # código estruturado
    "message": "Mensagem amigável",  # em português
    "details": {  # opcional, mais informações
        "campo_específico": "valor"
    }
}
```

**Locais para padronizar:**
- Linha ~50: Validação de campos obrigatórios
- Linha ~80: Validação de conteúdo (html/text)  
- Linha ~90: Validação de destinatários
- Linha ~120: Domínio não encontrado
- Linha ~130: Conta não encontrada
- Linha ~140: Rate limit excedido
- Linha ~160: Validação de anexos

**Exemplo de padronização:**
```python
# ANTES (inconsistente)
return jsonify({'error': 'validation failed', 'msg': 'Missing fields'}), 400

# DEPOIS (padronizado)
return jsonify({
    'success': False,
    'error': 'validation_failed',
    'message': 'Campos obrigatórios em falta',
    'details': {
        'missing_fields': missing_fields,
        'required_fields': required_fields
    }
}), 400
```

#### 2.2 Revisar Web Endpoints
Arquivo: `sendcraft/routes/web.py`

Focar nos endpoints AJAX:
- `/api/accounts/<int:account_id>/test-smtp` (linha ~1400)
- `/api/accounts/<int:account_id>/test-imap` (linha ~1480)  
- `/emails/send` (linha ~1200)

Garantir respostas consistentes:
```python
# Sucesso
return jsonify({
    'success': True,
    'message': 'Operação concluída com sucesso',
    'details': {
        'server': server_name,
        'response_time': response_time,
        'status': 'connected'
    }
})

# Erro
return jsonify({
    'success': False,
    'error': 'connection_failed',
    'message': 'Falha na ligação SMTP',
    'details': {
        'server': server_name,
        'error_details': str(e)
    }
}), 500
```

### 🛠️ **TAREFA 3: Validar Anexos e Limites (30 min)**

#### 3.1 Verificar AttachmentService
Arquivo: `sendcraft/services/attachment_service.py`

Confirmar limites e mensagens:
```python
# Verificar constantes
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_TOTAL_SIZE = 50 * 1024 * 1024  # 50MB

# Verificar mensagens de erro em português
"Anexo demasiado grande (máximo 10MB)"
"Tamanho total de anexos excede 50MB"
"Tipo de ficheiro não permitido"
```

#### 3.2 Verificar Consistência com Email API
No `email_api.py`, confirmar que usa AttachmentService para validação:
```python
# Deve usar attachment_service.validate_attachments()
# Mensagens de erro devem ser consistentes entre API e UI
```

### 🛠️ **TAREFA 4: Criar Documentação no Repositório (60 min)**

#### 4.1 Estrutura de Documentação
```bash
# Criar estrutura
mkdir -p docs/phase17

# Arquivos a criar
touch docs/phase17/api-reference.md     # [Já criado - usar artifact 124]
touch docs/phase17/ui-guide.md         # [Já criado - usar artifact 125] 
touch docs/phase17/overview.md         # Visão geral da phase
touch docs/phase17/CHANGELOG.md        # Mudanças aplicadas
```

#### 4.2 Overview da Phase
`docs/phase17/overview.md`:
```markdown
# SendCraft Phase 17 - Consolidação e Documentação

## Objetivo
Consolidar a API v1 e UI de gestão com documentação completa e melhorias de UX.

## O que foi feito
- ✅ API Reference completa com exemplos
- ✅ UI Guide detalhado
- ✅ Melhorias UX API Keys (exibição única, cópia automática)
- ✅ Padronização respostas JSON
- ✅ Validação limites de anexos

## Funcionalidades Principais
- API v1: /send, /status, /upload
- UI: Domínios, Contas, Templates, Logs, Inbox
- API Keys: Gestão completa via UI
- SMTP/IMAP: Testes automáticos

## Próximas Phases
- Phase 17B: Testes E2E com Playwright MCP
- Phase 18: Guias de integração para projetos externos
```

#### 4.3 Changelog
`docs/phase17/CHANGELOG.md`:
```markdown
# SendCraft Phase 17A - Changelog

## UI Improvements
- ✅ API Key display: one-time show com botão copy
- ✅ Visual feedback para copy clipboard
- ✅ Estado da chave mais claro (ativa/desativada)

## API Standardization
- ✅ Respostas JSON padronizadas (success, error, message, details)
- ✅ Mensagens de erro em português
- ✅ Códigos de erro estruturados

## Documentation  
- ✅ API Reference completa (124 páginas)
- ✅ UI Guide completo (gestão total)
- ✅ Exemplos práticos (cURL, Node.js, PHP)

## Validation & Limits
- ✅ Anexos: 10MB/file, 50MB/total confirmado
- ✅ Mensagens consistentes API/UI
- ✅ AttachmentService validação padronizada

## Testing Preparation
- ✅ Conta geral@artnshine.pt configurada
- ✅ API Key flow preparado para testes E2E
- ✅ Endpoints health check funcionais
```

#### 4.4 Integrar Documentação Existente
```bash
# Copiar documentação criada
cp artifact_124_content.md docs/phase17/api-reference.md
cp artifact_125_content.md docs/phase17/ui-guide.md
```

### 🛠️ **TAREFA 5: Validação Final (30 min)**

#### 5.1 Teste Manual das Melhorias
1. **Aceder** http://localhost:5000
2. **Ir** para Contas → geral@artnshine.pt → API
3. **Ativar** API (se não estiver)
4. **Gerar** nova API key
5. **Verificar** se aparece alerta com botão copy
6. **Copiar** chave para clipboard
7. **Revogar** chave e verificar mensagens
8. **Gerar** novamente para confirmar fluxo

#### 5.2 Teste API com Nova Chave
```bash
# Testar endpoint com a chave copiada
curl -X POST http://localhost:5000/api/v1/send \
  -H "Authorization: Bearer SUA_API_KEY_COPIADA" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["geral@artnshine.pt"],
    "subject": "Teste Phase 17A",
    "html": "<h1>API funcionando!</h1>",
    "domain": "artnshine.pt", 
    "account": "geral"
  }'

# Verificar se retorna JSON padronizado
```

#### 5.3 Teste Endpoints AJAX
```bash
# Teste SMTP via browser console
fetch('/api/accounts/ID_DA_CONTA/test-smtp', {method: 'POST'})
  .then(r => r.json())
  .then(console.log)

# Verificar se resposta segue padrão {success, message, details}
```

---

## ✅ **CRITÉRIOS DE SUCESSO PHASE 17A**

### **UX Melhorado:**
- [ ] API Key mostra alerta "uma vez só" com botão copy
- [ ] Clipboard copy funciona com feedback visual  
- [ ] Estados da chave (ativa/desativada) claros

### **JSON Padronizado:**
- [ ] Todos os endpoints API retornam {success, error, message, details}
- [ ] Mensagens de erro em português
- [ ] Códigos de erro estruturados

### **Documentação Completa:**
- [ ] docs/phase17/api-reference.md (referência técnica)
- [ ] docs/phase17/ui-guide.md (guia utilizador)
- [ ] docs/phase17/overview.md (visão geral)
- [ ] docs/phase17/CHANGELOG.md (mudanças aplicadas)

### **Validação Funcionando:**
- [ ] Anexos: limites corretos e mensagens consistentes
- [ ] SMTP/IMAP: testes via UI retornam JSON padronizado
- [ ] API Key: fluxo completo gerar→copiar→revogar→gerar

### **Teste Manual Bem-sucedido:**
- [ ] UI: Gestão API key funcional
- [ ] API: Chamada com nova chave bem-sucedida
- [ ] JSON: Respostas padronizadas nos endpoints

---

## 🎯 **ENTREGA PHASE 17A**

**Quando concluído:**
- ✅ **UX melhorado** para gestão API keys
- ✅ **JSON padronizado** em todos os endpoints  
- ✅ **Documentação completa** em docs/phase17/
- ✅ **Validação funcionando** com limites corretos
- ✅ **Teste manual** confirmando melhorias

**Próximo passo:** Phase 17B - Testes E2E com Playwright MCP

**Estado esperado:** SendCraft UI/API consolidado, documentado e pronto para testes automatizados completos! 🚀