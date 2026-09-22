# -*- coding: utf-8 -*-
"""
一箭又一箭 —— 点击式箭头解谜小游戏
使用 Python + Pygame 实现
"""

import pygame
import sys
import math
import os

# ================ 游戏常量 ================
CELL_SIZE = 70          # 每个格子的像素大小
MARGIN = 30             # 棋盘外边距
TOP_HUD = 90            # 顶部信息栏高度
BOTTOM_HUD = 80         # 底部按钮栏高度
FPS = 60

# 颜色定义
COLOR_BG = (30, 34, 55)
COLOR_BOARD = (48, 55, 82)
COLOR_CELL = (60, 68, 98)
COLOR_CELL_ALT = (55, 62, 90)
COLOR_ARROW = (255, 255, 255)
COLOR_ARROW_COLLIDE = (255, 80, 80)
COLOR_TEXT = (240, 240, 240)
COLOR_TEXT_DARK = (180, 180, 200)
COLOR_HEART_FULL = (255, 80, 120)
COLOR_HEART_EMPTY = (80, 80, 100)
COLOR_BUTTON = (80, 140, 220)
COLOR_BUTTON_HOVER = (110, 170, 255)
COLOR_TITLE = (255, 220, 100)
COLOR_BTN_BG = (70, 80, 120)
COLOR_BTN_BG_HOVER = (100, 115, 165)

# 方向向量
DIRS = {
    'U': (0, -1),
    'D': (0, 1),
    'L': (-1, 0),
    'R': (1, 0),
}

# 关卡数据：'R'右 'L'左 'U'上 'D'下 '.'空
LEVELS = [
    # ---- 关卡 1 (5x5, 8 箭头) ----
    [
        ['L', '.', '.', '.', '.'],
        ['L', 'U', 'D', '.', '.'],
        ['L', '.', '.', '.', 'U'],
        ['.', '.', '.', 'R', '.'],
        ['.', '.', '.', 'R', '.'],
    ],
    # ---- 关卡 2 (5x5, 8 箭头) ----
    [
        ['.', '.', 'U', '.', 'U'],
        ['.', '.', 'R', '.', '.'],
        ['.', 'L', 'D', '.', '.'],
        ['U', '.', '.', '.', '.'],
        ['.', 'D', '.', '.', 'R'],
    ],
    # ---- 关卡 3 (5x5, 8 箭头) ----
    [
        ['.', 'D', 'R', '.', '.'],
        ['.', '.', '.', 'L', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', 'R', '.', '.', '.'],
        ['L', 'D', 'L', '.', 'R'],
    ],
    # ---- 关卡 4 (6x6, 9 箭头) ----
    [
        ['.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', 'U'],
        ['.', '.', '.', 'L', 'L', 'L'],
        ['.', '.', '.', 'L', 'D', '.'],
        ['.', 'U', '.', 'D', '.', '.'],
        ['.', '.', '.', '.', 'D', '.'],
    ],
    # ---- 关卡 5 高难度 (6x6, 12 箭头) ----
    [
        ['.', '.', '.', '.', 'R', '.'],
        ['.', 'L', '.', 'D', 'R', '.'],
        ['.', 'L', '.', '.', 'R', '.'],
        ['D', '.', '.', '.', '.', 'R'],
        ['.', '.', '.', '.', 'D', 'R'],
        ['.', '.', '.', 'R', 'R', '.'],
    ],
    # ---- 关卡 6 最高难度 (7x7, 16 箭头) ----
    [
        ['L', 'D', 'R', '.', '.', '.', '.'],
        ['L', 'D', '.', '.', '.', 'R', 'R'],
        ['.', '.', '.', 'U', '.', '.', '.'],
        ['.', 'L', 'D', 'R', '.', '.', '.'],
        ['D', '.', '.', '.', '.', '.', '.'],
        ['.', '.', 'R', '.', '.', '.', '.'],
        ['R', '.', 'D', 'R', '.', '.', '.'],
    ],
]

MAX_MISTAKES = 3


# ================ 辅助函数 ================
def draw_heart(surf, center, size, filled):
    x, y = center
    color = COLOR_HEART_FULL if filled else COLOR_HEART_EMPTY
    half = size // 2
    pts = [
        (x, y + half * 0.6),
        (x - half * 0.9, y - half * 0.1),
        (x - half * 0.5, y - half * 0.9),
        (x, y - half * 0.3),
        (x + half * 0.5, y - half * 0.9),
        (x + half * 0.9, y - half * 0.1),
    ]
    pygame.draw.polygon(surf, color, pts)


def draw_text(surf, text, font, color, center, antialias=True):
    img = font.render(text, antialias, color)
    rect = img.get_rect(center=center)
    surf.blit(img, rect)


# ================ 箭头实体 ================
class Arrow:
    def __init__(self, row, col, direction, board_offset):
        self.row = row
        self.col = col
        self.direction = direction
        self.base_offset = board_offset
        self.state = 'idle'     # idle / flying / collide / disappeared
        self.timer = 0
        self.fly_speed = 600
        self.color = COLOR_ARROW

    @property
    def pos(self):
        ox, oy = self.base_offset
        return (ox + self.col * CELL_SIZE + CELL_SIZE // 2,
                oy + self.row * CELL_SIZE + CELL_SIZE // 2)

    @property
    def rect(self):
        cx, cy = self.pos
        s = CELL_SIZE - 8
        return pygame.Rect(cx - s // 2, cy - s // 2, s, s)

    def update(self, dt):
        if self.state == 'flying':
            self.timer += dt
            dx, dy = DIRS[self.direction]
            cx, cy = self.pos
            if (cx + dx * self.fly_speed * self.timer < -CELL_SIZE or
                    cx + dx * self.fly_speed * self.timer > 5000 or
                    cy + dy * self.fly_speed * self.timer < -CELL_SIZE or
                    cy + dy * self.fly_speed * self.timer > 5000):
                self.state = 'disappeared'
        elif self.state == 'collide':
            self.timer += dt
            if self.timer > 0.45:
                self.state = 'idle'
                self.timer = 0
                self.color = COLOR_ARROW

    def start_fly(self):
        self.state = 'flying'
        self.timer = 0

    def start_collide(self):
        self.state = 'collide'
        self.timer = 0
        self.color = COLOR_ARROW_COLLIDE

    def draw(self, surf, arrow_font):
        if self.state == 'disappeared':
            return
        cx, cy = self.pos
        if self.state == 'flying':
            dx, dy = DIRS[self.direction]
            cx += dx * self.fly_speed * self.timer
            cy += dy * self.fly_speed * self.timer
        elif self.state == 'collide':
            t = self.timer
            freq = 25
            decay = max(0, 1 - t / 0.45)
            cx += math.sin(t * freq * 2 * math.pi) * 6 * decay
            cy += math.cos(t * freq * 2 * math.pi) * 3 * decay

        symbol_map = {'U': '↑', 'D': '↓', 'L': '←', 'R': '→'}
        img = arrow_font.render(symbol_map[self.direction], True, self.color)
        surf.blit(img, img.get_rect(center=(cx, cy)))


# ================ 游戏主体 ================
class Game:
    def __init__(self):
        pygame.init()
        max_rows = max(len(lv) for lv in LEVELS)
        max_cols = max(len(lv[0]) for lv in LEVELS)
        board_w = max_cols * CELL_SIZE + MARGIN * 2
        board_h = max_rows * CELL_SIZE + MARGIN * 2
        # 选关界面需要更大宽度
        select_w = max(board_w + 100, 600)
        self.width = select_w
        self.height = TOP_HUD + board_h + BOTTOM_HUD
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("一箭又一箭")
        self.clock = pygame.time.Clock()

        chinese_font_path = self._find_chinese_font()
        self.font_title = pygame.font.Font(chinese_font_path, 48)
        self.font_h1 = pygame.font.Font(chinese_font_path, 36)
        self.font_h2 = pygame.font.Font(chinese_font_path, 28)
        self.font_body = pygame.font.Font(chinese_font_path, 24)
        self.font_small = pygame.font.Font(chinese_font_path, 20)
        self.font_arrow = pygame.font.Font(chinese_font_path, int(CELL_SIZE * 0.75))

        self.state = 'start'        # start / select / playing / win / lose
        self.level_idx = 0
        self.board_rows = 0
        self.board_cols = 0
        self.arrows = []
        self.mistakes = MAX_MISTAKES
        self.hint_text = ''
        self.hint_timer = 0

        self.btn_restart = None
        self.btn_next = None
        self.btn_start = None
        self.btn_select_levels = None   # 开始界面的"选关"按钮
        self.btn_back_to_start = None   # 游戏界面的返回按钮
        self.level_buttons = []         # 选关界面的关卡按钮列表

        # 通关记录：哪些关卡已通关过
        self.cleared = [False] * len(LEVELS)

        self.load_level(0)

    @staticmethod
    def _find_chinese_font():
        candidates = [
            r"C:\Windows\Fonts\msyh.ttc",
            r"C:\Windows\Fonts\msyh.ttf",
            r"C:\Windows\Fonts\msyhbd.ttc",
            r"C:\Windows\Fonts\simhei.ttf",
            r"C:\Windows\Fonts\simsun.ttc",
            r"/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            r"/System/Library/Fonts/PingFang.ttc",
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return None

    # --------- 关卡加载 ---------
    def load_level(self, idx):
        self.level_idx = idx
        level = LEVELS[idx]
        self.board_rows = len(level)
        self.board_cols = len(level[0])
        self.mistakes = MAX_MISTAKES
        self.arrows = []

        board_w = self.board_cols * CELL_SIZE
        board_h = self.board_rows * CELL_SIZE
        ox = (self.width - board_w) // 2
        oy = TOP_HUD + (self.height - TOP_HUD - BOTTOM_HUD - board_h) // 2
        self.board_offset = (ox, oy)

        for r, row in enumerate(level):
            for c, ch in enumerate(row):
                if ch in DIRS:
                    self.arrows.append(Arrow(r, c, ch, self.board_offset))

        btn_w, btn_h = 140, 46
        self.btn_restart = pygame.Rect(
            self.width // 2 - btn_w // 2,
            self.height - BOTTOM_HUD // 2 - btn_h // 2,
            btn_w, btn_h)
        # 返回选关按钮
        self.btn_back_to_start = pygame.Rect(
            self.btn_restart.right + 20,
            self.height - BOTTOM_HUD // 2 - btn_h // 2,
            btn_w, btn_h)

    # --------- 路径检测 ---------
    def get_arrow_at(self, row, col):
        for a in self.arrows:
            if a.row == row and a.col == col and a.state == 'idle':
                return a
        return None

    def check_path_blocked(self, arrow):
        dx, dy = DIRS[arrow.direction]
        r, c = arrow.row, arrow.col
        while True:
            r += dy
            c += dx
            if r < 0 or r >= self.board_rows or c < 0 or c >= self.board_cols:
                return False
            if self.get_arrow_at(r, c) is not None:
                return True

    # --------- 点击处理 ---------
    def handle_click(self, pos):
        # 返回选关（底部第二个按钮）
        if self.btn_back_to_start and self.btn_back_to_start.collidepoint(pos):
            self.state = 'select'
            return

        if self.state != 'playing':
            return

        if self.btn_restart and self.btn_restart.collidepoint(pos):
            self.load_level(self.level_idx)
            self.state = 'playing'
            return

        for a in self.arrows:
            if a.state != 'idle':
                continue
            if a.rect.collidepoint(pos):
                if self.check_path_blocked(a):
                    self.mistakes -= 1
                    a.start_collide()
                    self.hint_text = "被阻挡！"
                    self.hint_timer = 1.2
                    if self.mistakes <= 0:
                        pygame.time.wait(400)
                        self.state = 'lose'
                else:
                    a.start_fly()
                    self.hint_text = "飞出！"
                    self.hint_timer = 0.8
                return

    # --------- 更新 ---------
    def update(self, dt):
        for a in self.arrows:
            a.base_offset = self.board_offset
            a.update(dt)

        if self.hint_timer > 0:
            self.hint_timer -= dt

        if self.state == 'playing':
            if self.arrows and all(a.state in ('flying', 'disappeared') for a in self.arrows):
                self.cleared[self.level_idx] = True
                self.state = 'win'

    # --------- 绘制 ---------
    def draw(self):
        self.screen.fill(COLOR_BG)

        if self.state == 'start':
            self.draw_start_screen()
        elif self.state == 'select':
            self.draw_select_screen()
        else:
            self.draw_hud()
            self.draw_board()
            self.draw_arrows()
            self.draw_bottom_buttons()
            if self.state == 'win':
                self.draw_win_screen()
            elif self.state == 'lose':
                self.draw_lose_screen()

        pygame.display.flip()

    def draw_start_screen(self):
        cx, cy = self.width // 2, self.height // 2
        draw_text(self.screen, "一箭又一箭", self.font_title, COLOR_TITLE, (cx, cy - 130))
        draw_text(self.screen, "点击箭头，让它飞出棋盘", self.font_body, COLOR_TEXT_DARK, (cx, cy - 60))
        draw_text(self.screen, "箭头方向上有阻挡则不能飞出", self.font_body, COLOR_TEXT_DARK, (cx, cy - 30))

        # 开始游戏
        bw, bh = 220, 58
        self.btn_start = pygame.Rect(cx - bw // 2, cy + 20, bw, bh)
        hover = self.btn_start.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.screen,
                         COLOR_BUTTON_HOVER if hover else COLOR_BUTTON,
                         self.btn_start, border_radius=12)
        draw_text(self.screen, "开始游戏", self.font_h2, (255, 255, 255), self.btn_start.center)

        # 选关按钮
        bw2 = 180
        self.btn_select_levels = pygame.Rect(cx - bw2 // 2, cy + 100, bw2, 48)
        hover2 = self.btn_select_levels.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.screen,
                         COLOR_BUTTON_HOVER if hover2 else COLOR_BTN_BG,
                         self.btn_select_levels, border_radius=10)
        draw_text(self.screen, "选择关卡", self.font_body, (255, 255, 255), self.btn_select_levels.center)

        draw_text(self.screen, f"共 {len(LEVELS)} 关", self.font_small, COLOR_TEXT_DARK, (cx, cy + 180))

    def draw_select_screen(self):
        """选关界面"""
        cx, cy = self.width // 2, 110
        draw_text(self.screen, "选择关卡", self.font_title, COLOR_TITLE, (cx, cy))
        draw_text(self.screen, "点击即可进入", self.font_small, COLOR_TEXT_DARK, (cx, cy + 40))

        # 6 个关卡按钮，2 行 3 列
        cols, rows = 3, 2
        btn_w, btn_h = 160, 120
        gap_x, gap_y = 30, 30
        total_w = cols * btn_w + (cols - 1) * gap_x
        total_h = rows * btn_h + (rows - 1) * gap_y
        start_x = (self.width - total_w) // 2
        start_y = cy + 80

        self.level_buttons = []
        for idx in range(len(LEVELS)):
            r, c = idx // cols, idx % cols
            bx = start_x + c * (btn_w + gap_x)
            by = start_y + r * (btn_h + gap_y)
            rect = pygame.Rect(bx, by, btn_w, btn_h)
            self.level_buttons.append(rect)

            hover = rect.collidepoint(pygame.mouse.get_pos())
            bg = COLOR_BUTTON_HOVER if hover else COLOR_BUTTON
            pygame.draw.rect(self.screen, bg, rect, border_radius=14)
            pygame.draw.rect(self.screen, (60, 90, 150), rect, 2, border_radius=14)

            # 关卡号
            draw_text(self.screen, f"关卡 {idx + 1}", self.font_h2, (255, 255, 255),
                      (rect.centerx, rect.centery - 15))
            # 通关标记
            if self.cleared[idx]:
                draw_text(self.screen, "✓ 已通关", self.font_small, COLOR_TITLE,
                          (rect.centerx, rect.centery + 25))
            else:
                draw_text(self.screen, "未通关", self.font_small, COLOR_TEXT_DARK,
                          (rect.centerx, rect.centery + 25))

        # 返回按钮
        bw3, bh3 = 160, 46
        self.btn_start = pygame.Rect(self.width // 2 - bw3 // 2,
                                      self.height - TOP_HUD // 2 - bh3 // 2,
                                      bw3, bh3)
        hover3 = self.btn_start.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.screen,
                         COLOR_BUTTON_HOVER if hover3 else COLOR_BTN_BG,
                         self.btn_start, border_radius=10)
        draw_text(self.screen, "返回主界面", self.font_body, (255, 255, 255), self.btn_start.center)

    def draw_hud(self):
        pygame.draw.rect(self.screen, COLOR_BOARD, (0, 0, self.width, TOP_HUD))
        draw_text(self.screen, f"关卡 {self.level_idx + 1} / {len(LEVELS)}",
                  self.font_h2, COLOR_TEXT, (self.width // 2, TOP_HUD // 2))
        remaining = sum(1 for a in self.arrows if a.state != 'disappeared')
        draw_text(self.screen, f"剩余: {remaining}", self.font_body, COLOR_TEXT_DARK,
                  (100, TOP_HUD // 2))
        heart_size = 32
        start_x = self.width - 100 - (MAX_MISTAKES - 1) * (heart_size + 6)
        hy = TOP_HUD // 2
        for i in range(MAX_MISTAKES):
            draw_heart(self.screen, (start_x + i * (heart_size + 6), hy), heart_size, i < self.mistakes)

    def draw_board(self):
        ox, oy = self.board_offset
        board_w = self.board_cols * CELL_SIZE
        board_h = self.board_rows * CELL_SIZE
        pygame.draw.rect(self.screen, COLOR_BOARD,
                         (ox - MARGIN // 2, oy - MARGIN // 2,
                          board_w + MARGIN, board_h + MARGIN),
                         border_radius=16)
        for r in range(self.board_rows):
            for c in range(self.board_cols):
                rect = pygame.Rect(ox + c * CELL_SIZE, oy + r * CELL_SIZE,
                                   CELL_SIZE, CELL_SIZE)
                color = COLOR_CELL if (r + c) % 2 == 0 else COLOR_CELL_ALT
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (40, 46, 70), rect, 1)

    def draw_arrows(self):
        for a in self.arrows:
            a.draw(self.screen, self.font_arrow)

    def draw_bottom_buttons(self):
        cy = self.height - BOTTOM_HUD // 2

        # 重新开始
        if self.btn_restart:
            hover = self.btn_restart.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(self.screen,
                             COLOR_BUTTON_HOVER if hover else COLOR_BUTTON,
                             self.btn_restart, border_radius=10)
            draw_text(self.screen, "重新开始", self.font_body, (255, 255, 255),
                      self.btn_restart.center)

        # 返回选关
        if self.btn_back_to_start:
            hover2 = self.btn_back_to_start.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(self.screen,
                             COLOR_BUTTON_HOVER if hover2 else COLOR_BTN_BG,
                             self.btn_back_to_start, border_radius=10)
            draw_text(self.screen, "返回选关", self.font_body, (255, 255, 255),
                      self.btn_back_to_start.center)

        if self.hint_timer > 0 and self.hint_text:
            draw_text(self.screen, self.hint_text, self.font_small,
                      COLOR_TITLE if "飞出" in self.hint_text else COLOR_ARROW_COLLIDE,
                      (self.width // 2, TOP_HUD + 14))

    def draw_win_screen(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        cx, cy = self.width // 2, self.height // 2 - 20
        draw_text(self.screen, "🎉 通关！", self.font_title, COLOR_TITLE, (cx, cy - 70))
        draw_text(self.screen, f"关卡 {self.level_idx + 1} 完成", self.font_h2, COLOR_TEXT, (cx, cy - 20))

        bw, bh = 180, 50
        # 主按钮：下一关 或 返回选关
        self.btn_next = pygame.Rect(cx - bw - 10, cy + 40, bw, bh)
        main_text = "下一关" if self.level_idx + 1 < len(LEVELS) else "返回选关"
        pygame.draw.rect(self.screen, COLOR_BUTTON, self.btn_next, border_radius=10)
        draw_text(self.screen, main_text, self.font_body, (255, 255, 255), self.btn_next.center)

        # 次按钮：返回选关（如果还有下一关的话）
        if self.level_idx + 1 < len(LEVELS):
            self.btn_back_to_start = pygame.Rect(cx + 10, cy + 40, bw, bh)
            pygame.draw.rect(self.screen, COLOR_BTN_BG, self.btn_back_to_start, border_radius=10)
            draw_text(self.screen, "返回选关", self.font_body, (255, 255, 255),
                      self.btn_back_to_start.center)
        else:
            self.btn_back_to_start = None

    def draw_lose_screen(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        cx, cy = self.width // 2, self.height // 2 - 20
        draw_text(self.screen, "💔 失败", self.font_title, COLOR_ARROW_COLLIDE, (cx, cy - 70))
        draw_text(self.screen, "失误次数耗尽", self.font_h2, COLOR_TEXT, (cx, cy - 20))

        bw, bh = 180, 50
        self.btn_next = pygame.Rect(cx - bw - 10, cy + 40, bw, bh)
        pygame.draw.rect(self.screen, COLOR_BUTTON, self.btn_next, border_radius=10)
        draw_text(self.screen, "重新开始", self.font_body, (255, 255, 255), self.btn_next.center)

        self.btn_back_to_start = pygame.Rect(cx + 10, cy + 40, bw, bh)
        pygame.draw.rect(self.screen, COLOR_BTN_BG, self.btn_back_to_start, border_radius=10)
        draw_text(self.screen, "返回选关", self.font_body, (255, 255, 255),
                  self.btn_back_to_start.center)

    # --------- 事件处理 ---------
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        pos = event.pos

        if self.state == 'start':
            if self.btn_start and self.btn_start.collidepoint(pos):
                self.state = 'playing'
                self.load_level(0)
            elif self.btn_select_levels and self.btn_select_levels.collidepoint(pos):
                self.state = 'select'

        elif self.state == 'select':
            # 点击关卡按钮进入游戏
            for i, rect in enumerate(self.level_buttons):
                if rect.collidepoint(pos):
                    self.load_level(i)
                    self.state = 'playing'
                    return
            # 返回主界面
            if self.btn_start and self.btn_start.collidepoint(pos):
                self.state = 'start'

        elif self.state == 'playing':
            self.handle_click(pos)

        elif self.state == 'win':
            # 主按钮：下一关 / 返回选关
            if self.btn_next and self.btn_next.collidepoint(pos):
                if self.level_idx + 1 < len(LEVELS):
                    self.load_level(self.level_idx + 1)
                    self.state = 'playing'
                else:
                    self.state = 'select'
                return
            # 次按钮：返回选关
            if self.btn_back_to_start and self.btn_back_to_start.collidepoint(pos):
                self.state = 'select'

        elif self.state == 'lose':
            if self.btn_next and self.btn_next.collidepoint(pos):
                self.load_level(self.level_idx)
                self.state = 'playing'
            elif self.btn_back_to_start and self.btn_back_to_start.collidepoint(pos):
                self.state = 'select'

    # --------- 主循环 ---------
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()


if __name__ == '__main__':
    Game().run()
