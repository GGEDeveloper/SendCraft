# 🎯 FASE 2: TESTES INICIAIS SISTEMA

## 📋 **OBJETIVO**
Executar primeira inicialização do SendCraft em modo development (local → MySQL remoto) e identificar problemas antes de avançar.

---

## 🔧 **AÇÕES DO UTILIZADOR**

### **2.1. Teste Conexão Python → MySQL**
```bash
# Testar importação e conexão no Python
python3 -c "
import pymysql
try:
    conn = pymysql.connect(
        host='artnshine.pt',
        user='artnshin_sendcraft', 
        password='g>bxZmj%=JZt9Z,i',
        database='artnshin_sendcraft',
        connect_timeout=10
    )
    print('✅ Python PyMySQL connection OK')
    conn.close()
except Exception as e:
    print(f'❌ Python connection failed: {e}')
"
```

### **2.2. Primeira Execução Development Mode**
```bash
# Executar script development
python run_dev.py

# Observar output:
# - ✅ "Remote MySQL connection OK"
# - ✅ "SendCraft Development Ready!"
# - ✅ Server running on http://localhost:5000
```

### **2.3. Teste Interface Web Básico**
```bash
# Em outro terminal, testar endpoints básicos
curl http://localhost:5000/
curl http://localhost:5000/api/v1/health

# OU abrir browser: http://localhost:5000
```

---

## 🐛 **PROBLEMAS ESPERADOS E SOLUÇÕES**

### **Problema: ImportError models**
```bash
# Se erro: "cannot import name 'Domain' from sendcraft.models"
# Verificar se existem ficheiros models
ls -la sendcraft/models/
```

### **Problema: Database tables missing**
```bash
# Se erro: "Table 'domains' doesn't exist"
# Executar migrations/criação tabelas (será tratado na FASE 3)
```

### **Problema: Connection timeout**
```bash
# Se timeout MySQL, verificar firewall/connectivity
# Tentar aumentar timeout em .env.development
```

---

## 📊 **LOG DO QUE OBSERVAR**

### **Startup Logs Esperados:**
```
🔧 SendCraft Development Mode (Remote MySQL → dominios.pt)
============================================================
📡 Testando conexão com MySQL remoto...
✅ Remote MySQL connection OK
✅ Loaded environment from .env.development  
🌐 Conectando ao MySQL remoto (dominios.pt)
✅ SendCraft Development Ready!
🌐 Web Interface: http://localhost:5000
🗄️ Database: Remote MySQL (dominios.pt)
============================================================
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://localhost:5000
```

---

## 📋 **CHECKLIST VALIDAÇÃO**

### **Backend (Terminal):**
- [ ] Script run_dev.py executa sem erro
- [ ] "Remote MySQL connection OK" aparece
- [ ] Flask server arranca na porta 5000
- [ ] Sem erros de import/database

### **Frontend (Browser):**
- [ ] http://localhost:5000 abre (mesmo que com erro 500)
- [ ] Não há erro de conexão recusada
- [ ] Loading page ou conteúdo aparece

---

## ✅ **CRITÉRIOS SUCESSO FASE 2**
- ✅ run_dev.py executa sem crash
- ✅ MySQL connection OK
- ✅ Flask server ativo
- ✅ Port 5000 acessível no browser

## ❌ **SE FALHA FASE 2**
- Documentar erros específicos
- Proceder para **FASE 2B: Correções Agente AI**

---

## 🔄 **PRÓXIMA FASE**
Se sucesso ✅ → **FASE 3: Estrutura Base Dados**
Se falha ❌ → **FASE 2B: Correções Agente AI**