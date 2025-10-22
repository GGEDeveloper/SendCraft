#!/usr/bin/env python3
"""SendCraft Development com Remote MySQL"""
import os
import sys

# Compatibility check - only run if not in production
if os.environ.get('FLASK_ENV') == 'production':
    print("❌ run_dev.py não deve ser usado em produção!")
    print("✅ Use app.py ou passenger_wsgi.py para produção")
    sys.exit(1)

def main():
    print("🔧 SendCraft Development Mode (Remote MySQL → dominios.pt)")
    print("=" * 60)
    
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Test MySQL connection
    try:
        import pymysql
        print("📡 Testando conexão com MySQL remoto...")
        connection = pymysql.connect(
            host='artnshine.pt',
            user='artnshin_sendcraft',
            password='g>bxZmj%=JZt9Z,i',
            database='artnshin_sendcraft',
            connect_timeout=10
        )
        connection.close()
        print("✅ Remote MySQL connection OK")
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("\n💡 Dica: Verifique se o servidor remoto está acessível")
        print("   - Confirme que o IP está autorizado no servidor")
        print("   - Verifique as credenciais MySQL")
        sys.exit(1)
    
    from sendcraft import create_app
    app = create_app('development')
    
    print("✅ SendCraft Development Ready!")
    print("🌐 Web Interface: http://localhost:5000")
    print("🗄️ Database: Remote MySQL (dominios.pt)")
    print("🛑 Ctrl+C para parar")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)

if __name__ == '__main__':
    main()