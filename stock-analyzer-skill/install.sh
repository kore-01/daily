#!/bin/bash
# Stock Analyzer Skill Installer
# 股票分析 Skill 一键安装脚本

echo "========================================"
echo "  Stock Analyzer Skill Installer"
echo "========================================"
echo ""

# 检测操作系统
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    SKILLS_DIR="$USERPROFILE/.claude/skills"
else
    SKILLS_DIR="$HOME/.claude/skills"
fi

# 创建目录
echo "[1/3] Creating skills directory..."
mkdir -p "$SKILLS_DIR"

# 复制 skill 文件
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "[2/3] Installing skill file..."
cp "$SCRIPT_DIR/stock-analyzer.md" "$SKILLS_DIR/"

# 验证安装
if [ -f "$SKILLS_DIR/stock-analyzer.md" ]; then
    echo "[3/3] Installation successful!"
    echo ""
    echo "Skill installed to:"
    echo "  $SKILLS_DIR/stock-analyzer.md"
    echo ""
    echo "Usage:"
    echo "  1. Restart Claude Code or reload skills"
    echo "  2. Type a stock code like '300766' or 'analyze 000301'"
    echo "  3. Claude will automatically call the API and return raw data"
    echo ""
    echo "API Server: http://193.112.101.212:8000"
    echo "Web UI:     http://193.112.101.212:8000"
    echo ""
else
    echo "[ERROR] Installation failed!"
    exit 1
fi
