# T1 Q3 上下文窗口实验（学员作答版）
# 撞墙记录：
#   墙1：budget_report 一开始把「回复」也算进 history 再判断截断，
#        导致第 4 轮就显示 will_truncate=True，和 chat 的实际行为对不上；
#        修复：budget 只统计「下一次请求要带上的历史」。
# 思路：HTTP 无状态挂靠——每次请求带全历史；窗口 = 这一次请求的内存上限。
# 截断策略我选「丢最旧的」（保留最近），和 LRU 淘汰一个直觉。

def count_tokens(text):
    return len(text)  # mock：一字一 token

class MockWindowedModel:
    def __init__(self, window_tokens):
        self.window = window_tokens

    def chat(self, history, user_msg):
        """返回 (回复, 被丢弃的消息)。丢弃 = 模型看不见的部分。"""
        msgs = history + [user_msg]
        total = sum(count_tokens(m) for m in msgs)
        dropped = []
        i = 0
        while total > self.window and i < len(msgs) - 1:  # 至少保住当前提问
            dropped.append(msgs[i])
            total -= count_tokens(msgs[i])
            i += 1
        visible = msgs[i:]

        if "我叫什么" in user_msg:
            for m in visible:
                if "我叫" in m and "什么" not in m:
                    name = m.split("我叫")[-1].strip("，。 ")
                    return f"你叫{name}。（我还能看到这条信息）", dropped
            return "我不记得你叫什么了。（这条信息不在我这次的输入里）", dropped
        return f"[收到] {user_msg[:6]}…（本次可见 {len(visible)}/{len(msgs)} 条）", dropped

def budget_report(history, window_tokens):
    total = sum(count_tokens(m) for m in history)
    return {"total_tokens": total,
            "remaining_budget": max(0, window_tokens - total),
            "will_truncate": total > window_tokens}

if __name__ == "__main__":
    model = MockWindowedModel(window_tokens=180)
    history = []
    msgs = ["我叫王小明，请记住我的名字。"] + \
           [f"第{i}轮：聊一下话题{i}的最新进展和背景资料{i}。" for i in range(2, 10)]
    for i, m in enumerate(msgs, start=1):
        reply, dropped = model.chat(history, m)
        history += [m, reply]
        print(f"[轮{i}] 预算: {budget_report(history, 180)}")
        if dropped:
            print(f"[轮{i}] 被丢弃 {len(dropped)} 条，最早一条是: {dropped[0][:14]}…")
        if i in (3, 6, 9):
            probe, d2 = model.chat(history, "我叫什么？")
            print(f"[轮{i}] 抽查『我叫什么』: {probe}")
    # 观察点：前期答得出名字，名字消息被挤出窗口后开始「失忆」——
    # 遗忘发生的轮次 = 名字消息被丢弃的轮次，完全由窗口预算决定。
