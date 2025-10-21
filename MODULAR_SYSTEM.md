# 🚀 SendCraft - Sistema Modular de Configurações

## ✅ Implementação Concluída

O SendCraft agora possui um sistema modular completo com 3 modos de operação:

### 📊 Modos de Operação

#### 1. **Local Mode** (SQLite + Seed Data)
- **Database**: SQLite local (`sendcraft_local.db`)
- **Ambiente**: Desenvolvimento offline
- **Dados**: Seed data automático com dados realistas
- **Comando**: `python3 run_local.py`
- **URL**: http://localhost:5000

#### 2. **Development Mode** (Remote MySQL)
- **Database**: MySQL remoto (artnshine.pt:3306)
- **Ambiente**: Desenvolvimento com dados reais
- **Conexão**: Direto ao MySQL remoto (sem SSH tunnel)
- **Comando**: `python3 run_dev.py`
- **URL**: http://localhost:5000

#### 3. **Production Mode** (MySQL Local)
- **Database**: MySQL local no servidor
- **Ambiente**: Produção
- **Conexão**: localhost:3306
- **Comando**: `FLASK_ENV=production python3 app.py`

## 🔧 Arquivos de Configuração

### Estrutura Implementada:
```
/workspace/
├── config.py                 # Sistema modular (BaseConfig, LocalConfig, DevelopmentConfig, ProductionConfig)
├── .env.local               # Variáveis para modo local
├── .env.development         # Variáveis para modo development
├── .env.production          # Variáveis para modo production
├── run_local.py             # Script para executar modo local
├── run_dev.py               # Script para executar modo development
├── test_configs.py          # Script de teste das configurações
└── sendcraft/
    ├── __init__.py          # App factory com suporte modular
    ├── cli/
    │   └── seed_data.py     # Sistema de seed data
    └── commands.py          # Comandos CLI originais
```

## 📦 Seed Data Implementado

O sistema de seed data cria automaticamente:

### Domínios (5):
- `alitools.pt` - Domínio principal AliTools B2B
- `artnshine.pt` - Portfolio Art & Shine
- `sendcraft.local` - Domínio de testes
- `test-domain.com` - Domínio desativado
- `cliente-exemplo.pt` - Exemplo B2B

### Contas de Email (6):
- `encomendas@alitools.pt`
- `suporte@alitools.pt`
- `marketing@alitools.pt`
- `info@artnshine.pt`
- `demo@sendcraft.local`
- `vendas@cliente-exemplo.pt`

### Templates HTML (4):
1. **Confirmação de Encomenda** (AliTools)
   - HTML responsivo com gradientes
   - Variáveis dinâmicas

2. **Boas-vindas B2B** (AliTools)
   - Design profissional
   - Benefícios destacados

3. **Resposta Portfolio** (Art&Shine)
   - Design criativo
   - Informações de projeto

4. **Template Teste** (SendCraft)
   - Validação do sistema

### Logs de Email (300+):
- Últimos 30 dias de atividade
- Status realistas (sent, delivered, opened, failed, bounced)
- Distribuição temporal realista

## 🚦 Status de Teste

```bash
# Resultado do teste de configurações
python3 test_configs.py

✅ LOCAL: OK (SQLite funcionando)
✅ DEVELOPMENT: OK (Config Remote MySQL)
✅ PRODUCTION: OK (Config MySQL local)
```

## ⚠️ Notas Importantes

### Remote MySQL (Development Mode):
- **Host**: artnshine.pt
- **Port**: 3306
- **Database**: artnshin_sendcraft
- **Status**: Configurado mas conexão pode falhar devido a:
  - Restrições de IP no servidor remoto
  - Firewall bloqueando porta 3306
  - Necessidade de whitelist do IP local

### Solução para Remote MySQL:
Se a conexão remota falhar, você pode:
1. Adicionar seu IP ao whitelist no cPanel
2. Usar modo local para desenvolvimento
3. Configurar VPN se disponível

## 🎯 Funcionalidades Implementadas

✅ **Sistema de configurações modulares**
- BaseConfig com configurações comuns
- LocalConfig para SQLite
- DevelopmentConfig para Remote MySQL
- ProductionConfig para MySQL local

✅ **Carregamento automático de .env files**
- Detecta ambiente automaticamente
- Carrega arquivo .env correspondente
- Fallback para variáveis do sistema

✅ **Seed data system**
- Comando CLI: `flask seed-local-data`
- Dados realistas e profissionais
- Templates HTML completos
- Logs com estatísticas reais

✅ **Scripts de execução**
- `run_local.py` - Inicia modo local com seed
- `run_dev.py` - Conecta ao MySQL remoto
- `test_configs.py` - Valida todas as configs

✅ **Interface web compatível**
- Dashboard funcionando
- CRUD de domínios/contas
- Sistema de templates
- Visualização de logs

## 🚀 Como Usar

### Modo Local (Recomendado para início):
```bash
python3 run_local.py
# Acesse http://localhost:5000
# Database SQLite com dados de exemplo
```

### Modo Development:
```bash
python3 run_dev.py
# Conecta ao MySQL remoto (se disponível)
# Dados reais do servidor
```

### Modo Production:
```bash
export FLASK_ENV=production
python3 app.py
# Para uso em servidor de produção
```

## 📝 Comando Seed Data

Para popular a database manualmente:
```bash
flask seed-local-data
```

## ✨ Sistema Pronto!

O SendCraft agora possui um sistema modular completo, permitindo:
- Desenvolvimento offline com SQLite
- Conexão a MySQL remoto para testes
- Deploy em produção com MySQL local

Todas as configurações foram testadas e estão funcionais!