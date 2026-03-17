# Stock Analyzer Skill for Claude

股票分析 Skill，让 AI 自动调用 http://193.112.101.212:8000 API 进行股票分析

---

## 安装方法

### 方法1：直接安装（推荐）

```bash
# 复制 skill 文件到 Claude skills 目录
cp stock-analyzer.md ~/.claude/skills/

# 重启 Claude Code 或重新加载 skills
```

### 方法2：项目级安装

```bash
# 在项目根目录创建 .claude/skills 目录
mkdir -p .claude/skills

# 复制 skill 文件
cp stock-analyzer.md .claude/skills/

# Skill 将自动在该项目中可用
```

---

## 使用方法

安装后，Claude 会自动识别股票代码并调用 API

### 支持的输入

| 输入示例 | 说明 |
|----------|------|
| "分析 300766" | 直接说股票代码 |
| "看看000301这只股票" | 中文 + 代码 |
| "analyze stock 600000" | 英文 |
| "300766怎么样" | 代码 + 怎么样 |

### 股票代码格式

- **000XXX** / **001XXX** / **002XXX**: 深圳主板/中小板
- **300XXX** / **301XXX**: 深圳创业板
- **600XXX** / **601XXX** / **603XXX**: 上海主板
- **688XXX**: 科创板
- **920XXX**: 北交所

---

## 输出说明

**Skill 会直接输出 API 返回的原始 JSON 数据**，包含：

```json
{
  "stock_code": "股票代码",
  "stock_name": "股票名称",
  "current_price": 当前价格,
  "price_change_percent": 涨跌幅,
  "technical_analysis": {技术指标},
  "fundamental_analysis": {基本面数据},
  "ai_analysis": "AI分析文本",
  "risk_level": "风险等级",
  "summary": "综合总结"
}
```

**特点：**
- ✅ 完整原始数据，不丢失任何字段
- ✅ 包含 AI 生成的详细分析文本
- ✅ 技术面 + 基本面 + AI分析 三合一

---

## API 信息

- **服务器**: http://193.112.101.212:8000
- **Web UI**: http://193.112.101.212:8000
- **API 端点**: POST /api/v1/analyze
- **无需认证**: 直接调用

---

## 故障排查

### 服务无响应

```bash
# 检查服务状态
curl http://193.112.101.212:8000/api/health
```

### 股票代码错误

- 必须是6位数字
- 不要带.SZ/.SH后缀（API会自动处理）

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `stock-analyzer.md` | Skill 主文件 |
| `README.md` | 使用说明 |
| `install.sh` | 一键安装脚本 |

---

## 更新日志

### v1.0 (2026-03-17)
- 初始版本
- 支持单股票分析
- 支持批量股票分析
- 原始 JSON 输出
