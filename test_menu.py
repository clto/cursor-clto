import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from colorama import Fore, Style, init
init()

# Simple menu display without emoji issues
menu_items = {
    0: "退出程序",
    1: "重置机器 ID",
    2: "注册新的 Cursor 账号 (已过时)",
    3: "使用 Google 账号注册 (终身访问已启用)",
    4: "使用 GitHub 账号注册 (终身访问已启用)",
    5: "使用自定义邮箱注册 Cursor",
    6: "临时 GitHub 注册",
    7: "关闭 Cursor 应用",
    8: "切换语言",
    9: "禁用自动更新",
    10: "完全重置 Cursor",
    11: "为项目做贡献",
    12: "显示配置",
    13: "选择 Chrome 配置文件",
    14: "删除 Cursor Google 账号",
    15: "绕过版本检查",
    16: "检查用户授权",
    17: "绕过令牌限制"
}

print("\n" + "="*70)
print("可用选项:")
print("="*70)
for num, desc in sorted(menu_items.items()):
    print(f"  {num:2d}. {desc}")
print("="*70)
print("\n请输入选项编号 (0-17)")
