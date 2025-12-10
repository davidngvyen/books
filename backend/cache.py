from datetime import datetime, timedelta
from threading import Lock

class SimpleCache:
    
    def __init__(self):
        self._cache = {}
        self._lock = Lock()
    
    def get(self, key):
        #get from cache if still valid
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if datetime.now() < expiry:
                    return value
                else:
                    del self._cache[key]
            return None
    
    def set(self, key, value, ttl_seconds=60):
        with self._lock:
            expiry = datetime.now() + timedelta(seconds=ttl_seconds)
            self._cache[key] = (value, expiry)
    
    def delete(self, key):
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        with self._lock:
            self._cache.clear()

cache = SimpleCache()
