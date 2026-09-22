# -*- coding: utf-8 -*-
"""
路径检测 & 关卡可通关性测试（无 GUI）
"""
import sys, importlib
sys.path.insert(0, '.')

# 用文件方式导入，避免 pygame 初始化
import types
with open('arrow_game.py', encoding='utf-8') as f:
    src = f.read()
# 只把 LEVELS 和 DIRS 取出来
ns = {'pygame': None, 'sys': None, 'math': None, 'os': None}
import ast
tree = ast.parse(src)
code_blocks = []
for node in tree.body:
    if isinstance(node, ast.Assign):
        code_blocks.append(node)
mod = ast.Module(body=code_blocks, type_ignores=[])
exec(compile(mod, 'arrow_game.py', 'exec'), ns)
LEVELS = ns['LEVELS']
DIRS = ns['DIRS']


def simulate_level(level):
    """
    模拟某关卡的可通关性：
    每一轮找到所有"当前可飞出"的箭头，随机消除其中一个。
    反复迭代直到：全部消除 或 出现卡住（无任何可飞出箭头但棋盘未空）。
    返回 (是否通关, 通关步数)
    """
    rows = len(level)
    cols = len(level[0])
    # 活跃箭头集合：set of (row, col, dir)
    active = set()
    for r, row in enumerate(level):
        for c, ch in enumerate(row):
            if ch in DIRS:
                active.add((r, c, ch))

    def get_arrow_at(r, c):
        for item in active:
            if item[0] == r and item[1] == c:
                return item
        return None

    def is_blocked(r, c, d):
        dx, dy = DIRS[d]
        cur_r, cur_c = r + dy, c + dx
        while 0 <= cur_r < rows and 0 <= cur_c < cols:
            if get_arrow_at(cur_r, cur_c) is not None:
                return True
            cur_r += dy
            cur_c += dx
        return False

    steps = 0
    max_steps = rows * cols * 3
    while active and steps < max_steps:
        can_fly = []
        for ar in list(active):
            r, c, d = ar
            if not is_blocked(r, c, d):
                can_fly.append(ar)
        if not can_fly:
            return False, steps  # 卡住了
        # 消除一个（这里选第一个即可，顺序不影响可通关性判定）
        active.remove(can_fly[0])
        steps += 1

    return len(active) == 0, steps


print("=" * 60)
print("关卡可通关性测试")
print("=" * 60)

all_pass = True
for i, lv in enumerate(LEVELS):
    ok, steps = simulate_level(lv)
    status = "✅ 可通关" if ok else "❌ 卡住"
    print(f"关卡 {i+1} ({len(lv)}x{len(lv[0])}): {status}  通关步数≈{steps}")
    if not ok:
        all_pass = False
        # 打印关卡
        for row in lv:
            print('  ', ''.join(row))

print()
if all_pass:
    print("🎉 所有关卡均可通关！")
else:
    print("⚠️ 存在卡住的关卡，请调整！")
    sys.exit(1)
