# T6 Q3 结构化 trace（参考解法，仅教练分支）
# 目标：每轮结构化记录 + 表格渲染 + 汇总；注释回答「重复调用怎么查」

class Tracer:
    FIELDS = ("step", "decision", "tool", "args", "status", "tokens", "cum_tokens")

    def __init__(self):
        self.steps = []

    def record(self, step):
        prev = self.steps[-1]["cum_tokens"] if self.steps else 0
        step["cum_tokens"] = prev + step.get("tokens", 0)
        self.steps.append(step)

    def summary(self):
        fails = sum(1 for s in self.steps if s.get("status") == "error")
        return {"total_steps": len(self.steps),
                "total_tokens": self.steps[-1]["cum_tokens"] if self.steps else 0,
                "failures": fails}

    def render(self):
        header = " | ".join(f"{f:>9}" for f in self.FIELDS)
        lines = [header, "-" * len(header)]
        for s in self.steps:
            lines.append(" | ".join(f"{str(s.get(f, ''))[:9]:>9}" for f in self.FIELDS))
        return "\n".join(lines)

def run_task(tracer):
    """mock 4 轮任务：查天气 → 算换算 → 工具报错 → 收尾。"""
    tracer.record({"step": 1, "decision": "tool_call", "tool": "get_temp", "args": "北京", "status": "ok", "tokens": 320})
    tracer.record({"step": 2, "decision": "tool_call", "tool": "convert", "args": "20C->F", "status": "ok", "tokens": 280})
    tracer.record({"step": 3, "decision": "tool_call", "tool": "send_mail", "args": "报告", "status": "error", "tokens": 150})
    tracer.record({"step": 4, "decision": "final_answer", "tool": "-", "args": "-", "status": "ok", "tokens": 210})

if __name__ == "__main__":
    t = Tracer()
    run_task(t)
    print(t.render())
    print("\n汇总:", t.summary())
    # 注释回答 C5：这份 trace 能定位「重复调用」——扫相邻轮的 (tool,args) 指纹，
    # 连续重复 ≥2 次即触发停滞干预；错误轮的 status=error + args 还能区分
    # 「模型没读懂错误」还是「工具一直返回同样的错」。普通日志做不到：
    # trace 是结构化（字段可查询）+ 可回放（能重建决策序列）。
