// T2-Q4 Prototype 深拷贝：class 含引用成员
import Foundation
final class Author { var name: String; init(_ n: String) { name = n } }
final class Book {
    var title: String; var author: Author
    init(_ t: String, _ a: Author) { title = t; author = a }
    func deepCopy() -> Book { Book(title, Author(author.name)) }
}
let author = Author("张三")
let b1 = Book("Swift 模式", author)
let shallow = Book(b1.title, b1.author); shallow.author.name = "李四"
print("浅拷贝: b1.author=\(b1.author.name)（被连坐，引用成员共享）")
let deep = b1.deepCopy(); deep.author.name = "王五"
print("深拷贝: b1.author=\(b1.author.name)（独立）")
print("结论: struct 包 class 成员时拷贝的仍是引用；class 场景要递归深拷贝，值语义只对纯值类型免费")
