# collaborating-with-gemini

**中文**
- Codex CLI Skill：调用 Gemini CLI 做原型/调试/审阅；Codex 负责落地与验证。
- 强约束：只输出 raw Unified Diff（以 `--- ` 开始）、禁止 Markdown 代码围栏（```）、禁止实际修改任何文件。

**English**
- Codex CLI skill: call Gemini CLI for prototyping/debugging/review; Codex applies and verifies.
- Hard constraints: raw unified diff only (starts with `--- `), no Markdown fences (```), no actual file changes.

## Install / 安装

- Ensure [Gemini CLI](https://github.com/google-gemini/gemini-cli) is installed and `gemini` is in PATH.
- Copy this folder to:
  - Windows: `$env:USERPROFILE\.codex\skills\collaborating-with-gemini\`
  - macOS/Linux: `~/.codex/skills/collaborating-with-gemini/`

## Context / 上下文如何给 Gemini

- `--cd` sets Gemini workspace root (and default working directory). Gemini reads project files itself via its CLI tools; the bridge does not pre-send file contents.
- Multi-turn: keep the returned `SESSION_ID`, then pass it back via `--SESSION_ID`.

## Output / 返回内容在哪里

- Foreground: prints JSON to stdout.
- Background (recommended on Windows): use `--output-file` to write the same JSON to disk.
- `--output-file` safety: relative paths are written under OS temp directory `codex_gemini_bridge/` (avoids creating files inside your project folder).

## Prompt Template (MUST) / 提示词模板（必加）

Append these constraints to every task:

```
OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
Do NOT wrap output in Markdown fences (``` or ```diff). Output raw unified diff starting with '--- '.
```

## Usage / 用法

### Foreground / 前台

```powershell
python scripts/gemini_bridge.py --cd "E:\\path\\to\\project" --PROMPT "Review auth. OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications."
```

### Windows PowerShell (background) / Windows 后台

```powershell
$project = "E:\\path\\to\\project"
$prompt = @"
Review the authentication flow.
OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
Do NOT wrap output in Markdown fences (``` or ```diff). Output raw unified diff starting with '--- '.
"@

$promptFile = Join-Path $env:TEMP ("codex_gemini_prompt_" + [guid]::NewGuid() + ".txt")
$outFile = Join-Path $env:TEMP ("codex_gemini_" + [guid]::NewGuid() + ".json")
Set-Content -LiteralPath $promptFile -Value $prompt -Encoding utf8

Start-Process -FilePath python -ArgumentList "\"$env:USERPROFILE\\.codex\\skills\\collaborating-with-gemini\\scripts\\gemini_bridge.py\" --cd \"$project\" --PROMPT_FILE \"$promptFile\" --output-file \"$outFile\"" -NoNewWindow

$result = Get-Content -Raw $outFile | ConvertFrom-Json
Remove-Item -Force $promptFile, $outFile
$result.agent_messages
```

### Multi-turn / 续聊

```powershell
python scripts/gemini_bridge.py --cd "E:\\path\\to\\project" --PROMPT "First task. OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications."
python scripts/gemini_bridge.py --cd "E:\\path\\to\\project" --SESSION_ID "uuid-from-response" --PROMPT "Follow up. OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications."
```

## Output JSON / 输出 JSON

```json
{
  "success": true,
  "SESSION_ID": "uuid",
  "agent_messages": "Gemini response text",
  "output_file": "C:/Users/.../Temp/codex_gemini_bridge/out.json"
}
```

`output_file` is present only when `--output-file` is used.

## License

MIT. See [LICENSE](LICENSE).
