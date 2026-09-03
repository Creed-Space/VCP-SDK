"""Content-addressed cache primitives with explicit dependency vectors."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class CacheKey:
    namespace: str
    request_digest: str
    dependency_digests: tuple[str, ...]

    @property
    def identity(self) -> tuple[str, str, tuple[str, ...]]:
        return (self.namespace, self.request_digest, self.dependency_digests)


class ContentAddressedCache(Generic[T]):
    """Bounded in-process cache that cannot ignore declared dependencies."""

    def __init__(self, max_entries: int = 256) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be positive")
        self._max_entries = max_entries
        self._items: OrderedDict[tuple[str, str, tuple[str, ...]], T] = OrderedDict()
        self._lock = RLock()

    def get(self, key: CacheKey) -> T | None:
        with self._lock:
            value = self._items.get(key.identity)
            if value is not None:
                self._items.move_to_end(key.identity)
            return value

    def put(self, key: CacheKey, value: T) -> None:
        with self._lock:
            self._items[key.identity] = value
            self._items.move_to_end(key.identity)
            while len(self._items) > self._max_entries:
                self._items.popitem(last=False)

    def invalidate_dependency(self, digest: str) -> int:
        with self._lock:
            doomed = [key for key in self._items if digest in key[2]]
            for key in doomed:
                del self._items[key]
            return len(doomed)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._items)
