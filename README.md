# MIT-Swift-Migration：学员工作区

> 这是 Swift 迁移线的**学员分支**（`feat/mit-swift-study-student`，对应 worktree `../MIT-Migration-student`）。本目录只有题干与学习骨架，**不含密卷、旧作答、批改、费曼与解法代码**——这是防假学习机制，不是遗漏。

## 你在这里做什么

1. 读 `MIT-Swift-migration/00-学习计划.md`（计划 + 学员版台账）与 `01-学员人设卡.md`（你是谁、存量在哪）；
2. 每主题按 `T{n}-01-教练出题-<主题>.md` 闭卷作答：先自推五模型，再对教练版；概念题写 `T{n}-02-学员作答-<主题>.md`，逐题自评三档（有把握 / 半懂半猜 / 纯猜）；
3. 代码题在 `MIT-Swift-migration/代码/T{n}/` 里实现，用本机 `swift` 实跑，输出贴回作答稿——没跑起来 = 没验证；
4. 卡住按「弱 → 中 → 强」去教练目录看密卷提示，看过的级数如实记进作答稿；
5. 全过后写 `T{n}-04-费曼草稿-<主题>.md`（脱稿重推五模型 + OC/iOS 对照）。

完整规则见 [学员须知](MIT-Swift-migration/学员须知.md) 与 [使用说明书](MIT-Swift-migration/使用说明书-角色指南.md)。

## 教练内容在哪

教练分支 `feat/mit-swift-study`（对应 worktree `../MIT-Migration-coach`）含：

- 全量归档（旧作答 / 批改 / 费曼 / 解法代码）；
- 6 份 `T{n}-01-教练密卷-<主题>.md`（弱/中/强提示 + 评分要点 + 参考答案定位）；
- 教练版 `00-学习计划.md`（旧轮台账与覆盖度评估）。

**作答完成、自批完成之前，不要打开教练目录。**

## 快速开始

```bash
cd /Users/bigapple/Developments/MIT-Migration-student
# 从 T1 开始：读 00 → 01 → T1-01，闭卷作答
```

## 本分支与 main 的关系

`main` 是本仓库的归档分支（含 Swift / Python 两线全量内容）；本分支是 Swift 线重跑专用的学员视图，与 `feat/mit-swift-study`（教练视图）一一对应，两者通过 git worktree 同时挂载、互不干扰。
