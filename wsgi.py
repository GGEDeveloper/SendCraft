"""
SendCraft WSGI Entry Point.
Usado para deploy em produção (cPanel, Gunicorn, etc).
"""
import os
import sys

# Adicionar o diretório atual ao path (importante para cPanel)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar e criar aplicação
from sendcraft import create_app

# Criar aplicação em modo produção
application = create_app('production')

# Alias para compatibilidade
app = application


if __name__ == '__main__':
    # Se executado diretamente, executar em modo debug
    application.run(debug=False)