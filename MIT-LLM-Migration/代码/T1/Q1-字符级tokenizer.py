# T1 Q1 字符级 tokenizer 体验（参考解法，仅教练分支）
# 目标：encode/decode 往返无损；中英 token 数对比；注释解释 BPE 差异
import random  # noqa: F401  (保留脚手架习惯；本题无需随机)

def build_vocab(texts: list[str]) -> dict[str, int]:
    """字符级词表：每个出现过的字符一个 token id。"""
    chars = sorted({ch for t in texts for ch in t})
    return {ch: i for i, ch in enumerate(chars)}

def encode(text: str, vocab: dict[str, int]) -> list[int]:
    return [vocab[ch] for ch in text]

def decode(ids: list[int], vocab: dict[str, int]) -> str:
    inv = {i: ch for ch, i in vocab.items()}
    return "".join(inv[i] for i in ids)

if __name__ == "__main__":
    zh = "今天天气很好，我们去公园散步。"
    en = "The weather is nice today, let us walk in the park."
    vocab = build_vocab([zh, en])

    for label, text in [("中文", zh), ("英文", en)]:
        ids = encode(text, vocab)
        assert decode(ids, vocab) == text, "往返无损失败"
        print(f"{label}: {len(text)} 字符 -> {len(ids)} tokens（字符级：一字/母一 token）")

    # 解释（认知冲突点）：
    # 字符级切分下，英文每个字母一个 token，英文句子 token 数反而更多。
    # 真实 BPE tokenizer 不同：它把语料中高频的子串合并成单元——
    #   "the"、"weather"、"ing" 这类高频片段会成为单个 token，
    #   所以常见英文词 ≈ 1 token，长/罕见词才拆多段。
    # 中文在多数词表中一字一 token（合并机会少），
    # 因此同一语义内容，中文通常比英文「费 token」。
    # 结论：切分粒度由词表与语料统计决定，不由语言直觉决定。
    print("往返无损断言通过（encode -> decode == 原文）")
