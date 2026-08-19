# T6 Q2 权限闸门（参考解法，仅教练分支）
# 目标：四层闸门各拦一例；默认拒绝；审批可配置；沙箱防路径穿越

WHITELIST = {"read_file", "write_file", "delete_file"}
DANGEROUS = {"delete_file"}
SANDBOX_DIRS = ("/workspace/project", "/workspace/tmp")
APPROVAL = {"approved", "denied"}  # mock 人工确认结果，可配置

class PermissionGate:
    def __init__(self, approval_result="approved"):
        self.approval_result = approval_result

    def check(self, call):
        tool, args = call.get("tool"), call.get("args", {})
        # 层1 白名单（默认拒绝：未注册即拒，防模型幻觉出不存在的工具）
        if tool not in WHITELIST:
            return False, f"层1白名单拦截：{tool} 未注册"
        # 层2 参数校验
        path = args.get("path")
        if tool in ("read_file", "write_file", "delete_file") and not isinstance(path, str):
            return False, "层2参数校验拦截：缺少合法 path"
        # 层3 危险操作审批（mock 人工确认）
        if tool in DANGEROUS:
            if self.approval_result == "denied":
                return False, "层3审批拦截：人工确认拒绝"
            # approved 则放行到下一层
        # 层4 沙箱：只许访问白名单目录，且防路径穿越
        if path is not None:
            norm = path.replace("\\", "/")
            if ".." in norm.split("/"):
                return False, "层4沙箱拦截：路径穿越"
            if not any(norm.startswith(d) for d in SANDBOX_DIRS):
                return False, f"层4沙箱拦截：{norm} 不在允许目录"
        return True, "放行"

if __name__ == "__main__":
    cases = [
        ({"tool": "format_disk", "args": {}}, "未注册工具（模型幻觉）"),
        ({"tool": "read_file", "args": {}}, "缺 path"),
        ({"tool": "delete_file", "args": {"path": "/workspace/tmp/a.log"}}, "危险操作（审批拒绝）"),
        ({"tool": "read_file", "args": {"path": "/etc/passwd"}}, "沙箱外路径"),
        ({"tool": "read_file", "args": {"path": "/workspace/project/../../etc/passwd"}}, "路径穿越"),
        ({"tool": "read_file", "args": {"path": "/workspace/project/src/main.py"}}, "合法调用"),
    ]
    for call, label in cases[:3]:
        gate = PermissionGate(approval_result="denied")
        print(f"[{label}] {gate.check(call)}")
    for call, label in cases[3:]:
        print(f"[{label}] {PermissionGate().check(call)}")
    print("\n审批通过路径演示:", PermissionGate("approved").check(cases[2][0]), "<- 过了审批仍要过沙箱")
    print("原则：默认拒绝——允许清单可枚举，危险清单不可枚举（T3 注入 + 模型幻觉双重动机）。")
