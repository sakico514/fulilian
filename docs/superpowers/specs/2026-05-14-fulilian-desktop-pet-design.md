# 芙莉莲桌宠 — 设计文档

## 概述

基于 Windows 桌面悬浮窗的芙莉莲角色桌宠，使用 PyQt6 播放 GIF 动画，集成 Claude API 实现角色扮演对话。

## 技术栈

- **GUI 框架：** PyQt6（无边框透明悬浮窗）
- **动画：** QMovie 原生 GIF 播放
- **AI 对话：** Anthropic Claude API（Sonnet/Haiku）
- **打包发布：** PyInstaller (可选)

## 功能清单

### 核心功能

| 功能 | 优先级 | 说明 |
|------|--------|------|
| GIF 动画播放 | P0 | 9 个 GIF 对应 9 种动作状态，平滑切换 |
| 悬浮窗口 | P0 | 无边框、透明背景、始终置顶，不阻挡鼠标穿透 |
| 拖拽移动 | P0 | 鼠标拖拽宠物到屏幕任意位置 |
| 点击互动 | P1 | 点击触发反应动画 + 对话模式 |
| 右键菜单 | P1 | 切换动作 / 退出程序 |
| AI 对话 | P1 | 接入 Claude API，芙莉莲角色扮演 |
| 主动搭话 | P2 | 定时随机冒泡聊天 |
| 自动行为 | P2 | 随机走动、边缘反弹、定时动作 |

### 动画状态机

```
                 ┌──────────┐
          ┌─────→│  IDLE    │←────────┐
          │      │ idle.gif │         │
          │      └────┬─────┘         │
          │           │               │
    随机   │    ┌──────┼──────┐       │ 随机
          │    ▼      ▼      ▼       │
          │ ┌────┐ ┌────┐ ┌────┐     │
          │ │走动│ │跳跃│ │挥手│     │
          │ └──┬─┘ └──┬─┘ └────┘     │
          │    │      │              │
          │    ▼      ▼              │
          │ ┌────┐ ┌────┐            │
          └─┤等待│ │失败│────────────┘
            └────┘ └────┘
              │        ▲
              ▼        │
            ┌────┐     │
            │审视│─────┘
            └────┘
```

**状态定义：**

| GIF 文件 | 动作 | 触发方式 |
|-----------|------|---------|
| `idle.gif` | 待机 | 默认状态，无事件时 |
| `waving.gif` | 挥手 | 随机 / 点击 |
| `running.gif` / `running-left.gif` / `running-right.gif` | 走动 | 自动行为随机方向 |
| `jumping.gif` | 跳跃 | 双击 / 随机 |
| `waiting.gif` | 等待/坐 | 空闲一段时间后 / 随机 |
| `review.gif` | 审视 | 右键菜单 / 随机 |
| `failed.gif` | 失败/摔倒 | 随机 / 连续点击触发 |

## 架构

```
fulilian/
├── main.py                 # 入口，QApplication + PetWindow
├── pet_window.py           # 悬浮窗容器
├── animation_manager.py    # GIF 加载与播放控制
├── behavior_engine.py      # AI 行为状态机 + 定时器
├── interaction_handler.py  # 鼠标事件处理
├── ai_engine.py            # Claude API 调用
├── speech_bubble.py        # 聊天气泡组件
├── ai_config.py            # API 配置
├── chat_input.py           # 对话输入框
└── assets/                 # 9 个 GIF 文件
```

### 模块职责

| 模块 | 职责 |
|------|------|
| `pet_window.py` | 无边框透明悬浮窗，初始化所有子模块 |
| `animation_manager.py` | 预加载 GIF 为 QMovie 字典，按状态名切换播放 → `setMovie()` |
| `behavior_engine.py` | QTimer 驱动的状态机，随机间隔触发动作切换 |
| `interaction_handler.py` | 重写 `mousePressEvent/mouseMoveEvent/contextMenuEvent`，拖拽/点击/右键 |
| `ai_engine.py` | 封装 Anthropic SDK，`send_message(user_text, history)` → 返回回复 |
| `speech_bubble.py` | 无边框气泡 Widget，QLabel 打底，文字淡入淡出，自动消失 |
| `ai_config.py` | 从环境变量读取 API Key、模型名称、对话历史上限 |
| `chat_input.py` | 小型输入框弹窗，Enter 发送 |
| `main.py` | 创建 QApplication，实例化 PetWindow，`exec()` |

### 数据流

```
用户双击宠物
  → interaction_handler 捕获 doubleClick
  → behavior_engine 触发 "jumping" 状态
  → animation_manager 播放 jumping.gif
  → animation_manager 播放完毕后切回 "idle"
  → behavior_engine 定时器继续随机触发

用户点击宠物
  → interaction_handler 捕获 click
  → behavior_engine 触发随机反应动画
  → chat_input 弹出输入框
  → 用户输入文字 → ai_engine.send_message()
  → speech_bubble 逐字显示回复 → 自动消失

自动行为
  → behavior_engine 定时器到期
  → 随机选择 "running-left"/"waving"/"waiting"/"jumping"
  → animation_manager 切换到对应动画
  → 随机选择：原地播放 / 窗口移动 + 播放
  → 窗口移动沿 X 轴位移，遇到屏幕边缘反弹
  → 动画结束切回 "idle"
```

## AI 角色 Prompt

```
你是芙莉莲（Frieren），来自《葬送的芙莉莲》。
你是一个活了一千多年的精灵魔法使，性格悠闲、天然呆、
有点毒舌但内心温柔。你喜欢收集魔法，对一切感到好奇。

说话风格：
- 语气平淡、慵懒，偶尔带点挖苦
- 提及过去时，喜欢引用"以前和勇者他们一起旅行的时候..."
- 提到魔法时偶尔会眼睛发光
- 每句话控制在 1-3 句，不啰嗦
- 保持轻松、治愈的氛围

现在你作为桌宠陪伴主人。主人跟你说的话，你会用桌宠的语气回复。
```

## AI 对话配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| 模型 | `claude-sonnet-4-6` | 对话模型 |
| 最大历史 | 20 | 保留的对话轮数 |
| 主动搭话间隔 | 300-900s | 随机间隔 |
| API Key | 环境变量 `ANTHROPIC_API_KEY` | 从环境变量读取 |

## 边缘情况处理

- **API Key 未设置：** AI 对话不可用，主动搭话功能自动禁用，其他功能正常
- **网络错误：** 显示 "..." 或静默失败，不影响宠物动画
- **多显示器：** 在拖动到的显示器内继续行为，不跳屏
- **程序重启：** 不持久化状态，每次从 idle 开始
