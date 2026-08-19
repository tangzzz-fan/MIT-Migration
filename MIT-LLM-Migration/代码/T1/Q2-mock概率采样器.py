# T1 Q2 mock 概率采样器（参考解法，仅教练分支）
# 目标：greedy / temperature / top-p 三种解码，各 1000 次统计频率，验证三条结论
import random
from collections import Counter

CANDIDATES = {"好": 0.45, "行": 0.25, "可以": 0.15, "也许": 0.10, "不好说": 0.05}

def greedy(dist: dict[str, float]) -> str:
    return max(dist, key=dist.get)

def _normalize(weights: dict[str, float]) -> dict[str, float]:
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}

def sample_temperature(dist: dict[str, float], T: float, rng: random.Random) -> str:
    # temperature 作用在分布形状上：p_i^(1/T) 后重归一化（等价于 logits 除以 T）
    assert T > 0
    shaped = {k: p ** (1.0 / T) for k, p in dist.items()}
    shaped = _normalize(shaped)
    return rng.choices(list(shaped.keys()), weights=list(shaped.values()))[0]

def sample_top_p(dist: dict[str, float], p: float, rng: random.Random) -> str:
    # 降序累积到 >= p 截断（核），核内重归一化后采样
    ranked = sorted(dist.items(), key=lambda kv: kv[1], reverse=True)
    nucleus, acc = [], 0.0
    for k, prob in ranked:
        nucleus.append((k, prob))
        acc += prob
        if acc >= p:
            break
    nucleus_dist = _normalize(dict(nucleus))
    return rng.choices(list(nucleus_dist.keys()), weights=list(nucleus_dist.values()))[0]

def freq_table(samples: list[str]) -> str:
    c = Counter(samples)
    n = len(samples)
    return "  ".join(f"{k}:{c.get(k,0)/n:.3f}" for k in CANDIDATES)

if __name__ == "__main__":
    rng = random.Random(42)
    N = 1000
    print("原始概率      : " + "  ".join(f"{k}:{p:.3f}" for k, p in CANDIDATES.items()))
    print(f"greedy x{N}   : {set(greedy(CANDIDATES) for _ in range(N))}  <- 恒定单一输出")
    for T in (0.5, 1.0, 2.0):
        s = [sample_temperature(CANDIDATES, T, rng) for _ in range(N)]
        print(f"temperature={T}: {freq_table(s)}")
    for p in (0.7, 0.9):
        s = [sample_top_p(CANDIDATES, p, rng) for _ in range(N)]
        print(f"top_p={p}     : {freq_table(s)}")
    # 验证点：
    # 1) greedy 恒定（集合大小为 1）
    # 2) T 越大，低频候选（也许/不好说）频率越高 -> 分布越平
    # 3) p=0.7 时核 = {好, 行, 可以}，「也许/不好说」频率为 0 -> 只在核内采样
