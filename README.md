# 芙莉莲 — Windows 桌宠

基于 PyQt6 的《葬送的芙莉莲》桌面宠物，接入 DeepSeek AI 实现角色扮演对话。

## 特性

- **9 种 GIF 动画**：待机、挥手、跑动、跳跃、等待、审视、失败
- **AI 角色对话**：接入 DeepSeek API，芙莉莲语气回复，支持对话历史
- **桌面感知**：知道你在用什么软件、她站在哪个窗口旁边
- **真实移动**：奔跑时窗口平移、跳跃时抛物线弹跳、屏幕边缘自动反弹
- **电脑操作**：可帮你打开应用、搜索网页、打开网址
- **主动搭话**：每隔 5-15 分钟随机发表评论
- **尺寸缩放**：右键菜单切换 50%-200%
- **GIF 背景透明**：自动去除白底，无边框悬浮窗

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key
```

### 3. 启动

```bash
python main.py
```

### 4. 打包为 EXE（可选）

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "芙莉莲" --add-data "assets;assets" --add-data ".env;." main.py
# 输出在 dist/芙莉莲.exe
```

## 操作说明

| 操作 | 效果 |
|------|------|
| 拖拽 | 移动位置 |
| 单击 | 反应动画 + 弹出输入框 |
| 双击 | 跳跃 + 弹出输入框 |
| 右键 | 动作切换 / 尺寸 / 退出 |

## 对话示例

> 你：放音乐
> 芙莉莲：好的，帮你打开QQ音乐~  [自动打开QQ音乐]

> 你：搜一下 Python 教程
> 芙莉莲：以前和辛梅尔旅行时也经常查资料呢... [自动打开浏览器搜索]

## 项目结构

```
fulilian/
├── main.py                # 入口
├── pet_window.py          # 悬浮窗
├── animation_manager.py   # GIF 动画管理
├── behavior_engine.py     # 行为状态机 + 移动
├── interaction_handler.py # 鼠标交互
├── ai_engine.py           # DeepSeek API
├── ai_config.py           # 角色 Prompt + 配置
├── speech_bubble.py       # 聊天气泡
├── chat_input.py          # 输入框
├── desktop_context.py     # 桌面感知
├── app_actions.py         # 电脑操作
├── process_gifs.py        # GIF 背景去除
├── assets/                # GIF 文件
└── tests/                 # 测试
```

## 技术栈

- Python 3.13 + PyQt6
- DeepSeek API (OpenAI 兼容)
- GIF 背景透明：Pillow 泛洪填充 + 边缘侵蚀

## License

MIT
