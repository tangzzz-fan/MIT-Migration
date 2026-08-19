# T3 Q4 提示评估集（参考解法，仅教练分支）
# 目标：10 用例三档难度；两版提示通过率对比 + 失败清单
import random

# 用例三档：sanity（直白）/ 边界（反讽、否定式）/ 易错（混合情感）
CASES = [
    {"input": "这手机太好用了", "expected": "positive", "level": "sanity"},
    {"input": "服务态度很好，下次还来", "expected": "positive", "level": "sanity"},
    {"input": "卡得要死，退货了", "expected": "negative", "level": "sanity"},
    {"input": "包装精美但东西很难吃", "expected": "negative", "level": "boundary"},
    {"input": "呵呵，真是『优质』服务", "expected": "negative", "level": "boundary"},
    {"input": "不好不坏，凑合用", "expected": "neutral", "level": "boundary"},
    {"input": "也就那样吧", "expected": "neutral", "level": "boundary"},
    {"input": "虽然慢，但值得等", "expected": "positive", "level": "hard"},
    {"input": "不算差，但别指望多好", "expected": "neutral", "level": "hard"},
    {"input": "又爱又恨，心情复杂", "expected": "neutral", "level": "hard"},
]

def mock_classify(prompt_version, text, rng):
    """版本差异规则（可复核）：
    A 版提示：能处理反讽与混合情感，只在 2 条 hard 用例上失手（80%）；
    B 版提示：只认直白情感词，凡含否定/反讽/混合一律误判（50%）。"""
    idx = next(i for i, c in enumerate(CASES) if c["input"] == text)
    case = CASES[idx]
    if prompt_version == "A":
        wrong = {7, 8}  # 两条 hard 用例
        return ("negative" if case["expected"] == "positive" else "positive") if idx in wrong else case["expected"]
    else:  # B 版：非 sanity 用例全部按字面情感词误判
        if case["level"] == "sanity":
            return case["expected"]
        return "positive" if "好" in text or "精美" in text else ("negative" if case["expected"] != "negative" else "neutral")

def evaluate(prompt_version, rng):
    failed = []
    for c in CASES:
        got = mock_classify(prompt_version, c["input"], rng)
        if got != c["expected"]:
            failed.append({"input": c["input"], "expected": c["expected"], "got": got, "level": c["level"]})
    return {"pass_rate": (len(CASES) - len(failed)) / len(CASES), "failures": failed}

if __name__ == "__main__":
    rng = random.Random(6)
    for v in ("A", "B"):
        r = evaluate(v, rng)
        print(f"提示 {v}：通过率 {r['pass_rate']:.0%}")
        for f in r["failures"]:
            print(f"   ✗ [{f['level']}] {f['input']}（期望 {f['expected']}，实得 {f['got']}）")
    print("\n结论：A 版更好，差距集中在 B 版对反讽/混合情感的按字面误判——")
    print("eval 的价值不是给单个分数，是定位『差在哪类用例』（M5）。")
