# 一箭又一箭 🎯

基于 Python + Pygame 开发的点击式箭头解谜小游戏，参考微信小游戏《一箭又一箭》核心玩法。

## 🎮 游戏简介

棋盘中分布着方向为上/下/左/右的箭头，点击箭头后检查其前进方向：

- **无阻挡** → 箭头飞出棋盘并消除
- **有阻挡** → 红色晃动提示，消耗 1 次失误机会
- 失误 3 次 → 失败；清空全部箭头 → 通关

## 🛠️ 开发环境

- Python 3.10+
- Pygame 2.0+

## 🚀 安装与运行

```bash
# 安装依赖
pip install pygame

# 运行游戏
python arrow_game.py
```

## 🕹️ 操作说明

1. 进入开始界面，点击「开始游戏」或「选择关卡」
2. 点击棋盘上的箭头使其飞出
3. 点击「重新开始」重置当前关卡
4. 点击「返回选关」回到选关界面

## ✨ 特色功能

- 6 个难度递增的关卡（关卡 5/6 为高难度）
- 自动关卡生成器，保证所有关卡可通关
- 选关系统，通关关卡带 ✓ 标记
- 碰撞晃动、飞出动画等视觉反馈
- 失误次数心形显示

## 📦 项目结构

```
arrow_game.py       # 游戏主程序
test_levels.py      # 关卡可通关性测试
gen_levels.py       # 关卡自动生成器
```

## 📸 游戏截图

<img width="489" height="564" alt="开始界面" src="https://github.com/user-attachments/assets/b17cf0bb-8067-46c9-a89a-d0309b4b68cb" />
<img width="489" height="564" alt="选关" src="https://github.com/user-attachments/assets/0b6ceb64-313e-45ef-9fd6-57b6fbe54dbc" />
<img width="489" height="564" alt="失误扣血" src="https://github.com/user-attachments/assets/f88cd28e-4f80-483b-af9f-5e5e5600054a" />
<img width="489" height="564" alt="游戏界面" src="https://github.com/user-attachments/assets/0ce13d62-6c57-4043-94cd-3f4d03967a84" />
<img width="489" height="564" alt="失败界面" src="https://github.com/user-attachments/assets/f6c5590a-313c-4c6e-b053-bae5af4689b6" />
<img width="489" height="564" alt="通关界面" src="https://github.com/user-attachments/assets/ae2e0830-06bc-4f8f-979b-70ad5bbe5ced" />

