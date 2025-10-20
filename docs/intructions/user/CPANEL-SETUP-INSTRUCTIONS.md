# 🔧 **INSTRUÇÕES CPANEL - Preparação SendCraft**

**Data:** 20 de Outubro de 2025  
**Objetivo:** Preparar ambiente cPanel para deploy do SendCraft (Email Manager)  
**Subdomínio:** email.alitools.pt  

---

## 📋 **FASE 1: Criar Subdomínio (10 min)**

### **1.1 - Aceder ao cPanel**
```
URL: https://my.dominios.pt
Login: [suas credenciais]
Navegar: Serviços → Value Linux V2 → Login to cPanel
```

### **1.2 - Criar Subdomínio**
```
1. No cPanel, procurar secção "Domains"
2. Clicar "Create A New Domain"
3. Preencher:
   - Domain: email.alitools.pt
   - Desmarcar "Share document root with..."
   - Document Root: /public_html/sendcraft
4. Clicar "Submit"
5. Aguardar confirmação (pode levar 5-15 min para propagar)
```

### **1.3 - Verificar Criação**
```
- Ir para "File Manager"
- Verificar que foi criada pasta /public_html/sendcraft/
- Criar ficheiro teste: /public_html/sendcraft/index.html
  Conteúdo: <h1>SendCraft Coming Soon</h1>
- Abrir https://email.alitools.pt (deve mostrar a mensagem)
```

---

## 📦 **FASE 2: Python Application Setup (15 min)**

### **2.1 - Criar Python App**
```
1. No cPanel, procurar "Python App" (secção Software)
2. Clicar "Create Application"
3. Configurar:
   - Python Version: 3.9 (ou mais recente disponível)
   - Application Root: sendcraft
   - Application URL: email.alitools.pt
   - Application Startup File: app.py
4. Clicar "Create"
```

### **2.2 - Configurar Environment**
```
1. Na aplicação criada, ir para "Configuration"
2. Adicionar variáveis de ambiente:
   - FLASK_ENV: production
   - DATABASE_URL: sqlite:///email_manager.sqlite
3. Anotar o "Entry Point" gerado (será usado pelo agente)
```

### **2.3 - Testar Python**
```
1. Clicar "Open Terminal" na Python App
2. Executar:
   python3 --version
   pip --version
3. Verificar outputs (deve mostrar Python 3.9+ e pip funcionando)
```

---

## 🔐 **FASE 3: Configurações de Segurança (10 min)**

### **3.1 - Gerar Secrets**
```
No terminal local (WSL2 ou equivalente):

# Gerar SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY =', repr(secrets.token_urlsafe(32)))"

# Gerar API_KEY
python3 -c "import secrets; print('API_KEY_ALITOOLS =', repr('SC_' + secrets.token_urlsafe(32)))"

# Gerar ENCRYPTION_KEY
python3 -c "import secrets; print('ENCRYPTION_KEY =', repr(secrets.token_urlsafe(32)))"

# ANOTAR TODOS OS OUTPUTS GERADOS!
```

### **3.2 - Criar Ficheiro de Configuração**
```
No File Manager do cPanel:
1. Navegar para /public_html/sendcraft/
2. Criar pasta "instance"
3. Criar ficheiro "instance/config.py" com:

SECRET_KEY = '[OUTPUT_GERADO_ACIMA]'
API_KEYS = {
    'alitools-prod': '[API_KEY_GERADO_ACIMA]'
}
ENCRYPTION_KEY = '[ENCRYPTION_KEY_GERADO_ACIMA]'
DEFAULT_FROM_NAME = 'ALITOOLS'
SQLITE_PATH = '/home/[SEU_USERNAME_CPANEL]/public_html/sendcraft/email_manager.sqlite'

# Substituir [SEU_USERNAME_CPANEL] pelo username real!
```

---

## 📬 **FASE 4: Configuração SpamExperts (20 min)**

### **4.1 - Ativar SpamExperts**
```
1. Voltar a https://my.dominios.pt
2. Ir para área do serviço Value Linux V2
3. Procurar "SpamExperts" ou "E-mail Security"
4. Se não estiver ativo, abrir ticket:
   
   Assunto: Ativação SpamExperts Outbound para SendCraft
   
   Mensagem:
   Olá,
   
   Preciso ativar o serviço SpamExperts com funcionalidade 
   Outbound para o plano Value Linux V2 (alitools.pt).
   
   Objetivo: Envio de emails transacionais via aplicação Python 
   no subdomínio email.alitools.pt.
   
   Podem ativar este serviço?
   
   Obrigado!
```

### **4.2 - Configurar Utilizador Outbound** 
*(apenas se SpamExperts estiver disponível)*
```
1. Aceder painel SpamExperts via área cliente
2. Ir para "Outgoing" → "Users"
3. Clicar "Add User"
4. Configurar:
   - Domain: alitools.pt
   - Username: sendcraft-api
   - Password: [GERAR PASSWORD FORTE]
   - Rate Limit: 1000 per hour
   - Status: Enabled
5. ANOTAR USERNAME E PASSWORD GERADOS!
```

### **4.3 - Fallback: Configuração cPanel Direto**
*(se SpamExperts não estiver disponível)*
```
Usar configuração direta:
- SMTP Server: mail.alitools.pt
- Port: 587
- Username: encomendas@alitools.pt
- Password: 6f2zniWMN6aUFaD
- TLS: True

NOTA: Pode falhar por firewall (problema original)
```

---

## ✅ **FASE 5: Validação Final (5 min)**

### **5.1 - Checklist Pré-Deploy**
```
- [ ] Subdomínio email.alitools.pt criado e acessível
- [ ] Python App configurada (3.9+)
- [ ] Ficheiro instance/config.py criado com secrets
- [ ] SpamExperts configurado (ou fallback anotado)
- [ ] Terminal Python funcional
- [ ] File Manager com permissões de escrita
```

### **5.2 - Informações para o Agente**
```
Anotar e guardar para dar ao agente:

1. CPANEL_USERNAME: [seu username cPanel]
2. APPLICATION_ROOT: /public_html/sendcraft/
3. PYTHON_VERSION: [versão confirmada]
4. API_KEY_ALITOOLS: [key gerada]
5. SECRET_KEY: [key gerada]  
6. ENCRYPTION_KEY: [key gerada]
7. SMTP_CONFIG:
   - Server: smtp.antispamcloud.com (ou mail.alitools.pt)
   - Port: 587
   - Username: sendcraft-api@alitools.pt (ou encomendas@alitools.pt)
   - Password: [password do SpamExperts ou 6f2zniWMN6aUFaD]
```

---

## 🚨 **Resolução de Problemas Comuns**

### **Subdomínio não resolve:**
```
- Aguardar até 2 horas para propagação DNS
- Verificar se Document Root está correto
- Contactar suporte Domínios.pt se persistir
```

### **Python App não aparece:**
```
- Verificar se Value Linux V2 suporta Python Apps
- Tentar Python version diferente (3.8, 3.10)
- Contactar suporte se funcionalidade não existir
```

### **SpamExperts não disponível:**
```
- Usar configuração direta mail.alitools.pt:587
- Ou considerar relay Gmail como temporário
- Documentar para resolver firewall posteriormente
```

---

## 📞 **Suporte Domínios.pt**

Se encontrares problemas:
```
1. Abrir ticket na área de cliente
2. Mencionar: "Configuração para aplicação Python SendCraft"
3. Incluir: subdomínio, Python version, erro específico
4. Pedir assistência técnica especializada
```

---

**✅ Quando completares todas as fases, o ambiente estará pronto para o agente fazer o deploy!**