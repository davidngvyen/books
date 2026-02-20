from collections import OrderedDict
from threading import Lock

class BookSearchLRUCache:
    def __init__(self, max_size=100):
        self._cache = OrderedDict()
        self._max_size = max_size
        self._lock = Lock()

    def get(self, query):
        with self._lock:
            if query not in self._cache:
                return None
            self._cache.move_to_end(query)
            return self._cache[query]

    def set(self, query, value):
        with self._lock:
            if query in self._cache:
                self._cache.move_to_end(query)
            self._cache[query] = value
            if len(self._cache) > self._max_size:
                self._cache.popitem(last=False)

    def invalidate(self, query=None):
        with self._lock:
            if query is None:
                self._cache.clear()
                return
            self._cache.pop(query, None)

    def clear(self):
        self.invalidate()

    def size(self):
        with self._lock:
            return len(self._cache)

cache = BookSearchLRUCache(max_size=100)
