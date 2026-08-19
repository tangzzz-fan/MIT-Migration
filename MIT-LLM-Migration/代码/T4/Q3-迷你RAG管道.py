# T4 Q3 迷你 RAG 管道（参考解法，仅教练分支）
# 目标：五环中间产物全打印；库内照实、库外编造（两种幻觉路径）
import math, random

CORPUS = [
    "公司报销制度：差旅费需在结束后三十天内提交，超期不予受理。",
    "年假规则：入职满一年享五天年假，每多一年加一天，上限十五天。",
    "设备申领：新员工入职首周可申请笔记本，需部门负责人审批。",
]
# mock 句向量：[报销, 年假, 设备]
CORPUS_VECS = [[0.9, 0.0, 0.0], [0.0, 0.9, 0.0], [0.0, 0.0, 0.9]]
QUERY_VECS = {
    "出差费用多久内报销": [0.85, 0.0, 0.0],
    "工作满三年几天年假": [0.0, 0.8, 0.0],
    "新员工怎么领电脑":   [0.0, 0.0, 0.85],
    "办公室咖啡机在哪":   [0.3, 0.3, 0.3],   # 库外
    "期权行权价多少":     [0.2, 0.2, 0.2],   # 库外
}

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))

def mock_generate(context_chunks, query, rng):
    """生成环规则：上下文含答案关键句 → 照实；否则按 T1 Q4 方式编造并标记。"""
    joined = "".join(context_chunks)
    if "三十天" in joined or "年假" in joined or "笔记本" in joined:
        return f"根据公司制度：{joined[:40]}…", "grounded"
    return f"根据权威资料，{query}的答案是「泽塔-7 协议」，学界已有共识。", "confabulated"

def rag_pipeline(query, k=2):
    qv = QUERY_VECS[query]
    retrieval = sorted(range(len(CORPUS)), key=lambda i: cosine(CORPUS_VECS[i], qv), reverse=True)[:k]
    chunks = [CORPUS[i] for i in retrieval]
    prompt_ctx = f"参考资料：\n" + "\n".join(f"- {c}" for c in chunks)
    return {"环1切分": f"{len(CORPUS)} 块入库", "环2向量化": "mock 句向量",
            "环3检索": [(i, round(cosine(CORPUS_VECS[i], qv), 3)) for i in retrieval],
            "环4组装": prompt_ctx.replace("\n", " | "),
            "环5生成": None}

if __name__ == "__main__":
    rng = random.Random(9)
    for q in QUERY_VECS:
        r = rag_pipeline(q)
        ans, src = mock_generate([CORPUS[i] for i, _ in r["环3检索"]], q, rng)
        r["环5生成"] = f"[{src}] {ans[:50]}"
        print(f"查询: {q}")
        for stage, val in r.items():
            print(f"  {stage}: {val}")
        print()
    print("失败路径对照：库外查询 → 检索到不相关块 → 生成环编造（检索失败与知识缺失殊途同归，")
    print("但定位方式不同：看环3相似度分数即可区分，见 C3 排查顺序）。")
    print("对照指针：MIT-Python-Migration/代码/T8/（8.3 迷你 RAG，对拍用）")
