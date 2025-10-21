#!/usr/bin/env python3
"""SendCraft Local com SQLite + dados seed"""
import os
import sys

def main():
    print("🏠 SendCraft Local Mode (SQLite + Seed Data)")
    print("=" * 50)
    
    os.environ['FLASK_ENV'] = 'local'
    os.environ['FLASK_DEBUG'] = '1'
    
    from sendcraft import create_app
    app = create_app('local')
    
    # Check/seed database
    with app.app_context():
        try:
            from sendcraft.models import Domain
            if Domain.query.count() == 0:
                print("📊 Seeding local database...")
                from sendcraft.cli.seed_data import seed_local_data
                from click.testing import CliRunner
                runner = CliRunner()
                with app.app_context():
                    result = runner.invoke(seed_local_data)
                    if result.exit_code != 0:
                        print(f"Seed data error: {result.output}")
        except Exception:
            print("🔧 Creating and seeding database...")
            from sendcraft.extensions import db
            db.create_all()
            # Chamar seed data diretamente no contexto da app
            from sendcraft.cli.seed_data import seed_local_data
            from click.testing import CliRunner
            runner = CliRunner()
            with app.app_context():
                result = runner.invoke(seed_local_data)
                if result.exit_code != 0:
                    print(f"Seed data error: {result.output}")
    
    print("✅ SendCraft Local Ready!")
    print("🌐 Interface: http://localhost:5000")
    print("🗄️ Database: SQLite local")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()