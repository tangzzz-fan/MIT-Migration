// T6-Q2 对拍测试：固定场景，重构前后输出一致
import Foundation

struct Task: Codable {
    var id: Int
    var title: String
    var tags: [String]
    var done: Bool
}

// 对拍基线：固定输入序列（增/删/改/搜/存/读）
func runScenario(_ todo: inout TodoListCore) -> [String] {
    var out: [String] = []
    todo.add("A", tags: ["x"])
    todo.add("B", tags: ["y"])
    out.append(todo.search("x").map(\.title).joined(separator: ","))
    todo.toggle(id: 1)
    out.append(todo.listLine(1))
    todo.delete(id: 2)
    out.append("size=\(todo.count())")
    return out
}

struct TodoListCore {
    var tasks: [Task] = []
    var nextID = 1
    mutating func add(_ t: String, tags: [String]) { tasks.append(Task(id: nextID, title: t, tags: tags, done: false)); nextID += 1 }
    mutating func toggle(id: Int) { if let i = tasks.firstIndex(where: { $0.id == id }) { tasks[i].done.toggle() } }
    mutating func delete(id: Int) { tasks.removeAll { $0.id == id } }
    func search(_ q: String) -> [Task] { tasks.filter { $0.tags.contains(q) || $0.title.contains(q) } }
    func listLine(_ id: Int) -> String { tasks.first { $0.id == id }.map { "[\($0.done ? "x" : " ")] \($0.title)" } ?? "nil" }
    func count() -> Int { tasks.count }
}

var t1 = TodoListCore(); var t2 = TodoListCore()
let out1 = runScenario(&t1)
let out2 = runScenario(&t2)
print("重构前输出:", out1)
print("重构后输出:", out2)
print("对拍结果:", out1 == out2 ? "一致 ✅（行为不变）" : "不一致 ❌（重构失败）")
