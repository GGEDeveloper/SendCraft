# 🧪 SendCraft Phase 17B: Testes E2E com Playwright MCP

**Você é um engenheiro de testes sênior especializado em automação browser. Sua missão é validar completamente a UI SendCraft e API usando Playwright MCP para garantir que tudo funciona perfeitamente.**

## 🎯 OBJETIVO PHASE 17B
Executar **testes E2E abrangentes** para validar:
- ✅ **Gestão completa de API Keys** (ativar → gerar → copiar → revogar)
- ✅ **Funcionalidades críticas da UI** (domínios, contas, templates, logs)
- ✅ **Integração API v1** com chave real
- ✅ **Fluxos de envio de emails** via UI e API
- ✅ **Testes SMTP/IMAP** automáticos

## 📂 PRÉ-REQUISITOS
- **Phase 17A:** Concluída (UI melhorada, JSON padronizado)
- **SendCraft:** Rodando em `http://localhost:5000`
- **Conta:** geral@artnshine.pt configurada e ativa
- **Playwright MCP:** Disponível para automação browser

---

## 🧪 EXECUÇÃO PHASE 17B - TESTES E2E

### 🚀 **FASE 1: SETUP E VERIFICAÇÃO (10 min)**

#### 1.1 Verificar Pré-condições
```bash
# Verificar se SendCraft está rodando
curl -s http://localhost:5000/ > /dev/null && echo "✅ UI OK" || echo "❌ UI não responde"

# Verificar API health
curl -s http://localhost:5000/api/v1/health > /dev/null && echo "✅ API OK" || echo "❌ API não responde"

# Verificar se conta existe
curl -s http://localhost:5000/accounts | grep -q "geral@artnshine.pt" && echo "✅ Conta OK" || echo "❌ Conta não encontrada"
```

#### 1.2 Preparar Ambiente de Testes
Usar **Playwright MCP** para:
1. Navegar para `http://localhost:5000`
2. Capturar screenshot inicial: `homepage-inicial.png`
3. Verificar se elementos principais estão visíveis (Dashboard, Contas, Templates, etc.)

---

### 🔑 **FASE 2: TESTE GESTÃO API KEYS (25 min)**

#### 2.1 Localizar Conta de Teste
**Steps usando Playwright MCP:**

1. **Navegar para Contas**
   - Clicar em "Contas" no menu principal
   - Aguardar carregamento da lista
   - Screenshot: `contas-lista.png`

2. **Localizar geral@artnshine.pt**
   - Procurar na lista ou usar filtro se necessário
   - Clicar no botão "Editar" (ícone lápis) da conta
   - Screenshot: `conta-edicao.png`

3. **Aceder gestão API**
   - Localizar e clicar em "API" ou link equivalente
   - Screenshot: `api-gestao-inicial.png`

#### 2.2 Fluxo Completo de API Key
**Steps usando Playwright MCP:**

1. **Ativar API (se não estiver)**
   - Verificar estado atual da API
   - Se desativada, clicar "Ativar API"
   - Aguardar confirmação
   - Screenshot: `api-ativada.png`

2. **Gerar primeira API Key**
   - Clicar "Gerar API Key" 
   - **IMPORTANTE:** Aguardar aparecer o alerta com a chave
   - Verificar se aparece texto "mostrada apenas uma vez"
   - Verificar se existe botão "Copiar"
   - Screenshot: `api-key-gerada.png`

3. **Copiar API Key**
   - Clicar no botão "Copiar"
   - Verificar feedback visual (botão muda para "Copiado!" por 2s)
   - Guardar o valor em variável para testes posteriores
   - Screenshot: `api-key-copiada.png`

4. **Revogar API Key**
   - Scrollar ou navegar para encontrar botão "Revogar"
   - Clicar "Revogar API Key"
   - Confirmar no popup/modal se aparecer
   - Verificar mensagem de sucesso
   - Screenshot: `api-key-revogada.png`

5. **Regenerar API Key**
   - Clicar "Gerar API Key" novamente
   - Verificar se nova chave é gerada (diferente da anterior)
   - Copiar nova chave
   - Guardar para testes de API
   - Screenshot: `api-key-regenerada.png`

---

### 📧 **FASE 3: TESTE ENVIO VIA UI (20 min)**

#### 3.1 Acesso ao Inbox
**Steps usando Playwright MCP:**

1. **Navegar para Inbox**
   - Clicar em "Inbox" ou "Emails" no menu
   - Verificar se carrega interface de 3 painéis
   - Confirmar que conta geral@artnshine.pt está selecionada
   - Screenshot: `inbox-interface.png`

2. **Abrir Composer**
   - Localizar e clicar botão "Compor" ou "Novo Email"
   - Verificar se modal/página de composição abre
   - Screenshot: `composer-aberto.png`

#### 3.2 Envio de Email Teste
**Steps usando Playwright MCP:**

1. **Preencher formulário**
   - **Para:** geral@artnshine.pt (auto-envio para testar)
   - **Assunto:** "Teste E2E Playwright - Phase 17B"
   - **HTML:** `<h1>🧪 Teste Automático</h1><p>Email enviado via UI durante testes E2E.</p>`
   - Screenshot: `composer-preenchido.png`

2. **Adicionar anexo pequeno (opcional)**
   - Se interface permite, adicionar arquivo .txt pequeno (<1KB)
   - Verificar preview do anexo
   - Screenshot: `composer-com-anexo.png`

3. **Enviar email**
   - Clicar "Enviar"
   - Aguardar feedback (success/error)
   - Verificar se aparece toast/mensagem de confirmação
   - Screenshot: `email-enviado-feedback.png`

4. **Verificar no logs**
   - Navegar para Logs
   - Filtrar por data/horário recente
   - Localizar o email enviado
   - Verificar status (SENT/FAILED)
   - Screenshot: `log-email-enviado.png`

---

### 🌐 **FASE 4: TESTE API COM CHAVE REAL (15 min)**

#### 4.1 Teste POST /api/v1/send
**Steps usando Playwright MCP ou script externo:**

```bash
# Usar a API key copiada nos testes anteriores
API_KEY="sendcraft_dev_..." # obtida do teste anterior

# Teste básico de envio
curl -X POST http://localhost:5000/api/v1/send \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["geral@artnshine.pt"],
    "subject": "🚀 Teste API Phase 17B",
    "html": "<h1>API Funcionando!</h1><p>Teste automático da API v1.</p>",
    "domain": "artnshine.pt",
    "account": "geral",
    "idempotency_key": "e2e-test-'$(date +%s)'"
  }' \
  -v > api-test-result.json

# Verificar resposta JSON padronizada
echo "Resposta da API:"
cat api-test-result.json | jq .
```

#### 4.2 Teste GET /api/v1/send/{id}/status
```bash
# Extrair message_id da resposta anterior
MESSAGE_ID=$(cat api-test-result.json | jq -r .message_id)

# Consultar status
curl -H "Authorization: Bearer $API_KEY" \
  "http://localhost:5000/api/v1/send/$MESSAGE_ID/status" \
  | jq . > api-status-result.json

echo "Status do email:"
cat api-status-result.json
```

#### 4.3 Validar Resposta Padronizada
- Verificar se resposta contém `success`, `message`, `details`
- Confirmar `attachments_count` está presente
- Validar timestamps em formato ISO

---

### 🧪 **FASE 5: TESTES SMTP/IMAP AUTOMÁTICOS (15 min)**

#### 5.1 Teste SMTP via UI
**Steps usando Playwright MCP:**

1. **Voltar à edição da conta**
   - Navegar Contas → geral@artnshine.pt → Editar
   - Localizar botão "Testar SMTP"
   - Screenshot: `teste-smtp-botao.png`

2. **Executar teste SMTP**
   - Clicar "Testar SMTP"
   - Aguardar resposta (pode demorar até 10s)
   - Verificar modal/alerta com resultado
   - Capturar resultado (sucesso/erro)
   - Screenshot: `teste-smtp-resultado.png`

#### 5.2 Teste IMAP via UI
**Steps usando Playwright MCP:**

1. **Executar teste IMAP**
   - Clicar "Testar IMAP"
   - Aguardar resposta (pode demorar até 60s)
   - Verificar modal/alerta com resultado
   - Capturar detalhes técnicos mostrados
   - Screenshot: `teste-imap-resultado.png`

---

### 🏠 **FASE 6: TESTES CRUD DE DOMÍNIOS (20 min)**

#### 6.1 Gestão de Domínios
**Steps usando Playwright MCP:**

1. **Navegar para Domínios**
   - Clicar em "Domínios" no menu
   - Screenshot: `dominios-lista.png`

2. **Criar domínio de teste**
   - Clicar "Novo Domínio" ou equivalente
   - Preencher: Nome: `teste-e2e.local`, Descrição: `Domínio para testes E2E`
   - Marcar como ativo
   - Salvar
   - Screenshot: `dominio-criado.png`

3. **Editar domínio**
   - Localizar domínio criado na lista
   - Clicar "Editar"
   - Alterar descrição para `Domínio editado via E2E`
   - Salvar
   - Screenshot: `dominio-editado.png`

4. **Toggle ativo/inativo**
   - Clicar botão toggle/switch do domínio
   - Verificar mudança de estado visual
   - Screenshot: `dominio-inativo.png`
   - Toggle novamente para ativo

5. **Tentar eliminar com restrição**
   - Se houver contas associadas, tentar eliminar
   - Verificar se bloqueia e mostra mensagem apropriada
   - Screenshot: `dominio-delete-bloqueado.png`

6. **Eliminar domínio sem dependências**
   - Certificar que domínio não tem contas/templates
   - Clicar "Eliminar"
   - Confirmar no popup
   - Verificar se desaparece da lista
   - Screenshot: `dominio-eliminado.png`

---

### 📝 **FASE 7: TESTES DE TEMPLATES (15 min)**

#### 7.1 Gestão de Templates
**Steps usando Playwright MCP:**

1. **Navegar para Templates**
   - Clicar "Templates" no menu
   - Screenshot: `templates-lista.png`

2. **Criar template simples**
   - Clicar "Novo Template"
   - Preencher campos:
     - Domínio: artnshine.pt
     - Chave: `teste-e2e`
     - Nome: `Template E2E`
     - Assunto: `Teste {{nome_cliente}}`
     - HTML: `<h1>Olá {{nome_cliente}}!</h1><p>Template criado via E2E.</p>`
   - Salvar
   - Screenshot: `template-criado.png`

3. **Testar Preview**
   - Localizar botão "Preview" do template
   - Clicar e aguardar modal com preview
   - Verificar se variáveis foram substituídas por dados exemplo
   - Screenshot: `template-preview.png`

4. **Eliminar template**
   - Voltar à lista de templates
   - Localizar template criado
   - Clicar "Eliminar"
   - Confirmar
   - Screenshot: `template-eliminado.png`

---

### 📊 **FASE 8: VERIFICAÇÃO DE LOGS E ESTATÍSTICAS (10 min)**

#### 8.1 Sistema de Logs
**Steps usando Playwright MCP:**

1. **Navegar para Logs**
   - Clicar "Logs" no menu
   - Screenshot: `logs-lista.png`

2. **Aplicar filtros**
   - Filtrar por domínio: artnshine.pt
   - Filtrar por status: SENT
   - Filtrar por data: hoje
   - Aplicar filtros
   - Screenshot: `logs-filtrados.png`

3. **Ver detalhe de log**
   - Clicar em um log da lista (preferencialmente do teste anterior)
   - Verificar informações detalhadas
   - Screenshot: `log-detalhe.png`

#### 8.2 Dashboard de Estatísticas
**Steps usando Playwright MCP:**

1. **Voltar ao Dashboard**
   - Clicar logo/home para voltar ao dashboard
   - Verificar se estatísticas foram atualizadas
   - Confirmar contadores de emails enviados
   - Screenshot: `dashboard-atualizado.png`

---

### 📋 **FASE 9: CASOS EXTREMOS E VALIDAÇÕES (15 min)**

#### 9.1 Validações de Formulário
**Steps usando Playwright MCP:**

1. **Teste validação de email inválido**
   - Voltar ao composer
   - Tentar enviar com email inválido no "Para"
   - Verificar se bloqueia e mostra erro
   - Screenshot: `validacao-email-invalido.png`

2. **Teste campos obrigatórios**
   - Tentar enviar sem assunto
   - Verificar validação client-side ou server-side
   - Screenshot: `validacao-campos-obrigatorios.png`

#### 9.2 Teste de Anexos (se implementado)
1. **Anexo muito grande**
   - Tentar anexar arquivo >5MB
   - Verificar se bloqueia com mensagem apropriada
   - Screenshot: `anexo-muito-grande.png`

---

### 📄 **FASE 10: RELATÓRIO E EVIDÊNCIAS (10 min)**

#### 10.1 Compilar Screenshots
Organizar todos os screenshots capturados:
```bash
mkdir -p docs/phase17/screenshots/
# Mover todos os .png capturados para esta pasta
# Organizar por funcionalidade:
# - api-keys/
# - envio-email/
# - dominios/
# - templates/
# - logs/
# - validacoes/
```

#### 10.2 Criar Relatório de Testes
Gerar `docs/phase17/test-report.md`:
```markdown
# SendCraft Phase 17B - Relatório de Testes E2E

## Resumo Executivo
- **Data:** 24 Outubro 2025
- **Duração:** ~2.5 horas
- **Testes executados:** 12 cenários principais
- **Screenshots capturados:** 25+
- **Status geral:** ✅ SUCESSO

## Resultados por Funcionalidade

### 🔑 Gestão API Keys
- ✅ Ativação de API
- ✅ Geração de chave com alerta "uma vez só"
- ✅ Botão copiar com feedback visual
- ✅ Revogação de chave
- ✅ Regeneração de chave
- **Chave obtida:** `sendcraft_dev_abc123...`

### 📧 Envio via UI
- ✅ Interface inbox carrega corretamente
- ✅ Composer funcional
- ✅ Envio bem-sucedido
- ✅ Feedback apropriado
- ✅ Log gerado corretamente

### 🌐 API v1 Integração
- ✅ POST /send com chave real: HTTP 200
- ✅ GET /status: resposta completa com attachments_count
- ✅ Respostas JSON padronizadas
- ✅ Idempotency funcionando

### 🧪 Testes SMTP/IMAP
- ✅/❌ SMTP: [descrever resultado]
- ✅/❌ IMAP: [descrever resultado]

### 🏠 CRUD Domínios
- ✅ Criação de domínio
- ✅ Edição de domínio  
- ✅ Toggle ativo/inativo
- ✅ Proteção contra eliminação (dependências)
- ✅ Eliminação bem-sucedida

### 📝 CRUD Templates
- ✅ Criação de template
- ✅ Preview com variáveis
- ✅ Eliminação

### 📊 Logs e Dashboard
- ✅ Filtros de logs funcionais
- ✅ Detalhe de logs completo
- ✅ Estatísticas atualizadas

### 🚨 Validações
- ✅ Email inválido bloqueado
- ✅ Campos obrigatórios validados
- ✅/❌ Anexos grandes bloqueados (se testado)

## Issues Encontrados
[Listar problemas, se houver]

## Tempo de Execução
- Gestão API Keys: 25 min
- Envio via UI: 20 min  
- API com chave real: 15 min
- SMTP/IMAP: 15 min
- CRUD Domínios: 20 min
- Templates: 15 min
- Logs: 10 min
- Validações: 15 min
- **Total:** ~2.25 horas

## Conclusão
SendCraft UI e API estão funcionais e prontos para uso em produção.
```

---

## ✅ **CRITÉRIOS DE SUCESSO PHASE 17B**

### **Gestão API Keys (Crítico):**
- [ ] Ativação funciona
- [ ] Geração mostra chave uma única vez
- [ ] Botão copiar funciona com feedback
- [ ] Revogação funciona
- [ ] Regeneração gera nova chave diferente

### **Funcionalidades Core UI:**
- [ ] Dashboard carrega e mostra estatísticas
- [ ] Domínios: CRUD completo funcional
- [ ] Contas: edição e testes SMTP/IMAP  
- [ ] Templates: criação, preview, eliminação
- [ ] Logs: filtros e detalhes funcionais
- [ ] Inbox: composição e envio funcionais

### **API v1 Integração:**
- [ ] POST /send retorna 200 com message_id
- [ ] GET /status retorna dados completos
- [ ] Respostas JSON seguem padrão (success, message, details)
- [ ] Autenticação com Bearer token funciona

### **Validações e Segurança:**
- [ ] Emails inválidos bloqueados
- [ ] Campos obrigatórios validados
- [ ] Anexos grandes bloqueados (se testado)
- [ ] Feedback de erro apropriado

### **Evidências Capturadas:**
- [ ] 25+ screenshots organizados
- [ ] Relatório completo em markdown
- [ ] API key funcional guardada
- [ ] Log de todos os testes executados

---

## 🎯 **ENTREGA PHASE 17B**

**Quando concluído:**
- ✅ **Todos os fluxos críticos testados** via browser automation
- ✅ **Screenshots organizados** por funcionalidade
- ✅ **API key real obtida** e testada com sucesso
- ✅ **Relatório detalhado** documentando resultados
- ✅ **Issues identificados** (se houver) documentados
- ✅ **SendCraft validado** como pronto para integração

**Resultado esperado:** 
```
🎉 SENDCRAFT UI + API: 100% TESTADO E VALIDADO!

✅ Gestão API Keys: Functional
✅ UI Management: Complete  
✅ API v1 Integration: Working
✅ SMTP/IMAP Tests: [Results]
✅ Data Validation: Secure

🚀 Ready for External Project Integration!
```

**Próximo passo:** Phase 18 - Guias de integração para projetos externos (sem implementação, apenas documentação)