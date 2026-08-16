# MIT-DesignPattern-Migration：学员工作区

> 这是设计模式线的**学员分支**（`feat/mit-dp-study-student`，对应 worktree `../MIT-Migration-dp-student`）。本目录只有题干与学习骨架，**不含密卷、旧作答、批改、费曼与解法代码**——这是防假学习机制，不是遗漏。

## 你在这里做什么

1. 读 `MIT-DesignPattern-Migration/00-学习计划.md`（六主题计划 + 台账）与 `01-学员人设卡.md`（你是谁、存量在哪、预期哪里该错）；
2. 每主题按 `T{n}-01-教练出题-<主题>.md` 闭卷作答：先盘点 OC 存量写法，再自推五模型，对教练版标注差异；概念题写 `T{n}-02-学员作答-<主题>.md`，逐题自评三档；
3. 代码题在 `MIT-DesignPattern-Migration/代码/T{n}/` 里实现，用本机 `swift` 实跑，输出贴回作答稿——没跑起来 = 没验证；
4. 每个模式引入/拒绝的决定，写「问题-约束-代价」三行账；
5. 卡住按「弱 → 中 → 强」去教练目录看密卷提示，看过的级数如实记进作答稿；
6. 全过后写 `T{n}-04-费曼草稿-<主题>.md`（脱稿重推五模型 + OC/Swift 对照）。

完整规则见 [学员须知](MIT-DesignPattern-Migration/学员须知.md) 与 [使用说明书](MIT-DesignPattern-Migration/使用说明书-角色指南.md)。

## 教练内容在哪

教练分支 `feat/mit-dp-study`（对应 worktree `../MIT-Migration-dp-coach`）含：

- 全量归档与 `T{n}-01-教练密卷-<主题>.md`（提示梯 + 评分要点 + 参考答案）；
- 教练版 `00-学习计划.md`（台账由教练维护，当前为空）。

**作答完成、自批完成之前，不要打开教练目录。**

## 快速开始

```bash
cd /Users/bigapple/Developments/MIT-Migration-dp-student
# 从 T1 开始：读 00 → 01 → T1-01，闭卷作答
```

## 本分支与 main 的关系

`main` 是本仓库的归档分支；本分支是设计模式线专用的学员视图，与 `feat/mit-dp-study`（教练视图）一一对应，两者通过 git worktree 同时挂载、互不干扰。
