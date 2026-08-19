# T4 Q1 语义检索 vs 关键词检索（参考解法，仅教练分支）
# 目标：同义改写例（语义中、关键词空）+ 精确编号反例（关键词中、语义漂移）
import math

DOCS = [
    "缓解焦虑的方法与日常减压技巧",
    "如何管理压力并放松身心",
    "错误码 ERR_7721 的处理流程",
    "数据库连接池调优实践",
    "UITableView 滚动性能优化指南",
    "睡眠质量改善建议",
]
# mock 句向量：语义轴 [健康心理, 工程运维, 移动性能, 精确标识]
DOC_VECTORS = {
    0: [0.9, 0.0, 0.0, 0.0], 1: [0.85, 0.0, 0.0, 0.0],
    2: [0.0, 0.9, 0.0, 0.8], 3: [0.0, 0.9, 0.1, 0.1],
    4: [0.0, 0.1, 0.9, 0.0], 5: [0.7, 0.0, 0.1, 0.0],
}
QUERY_VECS = {
    "如何减轻心理负担": [0.88, 0.0, 0.0, 0.0],   # 与 0/1 零字重叠但语义近
    "ERR_7721":          [0.0, 0.5, 0.0, 0.9],   # 精确标识符
}

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))

def semantic_search(query_vec, k=2):
    ranked = sorted(DOC_VECTORS, key=lambda i: cosine(DOC_VECTORS[i], query_vec), reverse=True)
    return [(i, DOCS[i], round(cosine(DOC_VECTORS[i], query_vec), 3)) for i in ranked[:k]]

def keyword_search(query, k=2):
    hits = [(i, d) for i, d in enumerate(DOCS) if query in d]
    return hits[:k]

if __name__ == "__main__":
    q1 = "如何减轻心理负担"
    print(f"[例1 同义改写] 查询：{q1}")
    print("  语义检索:", [(d, s) for _, d, s in semantic_search(QUERY_VECS[q1])])
    print("  关键词检索:", keyword_search(q1) or "空（零字重叠，失联）")

    q2 = "ERR_7721"
    print(f"\n[例2 精确编号] 查询：{q2}")
    print("  关键词检索:", [d for _, d in keyword_search(q2)])
    print("  语义检索:", [(d, s) for _, d, s in semantic_search(QUERY_VECS[q2])], "<- 可能漂到邻近工程文档")
    print("\n结论：语义检索认内容（改写不失配），关键词认字面（标识符最稳）——混合检索的动机（D3）。")
    print("对照指针：MIT-Python-Migration/代码/T8/（8.1 余弦检索，对拍用）")
