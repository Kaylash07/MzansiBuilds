#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Create database tables
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Tables created')"
