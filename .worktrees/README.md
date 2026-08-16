# .worktrees：本仓库的多视图工作目录

这里是 MIT-Migration 的 git worktree 目录——同一仓库的多个分支各挂一个独立工作区，**不用切换分支**，同时打开即可：

| 目录 | 分支 | 视图 |
|------|------|------|
| `swift-coach` | `feat/mit-swift-study` | Swift 教练（全量 + 密卷 + 解法） |
| `swift-student` | `feat/mit-swift-study-student` | Swift 学员（闭卷：题干 + 骨架） |
| `python-coach` | `feat/mit-python-study` | Python 教练（全量 + 密卷） |
| `python-student` | `feat/mit-python-study-student` | Python 学员（闭卷） |
| `dp-coach` | `feat/mit-dp-study` | 设计模式教练（全量） |
| `dp-student` | `feat/mit-dp-study-student` | 设计模式学员（三处齐全，先闭卷后对照） |
| `coreml-coach` | `feat/mit-coreml-study` | CoreML 教练（全量） |
| `coreml-student` | `feat/mit-coreml-study-student` | CoreML 学员（三处齐全，先闭卷后对照） |

- 仓库根目录（main）= 全量归档 + README + 内容地图（[`00-内容地图.md`](../00-内容地图.md)）；
- 日常练习进对应 `*-student` 目录；判卷 / 看答案进 `*-coach` 目录；
- 本目录由 git 管理，**不要手动删改子目录**；清理用 `git worktree remove <路径>`。
