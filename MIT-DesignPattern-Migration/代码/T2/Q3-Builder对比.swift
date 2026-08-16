// T2-Q3 Builder vs 命名参数
import Foundation
struct Config {
    let apiKey: String, baseURL: String
    var timeout = 30.0, retries = 3, logEnabled = false
}
final class ConfigBuilder {
    private var apiKey: String?, baseURL: String?
    private var timeout = 30.0, retries = 3, logEnabled = false
    func apiKey(_ v: String) -> Self { apiKey = v; return self }
    func baseURL(_ v: String) -> Self { baseURL = v; return self }
    func timeout(_ v: Double) -> Self { timeout = v; return self }
    func build() -> Config? { guard let apiKey, let baseURL else { return nil }; return Config(apiKey: apiKey, baseURL: baseURL, timeout: timeout, retries: retries, logEnabled: logEnabled) }
}
let c1 = Config(apiKey: "k", baseURL: "u")
let c2 = ConfigBuilder().apiKey("k").baseURL("u").timeout(10).build()
print("命名参数版: 必选编译期强制，零样板（timeout=\(c1.timeout)）")
print("Builder 版: 多 1 类型、必选运行时校验（timeout=\(c2?.timeout ?? -1)）")
print("结论: 本场景命名参数胜；Builder 只在交叉校验 + 不可变产物场景胜出")
