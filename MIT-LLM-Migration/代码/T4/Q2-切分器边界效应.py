# T4 Q2 文档切分器边界效应（参考解法，仅教练分支）
# 目标：关键信息骑缝；无重叠丢失、有重叠找回；重叠代价

LONG_TEXT = ("第一段讲的是系统的整体架构，包含网关、服务与存储三层。"
             "第二段描述了部署流程与监控告警的配置方式。"
             "关键信息：退款超时必须设置为三十秒，否则会产生重复扣款。"
             "第四段补充了灰度发布的步骤与回滚预案，最后是附录与参考资料。")
QUERY = "退款超时"

def chunk_fixed(text, size, overlap):
    return [text[i:i + size] for i in range(0, len(text), size - overlap)]

def chunk_paragraph(text):
    return [s for s in text.split("。") if s.strip()]

def search(chunks, query):
    return [(i, c) for i, c in enumerate(chunks) if query in c]

if __name__ == "__main__":
    # 刻意构造：size=40 让关键句骑在切缝上（40/80 边界附近）
    c_no_overlap = chunk_fixed(LONG_TEXT, 40, 0)
    c_overlap = chunk_fixed(LONG_TEXT, 40, 14)
    c_para = chunk_paragraph(LONG_TEXT)

    for name, chunks in [("固定40无重叠", c_no_overlap), ("固定40重叠14", c_overlap), ("按句切分", c_para)]:
        hits = search(chunks, QUERY)
        print(f"[{name}] 共 {len(chunks)} 块，命中 {len(hits)} 块")
        for i, c in hits:
            print(f"   块{i}: {c[:30]}…")

    print("\n收益：重叠让骑缝的关键句在相邻块里再出现一次，检索找回。")
    print("代价：重叠段存储翻倍、可能重复命中（需去重/融合）；按句切分块数多、跨句推理断裂。")
    print("判据：块长按『答案典型长度 + 所需上下文句数』定，再用 hit@k 实测（C6），不拍脑袋。")
    print("对照指针：MIT-Python-Migration/代码/T8/（8.2 文档切分器，对拍用）")
