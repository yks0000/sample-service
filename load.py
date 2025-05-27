import logging
import random
import time

from locust import FastHttpUser, constant_pacing, events, task

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    logger.info("Initializing locust")


class SampleServiceLoad(FastHttpUser):

    wait_time = constant_pacing(1.0 / 600)

    def on_start(self):
        logger.info("Initializing sync test")

    @task
    def make_authz_request(self):
        start_time = time.perf_counter()
        range_param = random.randint(10, 100)
        try:
            self.client.get(f"/?range={range_param}")
            elapsed = time.perf_counter() - start_time
            self.environment.events.request.fire(
                request_type="get",
                name="sample-service",
                response_time=elapsed * 1000,
                response_length=0,
                exception=None,
            )
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            self.environment.events.request.fire(
                request_type="get",
                name="sample-service",
                response_time=elapsed * 1000,
                response_length=0,
                exception=e
            )


# locust -f load.py --host=https://authz-decision-prf.api.intuit.com --web-host=127.0.0.1 --web-port=8089 --processes 4 --loglevel WARNING
