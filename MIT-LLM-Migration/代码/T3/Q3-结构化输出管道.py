# T3 Q3 结构化输出管道（参考解法，仅教练分支）
# 目标：解析→校验→错误回填重试→降级；100 次统计三档成功率
import json, random

def mock_llm_json(prompt, feedback, rng):
    """30% 出故障（三种各占 1/3）；收到错误反馈后修复概率升到 90%。"""
    fail_p = 0.30 if feedback is None else 0.10
    if rng.random() < fail_p:
        kind = rng.choice(["缺引号", "尾逗号", "缺字段"])
        if kind == "缺引号":
            return '{"city: "北京", "temp": 22}'
        if kind == "尾逗号":
            return '{"city": "北京", "temp": 22,}'
        return '{"city": "北京"}'
    return '{"city": "北京", "temp": 22}'

def validate(text):
    """返回 (data|None, 错误列表)。"""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return None, [f"JSON 解析失败: {e.msg}"]
    errors = []
    if not isinstance(data.get("city"), str):
        errors.append("字段 city 缺失或非字符串")
    if not isinstance(data.get("temp"), (int, float)):
        errors.append("字段 temp 缺失或非数字")
    return (data if not errors else None), errors

def structured_pipeline(prompt, rng, max_retry=3):
    feedback = None
    for attempt in range(1 + max_retry):
        raw = mock_llm_json(prompt, feedback, rng)
        data, errors = validate(raw)
        if data is not None:
            return {"status": "ok" if attempt == 0 else "ok_after_retry",
                    "attempts": attempt + 1, "data": data}
        feedback = "; ".join(errors)   # 错误详情回填进上下文
    return {"status": "fallback", "attempts": 1 + max_retry, "data": {"city": "未知", "temp": None}}

if __name__ == "__main__":
    rng = random.Random(5)
    stats = {"ok": 0, "ok_after_retry": 0, "fallback": 0}
    for _ in range(100):
        stats[structured_pipeline("查询北京天气", rng)["status"]] += 1
    print(f"100 次管道运行：直出成功 {stats['ok']} / 重试后成功 {stats['ok_after_retry']} / 降级 {stats['fallback']}")
    print("结论：『要求输出 JSON』只抬概率；解析+校验+回填重试+降级才是完整契约（M4）。")
    print("对照指针：MIT-Python-Migration/代码/T7/（7.4 结构化输出管道，对拍用）")
