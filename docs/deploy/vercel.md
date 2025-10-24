# 🚀 SendCraft Deploy no Vercel

## Environment Variables para Vercel (CORRETAS)

### Obrigatórias:
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-minimum-32-characters-long
ENCRYPTION_KEY=your-32-char-encryption-key-for-passwords
SQLALCHEMY_DATABASE_URI=mysql+pymysql://user:password@host:3306/database
```

### Opcionais (Performance):
```bash
CORS_ORIGINS=*
SQLALCHEMY_POOL_PRE_PING=true
SQLALCHEMY_POOL_RECYCLE=280
API_RATE_LIMIT=1000/hour
LOG_LEVEL=INFO
```

### ❌ NÃO ADICIONAR (não são mais usadas):
```bash
# ❌ DELETAR ESTAS SE EXISTIREM:
# MAIL_SERVER=...      ← Cada conta usa seu próprio servidor
# MAIL_PORT=...        ← Configurado individualmente
# MAIL_USERNAME=...    ← Por conta na database
# MAIL_PASSWORD=...    ← Por conta encriptada
# MAIL_USE_TLS=...     ← Por conta
# MAIL_USE_SSL=...     ← Por conta
# DEFAULT_SENDER=...   ← Por conta
```

**IMPORTANTE**: SendCraft agora usa configuração SMTP individual por conta armazenada na database. Cada email usa o servidor SMTP da sua própria conta (ex: geral@artnshine.pt usa mail.artnshine.pt automaticamente).

## Arquitetura Limpa

✅ **Zero Flask-Mail**: Arquitetura limpa sem conflitos  
✅ **Multi-Domain**: geral@artnshine.pt → mail.artnshine.pt automaticamente  
✅ **Individual SMTP**: Cada conta usa seu próprio servidor  
✅ **Vercel Ready**: Environment vars limpos (3 variáveis apenas)  
✅ **Intelligent UI**: Sugestões automáticas baseadas no domínio  
✅ **Fully Tested**: Validação completa com script automatizado  

## Deploy Steps

1. **Configurar Environment Variables** no Vercel Dashboard
2. **Deploy** via GitHub integration
3. **Testar** endpoints principais
4. **Configurar** contas de email via interface web

## Status: READY FOR VERCEL DEPLOY 🚀