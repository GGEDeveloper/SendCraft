# 🎯 FASE 2B: CORREÇÕES AGENTE AI

## 📋 **OBJETIVO**
Corrigir problemas identificados na FASE 2 usando Claude Opus ou Cursor Agent para resolver imports, models, e estrutura base.

---

## 🤖 **PROMPT PARA CLAUDE OPUS - CORREÇÕES CRÍTICAS**

```
# SendCraft - Correções Críticas Import/Models/Database

## Contexto:
- Repo: https://github.com/GGEDeveloper/SendCraft  
- Branch: cursor/implement-modular-config-with-remote-mysql-access-42e8
- Problema: run_dev.py falha com erros de import ou models missing
- MySQL remoto: CONFIRMADO funcionando (artnshine.pt)

## Problemas Identificados:
[COLAR AQUI OS ERROS ESPECÍFICOS DA FASE 2]

## Tarefas Urgentes:

### 1. VERIFICAR/CRIAR estrutura sendcraft/models/
- sendcraft/models/__init__.py (imports corretos)
- sendcraft/models/domain.py (modelo Domain)
- sendcraft/models/email_account.py (modelo EmailAccount) 
- sendcraft/models/email_template.py (modelo EmailTemplate)
- sendcraft/models/email_log.py (modelo EmailLog)

### 2. VERIFICAR sendcraft/extensions.py
- SQLAlchemy db instance
- Mail extension
- CORS extension
- Todas exportadas corretamente

### 3. VERIFICAR sendcraft/routes/web.py
- Blueprints web_bp definido
- Routes básicas: /, /domains, /accounts, /templates, /logs
- Imports models funcionais

### 4. VERIFICAR sendcraft/api/v1/__init__.py  
- Blueprint api_v1_bp definido
- Route /health endpoint básico

### 5. CRIAR/VERIFICAR comandos CLI
- sendcraft/commands.py ou sendcraft/cli/
- Comando flask init-db para criar tabelas
- Import correto em sendcraft/__init__.py

## Especificações Técnicas:
- Database: Remote MySQL (artnshine.pt:3306/artnshin_sendcraft)
- SQLAlchemy: mysql+pymysql:// connection string
- Models: Domain, EmailAccount, EmailTemplate, EmailLog básicos
- Flask-SQLAlchemy db.Model inheritance

## Critério Sucesso:
✅ python run_dev.py arranca sem ImportError
✅ http://localhost:5000/ carrega (mesmo que erro 500 por falta tabelas)  
✅ flask --app sendcraft init-db funciona (se comando existe)
✅ Sem crashes de import ou missing modules

## Prioridade:
ALTA - Sistema deve arrancar para poder testar interface e criar tabelas.
```

---

## 🛠️ **AÇÕES UTILIZADOR APÓS CLAUDE**

### **Testar Correções:**
```bash
# Re-testar após Claude implementar correções
python run_dev.py

# Se arrancar OK, avançar para FASE 3
# Se ainda falhar, repetir com mais detalhes erro
```

### **Verificar Estrutura Criada:**
```bash
# Verificar ficheiros críticos foram criados
ls -la sendcraft/models/
ls -la sendcraft/routes/
ls -la sendcraft/api/v1/
ls -la sendcraft/extensions.py
```

---

## 🔄 **FLUXO DECISÃO**

### **Se Claude resolve os problemas:**
→ **FASE 3: Estrutura Base Dados**

### **Se problemas persistem:**
→ Repetir com **prompt mais específico** com erros exatos

### **Se imports OK mas sem tabelas MySQL:**
→ **FASE 3: Estrutura Base Dados** (normal)

---

## ⚠️ **NOTAS IMPORTANTES**

1. **Não alterar config.py** - está correto
2. **Não alterar .env.development** - está correto  
3. **Foco apenas em**: imports, models, routes básicas
4. **Objetivo**: Arrancar sistema para depois criar tabelas

---

## 🎯 **RESULTADO ESPERADO**

Após esta fase:
- ✅ `python run_dev.py` executa 
- ✅ Server Flask ativo em localhost:5000
- ✅ Pronto para criar estrutura base dados (FASE 3)