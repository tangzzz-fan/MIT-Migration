// T4-Q1 Observer 三版对拍：通知 vs Combine vs 手写
import Foundation
import Combine
final class LoginStore: ObservableObject { @Published var isLoggedIn = false; func login() { isLoggedIn = true } }
protocol LoginObserver: AnyObject { func onLogin() }
final class HandRolled { private var obs: [WeakBox] = []; func add(_ o: LoginObserver) { obs.append(WeakBox(o)) }; func post() { obs.forEach { $0.value?.onLogin() } } }
final class WeakBox { weak var value: LoginObserver?; init(_ v: LoginObserver) { value = v } }
final class Page: LoginObserver { let name: String; init(_ n: String) { name = n }; func onLogin() { print("\(name) 收到事件") } }

let store = LoginStore()
var c = Set<AnyCancellable>()
store.$isLoggedIn.sink { print("Combine(持有): \($0)") }.store(in: &c)
store.$isLoggedIn.sink { _ in print("Combine(不存): 触发不了——不存即取消") }
store.login()
print("版一通知: 注册后一直活到 removeObserver，忘移除=崩溃")
print("版二手写: 显式 add/remove，样板多")
print("版三 Combine: 不 store = 释放即取消；@Observable 则是自动依赖收集")
