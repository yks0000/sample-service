import hashlib
import random
import threading
import time

from flask import Flask, request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Gauge

app = Flask(__name__)

REQUEST_COUNT = Counter('request_count', 'Total number of requests.')
CPU_USAGE = Gauge('cpu_usage_percent', 'Current CPU usage percentage')
REQUESTS_PER_SECOND = Gauge('requests_per_second', 'Number of requests processed per second.')

# Internal counter for requests within the current second
_current_second_request_count = 0
_last_update_time = time.time()
_lock = threading.Lock() # To protect shared variables in multi-threaded access


def update_requests_per_second_loop():
    global _current_second_request_count
    global _last_update_time

    while True:
        start_time = time.time()
        time.sleep(1)
        end_time = time.time()
        time_elapsed = end_time - start_time

        with _lock:
            rps = _current_second_request_count / time_elapsed if time_elapsed > 0 else 0.0
            REQUESTS_PER_SECOND.set(rps)
            _current_second_request_count = 0
            _last_update_time = end_time


@app.route('/')
def hello():
    REQUEST_COUNT.inc()

    # Increment internal counter for RPS calculation
    with _lock:
        global _current_second_request_count
        _current_second_request_count += 1

    range_param = request.args.get('range', default=1, type=int)
    data = b'Hello, World!' * range_param
    for _ in range(range_param):
        hashlib.sha256(data).hexdigest()
    cpu_usage = min(100, range_param * 0.1)  # Scale CPU usage based on range_param
    CPU_USAGE.set(cpu_usage)
    return f'CPU-intensive task completed with range {range_param}!'

@app.route('/metrics')
def metrics():
    CPU_USAGE.set(random.uniform(10, 90)) # Simulate CPU usage
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    # Don't start a separate HTTP server here, Flask will serve the metrics
    request_thread = threading.Thread(target=update_requests_per_second_loop, daemon=True)
    request_thread.start()
    app.run(host='0.0.0.0', port=8000)