#!/usr/bin/env python3
"""Configuration pour Gunicorn sur Ubuntu"""

import multiprocessing
import os

# Configuration serveur
bind = "0.0.0.0:8000"
workers = min(4, multiprocessing.cpu_count() * 2 + 1)
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Timeout
timeout = 30
keepalive = 2

# Logging
loglevel = "info"
accesslog = "/tmp/whattowatch-access.log"
errorlog = "/tmp/whattowatch-error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "whattowatch-backend"

# Preload app
preload_app = True

# Démarrage/arrêt
def on_starting(server):
    server.log.info("🚀 Démarrage de WhatToWatch Backend...")

def when_ready(server):
    server.log.info("✅ WhatToWatch Backend prêt à recevoir des connexions")

def on_exit(server):
    server.log.info("🛑 Arrêt de WhatToWatch Backend")
