# T1 Q3 上下文窗口实验（参考解法，仅教练分支）
# 目标：超窗按「保留最近」截断（丢弃可见）；token 预算计算器；10 轮对话演示遗忘

def count_tokens(text: str) -> int:
    """mock tokenizer：字符级，一字一 token。"""
    return len(text)

class MockWindowedModel:
    def __init__(self, window_tokens: int):
        self.window_tokens = window_tokens

    def chat(self, history: list[str], user_msg: str) -> tuple[str, list[str]]:
        """返回 (回复, 被截断丢弃的消息)。模型只能看到窗口内的历史。"""
        messages = history + [user_msg]
        kept, dropped, total = [], [], 0
        # 从最新消息向前保留，直到窗口用尽（保留最近策略）
        for msg in reversed(messages):
            cost = count_tokens(msg)
            if total + cost <= self.window_tokens:
                kept.append(msg)
                total += cost
            else:
                dropped.append(msg)
        visible = list(reversed(kept))

        # mock 回复规则：若用户问「我叫什么」，只从窗口内可见的历史里找答案
        if "我叫什么" in user_msg:
            for msg in visible:
                if "我叫" in msg and "什么" not in msg:
                    name = msg.split("我叫")[-1].strip("，。 ")
                    return f"你叫{name}。（该信息仍在窗口内）", dropped
            return "抱歉，我不知道你叫什么。（该信息已不在窗口内）", dropped
        return f"收到：{user_msg[:8]}…（当前可见 {len(visible)}/{len(messages)} 条消息）", dropped

def budget_report(history: list[str], window_tokens: int) -> dict:
    total = sum(count_tokens(m) for m in history)
    return {
        "total_tokens": total,
        "remaining_budget": max(0, window_tokens - total),
        "will_truncate": total > window_tokens,
    }

if __name__ == "__main__":
    model = MockWindowedModel(window_tokens=200)
    history: list[str] = []
    scripts = ["我叫小明，请记住我的名字。"] + [f"第{i}轮闲聊：今天聊点关于话题{i}的内容，顺便介绍一下背景{i}。" for i in range(2, 10)]
    for i, msg in enumerate(scripts, start=1):
        reply, dropped = model.chat(history, msg)
        history.append(msg)
        history.append(reply)
        print(f"[轮{i}] 预算:{budget_report(history, 200)}")
        if dropped:
            print(f"[轮{i}] 被丢弃: {dropped}")
        # 每 3 轮抽查一次「我叫什么」
        if i in (3, 6, 9):
            probe, d2 = model.chat(history, "我叫什么？")
            print(f"[轮{i}] 抽查: {probe}" + (f"（丢弃:{d2}）" if d2 else ""))
    # 观察点：前期抽查能答出「小明」，后期窗口挤出早期消息后答不出 -> 遗忘发生的具体轮次
