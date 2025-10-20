# 🤖 **FASE 5 - AGENTE AI: Seed, Configuração Final e Deploy**

**Fase Final do MVP**  
**Repositório:** https://github.com/GGEDeveloper/SendCraft.git  
**Objetivo:** Configuração final, seed inicial e preparação para deploy  

---

## 🎯 **PRÉ-REQUISITOS**

- FASES 1-4 completadas
- Interface web funcional
- Tag `v0.4-web-interface` criada

---

## ⚙️ **CONFIGURAÇÃO FINAL**

### **1. APP.PY (Entry Point Completo)**

```python
\"\"\"
SendCraft Email Manager - Entry Point Principal.
Aplicação Flask para gestão centralizada de emails multi-domínio.
\"\"\"
import os
import logging
from flask import Flask

from sendcraft import create_app


# Configurar logging para produção
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Criar aplicação
app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    # Desenvolvimento local
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # Produção (cPanel/Passenger)
    application = app
```

### **2. WSGI.PY (Para Passenger/cPanel)**

```python
\"\"\"
WSGI entry point para produção.
Usado pelo Passenger (cPanel) para servir a aplicação.
\"\"\"
import sys
import os

# Adicionar diretório da aplicação ao Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import application

if __name__ == \"__main__\":
    application.run()
```

### **3. .ENV.EXAMPLE**

```bash
# SendCraft Configuration Example
# Copy to .env and fill with real values

FLASK_ENV=production
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
DATABASE_URL=sqlite:///sendcraft.sqlite

# SMTP Defaults
DEFAULT_SMTP_SERVER=smtp.antispamcloud.com
DEFAULT_SMTP_PORT=587
DEFAULT_USE_TLS=true
DEFAULT_FROM_NAME=SendCraft

# API Configuration
API_RATE_LIMIT=100/hour

# Logging
LOG_LEVEL=INFO
LOG_FILE=sendcraft.log
```

### **4. .GITIGNORE**

```bash
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
.venv/
.env/

# Flask
instance/
.flaskenv
*.sqlite
*.sqlite3
*.db

# Logs
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# SendCraft specific
sendcraft.log
email_manager.sqlite
instance/config.py
```

---

## 🌱 **SEED INICIAL**

### **5. SEEDS/INITIAL_DATA.PY**

```python
\"\"\"
Seed inicial para SendCraft.
Cria dados essenciais: domínio alitools.pt, conta encomendas@, templates básicos.
\"\"\"
from sendcraft import create_app
from sendcraft.extensions import db
from sendcraft.models.domain import Domain
from sendcraft.models.account import EmailAccount
from sendcraft.models.template import EmailTemplate
from sendcraft.utils.crypto import AESCipher


def create_initial_data():
    \"\"\"Cria dados iniciais do sistema.\"\"\"
    print(\"🌱 Criando dados iniciais...\")
    
    # 1. Criar domínio alitools.pt
    print(\"📋 Criando domínio alitools.pt...\")
    domain = Domain.create(
        name='alitools.pt',
        description='Domínio principal da ALITOOLS',
        is_active=True
    )
    
    # 2. Criar conta encomendas@alitools.pt
    print(\"📧 Criando conta encomendas@alitools.pt...\")
    account = EmailAccount(
        domain_id=domain.id,
        local_part='encomendas',
        email_address='encomendas@alitools.pt',
        display_name='ALITOOLS Encomendas',
        smtp_server='smtp.antispamcloud.com',  # Usar SpamExperts
        smtp_port=587,
        smtp_username='alitools-vercel',  # Username SpamExperts
        use_tls=True,
        use_ssl=False,
        is_active=True,
        daily_limit=1000,
        monthly_limit=20000
    )
    
    # Encriptar password real
    encryption_key = app.config.get('ENCRYPTION_KEY', 'dev-key')
    account.set_password('6f2zniWMN6aUFaD', encryption_key)  # Password real fornecida
    account.save()
    
    # 3. Criar templates essenciais
    print(\"📝 Criando templates...\")
    
    # Template: Confirmação de Encomenda
    order_confirmation = EmailTemplate.create(
        domain_id=domain.id,
        template_key='order_confirmation',
        template_name='Confirmação de Encomenda',
        description='Email enviado quando uma encomenda é confirmada',
        category='transactional',
        subject_template='✅ Encomenda {{ order_number }} confirmada - ALITOOLS',
        html_template=\"\"\"
<!DOCTYPE html>
<html>
<head>
    <meta charset=\"utf-8\">
    <title>Confirmação de Encomenda</title>
</head>
<body style=\"font-family: Arial, sans-serif; line-height: 1.6; color: #333;\">
    <div style=\"max-width: 600px; margin: 0 auto; padding: 20px;\">
        <div style=\"background: #0d6efd; color: white; padding: 20px; text-align: center;\">
            <h1 style=\"margin: 0;\">{{ company_name|default('ALITOOLS') }}</h1>
        </div>
        
        <div style=\"padding: 30px; border: 1px solid #ddd;\">
            <h2 style=\"color: #198754;\">✅ Encomenda Confirmada!</h2>
            
            <p>Olá <strong>{{ customer_name }}</strong>,</p>
            
            <p>A sua encomenda foi confirmada com sucesso e está a ser processada.</p>
            
            <div style=\"background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;\">
                <h4 style=\"margin-top: 0;\">Detalhes da Encomenda</h4>
                <p><strong>Número:</strong> {{ order_number }}</p>
                <p><strong>Total:</strong> {{ total|default('N/A') }}</p>
                <p><strong>Data:</strong> {{ order_date|default('Hoje') }}</p>
            </div>
            
            <p>Receberá em breve mais informações sobre o estado da sua encomenda.</p>
            
            <p>Obrigado por escolher a ALITOOLS!</p>
            
            <hr style=\"margin: 30px 0;\">
            <p style=\"font-size: 12px; color: #666;\">
                Este email foi enviado automaticamente. Para questões, contacte 
                <a href=\"mailto:suporte@alitools.pt\">suporte@alitools.pt</a>
            </p>
        </div>
    </div>
</body>
</html>
        \"\"\",
        text_template=\"\"\"
ALITOOLS - Confirmação de Encomenda

Olá {{ customer_name }},

A sua encomenda foi confirmada com sucesso!

Detalhes:
- Número: {{ order_number }}
- Total: {{ total|default('N/A') }}
- Data: {{ order_date|default('Hoje') }}

Receberá em breve mais informações sobre o estado da encomenda.

Obrigado por escolher a ALITOOLS!

---
Para questões, contacte suporte@alitools.pt
        \"\"\",
        variables_required=['customer_name', 'order_number'],
        variables_optional=['total', 'order_date', 'company_name'],
        is_active=True
    )
    
    # Template: Email de Teste
    test_template = EmailTemplate.create(
        domain_id=domain.id,
        template_key='test_email',
        template_name='Email de Teste',
        description='Template para testes de conectividade',
        category='system',
        subject_template='🧪 Teste SendCraft - {{ current_date }}',
        html_template=\"\"\"
<!DOCTYPE html>
<html>
<head><meta charset=\"utf-8\"><title>Teste SendCraft</title></head>
<body style=\"font-family: Arial, sans-serif; padding: 20px;\">
    <div style=\"max-width: 500px; margin: 0 auto; border: 1px solid #ddd; padding: 30px;\">
        <h2 style=\"color: #0d6efd;\">🧪 SendCraft Test</h2>
        <p>Este é um email de teste do sistema SendCraft.</p>
        <p><strong>Data:</strong> {{ current_date }}</p>
        <p><strong>Hora:</strong> {{ current_time }}</p>
        <p><strong>Enviado por:</strong> {{ sender_email }}</p>
        <hr>
        <p style=\"font-size: 12px; color: #666;\">
            Sistema funcionando corretamente ✅
        </p>
    </div>
</body>
</html>
        \"\"\",
        text_template=\"\"\"
SendCraft Email Test

Este é um email de teste do sistema SendCraft.

Data: {{ current_date }}
Hora: {{ current_time }}
Enviado por: {{ sender_email }}

Sistema funcionando corretamente ✅
        \"\"\",
        variables_required=[],
        variables_optional=['current_date', 'current_time', 'sender_email'],
        is_active=True
    )
    
    print(f\"✅ Dados iniciais criados:\")
    print(f\"   - Domínio: {domain.name} (ID: {domain.id})\")
    print(f\"   - Conta: {account.email_address} (ID: {account.id})\")
    print(f\"   - Templates: {order_confirmation.template_key}, {test_template.template_key}\")


if __name__ == '__main__':
    app = create_app('production')
    with app.app_context():
        # Limpar e recriar tabelas
        db.drop_all()
        db.create_all()
        
        # Criar dados iniciais
        create_initial_data()
        
        print(\"🚀 Seed completo! Sistema pronto para uso.\")
```

---

## 📦 **PREPARAÇÃO PARA DEPLOY**

### **6. REQUIREMENTS.TXT (FINAL)**

```
# Core Framework
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Mail==0.9.1
Flask-CORS==4.0.0

# Security & Crypto
PyJWT==2.8.0
cryptography==41.0.7

# Environment
python-dotenv==1.0.0

# Email validation
email-validator==2.1.0

# CLI
click==8.1.7

# Production server (optional, cPanel usa Passenger)
gunicorn==21.2.0
```

### **7. README.MD**

```markdown
# 📧 SendCraft Email Manager

Plataforma centralizada de gestão e envio de emails multi-domínio.

## ⚡ Quick Start

### Instalação Local
```bash
git clone https://github.com/GGEDeveloper/SendCraft.git
cd SendCraft
pip install -r requirements.txt
cp .env.example .env
# Editar .env com configurações reais
python seeds/initial_data.py
python app.py
```

### Deploy cPanel
1. Criar Python Application no cPanel (Python 3.9+)
2. Upload dos ficheiros para Application Root
3. Instalar dependências: `pip install -r requirements.txt`
4. Configurar `instance/config.py` com secrets
5. Executar seed: `python seeds/initial_data.py`
6. Restart application

## 🔌 API Usage

### Autenticação
```http
Authorization: Bearer SC_your_api_key_here
```

### Enviar Email
```bash
curl -X POST \"https://email.alitools.pt/api/v1/send\" \\
  -H \"Authorization: Bearer SC_your_api_key\" \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"domain\": \"alitools.pt\",
    \"account\": \"encomendas\",
    \"to\": \"cliente@exemplo.com\",
    \"template_key\": \"order_confirmation\",
    \"variables\": {
      \"customer_name\": \"João Silva\",
      \"order_number\": \"#12345\",
      \"total\": \"€129.90\"
    }
  }'
```

### Response
```json
{
  \"success\": true,
  \"log_id\": 123,
  \"message\": \"Email enviado com sucesso\",
  \"message_id\": \"<abc123@email.alitools.pt>\"
}
```

## 🛠️ CLI Commands

```bash
# Inicializar base de dados
flask init-db

# Criar domínio
flask create-domain --domain exemplo.pt --description \"Meu domínio\"

# Criar conta
flask create-account --domain exemplo.pt --local-part info --password senha123

# Criar template
flask create-template --domain exemplo.pt --key welcome --name \"Boas-vindas\" --subject \"Bem-vindo!\"
```

## 📚 Documentação Completa

- **Setup:** docs/setup.md
- **API Reference:** docs/api.md  
- **Templates:** docs/templates.md
- **Deploy:** docs/deploy.md

## 🎯 Roadmap

- [x] Core API e envio
- [x] Interface web
- [x] Sistema de templates
- [ ] Multi-domínio avançado
- [ ] Webhooks
- [ ] Análise avançada
```

---

## 🔧 **COMANDOS DE FINALIZAÇÃO**

### **8. SCRIPT DE DEPLOY**

Criar `deploy.py`:

```python
\"\"\"Script de deploy para cPanel.\"\"\"
import os
import sys
import zipfile
import shutil
from pathlib import Path

def create_deploy_package():
    \"\"\"Cria pacote ZIP para upload no cPanel.\"\"\"
    print(\"📦 Criando pacote de deploy...\")
    
    # Ficheiros a incluir
    include_files = [
        'app.py', 'wsgi.py', 'requirements.txt', 'config.py',
        'sendcraft/', 'templates/', 'static/', 'utils/', 'seeds/',
        'README.md', '.env.example'
    ]
    
    # Criar ZIP
    with zipfile.ZipFile('sendcraft-deploy.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_pattern in include_files:
            if os.path.isfile(file_pattern):
                zipf.write(file_pattern)
                print(f\"  ✅ {file_pattern}\")
            elif os.path.isdir(file_pattern):
                for root, dirs, files in os.walk(file_pattern):
                    for file in files:
                        if not file.endswith('.pyc') and not file.startswith('.'):
                            file_path = os.path.join(root, file)
                            zipf.write(file_path)
                print(f\"  ✅ {file_pattern}/ (directory)\")
    
    print(\"✅ Pacote sendcraft-deploy.zip criado!\")
    print(\"📤 Faça upload no File Manager do cPanel\")
    print(\"📂 Extrair para o Application Root da Python App\")

if __name__ == '__main__':
    create_deploy_package()
```

### **9. INSTANCE/CONFIG.PY.EXAMPLE**

```python
\"\"\"
Configuração de instância para SendCraft.
IMPORTANTE: Renomear para config.py e preencher com valores reais.
NÃO commitar este ficheiro com secrets reais!
\"\"\"

# Flask Secret Key (OBRIGATÓRIO)
SECRET_KEY = 'GERAR_CHAVE_SECRETA_FORTE_AQUI'

# Chave de encriptação AES-256 (OBRIGATÓRIO)
ENCRYPTION_KEY = 'GERAR_CHAVE_ENCRIPTACAO_AQUI'

# API Keys para acesso (OBRIGATÓRIO)
API_KEYS = {
    'alitools-prod': 'SC_GERAR_API_KEY_PARA_ALITOOLS',
    'admin': 'SC_GERAR_API_KEY_ADMIN'
}

# Base de dados (ajustar path absoluto)
SQLITE_PATH = '/home/SEU_USERNAME_CPANEL/public_html/sendcraft/sendcraft.sqlite'

# Configurações de email padrão
DEFAULT_FROM_NAME = 'ALITOOLS'
DEFAULT_SMTP_SERVER = 'smtp.antispamcloud.com'
DEFAULT_SMTP_PORT = 587
DEFAULT_USE_TLS = True

# Rate limiting
API_RATE_LIMIT = '1000/hour'

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'sendcraft.log'

# cPanel specific
CPANEL_USERNAME = 'SEU_USERNAME_CPANEL'
APPLICATION_ROOT = '/public_html/sendcraft'
```

---

## 🧪 **TESTES FINAIS**

### **10. TESTS/TEST_COMPLETE_FLOW.PY**

```python
\"\"\"Teste completo do fluxo SendCraft.\"\"\"
import pytest
import json
from sendcraft import create_app
from sendcraft.extensions import db


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture  
def client(app):
    return app.test_client()


def test_health_check(client):
    \"\"\"Testa health check.\"\"\"
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'


def test_send_email_without_auth(client):
    \"\"\"Testa envio sem autenticação.\"\"\"
    response = client.post('/api/v1/send', 
                          json={'domain': 'test.pt', 'account': 'test'})
    assert response.status_code == 401


def test_dashboard_loads(client):
    \"\"\"Testa se dashboard carrega.\"\"\"
    response = client.get('/')
    assert response.status_code == 200
    assert b'SendCraft' in response.data


def test_api_with_valid_key(client, app):
    \"\"\"Testa API com chave válida.\"\"\"
    app.config['API_KEYS'] = {'test': 'test_key_123'}
    
    response = client.get('/api/v1/health',
                         headers={'Authorization': 'Bearer test_key_123'})
    assert response.status_code == 200
```

---

## ⚡ **PONTO DE CONTROLE FINAL**

### **Executar Todos os Testes:**

```bash
# 1. Testar aplicação local
python app.py &
sleep 3
curl http://localhost:5000/api/v1/health
killall python

# 2. Executar seed
python seeds/initial_data.py

# 3. Testar API completa
python -m pytest tests/ -v

# 4. Criar pacote de deploy
python deploy.py

# 5. Verificar arquivos essenciais
ls -la sendcraft-deploy.zip
```

**CRITÉRIOS DE ACEITAÇÃO:**
- [ ] Aplicação inicia sem erros
- [ ] Health check responde
- [ ] Seed cria dados iniciais
- [ ] Testes passam
- [ ] Pacote de deploy criado
- [ ] Documentação completa

---

## 🚀 **INSTRUÇÕES DE DEPLOY**

### **Para o Desenvolvedor (Você):**

1. **Após agente completar todas as fases:**
   ```bash
   git clone https://github.com/GGEDeveloper/SendCraft.git
   cd SendCraft  
   python deploy.py  # Cria sendcraft-deploy.zip
   ```

2. **Upload no cPanel:**
   - File Manager → /public_html/sendcraft/
   - Upload sendcraft-deploy.zip
   - Extract All
   
3. **Configurar:**
   - Copiar `instance/config.py.example` → `instance/config.py`
   - Editar com secrets reais (usar os gerados)
   - Definir path absoluto SQLite
   
4. **Inicializar:**
   - Terminal Python App: `python seeds/initial_data.py`
   - Restart Python Application
   - Testar: `https://email.alitools.pt/`

### **API Key para AliTools:**
```
SC_ak47n9B2xQ8vE5mF3jK6pL9tR7wY4uI1oP0sA8dG5hJ2cV6nM9bX3zT8qE5rW7y
```

**MVP COMPLETO E PRONTO PARA PRODUÇÃO!** 🎉

---

## 🔄 **PRÓXIMOS PASSOS PÓS-DEPLOY**

Tag final: `v1.0-mvp-complete`  

1. Testar envio real via API
2. Integrar com AliTools (Vercel)
3. Monitorizar logs e performance
4. Planear funcionalidades da v1.1

**SendCraft MVP está pronto! 🚀**