# T2 Q2 单头自注意力（参考解法，仅教练分支，numpy）
# 目标：QKV 生成 + √d 缩放 + softmax 行归一 + 加权求和；解释权重矩阵第 i 行
import numpy as np

def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)  # 数值稳定（Python 线 T3 softmax 存量）
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)

def attention(X, Wq, Wk, Wv):
    """返回 (输出, 权重矩阵)。X: (n, d)"""
    d = X.shape[1]
    Q, K, V = X @ Wq, X @ Wk, X @ Wv
    scores = Q @ K.T / np.sqrt(d)     # √d 缩放（T2 C3：防 softmax 饱和）
    weights = softmax(scores, axis=1)  # 每行 = 该位置对所有位置的注意力分配
    return weights @ V, weights

if __name__ == "__main__":
    rng = np.random.default_rng(2)
    n, d = 4, 8
    X = rng.normal(size=(n, d))
    Wq = rng.normal(size=(d, d)); Wk = rng.normal(size=(d, d)); Wv = rng.normal(size=(d, d))

    out, weights = attention(X, Wq, Wk, Wv)
    assert np.allclose(weights.sum(axis=1), 1.0), "行和必须为 1"
    print("注意力权重矩阵（行 i = 位置 i 对所有位置的分配）:")
    print(np.round(weights, 3))
    print(f"输出形状: {out.shape}（每个位置的输出 = 全体 V 的加权和）")
    # 对照指针：MIT-Python-Migration/代码/T9/ 9.2 自注意力 numpy 版（对拍用）
