# T1 Q1 tokenizer 体验（学员作答版）
# 撞墙记录：
#   墙1：decode 一开始用 vocab 直接下标取字符，vocab 是 dict 不能按 id 下标 → TypeError；
#        修复：建反向表 id->char。
# 思路：iOS 里像给 enum 建 rawValue 映射表，encode = 查表，decode = 反查。

def build_vocab(texts):
    # 按出现顺序建表（没排序，先见先得）
    vocab = {}
    for t in texts:
        for ch in t:
            if ch not in vocab:
                vocab[ch] = len(vocab)
    return vocab

def encode(text, vocab):
    return [vocab[ch] for ch in text]

def decode(ids, vocab):
    inv = {i: ch for ch, i in vocab.items()}
    return "".join(inv[i] for i in ids)

if __name__ == "__main__":
    zh = "机器学习让计算机从数据中学习规律"
    en = "Machine learning lets computers learn patterns from data"
    vocab = build_vocab([zh, en])

    zh_ids = encode(zh, vocab)
    en_ids = encode(en, vocab)
    assert decode(zh_ids, vocab) == zh
    assert decode(en_ids, vocab) == en

    print(f"中文句: {len(zh)} 字符 -> {len(zh_ids)} tokens")
    print(f"英文句: {len(en)} 字符 -> {len(en_ids)} tokens")
    print(f"词表大小: {len(vocab)}")

    # 关于 BPE 的理解（半懂，待教练确认）：
    # 我猜真实 tokenizer 不是逐字符切的——英文里 "learning" 这种高频词
    # 应该整个是一个 token，而罕见词会被拆成几段。中文大概一个字一个 token。
    # 如果是这样，「同样意思」的英文应该比中文省 token？和我字符级实验的
    # 结论正好反过来——说明切分单位完全由词表决定，和「字/词」直觉无关。
    # 「strawberry 数不对 r」大概因为 strawberry 整个就是一个 token，
    # 模型根本看不到里面的字母。（这一层我不确定，标半懂）
