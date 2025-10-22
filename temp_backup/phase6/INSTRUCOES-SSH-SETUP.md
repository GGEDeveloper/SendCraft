# 📋 INSTRUÇÕES SSH SETUP - Configuração Dominios.pt

## 🎯 **SETUP SSH PARA CONEXÃO REMOTA SENDCRAFT**

### **PASSO 1: Configurar SSH Key (Uma vez apenas)**

#### **1.1. Gerar Chave SSH (se não tens):**
```bash
# Gerar nova chave SSH dedicada para dominios.pt
ssh-keygen -t rsa -b 4096 -C "sendcraft@dominios.pt" -f ~/.ssh/dominios_pt

# Resultado: 
# ~/.ssh/dominios_pt (chave privada)
# ~/.ssh/dominios_pt.pub (chave pública)
```

#### **1.2. Adicionar Chave Pública ao Servidor:**
```bash
# Copiar chave pública para dominios.pt
ssh-copy-id -i ~/.ssh/dominios_pt.pub artnshin@ssh.dominios.pt

# OU manualmente:
cat ~/.ssh/dominios_pt.pub | ssh artnshin@ssh.dominios.pt "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

#### **1.3. Configurar SSH Config (Simplificar conexões):**
```bash
# Editar ~/.ssh/config
nano ~/.ssh/config

# Adicionar:
Host dominios-pt
    HostName ssh.dominios.pt
    User artnshin
    Port 22
    IdentityFile ~/.ssh/dominios_pt
    StrictHostKeyChecking no
    ServerAliveInterval 60
    ServerAliveCountMax 3
    
Host dominios-mysql
    HostName ssh.dominios.pt  
    User artnshin
    Port 22
    IdentityFile ~/.ssh/dominios_pt
    LocalForward 3307 localhost:3306
    StrictHostKeyChecking no
    ServerAliveInterval 60
```

#### **1.4. Testar Conexão SSH:**
```bash
# Teste simples
ssh dominios-pt "echo 'SSH OK'"

# Teste MySQL tunnel manual
ssh -L 3307:localhost:3306 dominios-pt -N &

# Testar conexão MySQL local
mysql -h localhost -P 3307 -u artnshin_sendcraft -p artnshin_sendcraft

# Parar tunnel
pkill -f "ssh.*-L 3307"
```

---

## **PASSO 2: Setup Ambiente Development**

### **2.1. Criar Estrutura de Configs:**
```bash
# No diretório SendCraft
cd SendCraft

# Criar ficheiros environment
touch .env.local .env.development .env.production

# Copiar configs (ver CONFIG-MODULAR-SSH-TUNNEL.md)
```

### **2.2. Instalar Dependências SSH:**
```bash
# Ativar virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependências SSH tunnel
pip install paramiko==3.3.1 sshtunnel==0.4.0

# Atualizar requirements
pip freeze > requirements.txt
```

### **2.3. Verificar Permissões SSH:**
```bash
# Permissões corretas para chaves SSH
chmod 700 ~/.ssh
chmod 600 ~/.ssh/dominios_pt
chmod 644 ~/.ssh/dominios_pt.pub
chmod 600 ~/.ssh/config
```

---

## **PASSO 3: Configurar SendCraft Modular**

### **3.1. Implementar Código Modular:**
```bash
# Backup config atual
cp config.py config.py.backup

# Implementar novos ficheiros (via Agent AI):
# - config.py (modular)
# - sendcraft/utils/ssh_tunnel.py
# - sendcraft/__init__.py (modificado)
# - .env.local, .env.development 
```

### **3.2. Testar Configurações:**
```bash
# Teste 1: Modo Local (SQLite)
export FLASK_ENV=local
python -c "from sendcraft import create_app; app = create_app(); print('Local OK')"

# Teste 2: Modo Development (SSH Tunnel)
export FLASK_ENV=development  
python -c "from sendcraft import create_app; app = create_app(); print('Development OK')"

# Teste 3: Modo Production (Direto)
export FLASK_ENV=production
python -c "from sendcraft import create_app; app = create_app(); print('Production OK')"
```

---

## **PASSO 4: Scripts de Execução**

### **4.1. Script Desenvolvimento Local com SSH (`run_dev.py`):**
```python
#!/usr/bin/env python3
"""
SendCraft Development com SSH Tunnel automático
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Executar SendCraft development com SSH tunnel"""
    
    print("🚀 SendCraft Development Mode (SSH Tunnel → dominios.pt)")
    print("=" * 60)
    
    # Set environment
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Verificar SSH key
    ssh_key = Path('~/.ssh/dominios_pt').expanduser()
    if not ssh_key.exists():
        print("❌ SSH key não encontrada: ~/.ssh/dominios_pt")
        print("💡 Execute: ssh-keygen -t rsa -b 4096 -f ~/.ssh/dominios_pt")
        sys.exit(1)
    
    # Testar conexão SSH
    print("🔧 Testando conexão SSH...")
    result = subprocess.run(
        ['ssh', '-i', str(ssh_key), '-o', 'ConnectTimeout=5', 
         'artnshin@ssh.dominios.pt', 'echo SSH_OK'],
        capture_output=True, text=True, timeout=10
    )
    
    if result.returncode != 0:
        print("❌ Falha conexão SSH:")
        print(f"   {result.stderr}")
        sys.exit(1)
    
    print("✅ Conexão SSH OK")
    
    # Import and create app (com SSH tunnel automático)
    try:
        from sendcraft import create_app
        app = create_app('development')
    except Exception as e:
        print(f"❌ Erro ao criar aplicação: {e}")
        sys.exit(1)
    
    print("✅ SendCraft Development Ready!")
    print("🌐 Web Interface: http://localhost:5000")
    print("📡 API Docs: http://localhost:5000/api/v1/")
    print("🗄️ Database: MySQL via SSH tunnel (dominios.pt)")
    print("🛑 Ctrl+C para parar (cleanup automático)")
    print("=" * 60)
    
    # Run server
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n👋 SendCraft parado. SSH tunnel limpo.")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
if __name__ == '__main__':
    main()
```

### **4.2. Script Local SQLite (`run_local.py`):**
```python
#!/usr/bin/env python3
"""
SendCraft Local com SQLite + dados seed
"""
import os
import sys

def main():
    """Executar SendCraft local SQLite"""
    
    print("🏠 SendCraft Local Mode (SQLite + Seed Data)")
    print("=" * 50)
    
    # Set environment  
    os.environ['FLASK_ENV'] = 'local'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Create app
    from sendcraft import create_app
    app = create_app('local')
    
    # Check/seed database
    with app.app_context():
        from sendcraft.cli.seed_data import seed_local_data
        
        try:
            from sendcraft.models import Domain
            if Domain.query.count() == 0:
                print("📊 Seeding local database...")
                seed_local_data.callback()
        except Exception:
            print("🔧 Creating and seeding database...")
            from sendcraft.extensions import db
            db.create_all()
            seed_local_data.callback()
    
    print("✅ SendCraft Local Ready!")
    print("🌐 Interface: http://localhost:5000")
    print("🗄️ Database: SQLite local")
    print("🎭 Data: Seed realista (domínios, contas, templates)")
    print("=" * 50)
    
    # Run server
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
```

---

## **PASSO 5: Comandos de Execução Final**

### **5.1. Desenvolvimento Local (SQLite):**
```bash
# Execução simples SQLite + seed data
python run_local.py

# URLs:
# http://localhost:5000 - Interface web
# http://localhost:5000/api/v1/health - API test
```

### **5.2. Desenvolvimento Remoto (SSH Tunnel):**
```bash
# Execução com SSH tunnel automático → dominios.pt
python run_dev.py

# URLs:
# http://localhost:5000 - Interface web (dados MySQL dominios.pt)
# http://localhost:5000/api/v1/health - API test
```

### **5.3. Produção (Direto no Servidor):**
```bash
# No servidor dominios.pt
export FLASK_ENV=production
python -c "from sendcraft import create_app; app = create_app(); app.run(host='0.0.0.0', port=9000)"

# URL produção:
# http://email.artnshine.pt:9000
```

---

## **PASSO 6: Troubleshooting**

### **6.1. Problemas SSH:**
```bash
# Testar SSH manual
ssh -v artnshin@ssh.dominios.pt

# Verificar chaves
ls -la ~/.ssh/dominios_pt*

# Recriar tunnel manual
ssh -L 3307:localhost:3306 artnshin@ssh.dominios.pt -N -v
```

### **6.2. Problemas MySQL:**
```bash
# Testar MySQL via tunnel
mysql -h localhost -P 3307 -u artnshin_sendcraft -p

# Ver processos SSH
ps aux | grep ssh

# Matar tunnels
pkill -f "ssh.*-L 3307"
```

### **6.3. Problemas Python:**
```bash
# Testar imports
python -c "from sendcraft.utils.ssh_tunnel import SSHTunnelManager; print('OK')"

# Ver logs detalhados
export LOG_LEVEL=DEBUG
python run_dev.py
```

---

## ✅ **RESULTADO FINAL**

Após este setup:

**Tens 3 modos de execução:**
- 🏠 **Local**: `python run_local.py` (SQLite + seed)
- 🔧 **Development**: `python run_dev.py` (SSH tunnel → dominios.pt MySQL)  
- 🚀 **Production**: Direto no servidor (MySQL local)

**Vantagens:**
- ✅ Desenvolvimento offline (SQLite)
- ✅ Testing com dados reais (SSH tunnel)
- ✅ Deploy simples (produção)
- ✅ SSH automático (sem configuração manual)
- ✅ Cleanup automático (sem processos órfãos)
- ✅ Configs modulares (.env específicos)

**Comandos simples para utilizar:**
```bash
python run_local.py    # SQLite local
python run_dev.py      # MySQL dominios.pt via SSH
```