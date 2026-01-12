---
name: collaborating-with-gemini
description: Delegates coding tasks to Gemini CLI for prototyping, debugging, and code review. Supports multi-turn sessions via SESSION_ID. / 将任务委托给 Gemini CLI 做原型/调试/审阅，支持 SESSION_ID 续聊。
---

## Quick Start / 快速开始

```powershell
python scripts/gemini_bridge.py --cd "E:\\path\\to\\project" --PROMPT "Your task"
```

## Prompt Suffix (MUST) / 提示词后缀（必加）

Append to every task:

```
OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
Do NOT wrap output in Markdown fences (``` or ```diff). Output raw unified diff starting with '--- '.
```

## Output / 输出

- Foreground: prints JSON to stdout.
- Background: use `--output-file` to write JSON to disk.
- `--output-file` relative paths are written under OS temp directory `codex_gemini_bridge/`.

JSON fields:

- `success`: boolean
- `SESSION_ID`: string (reuse with `--SESSION_ID`)
- `agent_messages`: Gemini assistant output (after optional code-fence stripping)
- `error`: string (when `success=false`)
- `all_messages`, `non_json_output`: only when `--return-all-messages`
- `output_file`: present only when `--output-file` is used

## Multi-turn / 续聊

```powershell
python scripts/gemini_bridge.py --cd "E:\\path\\to\\project" --PROMPT "First task"
python scripts/gemini_bridge.py --cd "E:\\path\\to\\project" --SESSION_ID "uuid-from-response" --PROMPT "Follow up"
```

## Key Args / 常用参数

- `--cd`: workspace root for Gemini (Gemini reads project files itself via its CLI tools)
- `--PROMPT` / `--PROMPT_FILE`: provide exactly one; prefer `--PROMPT_FILE` for long prompts on Windows
- `--output-file`: recommended for background execution
- `--approval-mode`: `default`/`auto_edit`/`yolo` (use `yolo` only when you explicitly need non-interactive tool calls)
