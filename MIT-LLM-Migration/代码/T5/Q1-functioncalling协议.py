# T5 Q1 function calling 协议（参考解法，仅教练分支）
# 目标：schema 声明 + mock 模型发调用 + 校验拦截 + 执行；非法参数用例

TOOLS = [
    {"name": "get_weather",
     "description": "查询指定城市的当前天气。只支持城市名，不能查区县。",
     "parameters": {"city": {"type": "str", "required": True}}},
    {"name": "add",
     "description": "计算两个整数之和。",
     "parameters": {"a": {"type": "int", "required": True}, "b": {"type": "int", "required": True}}},
]

def mock_model_call(task):
    """模型只『提议』调用（结构化 dict），从不直接执行。"""
    if "天气" in task:
        city = task.split("天气")[0].replace("查", "").strip() or "北京"
        return {"tool": "get_weather", "args": {"city": city}}
    if "加" in task or "求和" in task:
        return {"tool": "add", "args": {"a": 3, "b": 5}}
    return {"tool": None, "args": {}}

def validate_call(call):
    schema = next((t for t in TOOLS if t["name"] == call.get("tool")), None)
    if schema is None:
        return [f"工具 {call.get('tool')} 未注册（白名单拦截，可能是模型幻觉）"]
    errors = []
    for pname, spec in schema["parameters"].items():
        val = call["args"].get(pname)
        if val is None and spec["required"]:
            errors.append(f"缺少必填参数 {pname}")
        elif val is not None and spec["type"] == "int" and not isinstance(val, int):
            errors.append(f"参数 {pname} 类型应为 int，实得 {type(val).__name__}")
    return errors

def execute(call):
    if call["tool"] == "get_weather":
        return f"{call['args']['city']}：晴，22°C"
    if call["tool"] == "add":
        return str(call["args"]["a"] + call["args"]["b"])
    raise ValueError("未注册工具")

if __name__ == "__main__":
    for task in ["查北京天气", "求和"]:
        call = mock_model_call(task)
        errors = validate_call(call)
        print(f"任务: {task}\n  模型提议: {call}\n  校验: {errors or '通过'}\n  执行: {execute(call) if not errors else '拦截'}\n")
    # 非法参数用例：模型幻觉出错误类型
    bad = {"tool": "add", "args": {"a": "三", "b": 5}}
    errors = validate_call(bad)
    print(f"非法用例: {bad}\n  校验: {errors}\n  观察回填: {'错误: ' + '; '.join(errors)}  <- 给模型看的观察（Q3 铺垫）")
