#!/usr/bin/env python3
"""Demonstração da Interface Web SendCraft"""
import os
import sys
import time
from threading import Thread
import webbrowser

def run_server():
    """Executa o servidor Flask"""
    os.environ['FLASK_ENV'] = 'local'
    os.environ['FLASK_DEBUG'] = '0'  # Disable debug for demo
    
    from sendcraft import create_app
    app = create_app('local')
    
    # Run server
    app.run(host='0.0.0.0', port=5000, debug=False)

def main():
    print("🚀 SendCraft Email Manager - Demo Interface Web")
    print("="*60)
    
    # Start server in background thread
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("⏳ Iniciando servidor...")
    time.sleep(3)
    
    print("\n✅ Servidor iniciado com sucesso!")
    print("\n📊 Interface Web disponível em:")
    print("   🌐 http://localhost:5000")
    print("\n📋 Páginas disponíveis:")
    print("   • Dashboard: http://localhost:5000/")
    print("   • Domínios: http://localhost:5000/domains")
    print("   • Contas: http://localhost:5000/accounts")
    print("   • Templates: http://localhost:5000/templates")
    print("   • Logs: http://localhost:5000/logs")
    print("\n🔧 API Health: http://localhost:5000/api/v1/health")
    
    print("\n💾 Database: SQLite local com dados seed")
    print("   • 5 domínios configurados")
    print("   • 6 contas de email")
    print("   • 4 templates HTML")
    print("   • 300+ logs de exemplo")
    
    print("\n🛑 Pressione Ctrl+C para parar o servidor")
    print("="*60)
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Servidor parado. Até logo!")
        sys.exit(0)

if __name__ == '__main__':
    main()