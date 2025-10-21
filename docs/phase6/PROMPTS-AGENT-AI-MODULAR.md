# 🎯 PROMPTS FINAIS AGENT AI - Implementação Modular SendCraft

## 📋 **PROMPT 1: IMPLEMENTAR SISTEMA MODULAR + SSH TUNNEL (PRIORITÁRIO)**

```
SendCraft - Implementar Sistema Modular + SSH Tunnel Support

## Contexto:
- Repo: https://github.com/GGEDeveloper/SendCraft
- Branch: cursor/complete-sendcraft-web-interface-phase-5-7120
- Objetivo: Sistema modular (local SQLite + development SSH tunnel + production MySQL)

## Problema Atual:
- Config não é modular (apenas MySQL)
- Não há conexão local → dominios.pt via SSH tunnel  
- Falta sistema seed data para desenvolvimento

## Task Principal:
Implementar sistema de configurações modulares com SSH tunnel support para conectar localmente ao MySQL dominios.pt.

## Implementações Necessárias:

### 1. SUBSTITUIR config.py completo
- BaseConfig, LocalConfig, DevelopmentConfig, ProductionConfig, TestingConfig
- SSH tunnel configs para development mode
- SQLite para local mode
- MySQL direto para production

### 2. CRIAR sendcraft/utils/ssh_tunnel.py (NOVO)
- Classe SSHTunnelManager 
- Auto-setup SSH tunnel quando FLASK_ENV=development
- Gestão automática tunnel (start/stop/cleanup)
- Test MySQL connection via tunnel

### 3. MODIFICAR sendcraft/__init__.py
- Adicionar setup_ssh_tunnel_if_needed() antes init_extensions
- Load environment files (.env.local, .env.development, .env.production)
- Register cleanup handlers para SSH tunnel

### 4. CRIAR ficheiros environment
- .env.local (SQLite config)
- .env.development (SSH tunnel config)
- .env.production (MySQL direto)

### 5. CRIAR sendcraft/cli/seed_data.py
- Comando: flask seed-local-data
- Dados realistas: 5 domínios, 6 contas, 4 templates, 300+ logs
- Templates HTML profissionais (encomendas AliTools, boas-vindas B2B, portfolio Art&Shine)

### 6. ATUALIZAR requirements.txt
- Adicionar: paramiko==3.3.1, sshtunnel==0.4.0

### 7. CRIAR scripts execução
- run_local.py (SQLite mode)
- run_dev.py (SSH tunnel mode)

## Especificações Técnicas:

### SSH Tunnel Config:
- Host: ssh.dominios.pt
- User: artnshin  
- Key: ~/.ssh/dominios_pt
- Local port: 3307 → Remote port: 3306
- MySQL URL: mysql+pymysql://artnshin_sendcraft:g>bxZmj%25=JZt9Z%2Ci@localhost:3307/artnshin_sendcraft

### Modos Operação:
1. **local**: SQLite + seed data (offline development)
2. **development**: SSH tunnel → dominios.pt MySQL (testing com dados reais)
3. **production**: MySQL direto no servidor (deployment)

### Environment Files:
- .env.local: FLASK_ENV=local, DATABASE_URL=sqlite:///sendcraft_local.db
- .env.development: FLASK_ENV=development, SSH configs, MySQL via tunnel
- .env.production: FLASK_ENV=production, MySQL direto

## Resultado Esperado:
Sistema modular funcionando com 3 modos:
- python run_local.py (SQLite offline)
- python run_dev.py (SSH tunnel dominios.pt)
- FLASK_ENV=production python app.py (produção)

## Referências Implementação:
- docs/phase5/CONFIG-MODULAR-SSH-TUNNEL.md (especificação completa)
- docs/phase5/SEED-DATA-LOCAL.md (seed data system)
- docs/phase5/INSTRUCOES-SSH-SETUP.md (SSH setup)

Manter compatibilidade total com interface web já implementada.
```

---

## 📋 **PROMPT 2: TEMPLATES ENTERPRISE COMPLETOS (APÓS PROMPT 1)**

```
SendCraft - Completar Templates Enterprise HTML

## Contexto:
- Sistema modular implementado (Prompt 1)
- Templates atuais muito básicos
- Preciso templates enterprise quality

## Task:
Substituir templates básicos por templates enterprise completos baseados nas especificações.

## Templates a Implementar:

### 1. SUBSTITUIR templates/domains/list.html
- Baseado em docs/phase5/TEMPLATE-domains-list.md
- Funcionalidades: search, filtros, bulk operations, AJAX toggle
- Estatísticas cards, paginação avançada, modals confirmação
- Mobile responsive, toast notifications

### 2. CRIAR templates/accounts/list.html + form.html  
- Baseado em docs/phase5/TEMPLATE-accounts-list.md + TEMPLATE-accounts-form.md
- Lista: SMTP testing, progress bars limits, status badges
- Form: preview email, validation, SMTP config help

### 3. CRIAR templates/templates/list.html + editor.html
- Interface gestão templates
- Editor HTML com preview, syntax highlighting
- Variáveis help, category management

### 4. CRIAR templates/logs/list.html + detail.html
- Interface logs com filtros avançados
- Status timeline, search, export options
- Log detail com debug info

### 5. CRIAR templates/errors/404.html + 500.html
- Error pages SendCraft branded
- Navigation back, helpful links

## Requisitos:
- Bootstrap 5 classes (manter compatibilidade)
- Integração com sendcraft/routes/web.py (variáveis existentes)
- HTMX para CRUD operations
- Mobile responsive
- Toast notifications system
- Modals para confirmações

## Funcionalidades Avançadas:
- Bulk operations com checkboxes
- Real-time SMTP testing
- Form validations client-side
- Loading states
- Confirm dialogs Bootstrap

Resultado: Interface enterprise completa, professional quality.
```

---

## 📋 **PROMPT 3: JAVASCRIPT AVANÇADO + BUG FIXES**

```
SendCraft - JavaScript Avançado + Bug Fixes Finais

## Task:
Expandir static/js/app.js com funcionalidades avançadas + corrigir bugs identificados.

## JavaScript Implementações:

### 1. SMTP Testing Avançado
- Modal results detalhados (servidor, porta, tempo resposta, security)
- Visual feedback durante teste
- Update status badges real-time
- Batch testing todas as contas

### 2. Real-time Dashboard Updates  
- Auto-refresh stats cada 30s via /api/stats/live
- Chart.js smooth updates
- Live notifications
- Connection status indicator

### 3. Form Validations
- Client-side validation domínios (format, duplicates)
- Email format validation
- SMTP config validation
- Real-time feedback Bootstrap classes

### 4. Bulk Operations
- Select all/individual checkboxes
- Bulk activate/deactivate
- Bulk delete com progress
- Confirm modals Bootstrap

### 5. UX Enhancements
- Loading states em buttons
- Auto-save drafts (templates)
- Copy to clipboard
- Keyboard shortcuts (Ctrl+S save, etc.)

## Bug Fixes:

### 1. URLs Inconsistentes
- url_for('web.domain_new') → url_for('web.domains_new')
- url_for('web.domain_detail') → remover ou criar rota
- Corrigir todos os URL references

### 2. Methods Missing
- EmailAccount.get_smtp_password() usar get_password()
- EmailAccount.set_smtp_password() usar set_password()

### 3. Error Handling
- Flash messages consistentes
- Graceful degradation APIs
- CSRF token handling

## Success Criteria:
- ✅ SMTP testing com modal detalhado
- ✅ Real-time dashboard updates
- ✅ Form validations funcionam
- ✅ Bulk operations sem erros
- ✅ Mobile responsive
- ✅ URLs todos corretos

Resultado: Interface interativa moderna, UX profissional.
```

---

## 📋 **PROMPT 4: DOCUMENTAÇÃO E SETUP FINAL**

```
SendCraft - Documentação Setup + Validation

## Task:
Criar documentação final setup e scripts validação.

## Criar Ficheiros:

### 1. README.md atualizado
- Setup instructions (local, development, production)
- SSH tunnel setup
- Environment configs
- Troubleshooting

### 2. INSTALL.md
- Step-by-step installation
- Dependencies
- SSH key setup
- Database setup

### 3. Scripts Validação
- validate_setup.py (test all configs)
- test_ssh_tunnel.py (test SSH connection)  
- test_mysql.py (test database connections)

### 4. Docker Support (opcional)
- Dockerfile para development
- docker-compose.yml
- ENV configs para containers

## Validações Implementar:

### 1. Config Validation
- Test local SQLite mode
- Test development SSH tunnel mode  
- Test production MySQL mode
- Verify all environment variables

### 2. Database Validation
- Test SQLite creation + seed
- Test SSH tunnel MySQL connection
- Test production MySQL connection
- Verify all models work

### 3. Interface Validation  
- Test all routes (no 404s)
- Test CRUD operations
- Test SMTP functionality
- Test responsive design

## Resultado:
Documentação completa, setup automatizado, validation scripts funcionais.
```

---

## 🎯 **SEQUÊNCIA DE EXECUÇÃO RECOMENDADA**

### **1º PROMPT 1: Sistema Modular (CRÍTICO - 2h)**
- Implementa configurações modulares + SSH tunnel
- Resultado: 3 modos operação (local/dev/prod)

### **2º PROMPT 2: Templates Enterprise (1.5h)**
- Templates profissionais completos
- Resultado: Interface visual enterprise

### **3º PROMPT 3: JavaScript + Bugs (1h)**
- Funcionalidades avançadas + correções
- Resultado: UX moderna interativa

### **4º PROMPT 4: Documentação (30min - opcional)**
- Setup docs + validation
- Resultado: Sistema completo documentado

---

## ✅ **RESULTADO FINAL ESPERADO**

**SendCraft Email Manager Enterprise 100%:**

### **Funcionalidades:**
- 🏠 Dashboard real-time KPIs + charts
- 🌐 CRUD Domínios (bulk ops, search, filtros)
- 📧 CRUD Contas (SMTP testing, limits tracking)
- 📝 Editor Templates HTML (preview, variables)
- 📊 Logs interface (filtros, export, detail)
- ⚙️ SSH tunnel automático para development

### **Modos de Execução:**
```bash
# Local Development (SQLite + seed data)
python run_local.py
→ http://localhost:5000

# Development com Dados Reais (SSH tunnel → dominios.pt)
python run_dev.py  
→ http://localhost:5000 (dados MySQL dominios.pt)

# Production (servidor)
FLASK_ENV=production python app.py
→ http://email.artnshine.pt:9000
```

### **Vantagens Sistema:**
- ✅ Desenvolvimento offline (SQLite)
- ✅ Testing dados reais (SSH tunnel)
- ✅ Deploy production simples
- ✅ Configs modulares
- ✅ SSH automático
- ✅ Cleanup automático
- ✅ Interface enterprise

**Prompts optimizados para execução sequencial e resultado production-ready!** 🚀