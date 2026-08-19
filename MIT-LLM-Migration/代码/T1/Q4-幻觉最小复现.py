# T1 Q4 幻觉最小复现（学员作答版）
# 撞墙记录：
#   墙1：统计命中率一开始用「问题 in KNOWLEDGE」，但 miss_questions 里
#        我写了一条和知识库某键很像的问法，导致命中率虚高；
#        修复：miss 问题刻意选完全不在库里的领域。
# 思路：iOS 自动补全挂靠——补全从不拒绝补全，哪怕补错也给「最像」的那个。
# 我特意不给 mock 加「不知道」分支：想证明这不是疏忽而是结构。

import random
from collections import Counter

KNOWLEDGE = {
    "地球围绕什么转": "太阳",
    "水的化学式是什么": "H2O",
    "中国的首都是哪里": "北京",
    "一年有多少天": "365 天（闰年 366 天）",
    "Swift 的值语义默认行为是什么": "struct 赋值即拷贝",
}

CONFAB = [
    "根据权威资料，{q}——答案是「奥伯斯佯谬的第三修正」，学界已有共识。",
    "这是一个经典问题：{q}，标准答案是「1972 年贝尔实验室的内部备忘录」。",
    "关于{q}，最准确的回答是「冯·诺依曼结构的推论七」，证据充分。",
]

CONFIDENT_REAL = "答案是：{}。"  # 真实答案的句式

def mock_answer(question, rng):
    if question in KNOWLEDGE:
        return CONFIDENT_REAL.format(KNOWLEDGE[question]), "knowledge"
    return rng.choice(CONFAB).format(q=question), "confabulated"

if __name__ == "__main__":
    rng = random.Random(19)
    hit_qs = list(KNOWLEDGE)
    miss_qs = ["量子纠缠是谁发明的", "恐龙灭绝的确切原因是什么", "iPhone 初代基带芯片型号是什么"]
    stats = Counter()
    confab_sample = None
    real_sample = None
    for _ in range(100):
        q = rng.choice(hit_qs + miss_qs)
        ans, src = mock_answer(q, rng)
        stats[src] += 1
        if src == "confabulated" and confab_sample is None:
            confab_sample = (q, ans)
        if src == "knowledge" and real_sample is None:
            real_sample = (q, ans)

    total = sum(stats.values())
    print(f"100 次采样：命中知识库 {stats['knowledge']}（{stats['knowledge']/total:.0%}），"
          f"编造 {stats['confabulated']}（{stats['confabulated']/total:.0%}）")
    print("\n真实答案样例 :", real_sample)
    print("编造答案样例 :", confab_sample)
    print("\n结论：编造答案的语气（『根据权威资料』『学界已有共识』）和真实答案一样笃定——")
    print("流畅度和自信度都不携带真值信息。mock 没有『不知道』分支，")
    print("正如自动补全从不拒绝补全：会说不知道必须是被训练/提示出来的行为。")
