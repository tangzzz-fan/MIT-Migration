# T2 Q3 因果 mask 验证（参考解法，仅教练分支，numpy）
# 目标：有/无 mask 权重对比；扰动实验证明「位置 0 看不到未来」
import numpy as np

def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)

def causal_mask(n):
    # 注意：不能用 triu(ones) * -inf（0 * -inf = NaN）——这是本参考实现撞过的墙，留档
    future = np.triu(np.ones((n, n)), k=1).astype(bool)
    return np.where(future, -np.inf, 0.0)  # 上三角 = 未来位置

def attention_with_mask(X, Wq, Wk, Wv, mask=None):
    d = X.shape[1]
    Q, K, V = X @ Wq, X @ Wk, X @ Wv
    scores = Q @ K.T / np.sqrt(d)
    if mask is not None:
        scores = scores + mask
    return softmax(scores, axis=1) @ V, softmax(scores, axis=1)

if __name__ == "__main__":
    rng = np.random.default_rng(3)
    n, d = 4, 8
    X = rng.normal(size=(n, d))
    Wq = rng.normal(size=(d, d)); Wk = rng.normal(size=(d, d)); Wv = rng.normal(size=(d, d))

    out_free, w_free = attention_with_mask(X, Wq, Wk, Wv)
    out_causal, w_causal = attention_with_mask(X, Wq, Wk, Wv, causal_mask(n))
    print("无 mask 权重（位置 0 能看全部）:\n", np.round(w_free[0], 3))
    print("因果 mask 权重（位置 0 只能看自己）:\n", np.round(w_causal[0], 3))

    # 扰动实验：只改最后一个位置的输入，观察位置 0 的输出
    X2 = X.copy(); X2[-1] += 10.0
    d_free = np.abs(attention_with_mask(X2, Wq, Wk, Wv)[0][0] - out_free[0]).max()
    d_causal = np.abs(attention_with_mask(X2, Wq, Wk, Wv, causal_mask(n))[0][0] - out_causal[0]).max()
    print(f"\n扰动未来位置后，位置 0 输出的最大变化：")
    print(f"  无 mask : {d_free:.6f}  <- 被未来影响（非 0）")
    print(f"  因果mask: {d_causal:.6f}  <- 看不到未来（= 0）")
    assert d_free > 1e-6 and d_causal < 1e-9, "mask 语义验证失败"
    print("断言通过：因果 mask 保证位置 0 对未来扰动完全免疫")
