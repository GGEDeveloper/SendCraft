#!/usr/bin/env python3
"""
SendCraft Passenger WSGI Entry Point
Auto-generated entry point for cPanel Passenger WSGI
Compatible with cPanel Python App deployment
"""
import os
import sys
from pathlib import Path

# Add project to Python path for imports
project_path = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_path))

# Set production environment
os.environ['FLASK_ENV'] = 'production'

# Import WSGI application from app.py
from app import application

# Passenger WSGI expects 'application' callable
# This is automatically used by cPanel Passenger

# Optional: Direct run for debugging
if __name__ == '__main__':
    """Test WSGI application locally (debug only)"""
    from sendcraft import create_app
    
    app = create_app('production')
    print("🧪 Testing Passenger WSGI...")
    print("🌐 Production: https://email.artnshine.pt")
    
    app.run(host='0.0.0.0', port=5000, debug=False)