#!/usr/bin/env python3
"""
SendCraft Email Manager - Entry Point
Main application entry point for development server.
"""
import os
import sys
from typing import Optional

# Adicionar o diretório atual ao path (importante para cPanel)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sendcraft import create_app

# Criar aplicação
app = create_app(os.environ.get('FLASK_ENV', 'development'))


if __name__ == '__main__':
    # Configuração para desenvolvimento
    port = int(os.environ.get('PORT', 5000))
    debug = app.config.get('DEBUG', True)
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║         SendCraft Email Manager          ║
    ║            Version 0.1.0                 ║
    ╠══════════════════════════════════════════╣
    ║  Running in {app.config.get('ENV', 'development').upper():^28}║
    ║  Debug Mode: {str(debug):^28}║
    ║  Port: {port:^34}║
    ╚══════════════════════════════════════════╝
    """)
    
    # Executar servidor de desenvolvimento
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )