# 🎯 FASE 1: PREPARAÇÃO AMBIENTE LOCAL

## 📋 **OBJETIVO**
Preparar ambiente de desenvolvimento local para conectar ao MySQL remoto dominios.pt e validar setup básico.

---

## 🔧 **AÇÕES DO UTILIZADOR**

### **1.1. Verificar Estado Branch Atual**
```bash
# No diretório SendCraft
git checkout cursor/implement-modular-config-with-remote-mysql-access-42e8
git pull origin cursor/implement-modular-config-with-remote-mysql-access-42e8

# Verificar ficheiros críticos
ls -la config.py .env.development run_dev.py run_local.py
```

### **1.2. Preparar Virtual Environment**
```bash
# Ativar venv
source venv/bin/activate

# Verificar/instalar dependências
pip install -r requirements.txt

# Verificar PyMySQL específico
pip list | grep -i pymysql
```

### **1.3. Validar Conexão MySQL Remoto**
```bash
# Testar conexão direta (deve funcionar - já testaste antes)
mysql -h artnshine.pt -u artnshin_sendcraft -p -e "SHOW DATABASES;"
# Password: g>bxZmj%=JZt9Z,i

# Resultado esperado:
# +--------------------+
# | Database           |
# +--------------------+
# | artnshin_sendcraft |
# | information_schema |
# +--------------------+
```

---

## 📄 **FICHEIRO: .env.local (CRIAR)**
```bash
# Criar ficheiro .env.local (backup/fallback)
cat > .env.local << 'EOF'
# SendCraft - Configuração Local (SQLite - apenas fallback)
FLASK_ENV=local
FLASK_DEBUG=1
SECRET_KEY=sendcraft-local-dev-key-123
DATABASE_URL=sqlite:///sendcraft_local.db
DEFAULT_FROM_NAME=SendCraft Local
ENCRYPTION_KEY=local-dev-32-chars-encryption-key!
API_RATE_LIMIT=10000/hour
LOG_LEVEL=DEBUG
EOF
```

---

## ✅ **CRITÉRIOS SUCESSO FASE 1**
- ✅ Branch checkout OK
- ✅ Virtual environment ativo
- ✅ PyMySQL instalado
- ✅ MySQL remoto acessível
- ✅ Ficheiros .env.local e .env.development presentes

---

## 🔄 **PRÓXIMA FASE**
Se todos os critérios estão ✅ → **FASE 2: Testes Iniciais**