# 🎯 **PROMPT DEFINITIVO PARA AGENT**

```markdown
SendCraft Phase 12 Production Deployment Complete Setup

## Context:
Implement complete Phase 12 production deployment files for SendCraft email.artnshine.pt while maintaining development compatibility. Current main branch lacks essential production files and has incomplete deployment configuration.

## Task: Phase 12 Complete Production Setup (20 minutes)

### Objective:
Create all production deployment files maintaining dual environment support:
- Development: python3 run_dev.py (local with VPN/network workarounds)  
- Production: https://email.artnshine.pt (server deployment without network issues)

### Phase 12 Requirements:

1. **Create docs/phase12/ structure with all documentation**
2. **Create 5 essential production files with exact content**
3. **Update existing files for production compatibility** 
4. **Maintain full development mode functionality**
5. **Enable cPanel auto-deployment**

### Exact Steps:

#### Step 1: Create Documentation Structure (3 min)
```bash
mkdir -p docs/phase12
echo "📁 Creating Phase 12 documentation structure..."
```

#### Step 2: Create All Production Files (10 min)
Create these files with exact content (refer to documentation):

1. **app.py** - Production entry point with WSGI application()
2. **passenger_wsgi.py** - cPanel Passenger WSGI entry point  
3. **instance/config.py** - Production secrets template
4. **Update .cpanel.yml** - Complete deployment with pip install
5. **Update requirements.txt** - Add Flask-Migrate, chardet, Werkzeug

#### Step 3: Documentation Files (5 min)
Create complete documentation in docs/phase12/:
1. **README.md** - Phase 12 overview and architecture
2. **FILES-TO-CREATE.md** - Exact file content and creation guide
3. **DEPLOY-INSTRUCTIONS.md** - Complete cPanel deployment steps

#### Step 4: Compatibility & Testing (2 min)
- Ensure run_dev.py maintains development functionality
- Add production environment detection  
- Test import compatibility

### Success Criteria:
✅ All 5 production files created with exact content
✅ Complete docs/phase12/ documentation structure  
✅ Dual environment compatibility maintained
✅ cPanel deployment ready (.cpanel.yml complete)
✅ All dependencies included (Flask-Migrate, chardet, Werkzeug)
✅ Development workflow preserved (run_dev.py works)

### Final Structure Expected:
```
SendCraft/
├── app.py                    # [NEW] Production entry
├── passenger_wsgi.py         # [NEW] WSGI entry
├── instance/config.py        # [NEW] Production secrets  
├── .cpanel.yml              # [UPDATED] Complete deployment
├── requirements.txt         # [UPDATED] All dependencies
├── run_dev.py              # [PRESERVED] Development
└── docs/phase12/
    ├── README.md           # Phase overview
    ├── FILES-TO-CREATE.md  # Exact file contents
    └── DEPLOY-INSTRUCTIONS.md # cPanel deployment steps
```

Execute Phase 12 complete setup creating production-ready SendCraft while maintaining development compatibility.
```

---

## 📁 **FICHEIROS PARA CRIAR EM docs/phase12/:**

Vou criar os 4 ficheiros de documentação que o agent precisará:

1. **docs/phase12/README.md** ✅ [244]
2. **docs/phase12/FILES-TO-CREATE.md** ✅ [245] 
3. **docs/phase12/DEPLOY-INSTRUCTIONS.md** ✅ [246]
4. **docs/phase12/CPANEL-SETUP.md** (brief guide)

---

## ✅ **RESULTADO ESPERADO:**

### **APÓS AGENT EXECUTAR:**
- **Todos ficheiros produção** criados com conteúdo exacto
- **Documentação completa** docs/phase12/  
- **Compatibilidade dual** development + production
- **Ready to commit** e fazer deploy cPanel

### **DEPLOY WORKFLOW:**
1. **Agent cria ficheiros** (20 min)
2. **Tu fazes commit** + push GitHub
3. **cPanel auto-deploy** via .cpanel.yml  
4. **https://email.artnshine.pt** live!

**O agent vai criar tudo perfeitamente seguindo as instruções exactas!** 🚀

**SendCraft ficará 100% production-ready mantendo development workflow!** ✅