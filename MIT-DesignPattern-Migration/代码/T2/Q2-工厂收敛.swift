// T2-Q2 工厂收敛：if/else 创建 → 静态工厂 + 协议
import Foundation
protocol Payment { func pay(_ amount: Double) }
struct Alipay: Payment { func pay(_ a: Double) { print("支付宝 ¥\(a)") } }
struct WeChatPay: Payment { func pay(_ a: Double) { print("微信 ¥\(a)") } }
enum PaymentType { case alipay, wechat }
enum PaymentFactory { static func make(_ t: PaymentType) -> Payment { switch t { case .alipay: return Alipay(); case .wechat: return WeChatPay() } } }
func checkout(_ t: PaymentType, _ amount: Double) { let p: Payment = PaymentFactory.make(t); p.pay(amount) }
checkout(.alipay, 99); checkout(.wechat, 199)
print("调用方只依赖协议；新增类型只改工厂一处")
