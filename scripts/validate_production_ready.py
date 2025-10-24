#!/usr/bin/env python3
"""
Script de validação final para confirmar que SendCraft está production-ready.
"""

def validate_architecture():
    """Validar arquitetura limpa."""
    print("🔍 Validando arquitetura...")
    
    # Test 1: Flask-Mail removido
    try:
        from sendcraft.extensions import mail
        print("❌ CRITICAL: Flask-Mail ainda presente")
        return False
    except ImportError:
        print("✅ Flask-Mail removido")
    
    # Test 2: App carrega
    try:
        from sendcraft import create_app
        app = create_app('production')
        print("✅ App carrega em production mode")
    except Exception as e:
        print(f"❌ CRITICAL: App não carrega: {e}")
        return False
    
    # Test 3: Database connection
    try:
        with app.app_context():
            from sendcraft.models.account import EmailAccount
            count = EmailAccount.query.count()
            print(f"✅ Database: {count} contas encontradas")
    except Exception as e:
        print(f"❌ CRITICAL: Database error: {e}")
        return False
    
    return True

def validate_smtp_configs():
    """Validar configurações SMTP por conta."""
    print("\n📧 Validando configurações SMTP...")
    
    from sendcraft import create_app
    from sendcraft.models.account import EmailAccount
    
    app = create_app('development')
    with app.app_context():
        accounts = EmailAccount.query.all()
        
        issues = 0
        for account in accounts:
            config = account.get_smtp_config(app.config.get('SECRET_KEY', ''))
            server = config.get('server', '')
            
            # Verificar se usa servidor baseado no domínio
            expected = f'mail.{account.domain.name}'
            
            if server == expected:
                print(f"✅ {account.email_address}: {server}")
            elif 'antispamcloud' in server:
                print(f"❌ {account.email_address}: ainda usa default global ({server})")
                issues += 1
            else:
                print(f"⚠️ {account.email_address}: custom server ({server})")
        
        if issues > 0:
            print(f"❌ CRITICAL: {issues} contas com configuração incorreta")
            return False
        
        print(f"✅ Todas as {len(accounts)} contas com SMTP correto")
        return True

def validate_hardcoded_references():
    """Verificar que não há referências hardcoded."""
    print("\n🔍 Verificando hardcoded references...")
    
    import subprocess
    import os
    
    os.chdir('sendcraft')
    
    # Check for alitools hardcoded (ignore backup files and seed files)
    result = subprocess.run(['grep', '-r', 'mail.alitools.pt', '.', '--exclude-dir=__pycache__', '--exclude=*.backup*', '--exclude=seed_imap_account.py'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("❌ CRITICAL: Hardcoded mail.alitools.pt found:")
        print(result.stdout)
        return False
    
    # Check for antispamcloud hardcoded (ignore backup files)
    result = subprocess.run(['grep', '-r', 'smtp.antispamcloud', '.', '--exclude-dir=__pycache__', '--exclude=*.backup*'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("❌ CRITICAL: Hardcoded smtp.antispamcloud found:")
        print(result.stdout)
        return False
    
    print("✅ Sem referências hardcoded")
    return True

def main():
    """Executar todas as validações."""
    print("🎯 SENDCRAFT PRODUCTION READINESS VALIDATION")
    print("=" * 50)
    
    success = True
    
    success &= validate_architecture()
    success &= validate_smtp_configs() 
    success &= validate_hardcoded_references()
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 VALIDATION PASSED - SENDCRAFT PRODUCTION READY!")
        print("🚀 Deploy no Vercel pode prosseguir")
        return True
    else:
        print("❌ VALIDATION FAILED - Corrigir problemas antes do deploy")
        return False

if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
