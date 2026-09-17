"""通用工具函数"""
import math
import re
import json
from datetime import date, datetime, timedelta
from typing import Optional, Any


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """球面距离（km）"""
    if None in (lat1, lng1, lat2, lng2):
        return 0.0
    R = 6371.0
    lat1r, lat2r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1r) * math.cos(lat2r) * math.sin(dlng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def extract_json(text: str) -> Optional[Any]:
    """从模型输出中提取首个 JSON 对象/数组（兼容 ```json 围栏）"""
    if not text:
        return None
    t = text.strip()
    # 去除 markdown 围栏
    if "```" in t:
        m = re.search(r"```(?:json)?\s*(.*?)```", t, re.DOTALL)
        if m:
            t = m.group(1).strip()
    try:
        return json.loads(t)
    except Exception:
        pass
    # 退而求其次：截取首个 { 到末个 } 或 [ 到 ]
    for lch, rch in (("{", "}"), ("[", "]")):
        s, e = t.find(lch), t.rfind(rch)
        if s != -1 and e != -1 and e > s:
            try:
                return json.loads(t[s:e + 1])
            except Exception:
                continue
    return None


def parse_flexible_date(s: str) -> Optional[date]:
    """解析多种日期格式：YYYY-MM-DD / YYYY/MM/DD / MM-DD（当年）"""
    if not s:
        return None
    s = s.strip().strip("。.，, ")
    fmts = ["%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%m-%d", "%m/%d"]
    for f in fmts:
        try:
            d = datetime.strptime(s, f).date()
            if f in ("%m-%d", "%m/%d") and d.year == 1900:
                d = d.replace(year=date.today().year)
            return d
        except Exception:
            continue
    return None


def add_days(d: date, n: int) -> date:
    return d + timedelta(days=n)


def weekday_cn(d: date) -> str:
    return ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][d.weekday()]


def nearest_neighbor_order(items, get_lat, get_lng):
    """贪心最近邻排序，返回排序后的索引列表"""
    n = len(items)
    if n <= 2:
        return list(range(n))
    import sys
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                dist[i][j] = haversine(get_lat(items[i]), get_lng(items[i]),
                                       get_lat(items[j]), get_lng(items[j]))
    visited = [False] * n
    route = [0]
    visited[0] = True
    for _ in range(n - 1):
        cur = route[-1]
        nxt, best = -1, float("inf")
        for j in range(n):
            if not visited[j] and dist[cur][j] < best:
                nxt, best = j, dist[cur][j]
        if nxt == -1:
            break
        route.append(nxt)
        visited[nxt] = True
    return route
