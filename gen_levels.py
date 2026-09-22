# -*- coding: utf-8 -*-
"""生成 6 个可通关关卡（关卡 5、6 提升难度）"""
import random

DIRS = ['U', 'D', 'L', 'R']
dir_vec = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}


def gen(rows, cols, target_arrows, seed):
    """生成关卡：贪心放置，每个箭头朝边界路径必须畅通"""
    random.seed(seed)
    arrows = []

    def can_place(r, c, d):
        dr, dc = dir_vec[d]
        nr, nc = r + dr, c + dc
        while 0 <= nr < rows and 0 <= nc < cols:
            if (nr, nc) in {(a[0], a[1]) for a in arrows}:
                return False
            nr += dr
            nc += dc
        return True

    cells = [(r, c) for r in range(rows) for c in range(cols)]
    random.shuffle(cells)
    for r, c in cells:
        if len(arrows) >= target_arrows:
            break
        dirs = [d for d in DIRS if can_place(r, c, d)]
        if dirs:
            arrows.append((r, c, random.choice(dirs)))

    lv = [['.' for _ in range(cols)] for _ in range(rows)]
    for r, c, d in arrows:
        lv[r][c] = d
    return lv


def simulate_solve(level):
    """BFS 式模拟：反复消除一个可飞出的箭头直到完成或卡住"""
    rows = len(level)
    cols = len(level[0])
    active = set()
    for r in range(rows):
        for c in range(cols):
            if level[r][c] in DIRS:
                active.add((r, c, level[r][c]))

    def get_at(r, c):
        for a in active:
            if a[0] == r and a[1] == c:
                return a
        return None

    def blocked(r, c, d):
        dr, dc = dir_vec[d]
        nr, nc = r + dr, c + dc
        while 0 <= nr < rows and 0 <= nc < cols:
            if get_at(nr, nc) is not None:
                return True
            nr += dr
            nc += dc
        return False

    steps = 0
    while active:
        can_fly = [a for a in active if not blocked(*a)]
        if not can_fly:
            return False, steps
        active.remove(can_fly[0])
        steps += 1
    return True, steps


# 关卡规格：(rows, cols, 目标箭头数)
specs = [
    (5, 5, 8),   # 关卡1
    (5, 5, 8),   # 关卡2
    (5, 5, 8),   # 关卡3
    (6, 6, 9),   # 关卡4
    (6, 6, 12),  # 关卡5 高难度
    (7, 7, 16),  # 关卡6 最高难度
]

results = []
for i, (r, c, n) in enumerate(specs):
    for attempt in range(5000):
        lv = gen(r, c, n, seed=i * 10000 + attempt)
        ok, steps = simulate_solve(lv)
        if ok and sum(1 for row in lv for ch in row if ch in DIRS) >= n:
            results.append((i + 1, lv, steps))
            print(f"关卡 {i+1}: ✅ {r}x{c}  {sum(1 for row in lv for ch in row if ch in DIRS)}箭头  通关≈{steps}步")
            break
    else:
        print(f"关卡 {i+1}: ❌ 生成失败!")

# 输出代码
print("\n" + "=" * 50)
print("LEVELS = [")
for idx, lv, _ in results:
    rows = len(lv)
    cols = len(lv[0])
    cnt = sum(1 for row in lv for ch in row if ch in DIRS)
    print(f"    # ---- 关卡 {idx} ({rows}x{cols}, {cnt} 箭头) ----")
    print("    [")
    for row in lv:
        print("        ['" + "', '".join(row) + "'],")
    print("    ],")
print("]")
