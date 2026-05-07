import threading
import time
import random
import queue


# ---------------- PRODUCER ---------------- #
class TrafficDataGenerator(threading.Thread):
    def __init__(self, q):
        super().__init__()
        self.q = q
        self.running = True

    def run(self):
        cameras = [f"Camera_{i}" for i in range(1, 6)]

        while self.running:
            for cam in cameras:
                data = {
                    "camera": cam,
                    "speed": random.randint(10, 120),
                    "vehicles": random.randint(10, 100),
                    "status": random.choice(["LOW", "MEDIUM", "HIGH"]),
                    "anomaly": random.choice([False, False, False, True])
                }

                if not self.q.full():
                    self.q.put(data)

            time.sleep(0.5)

    def stop(self):
        self.running = False


# ---------------- CONSUMER (REAL PARALLEL WORKERS) ---------------- #
class ParallelAnalyzer:
    def __init__(self, q, shared_results):
        self.q = q
        self.results = shared_results
        self.running = True
        self.lock = threading.Lock()

        self.worker_stats = {
            "Worker_1": 0,
            "Worker_2": 0,
            "Worker_3": 0,
            "Worker_4": 0
        }

    def worker_loop(self, name):
        while self.running:
            try:
                data = self.q.get(timeout=1)

                # simulate processing delay
                time.sleep(0.2)

                result = {
                    "worker": name,
                    "actual_speed": data["speed"],
                    "vehicle_count": data["vehicles"],
                    "congestion_status": data["status"],
                    "is_anomaly": data["anomaly"]
                }

                with self.lock:
                    self.results[data["camera"]] = result
                    self.worker_stats[name] += 1

                self.q.task_done()

            except:
                pass

    def start(self, n_workers=4):
        self.threads = []

        for i in range(n_workers):
            t = threading.Thread(
                target=self.worker_loop,
                args=(f"Worker_{i+1}",),
                daemon=True
            )
            t.start()
            self.threads.append(t)

    def stop(self):
        self.running = False