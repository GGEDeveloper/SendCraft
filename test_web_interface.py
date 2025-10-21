#!/usr/bin/env python3
"""Teste completo da interface web SendCraft"""
import os
import sys

def test_web_interface():
    """Testa todas as rotas da interface web"""
    print("🚀 SendCraft - Teste da Interface Web")
    print("="*60)
    
    os.environ['FLASK_ENV'] = 'local'
    
    from sendcraft import create_app
    app = create_app('local')
    
    routes_to_test = [
        ('/', 'Dashboard'),
        ('/domains', 'Domains List'),
        ('/accounts', 'Accounts List'),
        ('/templates', 'Templates List'),
        ('/logs', 'Logs List'),
        ('/api/v1/health', 'API Health'),
    ]
    
    with app.test_client() as client:
        print("📋 Testando rotas principais:")
        print("-"*60)
        
        all_ok = True
        for route, name in routes_to_test:
            response = client.get(route, follow_redirects=True)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name:20} ({route:20}) : {response.status_code}")
            
            if response.status_code != 200:
                all_ok = False
                if response.status_code == 500:
                    # Try to get error details
                    print(f"   Error: Check logs for details")
        
        print("-"*60)
        
        # Test static files
        print("\n📁 Testando arquivos estáticos:")
        print("-"*60)
        
        static_files = [
            '/static/css/app.css',
            '/static/js/app.js'
        ]
        
        for file_path in static_files:
            response = client.get(file_path)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {file_path:30} : {response.status_code}")
            
            if response.status_code != 200:
                all_ok = False
        
        print("-"*60)
        
        # Summary
        print("\n📊 RESUMO DO TESTE")
        print("="*60)
        
        if all_ok:
            print("✅ Todos os testes passaram!")
            print("\n🎉 Interface web está funcionando corretamente!")
            print("\n💡 Para iniciar o servidor:")
            print("   python3 run_local.py")
            print("\n🌐 Acesse: http://localhost:5000")
        else:
            print("❌ Alguns testes falharam")
            print("\n⚠️ Verifique os logs para mais detalhes")
            
        return all_ok

if __name__ == '__main__':
    success = test_web_interface()
    sys.exit(0 if success else 1)