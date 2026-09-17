"""哈希 n-gram 向量化（零依赖，中文友好）

设计：将文本按字符 2~3 gram 切分，对每个 gram 做 md5 取前若干位作为有符号整数，
累加到固定维度(默认 384)的向量，最后 L2 归一化。无需任何远端 embedding 服务即可工作，
中文/英文混合场景下余弦相似度表现稳定。若配置 OPENAI_EMBEDDING_MODEL 且有 Key，可切换远端。
"""
import hashlib
import re
from typing import List

DIM = 384


def _char_ngrams(text: str, n: int) -> List[str]:
    text = re.sub(r"\s+", "", text or "")
    if len(text) == 0:
        return []
    if len(text) < n:
        return [text]
    return [text[i:i + n] for i in range(len(text) - n + 1)]


def embed(text: str, dim: int = DIM) -> List[float]:
    vec = [0.0] * dim
    grams = set()
    for n in (2, 3):
        grams.update(_char_ngrams(text, n))
    if not grams:
        # 空文本返回单位向量，避免除零
        vec[0] = 1.0
        return vec
    for g in grams:
        h = hashlib.md5(g.encode("utf-8")).digest()
        # 取两个 32-bit 有符号整数
        a = int.from_bytes(h[0:4], "big", signed=True)
        b = int.from_bytes(h[4:8], "big", signed=True)
        idx1 = abs(a) % dim
        idx2 = abs(b) % dim
        vec[idx1] += 1.0 if a >= 0 else -1.0
        vec[idx2] += 1.0 if b >= 0 else -1.0
    # L2 归一化
    norm = sum(v * v for v in vec) ** 0.5
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def cosine(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class HashEmbeddings:
    """兼容 langchain Embeddings 接口（embed_documents / embed_query）"""

    def __init__(self, dim: int = DIM):
        self.dim = dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [embed(t, self.dim) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return embed(text, self.dim)
