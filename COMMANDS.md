# 📋 股票智能分析系统 - 命令速查表

## 🚀 快速启动

```bash
# 启动 Web 界面（最常用）
python main.py --webui-only

# 访问 http://127.0.0.1:8000
```

---

## 📊 分析命令

| 命令 | 说明 |
|------|------|
| `python main.py` | 分析 .env 中配置的所有股票 |
| `python main.py --stocks 300766,000301` | 分析指定股票 |
| `python main.py --no-notify` | 分析但不发送通知 |
| `python main.py --debug` | 调试模式（详细日志） |
| `python main.py --dry-run` | 测试模式（不调用AI） |
| `python main.py --market-review` | 执行大盘复盘 |
| `python main.py --no-market-review` | 跳过大盘复盘 |

---

## 🌐 Web 服务

| 命令 | 说明 |
|------|------|
| `python main.py --webui-only` | 仅启动 Web 界面 |
| `python main.py --webui` | 启动 Web + 执行分析 |
| `python main.py --serve` | 同 `--webui` |
| `python main.py --serve-only` | 同 `--webui-only` |
| `python main.py --port 8080` | 指定端口（默认8000） |
| `python main.py --host 0.0.0.0` | 允许外网访问 |

---

## ⏰ 定时任务

| 命令 | 说明 |
|------|------|
| `python main.py --schedule` | 启用定时任务模式 |
| `python main.py --no-run-immediately` | 启动时不立即执行 |
| `python main.py --force-run` | 非交易日也强制执行 |

---

## 🔧 测试与诊断

| 命令 | 说明 |
|------|------|
| `python test_env.py` | 测试环境配置 |
| `python test_env.py --llm` | 测试 LLM 调用 |
| `python test_env.py --fetch` | 测试数据获取 |
| `python test_env.py --notify` | 测试通知推送 |

---

## 📁 常用路径

| 路径 | 说明 |
|------|------|
| `logs/` | 日志文件目录 |
| `reports/` | 分析报告目录 |
| `data/stock_analysis.db` | SQLite 数据库 |
| `static/` | Web 前端资源 |
| `.env` | 环境变量配置 |

---

## 💡 常用组合

```bash
# 分析指定股票，不通知，调试模式
python main.py --stocks 300766 --no-notify --debug

# 启动 Web 服务，允许局域网访问
python main.py --webui-only --host 0.0.0.0 --port 8080

# 强制运行分析（不管是否交易日）
python main.py --force-run --no-notify

# 只执行大盘复盘
python main.py --market-review --no-notify
```

---

## ⚙️ 配置项速查

编辑 `.env` 文件：

| 配置项 | 说明 |
|--------|------|
| `STOCK_LIST` | 自选股代码，逗号分隔 |
| `OPENAI_API_KEY` | AI API 密钥 |
| `OPENAI_BASE_URL` | 中转站地址 |
| `LITELLM_MODEL` | 模型名称 |
| `TUSHARE_TOKEN` | Tushare Token |
| `FEISHU_WEBHOOK_URL` | 飞书机器人地址 |
| `WEBUI_ENABLED` | 是否启用 Web 界面 |
| `SCHEDULE_ENABLED` | 是否启用定时任务 |

---

*最后更新：2026-03-17*
