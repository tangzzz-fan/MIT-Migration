# T5 Q4 workflow vs agent 对拍（参考解法，仅教练分支）
# 目标：同任务两版实现；轨迹对比；三维度记账

WEATHER = {"北京": 20, "上海": 26}

def workflow_version(cities):
    """A：代码写死调用顺序——路径固定、可预测、可单测。"""
    trace = []
    results = {}
    for c in cities:                      # 步骤 1：逐个查询（写死）
        trace.append(f"步骤: 查询 {c}")
        results[c] = WEATHER[c]
    a, b = cities                          # 步骤 2：比较（写死）
    trace.append(f"步骤: 比较 {a} 与 {b}")
    winner = a if results[a] > results[b] else b
    return {"answer": f"{winner} 更暖和", "trace": trace}

def agent_version(task):
    """B：模型决策循环——路径由 mock 决策产生（用 Q2 的循环骨架）。"""
    from importlib import import_module  # 实际使用时复用 Q2；这里内联简化版
    observations, trace = [], []
    cities = [c for c in WEATHER if c in task]
    for c in cities:
        trace.append(f"决策: 模型决定先查 {c}（依据任务文本）")
        observations.append(WEATHER[c])
    trace.append("决策: 模型认为信息足够，输出比较结论")
    winner = cities[0] if observations[0] > observations[1] else cities[1]
    return {"answer": f"{winner} 更暖和", "trace": trace}

if __name__ == "__main__":
    task = "北京和上海哪个更暖和"
    for name, fn in [("A workflow", lambda: workflow_version(["北京", "上海"])),
                     ("B agent", lambda: agent_version(task))]:
        r = fn()
        print(f"[{name}] 答案: {r['answer']}")
        for t in r["trace"]:
            print("   ", t)
        print()

# 记账（问题-约束-代价，三维度）：
# 路径灵活性：A 只能跑写死的城市序列；B 可应对任务措辞变化（新增城市不用改代码）
# 失败模式：A 只有执行错（城市不在表里）；B 多了决策错（查错城市、提前收尾、绕圈）
# 可测试性：A 每步可断言；B 要测行为分布（多次采样看路径稳定性）→ eval（T6 伏笔）
# 结论：报销流程这类『步骤固定+需审计』选 A；开放式研究任务选 B；
#      多数现实系统 = workflow 骨架 + 局部 agent 节点（M5）。
