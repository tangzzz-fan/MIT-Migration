# T2 Q4 残差与 LayerNorm 实验（参考解法，仅教练分支，numpy）
# 目标：20 层随机变换，有/无残差的范数曲线；LayerNorm 拉回稳定
import numpy as np

def layer_norm(x, eps=1e-5):
    mean = x.mean(axis=-1, keepdims=True)
    var = x.var(axis=-1, keepdims=True)
    return (x - mean) / np.sqrt(var + eps)

def stack_forward(x, layers, residual):
    norms = [np.linalg.norm(x)]
    for W in layers:
        h = x @ W
        x = x + h if residual else h   # 残差 = 主干道 + 增量修正
        norms.append(np.linalg.norm(x))
    return norms

if __name__ == "__main__":
    rng = np.random.default_rng(4)
    d, L = 16, 20
    x = rng.normal(size=(1, d))
    # 谱半径 >1 的随机层：无残差时范数指数增长（「训不动」的数值化身）
    layers = [rng.normal(size=(d, d)) * 1.2 for _ in range(L)]

    n_plain = stack_forward(x, layers, residual=False)
    n_res = stack_forward(x, layers, residual=True)
    print("层数   无残差范数        有残差范数")
    for i in (0, 5, 10, 15, 20):
        print(f"{i:>3}   {n_plain[i]:>12.2f}   {n_res[i]:>12.2f}")

    # LayerNorm：把爆炸/坍缩的激活拉回零均值单位方差量级
    deep = x
    for W in layers:
        deep = deep @ W
    print(f"\n20 层无残差原始范数: {np.linalg.norm(deep):.2e}")
    print(f"LayerNorm 后范数    : {np.linalg.norm(layer_norm(deep)):.3f}  <- 回到稳定量级")
    # 结论：无残差 → 信息被逐层改写、梯度连乘爆炸/消失；
    # 残差让恒等映射成为默认解，LayerNorm 稳住各层输入分布——两者是可训练性脚手架，不是语义组件。
