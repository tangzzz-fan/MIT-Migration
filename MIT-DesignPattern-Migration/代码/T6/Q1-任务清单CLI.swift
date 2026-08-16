// T6-Q1 任务清单 CLI（直觉版，默认收束项目）
import Foundation

struct Task: Codable {
    var id: Int
    var title: String
    var tags: [String]
    var done: Bool
}

final class TodoList {
    private var tasks: [Task] = []
    private var nextID = 1
    private let file = "todos.json"

    func add(_ title: String, tags: [String] = []) {
        tasks.append(Task(id: nextID, title: title, tags: tags, done: false))
        nextID += 1
        print("已添加: \(title)")
    }
    func delete(id: Int) {
        tasks.removeAll { $0.id == id }
        print("已删除: #\(id)")
    }
    func toggle(id: Int) {
        if let i = tasks.firstIndex(where: { $0.id == id }) { tasks[i].done.toggle() }
    }
    func search(_ q: String) -> [Task] {
        tasks.filter { $0.title.contains(q) || $0.tags.contains(q) }
    }
    func list() {
        for t in tasks { print("#\(t.id) [\(t.done ? "x" : " ")] \(t.title) \(t.tags)") }
    }
    func save() {
        let data = try? JSONEncoder().encode(tasks)
        try? data?.write(to: URL(fileURLWithPath: file))
        print("已保存到 \(file)")
    }
    func load() {
        guard let data = try? Data(contentsOf: URL(fileURLWithPath: file)) else { return }
        tasks = (try? JSONDecoder().decode([Task].self, from: data)) ?? []
        nextID = (tasks.map(\.id).max() ?? 0) + 1
    }
}

let todo = TodoList()
todo.load()
todo.add("学习 MIT 方法", tags: ["学习"])
todo.add("重构任务清单", tags: ["工程"])
todo.search("工程").forEach { print("搜索命中: \($0.title)") }
todo.toggle(id: 1)
todo.list()
todo.save()
print("\n直觉版坏味道: ① 存储硬编码文件（换后端要改调用点）② 搜索逻辑写死 ③ 命令操作无撤销 ④ 状态散落")
