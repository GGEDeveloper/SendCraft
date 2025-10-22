# 📋 **PHASE 12 - README.md**

## 🚀 **SendCraft Production Deployment**

### **Objetivo:**
Preparar SendCraft para deploy produção em `email.artnshine.pt` mantendo compatibilidade com desenvolvimento local.

---

## 📊 **Estado Atual vs Target:**

### **✅ FUNCIONAL (Development):**
- `python3 run_dev.py` - Desenvolvimento com MySQL remoto
- Configuração cPanel VBS IMAP integrada  
- Interface three-pane email funcional
- geral@alitools.pt account configurada

### **❌ EM FALTA (Production):**
- `app.py` - Entry point produção cPanel
- `passenger_wsgi.py` - WSGI entry point
- `instance/config.py` - Configurações sensíveis  
- `.cpanel.yml` - Deploy automático completo
- Dependencies - Flask-Migrate, chardet, Werkzeug

---

## 🎯 **Arquitectura Dual Environment:**

### **DEVELOPMENT MODE:**
```bash
# Local development (VPN/network issues)
python3 run_dev.py
# → http://localhost:5000
# → Remote MySQL artnshine.pt (quando sem VPN)
# → IMAP test via scripts (quando com VPN)
```

### **PRODUCTION MODE:**  
```bash
# Server production (sem network issues)
# → https://email.artnshine.pt
# → Local MySQL localhost  
# → IMAP real geral@alitools.pt sync
# → Auto-deploy via GitHub
```

---

## 📁 **Estrutura Ficheiros Phase 12:**

```
SendCraft/
├── app.py                    # [NEW] Production entry point
├── passenger_wsgi.py         # [NEW] cPanel WSGI entry  
├── instance/
│   └── config.py            # [NEW] Production secrets
├── .cpanel.yml              # [UPDATE] Complete deploy
├── requirements.txt         # [UPDATE] Add dependencies
├── run_dev.py              # [KEEP] Development server
└── docs/phase12/
    ├── README.md           # Este ficheiro
    ├── DEPLOY-INSTRUCTIONS.md
    ├── FILES-TO-CREATE.md
    └── CPANEL-SETUP.md
```

---

## 🔄 **Workflow Completo:**

### **1. Development (Local):**
```bash
git clone https://github.com/GGEDeveloper/SendCraft.git  
cd SendCraft
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 run_dev.py  # Development server
```

### **2. Production (Deploy):**
```bash
# Phase 12 setup
git add . && git commit -m "feat: Phase 12 production deployment files"
git push origin main

# cPanel auto-deploy via .cpanel.yml
# → https://email.artnshine.pt live
```

---

## ✅ **Success Criteria Phase 12:**

### **✅ DUAL COMPATIBILITY:**
- Development: `run_dev.py` funciona como antes
- Production: `app.py` + `passenger_wsgi.py` funcionam  

### **✅ PRODUCTION READY:**
- Auto-deploy GitHub → cPanel  
- MySQL localhost produção
- IMAP real sem VPN issues
- Web interface https://email.artnshine.pt

### **✅ DEPENDENCIES COMPLETE:**
- Flask-Migrate para migrations
- chardet para email parsing  
- Werkzeug para Flask stability

---

## 🎯 **Next Steps:**

1. **Execute**: `docs/phase12/FILES-TO-CREATE.md`  
2. **Deploy**: `docs/phase12/DEPLOY-INSTRUCTIONS.md`
3. **Configure**: `docs/phase12/CPANEL-SETUP.md`

**SendCraft ficará 100% production-ready mantendo development workflow!** 🚀