from flask import Flask
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Gauge
import time
import random
import os

app = Flask(__name__)

REQUEST_COUNT = Counter('request_count', 'Total number of requests.')
CPU_USAGE = Gauge('cpu_usage_percent', 'Current CPU usage percentage')

@app.route('/')
def hello():
    REQUEST_COUNT.inc()
    time.sleep(random.uniform(0.1, 0.5)) # Simulate some work
    return "Hello from Sample Service!"

@app.route('/metrics')
def metrics():
    CPU_USAGE.set(random.uniform(10, 90)) # Simulate CPU usage
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    from prometheus_client import start_http_server
    # Don't start a separate HTTP server here, Flask will serve the metrics
    app.run(host='0.0.0.0', port=8000)