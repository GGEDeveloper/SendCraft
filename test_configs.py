#!/usr/bin/env python3
"""Teste das configurações modulares SendCraft"""
import os
import sys

def test_config(mode):
    """Testa uma configuração específica"""
    print(f"\n{'='*60}")
    print(f"🧪 Testando modo: {mode.upper()}")
    print('='*60)
    
    os.environ['FLASK_ENV'] = mode
    
    try:
        from sendcraft import create_app
        app = create_app(mode)
        
        print(f"✅ Configuração '{mode}' carregada com sucesso!")
        print(f"\n📋 Detalhes da configuração:")
        print(f"   • Environment: {app.config.get('FLASK_ENV', 'N/A')}")
        print(f"   • Debug: {app.config.get('DEBUG', False)}")
        print(f"   • Testing: {app.config.get('TESTING', False)}")
        
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'sqlite' in db_uri:
            print(f"   • Database: SQLite (local)")
        elif 'mysql' in db_uri:
            if 'localhost' in db_uri:
                print(f"   • Database: MySQL (localhost)")
            else:
                print(f"   • Database: MySQL (remote)")
                # Extrair host do URI
                import re
                match = re.search(r'@([^:/]+)', db_uri)
                if match:
                    print(f"   • Host: {match.group(1)}")
        
        print(f"   • Log Level: {app.config.get('LOG_LEVEL', 'INFO')}")
        print(f"   • API Rate Limit: {app.config.get('API_RATE_LIMIT', 'N/A')}")
        
        # Testar contexto e modelos
        with app.app_context():
            from sendcraft.models import Domain
            from sendcraft.extensions import db
            
            if 'sqlite' in db_uri:
                # Para SQLite, verificar se as tabelas existem
                try:
                    count = Domain.query.count()
                    print(f"\n   📊 Database status:")
                    print(f"      • Domínios: {count}")
                except Exception:
                    print(f"\n   📊 Database status:")
                    print(f"      • Database vazia (tabelas serão criadas)")
            else:
                print(f"\n   📊 Database status:")
                print(f"      • MySQL configurado (conexão não testada)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar configuração '{mode}': {e}")
        return False

def main():
    print("🚀 SendCraft - Teste de Configurações Modulares")
    print("="*60)
    
    modes = ['local', 'development', 'production']
    results = {}
    
    for mode in modes:
        results[mode] = test_config(mode)
    
    print(f"\n{'='*60}")
    print("📊 RESUMO DOS TESTES")
    print('='*60)
    
    for mode, success in results.items():
        status = "✅ OK" if success else "❌ FALHOU"
        print(f"   • {mode.upper()}: {status}")
    
    print('='*60)
    
    if all(results.values()):
        print("🎉 Todos os modos de configuração estão funcionando!")
    else:
        print("⚠️ Alguns modos apresentaram problemas.")
        print("💡 Nota: Remote MySQL pode falhar por restrições de rede.")

if __name__ == '__main__':
    main()