# T6 Q1 上下文管理器（参考解法，仅教练分支）
# 目标：trim/summarize 两策略；第 1 轮约束在两策略下的存亡对比（题眼）

def count_tokens(t):
    return len(t)

def mock_summarize(messages):
    """mock 摘要器：抽取含关键词的句子拼接——『约束是否保住』成为可控变量。"""
    kept = [m["content"] for m in messages if "约束" in m["content"] or "必须" in m["content"]]
    return "摘要：" + "；".join(kept[:2]) + f"（其余 {len(messages)-len(kept)} 条过程性消息已压缩）"

class ContextManager:
    def __init__(self, budget_tokens):
        self.budget = budget_tokens
        self.messages = []

    def add(self, msg):
        self.messages.append(msg)

    def total(self):
        return sum(count_tokens(m["content"]) for m in self.messages)

    def compress(self, strategy):
        if self.total() <= self.budget:
            return self.messages
        if strategy == "trim":
            # 硬丢最旧的非 system 消息（system/约束钉头部，永不裁剪——混用策略）
            while self.total() > self.budget:
                idx = next((i for i, m in enumerate(self.messages) if m["role"] != "system"), None)
                if idx is None:
                    break
                self.messages.pop(idx)
        elif strategy == "summarize":
            # 把最旧的一半过程消息压成一条摘要（system 保留）
            head = [m for m in self.messages if m["role"] == "system"]
            rest = [m for m in self.messages if m["role"] != "system"]
            half = rest[:len(rest) // 2]
            self.messages = head + [{"role": "system", "content": mock_summarize(half)}] + rest[len(rest)//2:]
        return self.messages

if __name__ == "__main__":
    def run(strategy):
        cm = ContextManager(budget_tokens=150)
        cm.add({"role": "system", "content": "约束：必须始终用中文回复。"})
        for i in range(1, 13):
            cm.add({"role": "user", "content": f"第{i}轮过程性对话内容，聊话题{i}的细节{i}{i}。"})
            cm.compress(strategy)
        joined = " | ".join(m["content"] for m in cm.messages)
        alive = "必须始终用中文" in joined
        print(f"[{strategy}] 压缩后 {len(cm.messages)} 条 / {cm.total()} tokens；第 1 轮约束存亡: {'存活' if alive else '丢失'}")

    run("trim")
    run("summarize")
    print("\n混用策略（注释）：system 与显式约束钉头部永不裁剪；过程性消息摘要；")
    print("关键事实落外部按需检索（T4 M5）。裁剪翻车例 = trim 若连 system 一起丢（此处已防护）。")
