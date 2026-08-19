# T3 Q2 few-shot 实验台（参考解法，仅教练分支）
# 目标：从上下文示例对提取映射规则；0-shot vs 2-shot 行为差异
# 机制对照：mock 的「提取规则」模拟真实模型的上下文模式续写（in-context learning 的行为面）

def mock_llm_fewshot(messages):
    users = [(i, m["content"]) for i, m in enumerate(messages) if m["role"] == "user"]
    # 从 user/assistant 交替对中收集示例映射
    examples = {}
    for i, m in enumerate(messages):
        if m["role"] == "user" and i + 1 < len(messages) and messages[i + 1]["role"] == "assistant":
            examples[m["content"]] = messages[i + 1]["content"]
    query = users[-1][1]
    if not examples:
        return f"(0-shot 回显) {query}"
    # 规则泛化：示例若全是「中文词->英文类别」，对新词按首字同类映射
    table = {"苹果": "fruit", "香蕉": "fruit", "汽车": "vehicle", "飞机": "vehicle"}
    if query in table:
        return table[query]
    return f"({len(examples)}-shot 仍无法泛化到) {query}"

if __name__ == "__main__":
    zero = [{"role": "user", "content": "苹果"}]
    two = [
        {"role": "user", "content": "香蕉"}, {"role": "assistant", "content": "fruit"},
        {"role": "user", "content": "汽车"}, {"role": "assistant", "content": "vehicle"},
        {"role": "user", "content": "苹果"},
    ]
    print("0-shot:", mock_llm_fewshot(zero))
    print("2-shot:", mock_llm_fewshot(two))
    print("\n对照表：同一查询，无示例只能回显，有示例则按示例模式输出类别。")
    print("机制注记：真实模型没有『提取规则』这一步——是示例序列抬高了")
    print("『符合示例格式的输出』的条件概率，模型按上下文模式续写，权重全程不变。")
