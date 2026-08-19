# T5 Q2 ReAct 循环最小实现（参考解法，仅教练分支）
# 目标：思考/行动/观察三段式 trace；双终止条件；断言轮数

def mock_decision(task, observations):
    """mock 模型决策：按任务关键词 + 已见观察推进（重点在循环骨架不在 mock 智能）。"""
    temps = {o["city"]: o["temp"] for o in observations if "temp" in o}
    if "北京" in task and "北京" not in temps:
        return {"thought": "需要先查北京气温", "action": {"tool": "get_temp", "city": "北京"}}
    if "上海" in task and "上海" not in temps:
        return {"thought": "还需要上海气温", "action": {"tool": "get_temp", "city": "上海"}}
    if len(temps) >= 2:
        diff = temps["北京"] - temps["上海"]
        return {"thought": "两地都查到了，可以比较", "final": f"北京比上海{'高' if diff>0 else '低'}{abs(diff)}°C"}
    return {"thought": "信息不足", "final": "无法完成"}

def mock_tool(action):
    return {"city": action["city"], "temp": {"北京": 20, "上海": 26}[action["city"]]}

def react_loop(task, max_steps=5):
    observations, trace = [], []
    for step in range(1, max_steps + 1):
        decision = mock_decision(task, observations)
        trace.append({"step": step, "thought": decision["thought"],
                      "action": decision.get("action") or "最终答案"})
        if "final" in decision:
            return {"answer": decision["final"], "trace": trace, "steps": step}
        obs = mock_tool(decision["action"])
        observations.append(obs)               # 观察回填 = 循环的燃料（M3）
        trace[-1]["observation"] = obs
    return {"answer": "达到最大轮数，未完成", "trace": trace, "steps": max_steps}

if __name__ == "__main__":
    result = react_loop("比较北京和上海的气温")
    for t in result["trace"]:
        print(t)
    print(f"\n最终答案: {result['answer']}（共 {result['steps']} 步）")
    assert result["steps"] == 3, "预期：查北京→查上海→比较，恰好 3 步"
    print("断言通过：循环在最终答案处终止；max_steps 是另一条保险丝（M4）。")
