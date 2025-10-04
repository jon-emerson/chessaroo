#!/bin/bash

# Entrypoint executed inside the production container (e.g. ECS/Fargate) that
# launches both the Flask API and the Next.js frontend processes.

# Start the Flask API backend on port 8000 in background
gunicorn --bind 0.0.0.0:8000 backend.app:app &

# Start Next.js frontend on port 3000 (ALB will route to this port)
cd frontend && node server.js
