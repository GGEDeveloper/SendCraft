# 🎯 FASE 3: ESTRUTURA BASE DADOS

## 📋 **OBJETIVO**
Criar estrutura de tabelas MySQL no servidor remoto (artnshine.pt) e povoar com dados básicos para testing da interface.

---

## 🔧 **AÇÕES DO UTILIZADOR**

### **3.1. Verificar Tabelas Existentes**
```bash
# Conectar e verificar estado atual da BD
mysql -h artnshine.pt -u artnshin_sendcraft -p artnshin_sendcraft -e "SHOW TABLES;"
# Password: g>bxZmj%=JZt9Z,i

# Resultado esperado (pode estar vazio):
# Empty set (0.00 sec)
# OU tabelas já existentes
```

### **3.2. Criar Tabelas via Flask CLI**
```bash
# Se comando CLI existe (implementado na FASE 2B)
flask --app sendcraft init-db

# OU forçar criação via Python
python3 -c "
from sendcraft import create_app
from sendcraft.extensions import db
app = create_app('development')
with app.app_context():
    db.create_all()
    print('✅ Tabelas criadas')
"
```

### **3.3. Verificar Estrutura Criada**
```bash
# Verificar tabelas foram criadas
mysql -h artnshine.pt -u artnshin_sendcraft -p artnshin_sendcraft -e "SHOW TABLES;"

# Verificar estrutura tabla domains (exemplo)
mysql -h artnshine.pt -u artnshin_sendcraft -p artnshin_sendcraft -e "DESCRIBE domains;"
```

---

## 🤖 **PROMPT PARA AGENTE AI - SEED DATA**

Se tabelas estão criadas mas vazias, usar este prompt:

```
# SendCraft - Criar Dados Seed para Testing Interface

## Contexto:
- Repo: https://github.com/GGEDeveloper/SendCraft
- Branch: cursor/implement-modular-config-with-remote-mysql-access-42e8  
- Database: Remote MySQL com tabelas criadas mas vazias
- Objetivo: Povoar BD com dados mínimos para testar interface web

## Tarefas:

### 1. CRIAR comando CLI seed-data
- sendcraft/cli/seed_data.py (se não existe)
- Comando: flask seed-data
- Registar em sendcraft/__init__.py

### 2. DADOS MÍNIMOS para insert:

#### Tabela domains:
- alitools.pt (ativo)
- artnshine.pt (ativo)  
- email.artnshine.pt (ativo)

#### Tabela email_accounts:
- encomendas@alitools.pt (SMTP Gmail)
- info@artnshine.pt (SMTP local)
- demo@email.artnshine.pt (SMTP teste)

#### Tabela email_templates:
- "Confirmação Encomenda AliTools" 
- "Contacto Portfolio Art&Shine"
- "Template Demo Sistema"

#### Tabela email_logs:
- 10-20 registos exemplo (estados: sent, delivered, failed)
- Datas últimos 7 dias

### 3. IMPLEMENTAR insert seguro
- Verificar se dados já existem (evitar duplicates)
- Usar SQLAlchemy ORM (não SQL raw)
- Commit transactions
- Log do que foi inserido

## Especificações:
- Models: Domain, EmailAccount, EmailTemplate, EmailLog
- Remote MySQL: artnshine.pt:3306/artnshin_sendcraft
- Dados realistas mas simples para testing
- Comando: flask --app sendcraft seed-data

## Resultado Esperado:
✅ flask --app sendcraft seed-data executa
✅ Dados inseridos na BD remota
✅ Interface web mostra dados (próxima fase)
```

---

## 🔍 **VALIDAÇÃO MANUAL DADOS**

### **Após Seed Data:**
```bash
# Verificar dados inseridos
mysql -h artnshine.pt -u artnshin_sendcraft -p artnshin_sendcraft -e "
SELECT COUNT(*) as total FROM domains;
SELECT COUNT(*) as total FROM email_accounts; 
SELECT COUNT(*) as total FROM email_templates;
SELECT COUNT(*) as total FROM email_logs;
"

# Resultado esperado:
# domains: 3+ registos
# email_accounts: 3+ registos  
# email_templates: 3+ registos
# email_logs: 10+ registos
```

---

## ✅ **CRITÉRIOS SUCESSO FASE 3**
- ✅ Tabelas MySQL criadas no servidor remoto
- ✅ Dados seed inseridos com sucesso
- ✅ Comando flask seed-data funcional
- ✅ BD remota povoada com dados testing

## ❌ **PROBLEMAS COMUNS**

### **Erro: Table already exists**
```bash
# Se tabelas já existem, apenas seed data
flask --app sendcraft seed-data
```

### **Erro: Connection timeout**
```bash
# Aumentar timeout em .env.development:
echo "MYSQL_CONNECT_TIMEOUT=30" >> .env.development
```

### **Erro: Permission denied**
```bash
# Verificar Remote MySQL access no cPanel dominios.pt
# Host % deve estar autorizado
```

---

## 🔄 **PRÓXIMA FASE**
Se sucesso ✅ → **FASE 4: Testes Interface Web**