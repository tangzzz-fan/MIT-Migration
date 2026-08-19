# T2 Q1 embedding 直觉实验（参考解法，仅教练分支）
# 目标：查表 + 余弦相似度；相近词 vs 无关词对比；玩具版向量类比
import math

# 手写 6 维向量，三个语义轴：[生物性, 宠物性, 机械性, 尺寸, 速度, 亲和度]
VOCAB = {
    "猫":   [0.9, 0.9, 0.0, 0.2, 0.5, 0.8],
    "狗":   [0.9, 0.9, 0.0, 0.4, 0.6, 0.9],
    "兔子": [0.9, 0.7, 0.0, 0.1, 0.6, 0.7],
    "汽车": [0.0, 0.0, 0.9, 0.7, 0.8, 0.1],
    "卡车": [0.0, 0.0, 0.9, 0.9, 0.6, 0.1],
    "自行车":[0.0, 0.1, 0.6, 0.3, 0.4, 0.5],
    "石头": [0.0, 0.0, 0.1, 0.3, 0.0, 0.0],
}

def lookup(word):
    return VOCAB[word]

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)

if __name__ == "__main__":
    pairs = [("猫", "狗"), ("猫", "兔子"), ("猫", "汽车"), ("汽车", "卡车"), ("狗", "石头")]
    for x, y in pairs:
        print(f"cos({x},{y}) = {cosine(lookup(x), lookup(y)):.3f}")
    # 期望：相近词（猫-狗、汽车-卡车）明显高于无关词（猫-汽车、狗-石头）

    # 玩具版向量类比：宠物 = 生物轴高+机械轴低；车 = 相反。
    # 构造「目标 = 猫 - 宠物特征 + 机械特征」的算术：
    target = [VOCAB["猫"][i] - VOCAB["兔子"][i] + VOCAB["汽车"][i] for i in range(6)]
    best = max(VOCAB, key=lambda w: cosine(VOCAB[w], target))
    print(f"\n类比实验：猫 - 兔子 + 汽车 ≈ {best}（向量算术落到机械区）")
    # 结论写在这里：坐标是人（训练）定的语义轴投影——
    # 真实模型的坐标由训练目标挤出来，维度上万，但「相近=近邻」的几何同构。
