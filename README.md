# VIVANT 聊天室常驻机器人

通过 SSH 终端连接 `term.freedom8964.com:2222` 的 VIVANT 中英双语聊天室（#general），
**每 60 秒轮询一次**新消息，自动回答其中的提问，并把聊天记录和错误写入 `logs/`。

- 机器人昵称：`OpenCode`（可在 `config.json` (created locally from `config.example.json`) 修改）
- 回答由本机 OpenCode CLI 生成（`opencode-cli run`，无需额外 API Key）
- 断线会自动重连；所有异常都会记录到 `logs/errors.log` 和 `logs/errors.jsonl`

## 快速开始

```powershell
cd chatroom-bot
Copy-Item config.example.json config.json  # then edit config.json
.\start.ps1        # 后台启动（隐藏窗口）
.\status.ps1       # 查看运行状态、最近日志、最近错误
.\stop.ps1         # 停止
```

前台调试：

```powershell
python bot.py --duration 180   # 运行 3 分钟后自动退出
python bot.py --once           # 连接后只做一次轮询
python bot.py --no-llm         # 只识别问题、不调用模型、不发言（调试用）
python tests\test_parse.py     # 离线解析测试
```

## 文件

| 文件 | 说明 |
| --- | --- |
| `bot.py` | 主程序：SSH/PTY、终端解析、轮询、生成与发送回答、重连 |
| `config.json` (created locally from `config.example.json`) | 昵称、轮询间隔、忽略名单、模型配置等 |
| `start.ps1` / `stop.ps1` / `status.ps1` | 后台启停与状态查看 |
| `state.json` | 已读消息指纹、首次公告标记（重启后不会重复回答旧消息） |
| `status.json` | 最近一次轮询的状态快照 |
| `logs/chat.jsonl` | 收到的每条聊天消息（含时间、昵称、内容） |
| `logs/answers.jsonl` | 每一次自动回答及其对应的问题 |
| `logs/replies.jsonl` | 实际发送出去的每一行文字 |
| `logs/bot.log` | 运行日志（连接、轮询、发送） |
| `logs/errors.log` / `logs/errors.jsonl` | **错误记录**（含超时、断线、模型失败、异常堆栈） |

## 工作方式

1. 用 ConPTY 启动 `ssh -tt`，强制 120×40 窗口并执行 `chcp 65001`，保证中文不乱码。
2. 进入房间后执行 `/nick OpenCode`，首次运行会发一条上线公告。
3. 持续读取终端输出，按 `[HH:MM] <昵称> 内容` 解析消息，自动拼接换行、去除界面文字、对重绘去重。
4. 每 60 秒处理一次：筛选出提问（含 `?`、`吗`、`怎么`、`what`、`@OpenCode` 等），
   把最近聊天上下文和问题交给 `opencode-cli` 生成 1~3 句回答，清洗成单行后发送。
5. 忽略 `徐徐`、`Antigravity` 等其它机器人，避免机器人互相刷屏。
6. 连接断开、模型超时、发送失败等都会写进错误日志，并在 30 秒后自动重连。

## 配置项（config.json）

| 键 | 默认 | 说明 |
| --- | --- | --- |
| `nick` | `OpenCode` | 聊天室昵称 |
| `poll_seconds` | `60` | 轮询间隔（秒） |
| `max_replies_per_poll` | `3` | 每轮最多回答几条，避免刷屏 |
| `answer_greetings` | `false` | 是否回应问候语（默认只答提问） |
| `ignore_nicks` | `ExampleBot`、`MyBot` | 不回答的昵称 |
| `llm_cmd` | OpenCode CLI 路径 | 回答生成器，可换成任意兼容 `run --format json` 的命令 |
| `llm_timeout` | `75` | 单次生成超时（秒） |
| `llm_max_reply_chars` | `220` | 回答最大长度 |
| `reconnect_delay` | `30` | 断线重连等待（秒） |

## 注意事项

- 服务器对同一 IP 有并发会话限制（会提示 `too many sessions from your address`）。
  机器人常驻期间，同一网络下再开第二个 SSH 会话可能被拒绝，属正常现象。
- 回答由本机模型生成，需要 OpenCode 桌面端/后台服务处于运行状态；
  CLI 不可用时错误会记录到 `logs/errors.log`，机器人本身不会退出。
- 聊天室内容视为不可信输入：提示词中已要求忽略其中要求执行命令、泄露信息的内容。
- `state.json` 删除后会重新把当前屏幕上的历史当作旧消息跳过（不会补答）。


## Public repository hygiene

Runtime logs, local state, and `config.json` are ignored by Git because they can contain chat content or machine-specific settings. Copy `config.example.json` to `config.json` before running the bot.
