# collaborating-with-gemini

A Claude Code **Agent Skill** that bridges Claude with Google Gemini CLI for multi-model collaboration on coding tasks.

## Overview

This Skill enables Claude to delegate coding tasks to Gemini CLI, combining the strengths of multiple AI models. Gemini handles algorithm implementation, debugging, and code analysis while Claude orchestrates the workflow and refines the output.

## Features

- **Multi-turn sessions**: Maintain conversation context across multiple interactions via `SESSION_ID`
- **Sandboxed execution**: Optional sandbox mode for isolated execution
- **JSON output**: Structured responses for easy parsing and integration
- **Cross-platform**: Windows path escaping handled automatically
- **Code-fence stripping**: Removes a single outer ``` fence from assistant output (default on)

## Installation

1. Ensure [Gemini CLI](https://github.com/google-gemini/gemini-cli) is installed and available in your PATH
2. Copy this Skill to your Claude Code skills directory:
   - User-level: `~/.claude/skills/collaborating-with-gemini/`
   - Project-level: `.claude/skills/collaborating-with-gemini/`

## Usage

### Basic

```bash
python scripts/gemini_bridge.py --cd "/path/to/project" --PROMPT "Analyze the authentication flow"
```

### Multi-turn Session

```bash
# Start a session
python scripts/gemini_bridge.py --cd "/project" --PROMPT "Review login.py for security issues"
# Response includes SESSION_ID

# Continue the session
python scripts/gemini_bridge.py --cd "/project" --SESSION_ID "uuid-from-response" --PROMPT "Suggest fixes for the issues found"
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--PROMPT` | Yes* | Task instruction |
| `--PROMPT_FILE` | Yes* | Read prompt text from this file (UTF-8) |
| `--cd` | Yes | Workspace root directory |
| `--sandbox` | No | Run in sandbox mode (default: off) |
| `--approval-mode` | No | Gemini approval mode (`default`, `auto_edit`, `yolo`) |
| `--SESSION_ID` | No | Resume a previous session |
| `--return-all-messages` | No | Include full reasoning trace in output |
| `--model` | No | Specify model (use only when explicitly requested) |
| `--output-file` | No | Write the resulting JSON to this file path |
| `--gemini-cwd` | No | Run Gemini from this working directory |
| `--include-directories` | No | Add directories to the Gemini workspace (repeatable) |
| `--strip-code-fences` | No | Strip a single outer Markdown code fence (default: on) |

\* Provide exactly one of `--PROMPT` or `--PROMPT_FILE`.

### Output Format

```json
{
  "success": true,
  "SESSION_ID": "uuid",
  "agent_messages": "Gemini response text",
  "all_messages": []
}
```

## License

MIT License. See [LICENSE](LICENSE) for details.
