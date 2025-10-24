#!/usr/bin/env bash
# Vercel build script for Flask app
set -euo pipefail

# Install dependencies
pip install -r requirements.txt

# Collect static (if any) - placeholder
mkdir -p static

# Output hint
echo "Build complete. Using wsgi.py as entrypoint."
