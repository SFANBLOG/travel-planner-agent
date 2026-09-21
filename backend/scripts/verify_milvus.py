"""Milvus 向量库连通性回归检查。

覆盖三个曾经出问题的点：
  1. 远端 http(s):// URI 被 Windows os.path.dirname 切成 "http:" 导致 makedirs 失败；
  2. 集合创建后缺索引/未 load，search 报 "collection not loaded"；
  3. count() 受 flush 与一致性级别影响返回 0。

用法:
    python scripts/verify_milvus.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

TMP_COLLECTION = "verify_milvus_tmp"


def main() -> int:
    from app.config import settings
    from app.rag.chain import RAGChain
    from app.rag.vectorstore import MilvusVectorStore

    print(f"VECTOR_STORE_TYPE = {settings.VECTOR_STORE_TYPE}")
    print(f"MILVUS_URI        = {settings.MILVUS_URI}")
    print("-" * 62)

    failures: list[str] = []

    # 1) 初始化不应降级
    try:
        store = MilvusVectorStore(TMP_COLLECTION, settings.MILVUS_URI)
    except Exception as e:
        print(f"[FAIL] Milvus 初始化失败（会降级为内存库）: {e}")
        return 1
    print("[PASS] Milvus 初始化成功，未降级")

    # 2) 写入 + 计数
    docs = ["西湖 断桥残雪 杭州 5A景区", "故宫 天安门 北京 5A景区", "宽窄巷子 成都 历史街区"]
    metas = [{"city": "杭州"}, {"city": "北京"}, {"city": "成都"}]
    store.add_texts(docs, metas, ids=["s1", "s2", "s3"])
    n = store.count()
    print(f"[{'PASS' if n == 3 else 'FAIL'}] 写入 3 条，count() = {n}")
    if n != 3:
        failures.append("count() 不准确")

    # 3) 检索（需要集合已建索引并 load）
    try:
        hits = store.similarity_search_with_score("热门景点 5A", k=3)
        print(f"[{'PASS' if len(hits) == 3 else 'FAIL'}] 无过滤检索命中 {len(hits)} 条")
        if len(hits) != 3:
            failures.append("无过滤检索数量异常")
    except Exception as e:
        print(f"[FAIL] 检索失败: {e}")
        failures.append("检索失败")

    # 4) 元数据过滤检索
    try:
        fh = store.similarity_search_with_score("热门景点", k=5, filter={"city": "杭州"})
        ok = len(fh) == 1 and fh[0][0].metadata.get("city") == "杭州"
        print(f"[{'PASS' if ok else 'FAIL'}] 过滤 city=杭州 命中 {len(fh)} 条")
        if not ok:
            failures.append("过滤检索异常")
    except Exception as e:
        print(f"[FAIL] 过滤检索失败: {e}")
        failures.append("过滤检索失败")

    store._client.drop_collection(TMP_COLLECTION)

    # 5) 业务链路
    chain = RAGChain()
    print(f"[INFO] spot_store  = {type(chain.spot_store).__name__}  "
          f"count={chain.spot_store.count()}")
    print(f"[INFO] guide_store = {type(chain.guide_store).__name__}  "
          f"count={chain.guide_store.count()}")
    if not isinstance(chain.spot_store, MilvusVectorStore):
        failures.append("业务链路未使用 Milvus")

    print("-" * 62)
    if failures:
        print(f"结果: {len(failures)} 项异常 -> {failures}")
        return 1
    print("结果: 全部通过 ✅")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
