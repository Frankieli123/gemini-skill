# Collaborating with Gemini

<div align="center">

**[English](#english) | [中文](#中文)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

<a name="english"></a>
## 🇬🇧 English

### 📖 Introduction

A Cline/Claude Dev skill that enables collaboration with Google's Gemini CLI. Delegate prototyping, debugging, and code review tasks to Gemini while Cline handles implementation and verification.

**Key Features:**
- 🔄 Multi-turn conversation support via `SESSION_ID`
- 📝 Unified diff output for safe code review
- 🔒 Read-only by design - Gemini never modifies files directly
- 🌐 Cross-platform support (Windows/macOS/Linux)

### 📋 Prerequisites

1. **Python 3.8+** installed and in PATH
2. **Gemini CLI** installed and configured

#### Installing Gemini CLI

```bash
# Install via npm (recommended)
npm install -g @anthropic-ai/gemini-cli

# Or via pip
pip install gemini-cli

# Verify installation
gemini --version
```

Configure your API key:
```bash
# Set environment variable
export GEMINI_API_KEY="your-api-key-here"

# Or on Windows PowerShell
$env:GEMINI_API_KEY = "your-api-key-here"
```

### 🚀 Installation for Cline

#### Step 1: Download the Skill

**Option A: Clone via Git**
```bash
# Windows
git clone https://github.com/Frankieli123/gemini-skill.git "$env:USERPROFILE\.cline\skills\collaborating-with-gemini"

# macOS/Linux
git clone https://github.com/Frankieli123/gemini-skill.git ~/.cline/skills/collaborating-with-gemini
```

**Option B: Manual Download**
1. Download ZIP from [GitHub Releases](https://github.com/Frankieli123/gemini-skill/releases)
2. Extract to:
   - **Windows:** `%USERPROFILE%\.cline\skills\collaborating-with-gemini\`
   - **macOS/Linux:** `~/.cline/skills/collaborating-with-gemini/`

#### Step 2: Verify Directory Structure

```
.cline/skills/collaborating-with-gemini/
├── SKILL.md           # Skill definition
├── README.md          # This file
├── scripts/
│   └── gemini_bridge.py   # Bridge script
└── LICENSE
```

#### Step 3: Configure Cline Custom Instructions

Add the following to your Cline custom instructions (Settings → Custom Instructions):

```
## Gemini Collaboration Skill

When I ask you to use Gemini for code review, debugging, or prototyping:

1. Use the gemini_bridge.py script to delegate tasks to Gemini
2. Always append this suffix to prompts:
   OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
   Do NOT wrap output in Markdown fences. Output raw unified diff starting with '--- '.
3. Parse the returned JSON and apply the diff if appropriate
4. Maintain SESSION_ID for multi-turn conversations
```

### 📝 Prompt Templates (Required)

**⚠️ IMPORTANT:** Always append this constraint to every Gemini prompt:

```
OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
Do NOT wrap output in Markdown fences (``` or ```diff). Output raw unified diff starting with '--- '.
```

#### Example Prompts

**Code Review:**
```
Review the authentication module for security vulnerabilities.
Focus on: SQL injection, XSS, CSRF, and improper input validation.

OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
Do NOT wrap output in Markdown fences. Output raw unified diff starting with '--- '.
```

**Debugging:**
```
Debug the payment processing function. Users report timeout errors.
Analyze the async flow and identify potential race conditions.

OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
Do NOT wrap output in Markdown fences. Output raw unified diff starting with '--- '.
```

**Refactoring:**
```
Refactor the user service to use dependency injection pattern.
Maintain backward compatibility with existing interfaces.

OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
Do NOT wrap output in Markdown fences. Output raw unified diff starting with '--- '.
```

### 💻 Usage

#### Basic Usage (Foreground)

```powershell
python scripts/gemini_bridge.py --cd "E:\path\to\project" --PROMPT "Your task here. OUTPUT: Unified Diff Patch ONLY."
```

#### Background Execution (Windows Recommended)

```powershell
$project = "E:\path\to\project"
$prompt = @"
Review the authentication flow.
OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
Do NOT wrap output in Markdown fences. Output raw unified diff starting with '--- '.
"@

$promptFile = Join-Path $env:TEMP ("codex_gemini_prompt_" + [guid]::NewGuid() + ".txt")
$outFile = Join-Path $env:TEMP ("codex_gemini_" + [guid]::NewGuid() + ".json")
Set-Content -LiteralPath $promptFile -Value $prompt -Encoding utf8

Start-Process -FilePath python -ArgumentList "`"$env:USERPROFILE\.cline\skills\collaborating-with-gemini\scripts\gemini_bridge.py`" --cd `"$project`" --PROMPT_FILE `"$promptFile`" --output-file `"$outFile`"" -NoNewWindow -Wait

$result = Get-Content -Raw $outFile | ConvertFrom-Json
Remove-Item -Force $promptFile, $outFile
$result.agent_messages
```

#### Multi-turn Conversation

```powershell
# First turn
python scripts/gemini_bridge.py --cd "E:\project" --PROMPT "Analyze the auth module. OUTPUT: Unified Diff Patch ONLY."

# Continue conversation (use SESSION_ID from previous response)
python scripts/gemini_bridge.py --cd "E:\project" --SESSION_ID "uuid-from-response" --PROMPT "Now optimize the token validation. OUTPUT: Unified Diff Patch ONLY."
```

### 📊 Output Format

```json
{
  "success": true,
  "SESSION_ID": "550e8400-e29b-41d4-a716-446655440000",
  "agent_messages": "--- a/src/auth.py\n+++ b/src/auth.py\n@@ -15,7 +15,7 @@\n...",
  "output_file": "C:/Users/.../Temp/codex_gemini_bridge/out.json"
}
```

| Field | Description |
|-------|-------------|
| `success` | Boolean indicating execution success |
| `SESSION_ID` | Reuse for multi-turn conversations |
| `agent_messages` | Gemini's response (unified diff) |
| `error` | Error message (when `success=false`) |
| `output_file` | File path (when `--output-file` used) |

### 🔧 Command Line Arguments

| Argument | Description |
|----------|-------------|
| `--cd` | Workspace root directory for Gemini |
| `--PROMPT` | Direct prompt text |
| `--PROMPT_FILE` | File containing prompt (recommended for long prompts) |
| `--SESSION_ID` | Session ID for multi-turn conversations |
| `--output-file` | Output JSON to file (recommended for background execution) |
| `--approval-mode` | `default`/`auto_edit`/`yolo` |
| `--return-all-messages` | Include all messages in output |

### ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| `gemini: command not found` | Install Gemini CLI and add to PATH |
| `API key not configured` | Set `GEMINI_API_KEY` environment variable |
| Output contains markdown fences | Ensure prompt suffix is included |
| Session not persisting | Check `SESSION_ID` is passed correctly |

---

<a name="中文"></a>
## 🇨🇳 中文

### 📖 简介

一个 Cline/Claude Dev 技能插件，用于与 Google Gemini CLI 协作。将原型设计、调试和代码审查任务委托给 Gemini，而 Cline 负责实现和验证。

**核心特性：**
- 🔄 通过 `SESSION_ID` 支持多轮对话
- 📝 统一 diff 格式输出，安全可控
- 🔒 只读设计 - Gemini 不会直接修改文件
- 🌐 跨平台支持 (Windows/macOS/Linux)

### 📋 前置要求

1. **Python 3.8+** 已安装并添加到 PATH
2. **Gemini CLI** 已安装并配置

#### 安装 Gemini CLI

```bash
# 通过 npm 安装（推荐）
npm install -g @anthropic-ai/gemini-cli

# 或通过 pip 安装
pip install gemini-cli

# 验证安装
gemini --version
```

配置 API 密钥：
```bash
# 设置环境变量（Linux/macOS）
export GEMINI_API_KEY="your-api-key-here"

# Windows PowerShell
$env:GEMINI_API_KEY = "your-api-key-here"
```

### 🚀 Cline 安装指南

#### 第一步：下载技能

**方式 A：Git 克隆**
```bash
# Windows
git clone https://github.com/Frankieli123/gemini-skill.git "$env:USERPROFILE\.cline\skills\collaborating-with-gemini"

# macOS/Linux
git clone https://github.com/Frankieli123/gemini-skill.git ~/.cline/skills/collaborating-with-gemini
```

**方式 B：手动下载**
1. 从 [GitHub Releases](https://github.com/Frankieli123/gemini-skill/releases) 下载 ZIP
2. 解压到：
   - **Windows:** `%USERPROFILE%\.cline\skills\collaborating-with-gemini\`
   - **macOS/Linux:** `~/.cline/skills\collaborating-with-gemini/`

#### 第二步：验证目录结构

```
.cline/skills/collaborating-with-gemini/
├── SKILL.md           # 技能定义文件
├── README.md          # 本文档
├── scripts/
│   └── gemini_bridge.py   # 桥接脚本
└── LICENSE
```

#### 第三步：配置 Cline 自定义指令

在 Cline 设置中添加自定义指令（设置 → 自定义指令）：

```
## Gemini 协作技能

当我要求你使用 Gemini 进行代码审查、调试或原型设计时：

1. 使用 gemini_bridge.py 脚本将任务委托给 Gemini
2. 始终在提示词末尾添加以下约束：
   OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
   Do NOT wrap output in Markdown fences. Output raw unified diff starting with '--- '.
3. 解析返回的 JSON 并在适当时应用 diff
4. 保持 SESSION_ID 以支持多轮对话
```

### 📝 提示词模板（必需）

**⚠️ 重要：** 每次向 Gemini 发送提示时，必须在末尾添加以下约束：

```
OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
Do NOT wrap output in Markdown fences (``` or ```diff). Output raw unified diff starting with '--- '.
```

#### 示例提示词

**代码审查：**
```
审查认证模块的安全漏洞。
重点关注：SQL 注入、XSS、CSRF 和输入验证问题。

OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
Do NOT wrap output in Markdown fences. Output raw unified diff starting with '--- '.
```

**调试：**
```
调试支付处理函数。用户反馈超时错误。
分析异步流程并识别潜在的竞态条件。

OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
Do NOT wrap output in Markdown fences. Output raw unified diff starting with '--- '.
```

**重构：**
```
将用户服务重构为依赖注入模式。
保持与现有接口的向后兼容。

OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
Do NOT wrap output in Markdown fences. Output raw unified diff starting with '--- '.
```

### 💻 使用方法

#### 基本用法（前台运行）

```powershell
python scripts/gemini_bridge.py --cd "E:\path\to\project" --PROMPT "你的任务描述。OUTPUT: Unified Diff Patch ONLY."
```

#### 后台执行（Windows 推荐）

```powershell
$project = "E:\path\to\project"
$prompt = @"
审查认证流程。
OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
Do NOT wrap output in Markdown fences. Output raw unified diff starting with '--- '.
"@

$promptFile = Join-Path $env:TEMP ("codex_gemini_prompt_" + [guid]::NewGuid() + ".txt")
$outFile = Join-Path $env:TEMP ("codex_gemini_" + [guid]::NewGuid() + ".json")
Set-Content -LiteralPath $promptFile -Value $prompt -Encoding utf8

Start-Process -FilePath python -ArgumentList "`"$env:USERPROFILE\.cline\skills\collaborating-with-gemini\scripts\gemini_bridge.py`" --cd `"$project`" --PROMPT_FILE `"$promptFile`" --output-file `"$outFile`"" -NoNewWindow -Wait

$result = Get-Content -Raw $outFile | ConvertFrom-Json
Remove-Item -Force $promptFile, $outFile
$result.agent_messages
```

#### 多轮对话

```powershell
# 第一轮对话
python scripts/gemini_bridge.py --cd "E:\project" --PROMPT "分析认证模块。OUTPUT: Unified Diff Patch ONLY."

# 继续对话（使用上次返回的 SESSION_ID）
python scripts/gemini_bridge.py --cd "E:\project" --SESSION_ID "上次返回的uuid" --PROMPT "现在优化令牌验证。OUTPUT: Unified Diff Patch ONLY."
```

### 📊 输出格式

```json
{
  "success": true,
  "SESSION_ID": "550e8400-e29b-41d4-a716-446655440000",
  "agent_messages": "--- a/src/auth.py\n+++ b/src/auth.py\n@@ -15,7 +15,7 @@\n...",
  "output_file": "C:/Users/.../Temp/codex_gemini_bridge/out.json"
}
```

| 字段 | 描述 |
|------|------|
| `success` | 执行是否成功 |
| `SESSION_ID` | 用于多轮对话 |
| `agent_messages` | Gemini 的响应（unified diff 格式） |
| `error` | 错误信息（当 `success=false` 时） |
| `output_file` | 文件路径（使用 `--output-file` 时） |

### 🔧 命令行参数

| 参数 | 描述 |
|------|------|
| `--cd` | Gemini 工作区根目录 |
| `--PROMPT` | 直接提供提示文本 |
| `--PROMPT_FILE` | 包含提示的文件（长提示推荐） |
| `--SESSION_ID` | 多轮对话的会话 ID |
| `--output-file` | 输出 JSON 到文件（后台执行推荐） |
| `--approval-mode` | `default`/`auto_edit`/`yolo` |
| `--return-all-messages` | 在输出中包含所有消息 |

### ❓ 常见问题

| 问题 | 解决方案 |
|------|----------|
| `gemini: command not found` | 安装 Gemini CLI 并添加到 PATH |
| `API key not configured` | 设置 `GEMINI_API_KEY` 环境变量 |
| 输出包含 markdown 围栏 | 确保提示词包含约束后缀 |
| 会话不持久 | 检查 `SESSION_ID` 是否正确传递 |

---

## 📜 License / 许可证

MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Made with ❤️ for AI-assisted development**

[Report Bug](https://github.com/Frankieli123/gemini-skill/issues) · [Request Feature](https://github.com/Frankieli123/gemini-skill/issues)

</div>
