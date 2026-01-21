#!/bin/bash
# Azure App Service Startup Script

echo "Starting Job Matching API..."

# Database initialization (if needed)
if [ ! -f "./job_matching.db" ]; then
    echo "Initializing database..."
    python init_db.py
    python seed_db.py
fi

# Start the application
echo "Starting uvicorn server..."
python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
