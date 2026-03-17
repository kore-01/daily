# Tavily 多 Key 配置指南

## 概述

Tavily 提供免费版每月 **1000 次搜索请求**。对于大量股票分析需求，可以通过配置 **多个 API Key** 来突破配额限制。

---

## 配额策略

| Key 数量 | 月度配额 | 适用场景 |
|:--------:|:--------:|:---------|
| 1 个 | 1,000 次 | 每日分析 3-5 只股票 |
| 2 个 | 2,000 次 | 每日分析 10-15 只股票 |
| 3 个 | 3,000 次 | 每日分析 20-30 只股票 |

> **说明**：每只股票的完整分析约需 3-5 次搜索（新闻、行业、风险等）

---

## 配置方法

### 1. 本地运行 (.env 文件)

```env
# 单 Key
TAVILY_API_KEYS=tvly-xxxxxxxxxxxxx

# 多 Key（用逗号分隔）
TAVILY_API_KEYS=tvly-key1,tvly-key2,tvly-key3
```

### 2. GitHub Actions (Secrets)

在仓库 **Settings → Secrets and variables → Actions** 中添加：

| Secret Name | Value |
|-------------|-------|
| `TAVILY_API_KEYS` | `tvly-key1,tvly-key2,tvly-key3` |

### 3. Docker 运行

```bash
docker run -e TAVILY_API_KEYS="tvly-key1,tvly-key2" kore-01/daily
```

---

## 获取多个 API Key

### 方案一：多人协作
- 团队成员各自注册 Tavily 账号
- 收集每个人的 API Key
- 配置到系统中

### 方案二：多账号注册
- 使用不同邮箱注册多个 Tavily 账号
- 每个账号获取免费 API Key
- 注意：遵守 Tavily 服务条款

**注册地址**：https://app.tavily.com/home

---

## 工作原理

系统自动实现 **轮询 + 故障转移**：

```python
# 轮询策略
Key 1 → Key 2 → Key 3 → Key 1 → ...

# 错误处理
如果 Key 连续失败 3 次 → 暂时跳过 → 使用其他 Key
```

### 监控日志

```
[Tavily] 搜索完成，返回 6 条结果
[Tavily] API Key tvly-xxx... 使用次数: 156
```

---

## 配额监控

### 查看使用量

```bash
# 日志中搜索
grep "Tavily" logs/stock_analysis_*.log | grep "搜索完成" | wc -l
```

### 配额警告

当日志中出现以下信息时，表示需要增加 Key：

```
[Tavily] API 配额已用尽: rate limit exceeded
```

---

## 最佳实践

### 1. 合理估算配额

```
每日股票数 × 每只搜索次数 × 30天 = 月度需求

示例：
10只股票/天 × 4次搜索 × 30天 = 1,200次/月
→ 建议配置 2 个 Key (2,000次配额)
```

### 2. 优先使用 Tavily

在 `.env` 中配置多个搜索引擎优先级：

```env
# 优先使用 Tavily（配额多）
# 备选 SerpAPI（每月100次）
# 最后使用 SearXNG（自建，无配额）
```

### 3. 新闻时效调整

缩小新闻时间窗口可减少搜索次数：

```env
# 只搜索最近1天的新闻（减少无效结果）
NEWS_MAX_AGE_DAYS=1
```

---

## 故障排除

### 问题：所有 Key 都显示配额用尽

**解决方案**：
1. 检查日志确认所有 Key 都已用完
2. 注册新的 Tavily 账号获取 Key
3. 临时关闭新闻搜索（设置 `NEWS_MAX_AGE_DAYS=0`）

### 问题：某些 Key 无法使用

**解决方案**：
1. 在 Tavily 控制台检查 Key 状态
2. 删除失效的 Key，保留有效的
3. 系统会自动轮询可用的 Key

---

## 相关配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `TAVILY_API_KEYS` | Tavily API Key（逗号分隔） | 无 |
| `NEWS_MAX_AGE_DAYS` | 新闻最大时效（天） | 3 |
| `NEWS_STRATEGY_PROFILE` | 新闻策略窗口 | short |

---

## 更新记录

| 日期 | 内容 |
|------|------|
| 2026-03-17 | 添加多 Key 轮询支持 |
