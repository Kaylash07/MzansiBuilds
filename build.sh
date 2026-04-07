#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Create database tables
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Tables created')"

# Seed database if empty (only on first deploy)
python -c "
from app import app, db
from models import User
with app.app_context():
    if User.query.count() == 0:
        from flask.globals import current_app
        from click.testing import CliRunner
        runner = CliRunner()
        with app.app_context():
            from app import seed_db
            runner.invoke(seed_db, standalone_mode=False)
            print('Database seeded')
    else:
        print('Database already has data, skipping seed')
"
