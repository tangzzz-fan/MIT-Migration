# T5 Q3 错误恢复实验（参考解法，仅教练分支）
# 目标：故障注入；A 失败即崩 vs B 错误回填重试；熔断边界讨论

class FlakyTool:
    """前 fail_times 次调用必失败。"""
    def __init__(self, fail_times=1):
        self.fail_left = fail_times
        self.calls = 0
    def run(self, city):
        self.calls += 1
        if self.fail_left > 0:
            self.fail_left -= 1
            return None, "错误: 上游服务超时（可重试）"
        return {"city": city, "temp": 22}, None

def strategy_A(task, tool):
    """失败即崩：错误不进上下文，循环直接死。"""
    result, err = tool.run("北京")
    if err:
        raise RuntimeError(f"崩溃于第 {tool.calls} 次调用: {err}")
    return f"答案: {result}"

def strategy_B(task, tool, max_steps=4):
    """错误回填：把错误作为观察给『模型』，模型决策重试。"""
    observations = []
    for step in range(1, max_steps + 1):
        result, err = tool.run("北京")
        if err:
            observations.append(f"观察: {err} → 决策: 换备用线路重试")  # mock 模型的恢复决策
            continue
        return {"answer": f"答案: {result}", "trace": observations, "steps": step}
    return {"answer": "重试预算耗尽", "trace": observations, "steps": max_steps}

if __name__ == "__main__":
    try:
        strategy_A("查北京天气", FlakyTool())
    except RuntimeError as e:
        print(f"[A 失败即崩] {e}")
    r = strategy_B("查北京天气", FlakyTool())
    print(f"[B 错误回填] {r['answer']}（{r['steps']} 步）")
    for line in r["trace"]:
        print("   ", line)
    print("\n熔断边界（注释回答）：『可重试』错误（超时/限流）走 B；")
    print("鉴权失败、配额耗尽、同一错误连续重复 → 熔断退出或上报人工，")
    print("不让模型无限试（M4 停滞检测 + T6 权限闸门前哨）。")
