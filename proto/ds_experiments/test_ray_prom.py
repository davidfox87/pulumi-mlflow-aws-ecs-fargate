import time
import random

import ray
from ray.util.metrics import Counter, Gauge, Histogram

ray.init(address='ray://127.0.0.1:10001', _metrics_export_port=8080)

class Scorer:
    def __init__(self, name):
        self.gauge = Gauge(
        "curr_count",
        description="Current count held by the actor. Goes up and down.",
        tag_keys=("actor_name",),
        )
        self.gauge.set_default_tags({"actor_name": name})
        self._curr_count = 0

    def process(self, num):
        self._curr_count += num
        # Update the gauge to the new value.
        self.gauge.set(self._curr_count)


@ray.remote
class MyActor:
    def __init__(self, name):
        
        self.scorer = Scorer('my_test_scorer')

    def process_request(self, num):
        self.scorer.process(num)


print("Starting actor.")
my_actor = MyActor.remote("my_actor")

for i in range(30):
    time.sleep(5)
    my_actor.process_request.remote(random.uniform(-1, 1))

print("Exiting!")