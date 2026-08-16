// T6-Q3 按需引入：存储 Adapter + Command 撤销 + 量化记账
import Foundation

struct Task: Codable { var id: Int; var title: String; var tags: [String]; var done: Bool }

// 引入 1：存储 Adapter（协议隔离存储后端）
protocol TaskStorage { func load() -> [Task]; func save(_ tasks: [Task]) }
struct FileStorage: TaskStorage {
    let file = "todos.json"
    func load() -> [Task] { guard let d = try? Data(contentsOf: URL(fileURLWithPath: file)) else { return [] }; return (try? JSONDecoder().decode([Task].self, from: d)) ?? [] }
    func save(_ tasks: [Task]) { if let d = try? JSONEncoder().encode(tasks) { try? d.write(to: URL(fileURLWithPath: file)) } }
}

// 引入 2：Command 撤销
protocol Command { func execute(); func undo() }
final class AddTaskCommand: Command {
    let title: String; var todo: TodoCore; let tags: [String]
    init(_ title: String, _ tags: [String], _ todo: TodoCore) { self.title = title; self.tags = tags; self.todo = todo }
    func execute() { todo.add(title, tags: tags) }
    func undo() { todo.delete(id: todo.lastID) }
}
final class TodoCore {
    var tasks: [Task] = []; var lastID = 0; private var stack: [Command] = []
    let storage: TaskStorage
    init(storage: TaskStorage) { self.storage = storage; tasks = storage.load(); lastID = (tasks.map(\.id).max() ?? 0) }
    func add(_ t: String, tags: [String]) { lastID += 1; tasks.append(Task(id: lastID, title: t, tags: tags, done: false)) }
    func delete(id: Int) { tasks.removeAll { $0.id == id } }
    func run(_ c: Command) { c.execute(); stack.append(c); storage.save(tasks) }
    func undo() { guard let c = stack.popLast() else { return }; c.undo(); storage.save(tasks) }
}

let core = TodoCore(storage: FileStorage())
core.run(AddTaskCommand("引入模式", ["工程"], core))
core.run(AddTaskCommand("第二条", [], core))
core.undo()
print("撤销后任务数: \(core.tasks.count)")
print("\n量化: 存储改动点从 3 处（直写文件）收敛到 1 处（storage.save）；撤销能力 +18 行")
print("记账: 存储 Adapter 值得（换后端需求真实）；Command 值得（撤销需求真实）")
print("撤出条件: 若单一存储不再变 → 撤 Adapter；撤销无人用 → 撤 Command 栈")
