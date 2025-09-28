#!/bin/bash

# Run comprehensive database migration (drops and recreates all tables)
echo "🚀 Running comprehensive database migration..."
python3 migrate_database.py

# Start the Flask API backend on port 8000 in background
gunicorn --bind 0.0.0.0:8000 app:app &

# Start Next.js frontend on port 3000 (ALB will route to this port)
cd frontend && npm start