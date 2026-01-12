---
name: collaborating-with-gemini
description: Delegates coding tasks to Gemini CLI for prototyping, debugging, and code review. Use when needing algorithm implementation, bug analysis, or code quality feedback. Supports multi-turn sessions via SESSION_ID.
---

## Quick Start

```bash
python scripts/gemini_bridge.py --cd "/path/to/project" --PROMPT "Your task"
```

**Output:** JSON with `success`, `SESSION_ID`, `agent_messages`, and optional `error`.

## Parameters

```
usage: gemini_bridge.py [-h] (--PROMPT PROMPT | --PROMPT_FILE PROMPT_FILE) --cd CD [--sandbox] [--approval-mode {default,auto_edit,yolo}] [--SESSION_ID SESSION_ID] [--return-all-messages] [--model MODEL] [--output-file OUTPUT_FILE] [--gemini-cwd GEMINI_CWD] [--include-directories INCLUDE_DIRECTORIES] [--strip-code-fences | --no-strip-code-fences]

Gemini Bridge

options:
  -h, --help            show this help message and exit
  --PROMPT PROMPT       Instruction for the task to send to gemini.
  --PROMPT_FILE PROMPT_FILE
                        Read prompt text from this file (UTF-8).
  --cd CD               Set the workspace root for gemini before executing the task.
  --sandbox             Run in sandbox mode. Defaults to `False`.
  --approval-mode {default,auto_edit,yolo}
                        Set the approval mode for the gemini session.
  --SESSION_ID SESSION_ID
                        Resume the specified session of the gemini. Defaults to empty string, start a new session.
  --return-all-messages
                        Return all messages (e.g. reasoning, tool calls, etc.) from the gemini session. Set to `False` by default, only the agent's final reply message is
                        returned.
  --model MODEL         The model to use for the gemini session. This parameter is strictly prohibited unless explicitly specified by the user.
  --output-file OUTPUT_FILE
                        Write the resulting JSON to this file path (useful for background execution).
  --gemini-cwd GEMINI_CWD
                        Run gemini from this working directory. Defaults to --cd.
  --include-directories INCLUDE_DIRECTORIES
                        Additional directories to include in the gemini workspace (repeatable).
  --strip-code-fences, --no-strip-code-fences
                        Strip a single outer Markdown code fence from the assistant message.
```

## Multi-turn Sessions

**Always capture `SESSION_ID`** from the first response for follow-up:

```bash
# Initial task
python scripts/gemini_bridge.py --cd "/project" --PROMPT "Analyze auth in login.py"

# Continue with SESSION_ID
python scripts/gemini_bridge.py --cd "/project" --SESSION_ID "uuid-from-response" --PROMPT "Write unit tests for that"
```

## Common Patterns

**Prototyping (request diffs):**
```bash
python scripts/gemini_bridge.py --cd "/project" --PROMPT "Generate unified diff to add logging"
```

**Debug with full trace:**
```bash
python scripts/gemini_bridge.py --cd "/project" --PROMPT "Debug this error" --return-all-messages
```
