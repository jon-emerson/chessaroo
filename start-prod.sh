#!/bin/bash

# Run database migrations first
echo "🚀 Running database migrations..."
python3 migrations/refactor_player_names.py

# Start the Flask API backend on port 8000 in background
gunicorn --bind 0.0.0.0:8000 app:app &

# Start Next.js frontend on port 3000 (ALB will route to this port)
cd frontend && npm start