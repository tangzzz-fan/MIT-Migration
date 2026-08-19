# T3 Q1 消息结构最小客户端（参考解法，仅教练分支）
# 目标：role/content 协议；system 生效验证；消息顺序影响结果

def mock_llm(messages):
    """规则：system 含『只输出中文』→ 回复带中文前缀；回复 = 角色化拼接全部 user 内容。"""
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    users = [m["content"] for m in messages if m["role"] == "user"]
    body = " <- ".join(users)
    if "只输出中文" in system:
        return f"【中文回复】{body}"
    return f"echo: {body}"

def chat(system, user):
    msgs = ([{"role": "system", "content": system}] if system else [])
    msgs.append({"role": "user", "content": user})
    return mock_llm(msgs)

if __name__ == "__main__":
    # 测试 1：system 指令生效
    r1 = chat("只输出中文，简洁回答", "hello")
    assert r1.startswith("【中文回复】")
    print("测试1 system 生效 :", r1)

    # 测试 2：无 system 时行为不同
    r2 = chat(None, "hello")
    assert not r2.startswith("【中文回复】")
    print("测试2 无 system   :", r2)

    # 测试 3：消息顺序影响结果（上下文是序列，不是集合）
    a = mock_llm([{"role": "user", "content": "先装数据库"}, {"role": "user", "content": "再写接口"}])
    b = mock_llm([{"role": "user", "content": "再写接口"}, {"role": "user", "content": "先装数据库"}])
    assert a != b
    print("测试3 顺序敏感    :", a, "|", b)
    print("\n结论：system 是训练期偏置的槽位（mock 化为规则）；上下文是有序序列，顺序即语义。")
