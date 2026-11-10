import hmac
import threading
import time
from collections import OrderedDict, deque


def valid_token(provided, expected):
    return isinstance(provided, str) and hmac.compare_digest(provided.encode(), expected.encode())


class RateLimiter:
    """Limite por processo/IP em memória, sem persistir o endereço nos logs."""
    def __init__(self, maximum=120, window=60):
        self.maximum = maximum
        self.window = window
        self.buckets = OrderedDict()
        self.lock = threading.Lock()

    def allow(self, key):
        now = time.monotonic()
        with self.lock:
            bucket = self.buckets.setdefault(key, deque())
            self.buckets.move_to_end(key)
            while bucket and bucket[0] <= now - self.window:
                bucket.popleft()
            if len(self.buckets) > 2048:
                self.buckets.popitem(last=False)
            if len(bucket) >= self.maximum:
                return False
            bucket.append(now)
            return True
