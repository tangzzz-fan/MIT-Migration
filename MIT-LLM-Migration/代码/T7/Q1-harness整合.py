# T7 Q1 组件整合：单一入口 mini-harness（参考解法，仅教练分支）
# 六组件装配：LLM 适配器 / 工具注册表 / agent 循环 / 上下文管理 / 权限闸门 / trace
# mock 是一等公民：MockLLM 与未来的 RealLLM 实现同一接口，其余组件不感知

WEATHER = {"北京": 20, "上海": 26, "广州": 30}
DANGEROUS = {"delete_file"}

class LLMAdapter:
    """接口：complete(messages) -> 结构化决策（工具调用 or 最终答案）。"""
    def complete(self, messages):
        raise NotImplementedError

class MockLLM(LLMAdapter):
    def __init__(self, broken_descriptions=False):
        self.broken = broken_descriptions  # T7 Q3 回归注入用
    def complete(self, messages):
        task = next(m["content"] for m in messages if m["role"] == "user")
        seen = [m for m in messages if m["role"] == "tool"]
        obs = " ".join(m["content"] for m in seen)
        if "删除" in task and not self.broken:
            return {"call": {"tool": "delete_file", "args": {"path": "/workspace/tmp/x.log"}}}
        for city in WEATHER:
            if city in task and f"{city}=" not in obs:
                return {"call": {"tool": "get_temp", "args": {"city": city}}}
        temps = [seg for seg in obs.split() if "=" in seg]
        if len(temps) >= task.count("和") + 1 and "比较" in task:
            return {"final": f"比较结果：{', '.join(temps)}，较暖的是 {max(temps, key=lambda s: int(s.split('=')[1]))}"}
        if temps:
            return {"final": f"查询结果：{', '.join(temps)}"}
        return {"final": "信息不足，无法完成"}

class ToolRegistry:
    """声明式注册表：新工具 = 注册 schema + handler，循环零改动（M3）。"""
    def __init__(self):
        self.tools = {}
    def register(self, schema, handler):
        self.tools[schema["name"]] = {"schema": schema, "handler": handler}
    def execute(self, call):
        entry = self.tools.get(call["tool"])
        if entry is None:
            return f"错误: 工具 {call['tool']} 未注册"
        return entry["handler"](**call["args"])

class ContextManager:
    def __init__(self, budget=800):
        self.budget, self.messages = budget, []
    def add(self, msg):
        self.messages.append(msg)
        while sum(len(m["content"]) for m in self.messages) > self.budget and len(self.messages) > 2:
            self.messages.pop(1)  # 保留 system 与最新输入

class PermissionGate:
    def check(self, call):
        if call["tool"] in DANGEROUS:
            return False, f"闸门拦截：{call['tool']} 是危险操作，需人工确认"
        return True, "放行"

class Tracer:
    def __init__(self):
        self.steps = []
    def record(self, **kw):
        self.steps.append(kw)
    def summary(self):
        return {"steps": len(self.steps), "tokens": sum(s.get("tokens", 0) for s in self.steps)}

class Harness:
    def __init__(self, llm, registry, gate, ctx, tracer, max_steps=6):
        self.llm, self.registry, self.gate, self.ctx, self.tracer, self.max_steps = llm, registry, gate, ctx, tracer, max_steps
    def run(self, task):
        print(f"[装配] Harness <- LLM适配器({type(self.llm).__name__}) + 工具注册表({len(self.registry.tools)}个) + 循环 + 上下文管理 + 权限闸门 + trace")
        self.ctx.add({"role": "user", "content": task})
        for step in range(1, self.max_steps + 1):
            decision = self.llm.complete(self.ctx.messages)
            if "final" in decision:
                self.tracer.record(step=step, decision="final", tokens=90)
                return {"answer": decision["final"], "trace": self.tracer.steps}
            call = decision["call"]
            ok, reason = self.gate.check(call)
            if not ok:
                self.tracer.record(step=step, decision="blocked", tool=call["tool"], tokens=40)
                self.ctx.add({"role": "tool", "content": reason})
                continue
            result = self.registry.execute(call)
            self.ctx.add({"role": "tool", "content": f"{call['args'].get('city', call['args'])}={result}" if isinstance(result, int) else str(result)})
            self.tracer.record(step=step, decision="tool_call", tool=call["tool"], tokens=120)
        return {"answer": "达到最大轮数", "trace": self.tracer.steps}

def build_harness(**llm_kwargs):
    reg = ToolRegistry()
    reg.register({"name": "get_temp", "description": "查询城市气温", "parameters": {"city": "str"}},
                 lambda city: WEATHER.get(city, "未知城市"))
    reg.register({"name": "delete_file", "description": "删除文件（危险）", "parameters": {"path": "str"}},
                 lambda path: f"已删除 {path}")
    return Harness(MockLLM(**llm_kwargs), reg, PermissionGate(), ContextManager(), Tracer())

if __name__ == "__main__":
    h = build_harness()
    r = h.run("查北京气温")
    print("答案:", r["answer"])
    for s in r["trace"]:
        print("  trace:", s)
