// T4-Q2 Command 撤销栈 vs 闭包版
import Foundation
protocol Command { func execute(); func undo() }
final class AppendCommand: Command {
    let text: String; unowned var editor: Editor
    init(_ t: String, _ e: Editor) { text = t; editor = e }
    func execute() { editor.content += text }
    func undo() { editor.content.removeLast(text.count) }
}
final class Editor {
    var content = ""; private var stack: [Command] = []
    func run(_ c: Command) { c.execute(); stack.append(c); print("执行: \(content)") }
    func undo() { guard let c = stack.popLast() else { return }; c.undo(); print("撤销: \(content)") }
}
let e = Editor()
e.run(AppendCommand("你好", e)); e.run(AppendCommand("世界", e)); e.undo(); e.undo()
print("\n闭包版只有 execute 没有 undo——要么成对存逆闭包（易错），要么没有通用撤销；")
print("命令对象有身份 + undo()，可入栈/重做/记录")
