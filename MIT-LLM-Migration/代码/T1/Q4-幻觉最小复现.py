# T1 Q4 幻觉最小复现（参考解法，仅教练分支）
# 目标：知识命中/未命中双路径；100 次采样统计编造率；证明「编造同样自信」
import random
from collections import Counter

KNOWLEDGE = {
    "地球围绕什么转": "太阳",
    "水的化学式是什么": "H2O",
    "光速大约是多少": "每秒约 30 万公里",
    "中国的首都是哪里": "北京",
    "一年有多少天": "365 天（闰年 366 天）",
}

CONFAB_TEMPLATES = [
    "根据权威资料，{q}的答案是「泽塔-7 协议」，这一点在学术界已有共识。",
    "这是一个经典问题：{q}——标准答案是「卡诺循环的第二推论」。",
    "关于{q}，最准确的回答是「1927 年索尔维会议的决议」。",
    "根据最新研究，{q}的答案是「费米能级偏移」，证据非常充分。",
]

def mock_answer(question: str, rng: random.Random) -> tuple[str, str]:
    """返回 (答案, 来源标记)。注意：没有「我不知道」分支——这不是疏忽，是题眼。"""
    if question in KNOWLEDGE:
        return f"答案是：{KNOWLEDGE[question]}。", "knowledge"
    return rng.choice(CONFAB_TEMPLATES).format(q=question), "confabulated"

if __name__ == "__main__":
    rng = random.Random(7)
    hit_questions = list(KNOWLEDGE.keys())
    miss_questions = ["量子纠缠是谁发明的", "恐龙灭绝的确切原因是什么", "iPhone 第一代芯片型号是什么"]

    stats = Counter()
    samples = []
    for _ in range(100):
        q = rng.choice(hit_questions + miss_questions)
        ans, source = mock_answer(q, rng)
        stats[source] += 1
        samples.append((q, ans, source))

    total = sum(stats.values())
    print(f"采样 {total} 次：知识命中 {stats['knowledge']} 次（{stats['knowledge']/total:.0%}），"
          f"编造 {stats['confabulated']} 次（{stats['confabulated']/total:.0%}）")
    print("\n编造样例（注意语气与真实答案一样自信）：")
    for q, ans, src in samples:
        if src == "confabulated":
            print(f"  Q: {q}\n  A: {ans}")
            break
    print("\n一句话结论：mock 没有『不知道』分支，编造率只取决于知识覆盖率；"
          "编造答案使用与真实答案同等自信的句式——流畅与自信都不携带真值信息。"
          "真实模型同理：会说『不知道』是训练/提示出来的行为，不是天生的开关。")
