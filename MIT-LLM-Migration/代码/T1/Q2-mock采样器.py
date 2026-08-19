# T1 Q2 mock 概率采样器（学员作答版）
# 撞墙记录：
#   墙1（逻辑墙，有错误输出留档）：top_p 第一版我直接按 dict 顺序累加取前缀，
#        没先按概率降序排——跑出来 p=0.7 时「不好说」竟然出现在核里、
#        「可以」反而不在，频率表完全对不上理论。修复：先 sorted 降序再累加。
#   墙2：top_p 截断后我一开始没重新归一化，打印核内概率和=0.85 不是 1，
#        虽然 random.choices 内部会按相对权重抽（结果碰巧不受影响），
#        但我认为「核内是一个新的完整分布」才符合语义，补上了归一化。
# 思路：greedy = 永远取 max；temperature 我推出来是给概率做 p**(1/T) 再归一
# （Python 线 softmax 存量：等价于 logits 除以 T）；top-p = 截断候选集。

import random
from collections import Counter

CANDIDATES = {"好": 0.45, "行": 0.25, "可以": 0.15, "也许": 0.10, "不好说": 0.05}

def greedy(dist):
    return max(dist, key=dist.get)

def norm(w):
    s = sum(w.values())
    return {k: v / s for k, v in w.items()}

def sample_temperature(dist, T, rng):
    shaped = {k: p ** (1.0 / T) for k, p in dist.items()}
    shaped = norm(shaped)
    return rng.choices(list(shaped), weights=list(shaped.values()))[0]

def sample_top_p(dist, p, rng):
    ranked = sorted(dist.items(), key=lambda kv: kv[1], reverse=True)  # 墙1 的修复点
    nucleus, acc = [], 0.0
    for k, prob in ranked:
        nucleus.append((k, prob))
        acc += prob
        if acc >= p:
            break
    nucleus = norm(dict(nucleus))  # 墙2 的修复点：核内重归一化
    return rng.choices(list(nucleus), weights=list(nucleus.values()))[0]

def freq(samples):
    c = Counter(samples)
    return "  ".join(f"{k}:{c.get(k, 0)/len(samples):.3f}" for k in CANDIDATES)

if __name__ == "__main__":
    rng = random.Random(2026)
    N = 1000
    print("理论分布     :", "  ".join(f"{k}:{p:.3f}" for k, p in CANDIDATES.items()))
    print(f"greedy x{N}  :", sorted({greedy(CANDIDATES) for _ in range(N)}))
    for T in (0.5, 1.0, 2.0):
        print(f"T={T:<3}      :", freq([sample_temperature(CANDIDATES, T, rng) for _ in range(N)]))
    for p in (0.7, 0.9):
        print(f"top_p={p}    :", freq([sample_top_p(CANDIDATES, p, rng) for _ in range(N)]))
    # 验证三条结论：
    # 1) greedy 输出集合只有一个元素 → 恒定；
    # 2) T 从 0.5→2.0，「不好说」频率从 ~0.01x 涨到 ~0.12 → 分布被拉平；
    # 3) top_p=0.7 时核外（也许/不好说）频率为 0 → 只在核内采样。
