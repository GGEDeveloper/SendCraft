# 🚨 Correções Obrigatórias Pré-Deploy - SendCraft

## ❌ PROBLEMAS CRÍTICOS IDENTIFICADOS

### 1. **MAIL_SERVER Global vs SMTP Individual**

**Problema**: Documentação de deploy sugere configuração global, mas sistema usa configurações individuais por conta.

**Impacto**: Deploy no Vercel falhará porque:
- Flask-Mail será inicializado com servidor global inexistente
- SMTPService ignorará configurações globais
- Contas não conseguirão enviar emails

### 2. **Flask-Mail Não Utilizado**

**Problema**: Flask-Mail inicializado mas nunca usado no código real.

**Solução**: Remover Flask-Mail completamente ou usar apenas para notificações internas.

### 3. **Hardcoded Domain References**

**Problema**: Múltiplas referências hardcoded a dominios específicos.

**Locais Afetados**:
- `sendcraft/routes/web.py`: `or 'mail.alitools.pt'`
- Templates de formulário
- Defaults de configuração

---

## 🔧 CORREÇÕES OBRIGATÓRIAS

### **Fix 1: Remover Flask-Mail Global**

**Arquivo**: `sendcraft/extensions.py`
```python
# REMOVER
from flask_mail import Mail
mail = Mail()

# MANTER APENAS
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

db = SQLAlchemy()
cors = CORS()
migrate = Migrate()
```

**Arquivo**: `sendcraft/__init__.py`
```python
# REMOVER
from .extensions import db, mail, cors, migrate
mail.init_app(app)

# SUBSTITUIR POR
from .extensions import db, cors, migrate
```

### **Fix 2: Limpar config.py**

**Arquivo**: `config.py`
```python
# REMOVER configurações SMTP globais não utilizadas
# DEFAULT_SMTP_SERVER = '...'
# DEFAULT_SMTP_PORT = ...
# MAIL_SERVER = '...'
# MAIL_PORT = ...
# etc.

# MANTER APENAS
SECRET_KEY = os.environ.get('SECRET_KEY') or 'sendcraft-dev-key'
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'sendcraft-encryption-32-chars-key!!'
```

### **Fix 3: Corrigir Hardcoded IMAP**

**Arquivo**: `sendcraft/routes/web.py`
```python
# LINHA ~450-460 - CORRIGIR
# ANTES (ERRADO)
imap_server=request.form.get('imap_server', '').strip() or 'mail.alitools.pt'

# DEPOIS (CORRETO)
imap_server=request.form.get('imap_server', '').strip() or f'mail.{account.domain.name}'
```

### **Fix 4: EmailAccount Constructor**

**Arquivo**: `sendcraft/models/account.py`
```python
# LINHA ~45 - DEFAULT SMTP SERVER
# ANTES (ERRADO)
smtp_server = Column(String(200), nullable=False, default='smtp.antispamcloud.com')

# DEPOIS (CORRETO - usar domínio dinâmico)
smtp_server = Column(String(200), nullable=False)

# No __init__ method, adicionar lógica dinâmica
if 'smtp_server' not in kwargs and 'domain_id' in kwargs:
    domain = Domain.query.get(kwargs['domain_id'])
    if domain:
        kwargs['smtp_server'] = f'mail.{domain.name}'
```

### **Fix 5: Atualizar vercel.md**

**Arquivo**: `docs/deploy/vercel.md`
```bash
# REMOVER todas as configurações MAIL_* globais
# - MAIL_SERVER=smtp.alitools.pt  ❌
# - MAIL_PORT=587                 ❌
# - MAIL_USERNAME=...             ❌
# - MAIL_PASSWORD=...             ❌

# MANTER APENAS
- FLASK_ENV=production
- SECRET_KEY=sua-chave-secreta
- SQLALCHEMY_DATABASE_URI=mysql+pymysql://...
- ENCRYPTION_KEY=chave-32-chars-para-passwords
```

---

## 🧪 VALIDAÇÃO PÓS-CORREÇÕES

### **Test 1: Import Check**
```bash
python3 -c "from sendcraft import create_app; app=create_app('production'); print('✅ App loads without Flask-Mail')"
```

### **Test 2: Account SMTP Config**
```python
from sendcraft.models.account import EmailAccount
from sendcraft.services.smtp_service import SMTPService

# Cada conta deve ter sua própria configuração SMTP
account = EmailAccount.query.first()
config = account.get_smtp_config('test-key')
assert 'server' in config
assert config['server'] != 'smtp.antispamcloud.com'  # Não deve usar default global
```

### **Test 3: No Hardcoded Domains**
```bash
grep -r "mail.alitools.pt" sendcraft/ || echo "✅ Sem hardcoded alitools.pt"
grep -r "smtp.antispamcloud.com" sendcraft/ || echo "✅ Sem hardcoded antispamcloud"
```

---

## 🎯 RESUMO DE AÇÕES

**Críticas (Obrigatórias)**:
1. ✅ Remover Flask-Mail das extensions e init
2. ✅ Limpar configurações SMTP globais não utilizadas
3. ✅ Corrigir hardcoded `mail.alitools.pt` para dinâmico
4. ✅ Atualizar documentação de deploy (remover MAIL_* vars)
5. ✅ Testar que cada conta usa seu próprio SMTP

**Recomendadas**:
1. Adicionar validação de domínio nos formulários
2. Implementar defaults inteligentes por domínio
3. Logs para debug de configurações SMTP

---

**Tempo estimado**: 30-45 minutos para todas as correções
**Impacto**: Critical - Deploy falhará sem essas correções
**Prioridade**: P0 - Fazer antes do primeiro deploy
