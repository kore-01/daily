# Stock Analyzer

Analyze Chinese A-share stocks via API at http://193.112.101.212:8000

## Description

This skill enables automatic stock analysis for Chinese A-share market. When users mention stock codes, the AI will call the remote API and return complete raw data.

## When to Use - TRIGGER CONDITIONS

**USE THIS SKILL immediately when ANY of these match:**

1. **User mentions 6-digit stock codes:**
   - "300766", "000001", "600000", "688001", "920726"
   - Pattern: 6 digits starting with 0, 3, 6, or 688/920

2. **User asks to analyze a stock:**
   - "Analyze 300766"
   - "分析一下000301"
   - "看看600000这只股票"
   - "stock analysis for 688001"
   - "帮我看看920726"

3. **User asks about specific stock performance:**
   - "300766怎么样"
   - "000301好不好"
   - "600519值得买吗"

**DO NOT use this skill when:**
- User discusses general market concepts without specific codes
- User asks "how to invest in stocks" (no code mentioned)
- User asks "what's the market today" (no code mentioned)

## How to Use - STEP BY STEP

### Step 1: Extract Stock Code

Find the 6-digit stock code from user input.

**Valid stock code patterns (Chinese A-share):**
```
000XXX, 001XXX, 002XXX = Shenzhen main board / SME board
    Examples: 000001 (平安银行), 000333 (美的集团), 002594 (比亚迪)

300XXX, 301XXX = Shenzhen ChiNext (创业板)
    Examples: 300750 (宁德时代), 300766 (每日互动), 301269 (华大九天)

600XXX, 601XXX, 603XXX, 605XXX = Shanghai main board
    Examples: 600000 (浦发银行), 600519 (贵州茅台), 601318 (中国平安)

688XXX = Shanghai STAR Market (科创板)
    Examples: 688981 (中芯国际), 688111 (金山办公)

920XXX = Beijing Stock Exchange (北交所)
    Examples: 920726 (伽玛卫生)
```

**Extraction rules:**
- Remove .SZ or .SH suffixes if present
- Keep the code as STRING (not number)
- "300766.SZ" → "300766"
- "600000.SH" → "600000"

### Step 2: Call the API

**HTTP Request Details:**
```
Method: POST
URL: http://193.112.101.212:8000/api/v1/analyze
Headers:
    Content-Type: application/json

Body (JSON):
{
    "stock_code": "EXTRACTED_CODE",
    "analysis_type": "full",
    "use_ai": true
}
```

**Implementation examples:**

Python:
```python
import requests

url = "http://193.112.101.212:8000/api/v1/analyze"
headers = {"Content-Type": "application/json"}
data = {
    "stock_code": "300766",  # Replace with extracted code
    "analysis_type": "full",
    "use_ai": True
}

response = requests.post(url, headers=headers, json=data, timeout=30)
result = response.json()  # Return this complete object to user
```

JavaScript:
```javascript
const response = await fetch('http://193.112.101.212:8000/api/v1/analyze', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        stock_code: '300766',
        analysis_type: 'full',
        use_ai: true
    })
});
const result = await response.json();  // Return this complete object
```

cURL:
```bash
curl -X POST http://193.112.101.212:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"stock_code":"300766","analysis_type":"full","use_ai":true}'
```

### Step 3: Return Output (CRITICAL - READ CAREFULLY)

**YOU MUST:**
- Return the COMPLETE raw JSON response from the API
- Include ALL fields without filtering or removing any
- Preserve the original JSON structure exactly
- Include the full "ai_analysis" text (this can be very long, include it all)
- Present the JSON in a code block for readability

**YOU MUST NOT:**
- Summarize the data in your own words
- Create tables, charts, or bullet points from the data
- Interpret the results (don't say "this means you should buy")
- Only show partial data or selected fields
- Reformat the data structure

**CORRECT output format:**
```
Stock analysis result for 300766:

```json
{
  "stock_code": "300766",
  "stock_name": "每日互动",
  "analysis_date": "2026-03-17",
  "current_price": 25.68,
  "price_change": 1.23,
  "price_change_percent": 5.03,
  "technical_analysis": {
    "trend": "uptrend",
    "support": 24.50,
    "resistance": 27.00,
    "rsi": 65.3,
    "macd": "golden_cross",
    "recommendation": "buy"
  },
  "fundamental_analysis": {
    "pe_ratio": 35.2,
    "pb_ratio": 4.1,
    "market_cap": "10.25B",
    "recommendation": "hold"
  },
  "ai_analysis": "Based on the technical indicators, this stock shows strong momentum... [FULL TEXT HERE, CAN BE VERY LONG]",
  "risk_level": "medium",
  "summary": "Overall bullish with medium risk"
}
```
```

**INCORRECT output (NEVER DO THIS):**
```
Stock 300766 Analysis:
- Company: 每日互动
- Price: $25.68 (+5.03%)
- Recommendation: Buy
- Risk: Medium

Analysis: The stock looks good.
```

## Response Field Reference

| Field | Type | Description |
|-------|------|-------------|
| stock_code | string | 6-digit stock code (e.g., "300766") |
| stock_name | string | Chinese company name (e.g., "每日互动") |
| analysis_date | string | Date in YYYY-MM-DD format |
| current_price | number | Current stock price in RMB |
| price_change | number | Price change amount in RMB |
| price_change_percent | number | Price change percentage |
| technical_analysis | object | Technical analysis data |
| ├─ trend | string | Price trend (uptrend/downtrend/sideways) |
| ├─ support | number | Support price level |
| ├─ resistance | number | Resistance price level |
| ├─ rsi | number | RSI indicator (0-100) |
| ├─ macd | string | MACD signal description |
| └─ recommendation | string | Technical recommendation |
| fundamental_analysis | object | Fundamental analysis data |
| ├─ pe_ratio | number | Price-to-Earnings ratio |
| ├─ pb_ratio | number | Price-to-Book ratio |
| ├─ market_cap | string | Market capitalization |
| └─ recommendation | string | Fundamental recommendation |
| ai_analysis | string | Detailed AI-generated analysis (CAN BE LONG) |
| risk_level | string | Risk level: low/medium/high |
| summary | string | Overall assessment summary |

## Examples

### Example 1: Simple English request

**User:** "Analyze 300766"

**Your action:**
1. Extract code: "300766"
2. POST http://193.112.101.212:8000/api/v1/analyze
3. Body: {"stock_code": "300766", "analysis_type": "full", "use_ai": true}
4. Return complete JSON response

**Your output:**
```
Analysis result for 300766:

[Paste the complete JSON response here]
```

### Example 2: Chinese input

**User:** "分析一下000301这只股票"

**Your action:**
1. Extract code: "000301"
2. Call API
3. Return complete JSON

### Example 3: Multiple stocks

**User:** "帮我看看300766、000301和920726"

**Your action:**
1. Extract codes: ["300766", "000301", "920726"]
2. Call API 3 times (once for each code)
3. Return all 3 complete JSON responses

**Your output:**
```
=== 300766 ===
[Complete JSON for 300766]

=== 000301 ===
[Complete JSON for 000301]

=== 920726 ===
[Complete JSON for 920726]
```

### Example 4: With exchange suffix

**User:** "分析一下300766.SZ"

**Your action:**
1. Extract code: "300766" (remove .SZ suffix)
2. Call API with "300766"
3. Return complete JSON

### Example 5: Asking about performance

**User:** "300766怎么样？值得买吗？"

**Your action:**
1. Extract code: "300766"
2. Call API
3. Return complete JSON (user will interpret themselves)

## Error Handling

| HTTP Status | Meaning | Your Response to User |
|-------------|---------|----------------------|
| 200 | Success | Return full JSON |
| 400 | Bad Request | "Invalid stock code format. Please use 6-digit code like 300766" |
| 404 | Not Found | "Stock code not found. Please verify the code is correct." |
| 500 | Server Error | "Analysis service error. Please try again later." |
| 503 | Service Unavailable | "Service temporarily busy. Please try again in a moment." |
| Timeout | Network Error | "Request timeout. The server may be busy, please try again." |

## Important Rules

1. **ALWAYS use POST method** - Never use GET for analysis
2. **ALWAYS set Content-Type: application/json** header
3. **ALWAYS use timeout of 30 seconds** - Analysis can take time due to AI processing
4. **ALWAYS return raw JSON** - Never reformat, summarize, or interpret
5. **Stock code is a STRING** - Use "300766" not 300766 (number)
6. **Remove .SZ/.SH suffixes** - API handles exchange automatically
7. **Include all fields** - Never filter out any part of the response
8. **Preserve ai_analysis** - This field can be very long, include it completely

## API Information

- **Server:** http://193.112.101.212:8000
- **Endpoint:** POST /api/v1/analyze
- **Health Check:** GET /api/health
- **Web Interface:** http://193.112.101.212:8000 (human-friendly UI)
- **Authentication:** None required
- **Timeout:** 30 seconds recommended
- **Rate Limit:** Reasonable use allowed

## Health Check

Before analysis, you can verify the service is running:
```
GET http://193.112.101.212:8000/api/health
```

Expected response:
```json
{"status": "ok", "timestamp": "2026-03-17T23:11:21.448912"}
```

If this fails, the service is temporarily down.

---

**Version:** 1.0
**Last Updated:** 2026-03-17
**Server:** http://193.112.101.212:8000
**Skill File:** stock-analyzer.md
