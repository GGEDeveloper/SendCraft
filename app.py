#!/usr/bin/env python3
"""
SendCraft Production Entry Point
cPanel Python App entry point for email.artnshine.pt
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def application(environ, start_response):
    """WSGI application entry point for cPanel Passenger"""
    from sendcraft import create_app
    
    # Force production environment
    os.environ['FLASK_ENV'] = 'production'
    
    # Create Flask app in production mode
    app = create_app('production')
    
    return app(environ, start_response)

if __name__ == '__main__':
    """Direct run for testing (não usar em produção)"""
    from sendcraft import create_app
    
    os.environ['FLASK_ENV'] = 'production'
    app = create_app('production')
    
    print("🚀 SendCraft Production Mode")
    print("🌐 Running on https://email.artnshine.pt")
    
    # Run on all interfaces for cPanel
    app.run(host='0.0.0.0', port=5000, debug=False)