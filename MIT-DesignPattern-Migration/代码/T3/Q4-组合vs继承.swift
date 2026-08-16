// T3-Q4 协议组合 vs 继承对拍
import Foundation
protocol DataSource { func load() -> [String] }
class BaseDataSource: DataSource {
    func load() -> [String] { [] }
    func cache(_ items: [String]) { print("继承版缓存 \(items.count) 条") }
}
final class FileDataSource: BaseDataSource { override func load() -> [String] { ["file1"] } }
final class CachedFileDataSource: FileDataSource { override func load() { let items = super.load(); cache(items) } }

struct RemoteSource: DataSource { func load() -> [String] { ["remote1"] } }
struct CachedSource: DataSource { let w: DataSource; func load() -> [String] { let i = w.load(); print("组合版缓存 \(i.count) 条"); return i } }
struct LoggedSource: DataSource { let w: DataSource; func load() -> [String] { let i = w.load(); print("组合版日志 \(i.count) 条"); return i } }

_ = CachedFileDataSource().load()
let combo = LoggedSource(w: CachedSource(w: RemoteSource())); _ = combo.load()
print("\n继承版加能力要动继承树；组合版任意叠加（Logged>Cached>Remote），可替换可测试")
print("结论: 行为可叠加场景组合优先；is-a 身份（框架回调）时继承仍合理")
