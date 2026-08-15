---
title: "T6 教练出题集：Combine → async 迁移实操（增量轮，按校准后真实画像出题）"
topics: [learning, swift, combine, concurrency, asyncsequence, observable, migration, coaching]
type: note
date: 2026-08-15
status: draft
origin: chat
---

# T6 教练出题集：Combine → async 迁移实操（存量替换工程）

> 增量轮 · 教练 agent 产出。触发依据：[[00-学习计划.md|学习计划]] 第六节定向评估——「概念级边界」（何时用什么）已由 T4/T5 覆盖，「存量替换怎么做」缺独立轮次。本轮补三根支柱：①存量操作符管道 → AsyncSequence；②@Published ViewModel → @Observable；③增量迁移切分与混合共存。
> 学员画像（校准后，见 [[01-学员人设卡.md|人设卡]] 校准注记）：会一点 Swift、**用纯 Swift 实现过完整项目**、用过 Combine 但不多。因此本轮拷问重心是**迁移决策与替换工程**，不是 Combine 入门：工程切分直觉是主场（该对必须对），AsyncAlgorithms/AsyncStream 算子替换与 @Observable 重构细节是陌生区（如实陌生）。
> 环境约束声明：CLI 顶层脚本不可用外部 SPM 包——**AsyncAlgorithms 不可 import**，本轮代码题用手写等价实现逼出算子语义（这恰是拷问点：手写一遍才懂 debounce/retry 在 async 里到底等价于什么）。UIHostingController/UIViewRepresentable 无 UIKit 运行环境，口述验证、记「待真机验证」（C4 纪律）。
> 使用纪律：学员卡住按「弱→中→强」逐级给提示，禁止跳级；直接要答案 → 拒答并反问已排除了什么（C1/C2）。

## 一、共识：5 个核心心智模型

| # | 模型 | 一句话骨架 | 迁移锚点（学员存量） |
|---|------|-----------|---------------------|
| M1 | Publisher 与 AsyncSequence 是同一条流的两种形态：push+demand vs pull+挂起 | Combine 是**推模型**：上游按需求（demand）发货，订阅方被动收；AsyncSequence 是**拉模型**：消费方 `for await` 主动拉、拉不到就挂起。选型不是语法糖差异，是交付模型差异——需要「生产侧控制节奏、多个订阅者共享」留 Combine；「消费侧控制节奏、一条消费链」迁 async | 学员用过 Combine 的 sink/map——「发了就收」的手感是推模型；`for await` 的「我要才给」是第一次见面 |
| M2 | 操作符映射账本：同名不等价，缺项要手写 | map/filter/compactMap 两边同构，迁移零风险；debounce/throttle/merge 语义有细节差（时间窗 vs 采样、合并策略）；**retry/combineLatest 等在 async 标准库无内建**，要么 AsyncAlgorithms（外部包）要么手写循环。迁移成本不在能映射的，在映射不了与映射变形的 | 学员用过 debounce/map（少量）——账本从他会的那几行开始建，重点拷问「不会的那几行怎么迁」 |
| M3 | 寿命所有权移交：从「记得存住」到「结构自带」 | Combine 的寿命靠人：AnyCancellable 忘存即取消、存进永生持有者即永生（T4 C1/T5 M5 验过）；结构化并发把寿命交给结构：`.task` 绑视图寿命、TaskGroup 绑作用域、`for await` 退出即终止迭代。迁移 = 把「散落的凭证管理」收敛成「作用域设计」 | 学员存过 cancellable（少量 Combine 经验含这条）——「记得存」的手艺不丢，但义务从记忆力移交编译器 |
| M4 | 状态模型替换不是逐行翻译：@Published 链路 → @Observable 要重找管道的家 | ObservableObject = 对象级广播 + 内建 publisher 管道；@Observable = 属性级追踪、**无内建 publisher**（T5 Q4 段三量过爆炸半径 6:3）。重构时状态部分白赚属性级，但挂在 @Published 上的管道（防抖搜索、节流定位）必须搬家：UI 侧搬 `.task`+AsyncStream，或保留一小段 Combine 桥——「为了状态粒度引入管道断裂」是这笔账的代价 | 学员写过完整 Swift 项目的 ViewModel——@Published 是熟人；@Observable 只闻其名，重构手感是陌生区 |
| M5 | 增量迁移按屏切、不按文件切，桥是边界不是过渡品 | 切分单位是「一屏 + 它的状态闭环」，不是文件数；混合期靠双向桥共存（UIKit 侧 UIHostingController/UIViewRepresentable，流侧 values/AsyncPublisher）；桥不删——它长期承担「新旧世界边界」的职责，边界随迁移推进而移动，不消失 | 学员的工程常识主场：渐进迁移、混编边界收敛、先跑通再优化——本轮把直觉钉成规则 |

学员自检要求：合上表复述 M1–M5，每个模型给一条自己项目里的存量对应物（哪段 Combine 代码、哪个 ViewModel）。

## 二、争议：专家吵得最凶的 3 个焦点

**D1 存量 Combine 管道该全量替换成 async 吗？**
- 正方最强论据（替换派）：技术栈统一、结构化寿命白拿（M3）、调试栈浅（T4 D3 的账）；Apple 投入方向明确，AsyncAlgorithms 在补齐算子。
- 反方最强论据（共存派）：AsyncAlgorithms 是外部依赖且成熟度有限；share/multicast/combineLatest 类多播语义无等价物；能跑的管道重写就是引入回归风险——「没坏别修」。
- 对迁移者的意义：学员有完整项目经验，本题考他会不会拿工程常识压住技术冲动——答案应是按管道形态分档，不是全量或全不。

**D2 ObservableObject → @Observable 算不算平滑迁移？**
- 正方最强论据：属性级追踪直接消灭陪跑重算（T5 实锤），与 SwiftUI 深度集成，API 更薄。
- 反方最强论据：iOS 17+ 部署底线；@Published 上的管道无内建替代（M4 断裂）；`@Published private(set)` 等语义需要重新设计；第三方库绑定 ObservableObject。
- 对迁移者的意义：T5 停在「爆炸半径对比」，本轮要给出**重构判定清单**——什么样的 ViewModel 先迁、什么样的缓迁。

**D3 迁移顺序：UI 先行还是数据层先行？**
- UI 先行论据：用户可见收益快、SwiftUI 屏与状态闭环天然按屏切（M5）、倒逼状态模型整理。
- 数据层先行论据：管道与状态是 UI 的地基，先迁地基避免 UI 返工；桥的方向单一（新 UI 吃旧数据容易，旧 UI 吃新数据难）。
- 对迁移者的意义：没有标准答案，考的是「按依赖方向与风险给排序规则」的能力——学员的迁移直觉主场题。

## 三、概念拷问题（6 道，口述通道）

判定标准：能讲出「为什么」并迁移到新场景 = 过；只能复述定义 = 不过。每题配弱/中/强三级提示。

### C1 迁移决策：一条存量管道，换还是留？（主场+判定）

问题：你项目里有一条存量 Combine 管道：搜索框文本 → debounce(0.3) → 去重 → 网络请求（retry 2）→ 缓存 → 回主线程刷新列表。现在立项「迁移到 Concurrency」，这条管道换不换？给出你的判定框架（不是一句「换」或「不换」），并说出判定里的关键变量。

- 弱提示：T4 你做过 Combine vs async 的三轴判定——那三轴现在加上「存量已跑通」这个变量，权重怎么变？
- 中提示：关键变量：订阅者数量（单消费链 vs 多播）、算子可映射性（M2 账本：这条链上每个算子 async 侧有没有等价物）、寿命归属（这条链的取消该谁负责）、回归风险（跑通的管道重写的测试成本）。单消费+算子可手写+寿命想交给视图 → 换；多播/share/团队不熟 → 留，用 values 桥对接新世界。
- 强提示：结论形态：按管道形态分档——①单消费查询类管道（本例）适合迁；②多播/共享上游留 Combine 用桥对接；③迁的时候语义逐个对拍（同输入序列两边输出一致）才算迁完，不是删掉就算。
- 评分要点：死记硬背典型：「官方推荐 async，全换。」真懂特征：分档框架+关键变量+「对拍才算迁完」的验收意识（工程常识主场，该对必须对）。

### C2 操作符映射账本：哪些能直迁、哪些要手写？

问题：map、filter、debounce、throttle、retry、merge、combineLatest、share——逐个说出 async 侧的对应物（内建/AsyncAlgorithms/手写/无等价）。retry 在 async 里的标准写法是什么？为什么说「能映射的不是重点，映射不了的才是迁移成本」？

- 弱提示：AsyncSequence 协议本身只给了你什么（序列语义）？算子是谁的职责？
- 中提示：内建：map/filter/compactMap/merge（AsyncAlgorithms 亦有增强）；AsyncAlgorithms（外部包）：debounce/throttle/combineLatest/merge 等；标准库**无** retry——手写循环（while 计数 + catch）；share 语义（多播热共享）async 侧无直接等价，要靠 TaskGroup+缓存重设计。手写 retry 的标准形态：`for attempt in 1...n { do { try await f(); break } catch { if attempt == n { throw } } }`。
- 强提示：账本记忆钩：「同构的免费（map/filter）、变形的付费（debounce 时间窗语义）、缺项的自建（retry）、无解的重设计（share/多播）」。
- 评分要点：死记硬背典型：「AsyncAlgorithms 全都有。」真懂特征：账本分档清楚、retry 手写形态给得出、share 的「重设计」性质说出。

### C3 寿命移交：cancellable 的义务怎么翻译？

问题：存量代码里 `Set<AnyCancellable>` 存了一屏的所有订阅——这套「手动存凭证」在结构化并发里对应什么？`.task`、`Task {}`、`TaskGroup`、`for await` 各自的寿命由谁拥有？迁移时什么形态的订阅「翻译」最干净、什么形态翻译不了？

- 弱提示：T4 C1「不存即取消」翻面是「存进永生持有者即永生」——寿命问题的本质是什么（谁拥有凭证，谁决定何时了结）？
- 中提示：对应表：存进视图的 cancellable → `.task`（视图寿命）；存进 ViewModel 的长订阅 → ViewModel 作用域的 Task（或 AsyncStream + for await 由消费循环拥有）；多订阅聚合 → TaskGroup（作用域结束全部取消）。「翻译不动」的形态：需要**跨作用域存活**的订阅（全局事件总线式）——结构化并发没有「全局凭证」，要么显式长寿命 Task+手动取消，要么留 Combine。
- 强提示：迁移收益的本质：取消义务从「开发者的记忆力」移交「编译器能看见的结构」——忘存凭证这类 bug 直接绝种，代价是跨作用域场景要显式设计。
- 评分要点：真懂特征：对应表给得出；「翻译不动」的边界（跨作用域）诚实说出；收益/代价两栏都讲。

### C4 @Published → @Observable：哪些能直译、哪些要重设计？

问题：一个典型 ViewModel：`@Published var query`、`@Published private(set) var results`、init 里 query.$debounce → 网络 → results 赋值。迁 @Observable 时逐行说：哪些直接换、哪些语义变了、管道去哪了？`@Observable` 为什么「无内建 publisher」是设计取舍不是功能缺失？

- 弱提示：T5 Q4 段三量过两代底座的失效次数差——@Observable 的依赖收集发生在哪一步（读 vs 发）？
- 中提示：直译：两个属性加 @Observable 宏即可；变译：`private(set)` 的保护语义要保留（属性仍 private(set)）；管道的家：query 的观察改用 `.task { for await }` 或 `withObservationTracking` 起异步循环，debounce 手写/M4 账本。设计取舍：@Observable 走「读时追踪」而非「写时广播」，天然没有发布点——管道需求是少数场景，用组合（AsyncStream）补，不绑进底座。
- 强提示：重构判定清单（D2 收口）：先迁「纯状态、无管道」的 ViewModel（白赚属性级）；缓迁「管道重」的（先解决管道的家）；不迁「部署底线卡 iOS 16-」的。
- 评分要点：死记硬背典型：「把 @Published 删了加个宏。」真懂特征：管道搬家路径具体；private(set) 语义保留意识；判定清单分档给出。

### C5 增量切分：一屏一屏迁的刀怎么下？（主场）

问题：一个 10 屏的 UIKit+Combine 应用要迁 SwiftUI+Concurrency。给出你的切分规则：切分单位是什么、第一屏怎么选、桥开在哪一层、新旧模块的数据流向怎么约束？UIHostingController 与 UIViewRepresentable 各管哪个方向？

- 弱提示：你迁过 MRC→ARC、经历过 UIKit 混编——那些迁移里「切大了」的教训是什么？
- 中提示：切分单位 = 一屏 + 它的状态闭环（不是文件）；第一屏选「叶子屏」（依赖最少、可独立替换、出问题好回退）；桥开在**屏边界**：新屏嵌旧壳用 UIHostingController、旧屏嵌新组件用 UIViewRepresentable；流向约束：新屏可吃旧服务（values 桥拉上来），旧屏不吃新状态（避免双向依赖）——边界单向收敛。
- 强提示：顺序规则（D3 收口）：数据流方向上「下游先行」——叶子屏先行、共享服务最后收口；每迁一屏，桥的位置向内移动一格；全部迁完，桥剩「服务层边界」一处（或删）。
- 评分要点：真懂特征：切分单位、叶子屏起手、桥的方向约束三件齐；UIHostingController/UIViewRepresentable 方向不错；有回退意识（工程常识主场）。

### C6 混合共存的桥：values 与 AsyncPublisher 的时序账

问题：混合期两条桥：旧世界给新世界供货（`.values`）、新世界给旧世界供货（`AsyncPublisher`）。两条桥的寿命各由谁拥有？热 Subject 配 values 的经典翻车（T5 Q4 段二撞过）在迁移场景里怎么防？桥上的事件丢失了算谁的 bug？

- 弱提示：T5 Q4 段二你连撞三版才让 values 桥 4/4 不丢——丢件的那几版，生产者和消费者的时序各错在哪？
- 中提示：寿命：values 的迭代由 for-await 循环拥有（消费侧控制）；AsyncPublisher 的订阅仍是 cancellable 语义（回到旧世界义务）。防丢：热 Subject 的「订阅前的 send 没人收」——迁移场景要么生产侧带节拍（订阅就位再生产）、要么换冷启动设计（AsyncStream 按需起生产）、要么 CurrentValueSubject 带初始状态。归责：桥是边界契约——丢件先查「谁的生命周期没覆盖谁」。
- 强提示：工程姿势：桥两侧各打点（进出计数对拍），丢件即两侧计数差——T4 Q1 的打点手艺直接复用。
- 评分要点：真懂特征：两条桥寿命归属分清；热 Subject 翻车的时序本质说出；打点对拍姿势主动迁移。

## 四、代码任务题（4 道，代码通道）

判定标准：本机 `swift` CLI 跑通 + 输出符合预期 + 学员逐行能讲 = 过。代码落 `代码/T6/`，输出贴回批改稿。**AsyncAlgorithms 不可用（外部包），手写等价实现是本题设计意图**；UIHostingController 类结论记「待真机验证」。

### Q1 存量管道迁移与对拍（M1/M2，C1/C2 的代码实体）

任务：复刻 T4 Q1 那条管道的 Combine 版（文本流 → debounce → 去重 → 模拟请求（前两次失败后成功，配 retry 2）→ 收集结果）。然后写它的 async 迁移版：AsyncStream 生产文本流 + **手写 debounce**（时间窗收敛连发）+ 手写去重 + **手写 retry 循环**。两版喂相同输入序列，打印两边的输出序列与事件计数，**对拍一致**才算迁完。说出你手写 debounce 与 Combine debounce 的语义差异点（如有）。

- 评分要点：对拍一致（硬证据）；手写 retry 的「最后一次仍失败要抛」边界处理；debounce 语义差异能讲（时间窗起算点）；撞墙留档。

### Q2 @Published ViewModel → @Observable 重构（M4，C4/D2 的代码实体）

任务：先写「重构前」：一个 ObservableObject ViewModel（@Published query + @Published private(set) results + init 里挂 query→debounce→模拟查询→results 的管道）+ 一个 objectWillChange 失效计数器。再重构为 @Observable 版：属性级状态 + `.task` 风格的异步观察循环（CLI 用 withObservationTracking + Task 模拟）+ 同样的失效计数（复用 T5 Q4 探针法）。断言：同样的「改 query 3 次、改无关属性 3 次」输入下，新版失效次数严格少于旧版，且 results 行为等价。

- 评分要点：两版行为等价（results 序列一致）；失效次数差实测出来；private(set) 保留；「管道的家」安置方式讲得出。

### Q3 寿命移交：cancellable → 结构化寿命（M3，C3 的代码实体）

任务：写「旧形态」：一个 Screen 类持有 `Set<AnyCancellable>`，订阅一个定时事件源，Screen deinit 时订阅应终止（打点证明）。写「新形态」：同样的 Screen，用 `for await` 消费 AsyncStream 跑在 Screen 寿命内的 Task 里，Screen 消失 = Task 取消 = 流终止（onTermination 打点证明）。两形态对拍「创建→活 0.2s→销毁」后事件源的收尾行为一致。追加反例：把 Task 存进一个永生单例，演示「翻译不动」的跨作用域形态。

- 评分要点：两形态收尾行为对拍一致；onTermination/取消打点成立；反例的「永生」演示出来；寿命归属能逐句讲。

### Q4 双向混合桥共存（M5，C6/D1 的代码实体）

任务：同一程序里搭两条桥并共存：桥 A（旧→新）：Combine 侧 PassthroughSubject 模拟旧模块事件，经 `.values` 被 async 侧消费；桥 B（新→旧）：async 侧 AsyncStream 模拟新模块事件，被 Combine 侧 sink 消费（注：出题时预设用 `AsyncPublisher`，实跑已证伪——它是 Publisher→AsyncSequence 方向的桥，反向桥无现成件，需手搭：见代码/T6/Q4 撞墙③）。两桥各自对拍事件计数（生产 N = 消费 N），并打印「两桥共存」的寿命管理差异（values 归消费循环、手搭桥归 cancellable+泵 Task）。时序防线：先挂消费者再开生产者（T5 教训），打点证明 0 丢件。

- 评分要点：两桥 0 丢件（计数硬证据）；寿命差异讲得出；先挂后发的时序防线主动落实；「桥是边界不是过渡品」能结合 D1 讲。

## 五、验收规则

- 概念通道：6 题全过（允许批改后复攻）；代码通道：4 题全跑通。
- 任一通道未过 → 主题不记过关，缺口进台账（C3/C4）。
- 本轮按校准后画像判定：工程切分类主场题（C1/C5）该对必须对、不许装弱；AsyncStream 算子与 @Observable 重构细节是陌生区，半懂如实记。
- UIHostingController/UIViewRepresentable/AsyncAlgorithms 真机与真包行为记「待真机验证」，CLI 以手写等价实现为硬验证上限。
- 出题文件不含答案全文，只有评分要点。
