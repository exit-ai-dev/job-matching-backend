# Gunicorn Configuration for Azure App Service
import os
import multiprocessing

# Server Socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
backlog = 2048

# Worker Processes
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)  # Max 4 workers for Azure
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process Naming
proc_name = 'job-matching-api'

# Server Mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None
