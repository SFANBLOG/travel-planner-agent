"""向量存储：ChromaDB 优先，失败时降级为进程内余弦检索

对外接口保持一致：
- add_texts(texts, metadatas, ids=None)
- similarity_search_with_score(query, k, filter=None) -> [(doc, score), ...]
- similarity_search(query, k, filter=None) -> [doc, ...]
其中 doc 具有 .page_content 与 .metadata 属性（兼容 langchain Document 用法）。
"""
from typing import List, Dict, Any, Optional
import logging

from app.rag.embeddings import embed, cosine, HashEmbeddings

logger = logging.getLogger(__name__)


class _Doc:
    def __init__(self, page_content: str, metadata: Dict[str, Any]):
        self.page_content = page_content
        self.metadata = metadata


def _match_filter(metadata: Dict[str, Any], flt: Optional[Dict[str, Any]]) -> bool:
    if not flt:
        return True
    for k, v in flt.items():
        if v is None:
            continue
        if metadata.get(k) != v:
            return False
    return True


class MemoryVectorStore:
    """进程内向量存储（哈希 embedding + 余弦相似度）"""

    def __init__(self, name: str = "default"):
        self.name = name
        self._items: List[Dict[str, Any]] = []

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None,
                  ids: Optional[List[str]] = None) -> List[str]:
        metadatas = metadatas or [{} for _ in texts]
        ids = ids or [str(i) for i in range(len(texts))]
        for i, t in enumerate(texts):
            self._items.append({
                "id": ids[i],
                "content": t,
                "metadata": metadatas[i],
                "vec": embed(t),
            })
        return ids

    def similarity_search_with_score(self, query: str, k: int = 10,
                                     filter: Optional[Dict[str, Any]] = None) -> List:
        qv = embed(query)
        scored = []
        for it in self._items:
            if not _match_filter(it["metadata"], filter):
                continue
            sc = cosine(qv, it["vec"])
            scored.append((_Doc(it["content"], it["metadata"]), 1 - sc))
        scored.sort(key=lambda x: x[1])
        return scored[:k]

    def similarity_search(self, query: str, k: int = 10,
                          filter: Optional[Dict[str, Any]] = None) -> List:
        return [d for d, _ in self.similarity_search_with_score(query, k, filter)]

    def count(self) -> int:
        return len(self._items)


class ChromaVectorStore:
    """ChromaDB 后端（哈希 embedding，零远端依赖）"""

    def __init__(self, name: str, persist_directory: str):
        from langchain_chroma import Chroma
        self._chroma = Chroma(
            collection_name=name,
            embedding_function=HashEmbeddings(),
            persist_directory=persist_directory,
        )

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None,
                  ids: Optional[List[str]] = None) -> List[str]:
        ids = ids or [str(i) for i in range(len(texts))]
        self._chroma.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        return ids

    @staticmethod
    def _cvt_filter(flt: Optional[Dict[str, Any]]):
        """Chroma 要求组合过滤用 $and；把扁平多键 dict 转为 $and 列表"""
        if not flt:
            return None
        if any(str(k).startswith("$") for k in flt.keys()):
            return flt
        clauses = [{k: v} for k, v in flt.items() if v is not None]
        if len(clauses) <= 1:
            return clauses[0] if clauses else None
        return {"$and": clauses}

    def similarity_search_with_score(self, query: str, k: int = 10,
                                     filter: Optional[Dict[str, Any]] = None) -> List:
        return self._chroma.similarity_search_with_score(query=query, k=k, filter=self._cvt_filter(filter))

    def similarity_search(self, query: str, k: int = 10,
                          filter: Optional[Dict[str, Any]] = None) -> List:
        return self._chroma.similarity_search(query=query, k=k, filter=self._cvt_filter(filter))

    def count(self) -> int:
        try:
            return self._chroma._collection.count()
        except Exception:
            return 0


_stores: Dict[str, Any] = {}


def get_vector_store(name: str = "travel_spots") -> Any:
    """工厂：Chroma 优先，异常时降级为内存存储"""
    if name in _stores:
        return _stores[name]
    from app.config import settings
    store_type = settings.VECTOR_STORE_TYPE
    try:
        if store_type == "chroma":
            import os
            os.makedirs(settings.VECTOR_STORE_PATH, exist_ok=True)
            store = ChromaVectorStore(name, settings.VECTOR_STORE_PATH)
            logger.info("向量库使用 ChromaDB: %s", name)
            _stores[name] = store
            return store
    except Exception as e:
        logger.warning("ChromaDB 初始化失败，降级为内存向量库: %s", e)
    store = MemoryVectorStore(name)
    logger.info("向量库使用内存存储: %s", name)
    _stores[name] = store
    return store
