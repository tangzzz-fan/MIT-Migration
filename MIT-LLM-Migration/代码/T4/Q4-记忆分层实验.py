# T4 Q4 记忆分层实验（参考解法，仅教练分支）
# 目标：A 纯上下文（带窗口）vs B 上下文+外挂记忆；第 11 轮问偏好见分晓

def count_tokens(t):
    return len(t)

class MemoryStore:
    """外挂长期记忆（KV 版）。真实系统里对应：记忆抽取器 + 向量库/DB。"""
    def __init__(self):
        self.store = {}
    def write(self, key, value):
        self.store[key] = value
    def retrieve(self, query, k=1):
        # mock 检索：键包含查询关键词即命中
        hits = [(k, v) for k, v in self.store.items() if any(w in k for w in query.split())]
        return hits[:k]

def windowed_reply(history, user_msg, window=120, memory=None):
    """写回触发条件（mock）：消息含『偏好』关键词 → 存入外挂记忆（对应真实系统的记忆抽取）。"""
    if memory is not None and "偏好" in user_msg:
        memory.write("用户偏好", user_msg)
    msgs = history + [user_msg]
    total, i = sum(count_tokens(m) for m in msgs), 0
    while total > window and i < len(msgs) - 1:
        total -= count_tokens(msgs[i]); i += 1
    visible = msgs[i:]
    if "偏好" in user_msg and "什么" in user_msg:
        for m in visible:
            if "偏好" in m and "什么" not in m:
                return f"（上下文命中）你的偏好是：{m[:20]}"
        if memory is not None:
            hits = memory.retrieve("偏好")
            if hits:
                return f"（外挂记忆命中）你的偏好是：{hits[0][1][:20]}"
        return "我不记得你的偏好了。"
    return f"收到：{user_msg[:8]}…"

if __name__ == "__main__":
    script = ["我的偏好是深色模式和紧凑布局，请记住这个偏好。"] + \
             [f"第{i}轮闲聊：聊点关于话题{i}的内容和背景{i}。" for i in range(2, 11)] + \
             ["我的偏好是什么？"]
    for name, memory in [("A 纯上下文", None), ("B 上下文+外挂记忆", MemoryStore())]:
        history = []
        answer = None
        for i, m in enumerate(script, start=1):
            reply = windowed_reply(history, m, memory=memory)
            history += [m, reply]
            if i == len(script):
                answer = reply
        print(f"[{name}] 第 {len(script)} 轮回答: {answer}")
    print("\n结论：A 的偏好被挤出窗口后遗忘；B 靠写回（记忆抽取）+检索在新轮次找回。")
    print("组件对应：写回触发=记忆抽取器；MemoryStore=向量库/DB；retrieve=按需检索回填上下文。")
    print("断裂处：上下文清零是设计不是 bug——LLM 的持久化完全靠外挂（T4 C5）。")
