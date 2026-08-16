// T2-Q1 Singleton 重构：static let 共享 → 显式注入 + actor 隔离
import Foundation
final class OldCache { static let shared = OldCache(); private var s: [String: String] = [:]; func get(_ k: String) -> String? { s[k] }; func set(_ k: String, _ v: String) { s[k] = v } }
actor CacheManager { private var s: [String: String] = [:]; func get(_ k: String) -> String? { s[k] }; func set(_ k: String, _ v: String) { s[k] = v } }
struct Service { let cache: CacheManager; init(cache: CacheManager) { self.cache = cache } }
let sem = DispatchSemaphore(value: 0)
Task {
    let old = OldCache.shared; old.set("k", "v1")
    print("旧版：全局共享、测试无法替换，get(k)=\(old.get("k") ?? "nil")")
    let cache = CacheManager(); let svc = Service(cache: cache)
    await cache.set("k", "v2")
    print("新版：构造注入（测试可 new 独立实例），get(k)=\(await svc.cache.get("k") ?? "nil")，actor 隔离免锁")
    sem.signal()
}
sem.wait()
