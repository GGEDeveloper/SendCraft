# 🎛️ SendCraft UI - Guia Completo de Gestão

## 🚀 Visão Geral

A interface web do SendCraft fornece gestão completa do sistema de envio de emails, incluindo domínios, contas, API keys, templates, logs e inbox. Esta interface permite configurar e monitorizar todo o sistema sem necessidade de acesso direto à base de dados.

### **Acesso à Interface**
```
URL: http://localhost:5000
Login: Baseado em configuração (sem autenticação por padrão em desenvolvimento)
```

---

## 📊 **Dashboard Principal**

### **Localização:** `/` (página inicial)

O dashboard oferece uma visão geral do sistema:

#### **Métricas Principais**
- **Domínios:** Total e ativos
- **Contas:** Total e ativas  
- **Templates:** Total e ativos
- **Emails 24h:** Enviados/falhados e taxa de sucesso

#### **Secções**
- **Logs Recentes:** Últimos 10 envios
- **Domínios:** Lista com estatísticas de contas e templates
- **Estatísticas:** Gráficos de envio por período

#### **Funcionalidades**
- ✅ Refresh automático de estatísticas
- ✅ Links diretos para gestão
- ✅ Alertas para problemas (domínios inativos, contas com erro)

---

## 🏠 **Gestão de Domínios**

### **Localização:** `/domains`

#### **Funcionalidades Disponíveis**

**📋 Lista de Domínios**
- Paginação (20 por página)
- Filtros: pesquisa por nome, status (ativo/inativo)
- Estatísticas: contagem de contas, templates, emails enviados (30 dias)

**➕ Criar Domínio**
- **Validações:** Formato DNS válido, duplicação
- **Campos:** Nome (obrigatório), descrição, status ativo
- **Exemplo:** `loja.exemplo.com`, `empresa.pt`

**✏️ Editar Domínio**
- **Limitação:** Nome não editável (chave primária)
- **Editável:** Descrição, status ativo/inativo

**🔄 Toggle Ativo/Inativo**
- Via botão individual ou operações bulk
- **Impacto:** Domínios inativos bloqueiam envio de emails

**🗑️ Eliminação**
- **Proteção:** Não permite eliminar se tem contas ou templates associados
- **Verificação:** Alerta antes de eliminar

#### **Operações Bulk**
- Ativar múltiplos domínios
- Desativar múltiplos domínios
- Eliminar (respeitando dependências)

---

## 👥 **Gestão de Contas de Email**

### **Localização:** `/accounts`

#### **Funcionalidades Disponíveis**

**📋 Lista de Contas**
- Paginação (20 por página)
- Filtros: por domínio, pesquisa, status
- **Estatísticas em tempo real:**
  - Emails enviados hoje/mês
  - Limites diários/mensais
  - Status SMTP (testado/não testado)

**➕ Criar Conta**
- **Campos obrigatórios:**
  - Domínio (seleção)
  - Parte local (antes do @)
  - Servidor SMTP + porta
  - Username SMTP
  - Password SMTP (encriptada)
- **Configurações SMTP:**
  - TLS/SSL/Nenhum
  - Portas típicas: 587 (TLS), 465 (SSL), 25 (inseguro)
- **Configurações IMAP:**
  - Servidor, porta (padrão: 993 SSL)
  - Credenciais (partilhadas com SMTP)
- **Limites:**
  - Diário (padrão: 1000)
  - Mensal (padrão: 20000)

**✏️ Editar Conta**
- **Editável:** Todos os campos exceto email_address (calculado)
- **Password:** Apenas se fornecida nova (encriptação automática)
- **Estatísticas:** Apresentadas durante edição

**🧪 Testes de Conectividade**
- **Teste SMTP:** Conecta e autentica (via AJAX)
- **Teste IMAP:** Conecta, autentica e acede INBOX (via AJAX)
- **Timeout:** 60s para IMAP, 10s para SMTP
- **Feedback:** Detalhes técnicos (servidor, porta, segurança, tempo resposta)

**🔑 Gestão de API Keys (Secção Dedicada)**
- **Localização:** `/accounts/{id}/api`
- **Estados:**
  - API Desabilitada
  - API Habilitada sem chave
  - API Habilitada com chave ativa
- **Operações:**
  - Ativar/Desativar acesso API
  - Gerar chave (primeira vez)
  - Rotacionar chave (nova chave, invalida anterior)
  - Revogar chave (remove completamente)
- **UX Crítico:**
  - Chave mostrada **apenas uma vez** após geração
  - Botão "Copiar" para clipboard
  - Alerta: "Guarde esta chave agora, não será mostrada novamente"
  - Confirmação antes de rotação/revogação

**🗑️ Eliminação**
- **Proteção:** Bloqueia se tem logs de email ou emails na inbox
- **Verificação:** Contagem de dependências apresentada

---

## 📝 **Gestão de Templates**

### **Localização:** `/templates`

#### **Funcionalidades Disponíveis**

**📋 Lista de Templates**
- Filtros: por domínio, categoria
- Categorias: extraídas dinamicamente dos templates existentes
- Paginação: 20 por página

**➕ Criar Template**
- **Campos obrigatórios:**
  - Domínio (associação)
  - Chave (template_key - única por domínio)
  - Nome de apresentação
  - Assunto
- **Campos opcionais:**
  - Corpo HTML (editor básico)
  - Corpo texto simples
  - Categoria (organizacional)
  - Variáveis disponíveis (documentação)
- **Versioning:** Incremento automático a cada edição

**✏️ Editor de Templates**
- **Localização:** `/templates/{id}/edit`
- **Editor HTML:** Área de texto grande com syntax highlighting básico
- **Variáveis:** Suporte para placeholders `{{nome_variavel}}`
- **Preview em tempo real:** Via AJAX com dados exemplo

**👁️ Preview Dinâmico**
- **Endpoint:** `/templates/{id}/preview`
- **Dados exemplo:** Nome, número encomenda, total, data
- **Renderização:** HTML e assunto com variáveis substituídas
- **Apresentação:** Modal ou painel lateral

**🗑️ Eliminação**
- **Proteção:** Verificar se está a ser usado (implementação futura)
- **Confirmação:** Alerta antes de eliminar

---

## 📄 **Sistema de Logs**

### **Localização:** `/logs`

#### **Funcionalidades de Consulta**

**🔍 Filtros Avançados**
- **Por domínio:** Dropdown com domínios disponíveis
- **Por status:** PENDING, SENDING, SENT, DELIVERED, FAILED, BOUNCED
- **Por data:** Range de datas (from/to)
- **Paginação:** 50 logs por página

**📊 Visualização**
- **Lista:** Ordenação por data descendente
- **Campos mostrados:**
  - Timestamp (criação/envio)
  - Remetente (conta)
  - Destinatário
  - Assunto (truncado)
  - Status (com cores)
  - Ações (ver detalhe)

**🔍 Detalhe do Log**
- **Localização:** `/logs/{id}`
- **Informações completas:**
  - Metadata (IPs, User-Agent)
  - Payload original (se disponível)
  - Resposta SMTP
  - Timestamps de todas as transições
  - Variáveis usadas (templates)
  - Anexos enviados

#### **Estados de Log**
```
PENDING → SENDING → SENT → DELIVERED
                  ↓
                FAILED
```

---

## 📧 **Inbox de Emails**

### **Localização:** `/emails/inbox` ou `/emails/inbox/{account_id}`

#### **Interface de 3 Painéis**
- **Painel esquerdo:** Seletor de contas
- **Painel central:** Lista de emails
- **Painel direito:** Conteúdo do email selecionado

#### **Funcionalidades**

**📬 Visualização**
- **Multi-conta:** Switcher entre contas ativas
- **Lista:** Emails da conta selecionada
- **Preview:** HTML/texto com anexos

**✍️ Composição de Emails**
- **Localização:** Modal ou página dedicada
- **Campos:**
  - Para (múltiplos, separados por vírgula)
  - CC/BCC (opcional)
  - Assunto
  - Corpo HTML (editor)
  - Corpo texto (opcional)
- **Anexos:**
  - Upload múltiplo
  - Limite: 5MB por arquivo
  - Tipos aceites: PDF, DOC, IMG, etc.
  - Preview antes do envio
- **Validações:**
  - Formato de email (regex)
  - Sanitização HTML (remove scripts, iframes, handlers on*)
  - Tamanho total de anexos

**📤 Envio via UI**
- **Endpoint:** `POST /emails/send`
- **Processamento:** Via SMTP configurado na conta
- **Feedback:** Success/error com detalhes técnicos
- **Log:** Criação automática de EmailLog

---

## 🔧 **Configurações e Testes**

### **Testes SMTP/IMAP**

#### **Via Interface Individual**
- **Botão:** "Testar SMTP" na página de edição de conta
- **Processo:** Conexão → TLS/SSL → Autenticação → Desconexão
- **Resultado:** Modal com detalhes técnicos
- **Timeout:** 10s para SMTP, 60s para IMAP

#### **Via AJAX Genérico**
- **Endpoint:** `/api/smtp/test`
- **Payload:** Configurações SMTP temporárias
- **Uso:** Validação durante criação de conta

### **Estatísticas em Tempo Real**
- **Endpoint:** `/api/stats/live`
- **Refresh:** Automático de 30 em 30 segundos
- **Dados:** Contadores gerais, emails 24h, rate limits

---

## 🚨 **Alertas e Validações**

### **Validações de Formulário**
- **Client-side:** JavaScript básico para campos obrigatórios
- **Server-side:** Validações rigorosas com mensagens claras
- **UX:** Flash messages em português

### **Proteções de Sistema**
- **Eliminação:** Verificação de dependências
- **Configurações críticas:** Confirmação dupla
- **API Keys:** Geração segura, exibição única
- **Passwords:** Encriptação automática via SECRET_KEY

### **Estados de Erro Comuns**
- **SMTP inválido:** "Credenciais SMTP inválidas"
- **Conexão falhada:** "Erro de conexão ao servidor SMTP"
- **Timeout:** "Timeout na conexão (60s)"
- **Dependências:** "Não é possível eliminar X com Y associados"

---

## 📱 **Interface Responsiva**

### **Compatibilidade**
- **Desktop:** Interface completa
- **Tablet:** Layout adaptado
- **Mobile:** Navegação simplificada

### **Tecnologias**
- **Frontend:** Bootstrap 5, JavaScript vanilla
- **AJAX:** Fetch API para operações assíncronas
- **Icons:** Bootstrap Icons
- **Charts:** Chart.js (se aplicável)

---

## 🔐 **Segurança da UI**

### **Autenticação**
- **Desenvolvimento:** Sem autenticação (localhost)
- **Produção:** Configurar autenticação adequada

### **Autorização**
- **API Keys:** Geradas com cryptographically secure random
- **Passwords:** Encriptadas via SECRET_KEY do Flask
- **Sessions:** Gestão padrão do Flask

### **Validação de Input**
- **XSS:** Sanitização de HTML
- **CSRF:** Tokens em formulários (implementar se necessário)
- **SQL Injection:** SQLAlchemy ORM (proteção automática)

---

## 📋 **Fluxos de Trabalho Típicos**

### **Setup Inicial Completo**
1. **Domínio:** Criar domínio `empresa.pt`
2. **Conta:** Criar `vendas@empresa.pt` com SMTP válido
3. **Teste:** Verificar conectividade SMTP/IMAP
4. **API:** Ativar API e gerar chave
5. **Template:** Criar template de confirmação (opcional)
6. **Teste email:** Enviar via inbox para validar

### **Integração com Projeto Externo**
1. **API Key:** Gerar na UI, copiar uma única vez
2. **Documentação:** Consultar `/docs/phase17/api-reference.md`
3. **Teste:** `curl` básico para validar conectividade
4. **Implementação:** Usar exemplos Node.js/PHP/cURL
5. **Monitorização:** Logs na UI para debugging

### **Manutenção Regular**
1. **Logs:** Revisão semanal de falhas
2. **Limits:** Monitorizar aproximação aos limites
3. **Keys:** Rotação mensal de API keys
4. **Testes:** Verificação mensal de conectividade SMTP/IMAP

---

## 🆘 **Troubleshooting Comum**

### **API Key não funciona**
- Verificar se API está ativada na conta
- Confirmar formato: `Authorization: Bearer sendcraft_...`
- Gerar nova chave se necessário

### **SMTP falha**
- Testar conectividade na UI
- Verificar servidor/porta/credenciais
- Confirmar TLS/SSL apropriado

### **Emails não chegam**
- Verificar logs para status SENT/FAILED
- Validar configuração SMTP
- Verificar spam/quarentena do destinatário

### **Performance lenta**
- Verificar tamanho/número de anexos
- Considerar upload prévio para arquivos grandes
- Usar bulk=true para múltiplos destinatários

---

**Versão:** UI v1.0  
**Última atualização:** 24 Outubro 2025  
**Compatibilidade:** SendCraft Phase 15+