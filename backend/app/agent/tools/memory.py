"""简单的对话记忆管理（进程内，可选 Redis 持久化）"""
from typing import Dict, List, Any, Optional

import logging

logger = logging.getLogger(__name__)


class MemoryManager:
    """对话记忆：按 user_id + trip_id 维护消息历史"""

    def __init__(self):
        self._store: Dict[str, List[Dict[str, str]]] = {}

    def _key(self, user_id: str, trip_id: Optional[str]) -> str:
        return f"{user_id}:{trip_id or 'global'}"

    def append(self, user_id: str, role: str, content: str, trip_id: Optional[str] = None):
        k = self._key(user_id, trip_id)
        self._store.setdefault(k, []).append({"role": role, "content": content})

    def get(self, user_id: str, trip_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, str]]:
        k = self._key(user_id, trip_id)
        return self._store.get(k, [])[-limit:]

    def clear(self, user_id: str, trip_id: Optional[str] = None):
        self._store.pop(self._key(user_id, trip_id), None)


_memory_singleton: Optional[MemoryManager] = None


def get_memory() -> MemoryManager:
    global _memory_singleton
    if _memory_singleton is None:
        _memory_singleton = MemoryManager()
    return _memory_singleton
