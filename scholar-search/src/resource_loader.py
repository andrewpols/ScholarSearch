import os
import pickle
import threading
from typing import Callable


class ResourceCache:
    def __init__(self, cache_dir="../data/cache"):
        self._lock = threading.Lock()
        self._cache = {}
        self._query_cache = {}
        self._cache_dir = cache_dir

        if os.path.exists(self._cache_dir):
            files_iter = [f for f in os.listdir(self._cache_dir) if os.path.isfile(os.path.join(self._cache_dir, f))
                          and f != '.DS_Store']
            for file in files_iter:
                filename = file[:-4]
                filepath = os.path.join(self._cache_dir, file)
                with open(filepath, "rb", buffering=10 * 1024 * 1024) as f:
                    resource = pickle.load(f)
                self._cache[filename] = resource
        else:
            os.makedirs(self._cache_dir)

        print("finish")

    def get_one_resource(self, name: str, loader_fn: Callable):
        """Returns a cached resource or loads and caches it using loader_fn."""
        with self._lock:
            if name in self._cache:
                print(f'FOUND {name} IN CACHE!')
                return self._cache[name]

            path = os.path.join(self._cache_dir, f"{name}.pkl")

            if os.path.exists(path):
                print(f"[cache] Loading {name} from {path}")
                with open(path, "rb", buffering=10 * 1024 * 1024) as f:
                    resource = pickle.load(f)
            else:
                print(f"[cache] Building {name}...")
                resource = loader_fn()
                with open(path, "wb") as f:
                    pickle.dump(resource, f, protocol=pickle.HIGHEST_PROTOCOL)
                print(f"[cache] Cached {name} to {path}")

            self._cache[name] = resource
            return resource


CACHE = ResourceCache()


def get_resource(resource: str, resource_func: Callable):
    print(f'Looking for {resource}: {CACHE._cache.keys()}')
    return CACHE.get_one_resource(resource, resource_func)
