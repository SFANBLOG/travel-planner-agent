"""向量存储：Milvus 优先（嵌入式 lite 或独立服务），失败时降级为进程内余弦检索

对外接口保持一致：
- add_texts(texts, metadatas, ids=None)
- similarity_search_with_score(query, k, filter=None) -> [(doc, score), ...]
- similarity_search(query, k, filter=None) -> [doc, ...]
其中 doc 具有 .page_content 与 .metadata 属性（兼容 langchain Document 用法）。

默认使用 pymilvus 的 MilvusClient：
- uri 为本地文件（如 data/milvus/milvus.db）时走 milvus-lite 嵌入式，无需 Docker；
- uri 为 http://host:19530 时连接独立 Milvus 服务。
embedding 默认哈希 n-gram（零依赖），配置远端 EMBEDDING 时才走 OpenAI 类接口。
"""
import os
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


class MilvusVectorStore:
    """Milvus 后端（milvus-lite 嵌入式或独立服务，哈希 embedding，零远端依赖默认）

    使用 pymilvus.MilvusClient：
    - uri 为本地文件时走 milvus-lite 嵌入式（无需 Docker，数据持久化到该文件）；
    - uri 为 http://host:19530 时连接独立 Milvus 服务。
    元数据整体存入 JSON 字段，检索距离采用 COSINE（distance = 1 - cosine），
    与 MemoryVectorStore 的 score 语义一致，chain.py 的 relevance_score = 1 - score 直接复用。
    """

    def __init__(self, name: str, uri: str):
        from pymilvus import MilvusClient
        self._uri = uri
        parent = os.path.dirname(uri)
        if parent:
            os.makedirs(parent, exist_ok=True)
        self._client = MilvusClient(uri=uri)
        self._name = name
        self._ef = HashEmbeddings()
        self._dim = self._ef.dim
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        from pymilvus import DataType, FieldSchema, CollectionSchema
        if self._client.has_collection(self._name):
            return
        fields = [
            FieldSchema(name="pk", dtype=DataType.VARCHAR, is_primary=True, max_length=64),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="meta", dtype=DataType.JSON),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self._dim),
        ]
        schema = CollectionSchema(fields, description=self._name)
        self._client.create_collection(
            collection_name=self._name, schema=schema, metric_type="COSINE"
        )

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None,
                  ids: Optional[List[str]] = None) -> List[str]:
        metadatas = metadatas or [{} for _ in texts]
        ids = ids or [str(i) for i in range(len(texts))]
        self._ensure_collection()
        vectors = self._ef.embed_documents(texts)
        data = [
            {"pk": str(ids[i]), "text": texts[i], "meta": metadatas[i], "vector": vectors[i]}
            for i in range(len(texts))
        ]
        self._client.upsert(collection_name=self._name, data=data)
        return ids

    @staticmethod
    def _cvt_filter(flt: Optional[Dict[str, Any]]):
        """把扁平过滤 dict 转为 Milvus JSON 字段表达式（meta[\"key\"] op value）。"""
        if not flt:
            return None
        clauses = []
        for k, v in flt.items():
            if v is None:
                continue
            if isinstance(v, bool):
                clauses.append(f'meta["{k}"] == {str(v).lower()}')
            elif isinstance(v, (int, float)):
                clauses.append(f'meta["{k}"] == {v}')
            else:
                s = str(v).replace('"', '\\"')
                clauses.append(f'meta["{k}"] == "{s}"')
        return " and ".join(clauses) if clauses else None

    @staticmethod
    def _hit_text_meta(hit):
        ent = getattr(hit, "entity", hit)
        if isinstance(ent, dict):
            return ent.get("text", ""), ent.get("meta", {})
        try:
            return ent.get("text", ""), ent.get("meta", {})
        except Exception:
            return getattr(ent, "text", ""), getattr(ent, "meta", {})

    def similarity_search_with_score(self, query: str, k: int = 10,
                                     filter: Optional[Dict[str, Any]] = None) -> List:
        self._ensure_collection()
        expr = self._cvt_filter(filter)
        qv = self._ef.embed_query(query)
        res = self._client.search(
            collection_name=self._name,
            data=[qv],
            limit=k,
            filter=expr,
            output_fields=["text", "meta"],
        )
        out = []
        for hit in res[0]:
            text, meta = self._hit_text_meta(hit)
            if not isinstance(meta, dict):
                meta = {}
            out.append((_Doc(text, meta), float(getattr(hit, "distance", 0.0))))
        return out

    def similarity_search(self, query: str, k: int = 10,
                          filter: Optional[Dict[str, Any]] = None) -> List:
        return [d for d, _ in self.similarity_search_with_score(query, k, filter)]

    def count(self) -> int:
        try:
            return int(self._client.get_collection_stats(self._name).get("row_count", 0))
        except Exception:
            return 0


_stores: Dict[str, Any] = {}


def get_vector_store(name: str = "travel_spots") -> Any:
    """工厂：Milvus 优先，异常时按配置降级（chroma 可选回退），最终降级为内存存储"""
    if name in _stores:
        return _stores[name]
    from app.config import settings
    store_type = settings.VECTOR_STORE_TYPE
    try:
        if store_type == "milvus":
            store = MilvusVectorStore(name, settings.MILVUS_URI)
            logger.info("向量库使用 Milvus: %s (uri=%s)", name, settings.MILVUS_URI)
            _stores[name] = store
            return store
    except Exception as e:
        logger.warning("Milvus 初始化失败，降级为内存向量库: %s", e)
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
