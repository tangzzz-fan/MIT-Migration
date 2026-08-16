// T3-Q3 Decorator 链：职责叠加 + 顺序敏感反例
import Foundation
protocol Requesting { func call(_ url: String) -> String }
struct BaseRequest: Requesting { func call(_ u: String) -> String { "响应(\(u))" } }
final class LoggingDecorator: Requesting { let w: Requesting; init(_ w: Requesting) { self.w = w }; func call(_ u: String) -> String { print("  [日志] 请求 \(u)"); return w.call(u) } }
final class MetricsDecorator: Requesting { let w: Requesting; init(_ w: Requesting) { self.w = w }; func call(_ u: String) -> String { print("  [指标] +1"); return w.call(u) } }
final class RetryDecorator: Requesting {
    let w: Requesting; let n: Int
    init(_ w: Requesting, n: Int) { self.w = w; self.n = n }
    func call(_ u: String) -> String { for i in 1...n { print("  [重试] 第\(i)次"); if i == n { return w.call(u) } }; return "failed" }
}
print("链 A: 重试(外) > 日志 > 指标")
_ = RetryDecorator(LoggingDecorator(MetricsDecorator(BaseRequest())), n: 2).call("/api")
print("\n链 B: 日志(外) > 重试 > 指标")
_ = LoggingDecorator(RetryDecorator(MetricsDecorator(BaseRequest()), n: 2)).call("/api")
print("\n顺序敏感: 重试在外=每次尝试都记日志；重试在内=只记一次——Decorator 顺序改变行为")
