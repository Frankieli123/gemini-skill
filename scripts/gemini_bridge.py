"""
Gemini Bridge Script for Claude Agent Skills.
Wraps the Gemini CLI to provide a JSON-based interface for Claude.
"""

import json
import os
import queue
import subprocess
import sys
import threading
import time
import shutil
import argparse
import re
import tempfile
from pathlib import Path
from typing import Generator

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def run_shell_command(cmd: list[str], cwd: str | None = None) -> Generator[str, None, None]:
    """Execute a command and stream its output line-by-line."""
    popen_cmd = cmd.copy()
    gemini_path = shutil.which('gemini') or cmd[0]
    popen_cmd[0] = gemini_path

    # Set up environment with proper encoding
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'

    process = subprocess.Popen(
        popen_cmd,
        shell=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding='utf-8',
        errors='replace',
        cwd=cwd,
        env=env,
    )

    output_queue: queue.Queue[str | None] = queue.Queue()
    GRACEFUL_SHUTDOWN_DELAY = 0.3

    def is_turn_completed(line: str) -> bool:
        try:
            data = json.loads(line)
            return data.get("type") in {"turn.completed", "result"}
        except (json.JSONDecodeError, AttributeError, TypeError):
            return False

    def read_output() -> None:
        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                stripped = line.strip()
                output_queue.put(stripped)
                if is_turn_completed(stripped):
                    time.sleep(GRACEFUL_SHUTDOWN_DELAY)
                    process.terminate()
                    break
            process.stdout.close()
        output_queue.put(None)

    thread = threading.Thread(target=read_output)
    thread.start()

    while True:
        try:
            line = output_queue.get(timeout=0.5)
            if line is None:
                break
            yield line
        except queue.Empty:
            if process.poll() is not None and not thread.is_alive():
                break

    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    thread.join(timeout=5)

    while not output_queue.empty():
        try:
            line = output_queue.get_nowait()
            if line is not None:
                yield line
        except queue.Empty:
            break


def windows_escape(prompt):
    """Windows style string escaping."""
    result = prompt.replace('\\', '\\\\')
    result = result.replace('"', '\\"')
    result = result.replace('\n', '\\n')
    result = result.replace('\r', '\\r')
    result = result.replace('\t', '\\t')
    result = result.replace('\b', '\\b')
    result = result.replace('\f', '\\f')
    result = result.replace("'", "\\'")
    return result


def strip_outer_code_fence(text: str) -> str:
    def extract_unified_diff(candidate: str) -> str | None:
        lines = candidate.splitlines()
        for index, line in enumerate(lines):
            if not line.startswith("--- "):
                continue
            lookahead_end = min(index + 15, len(lines))
            if any(lines[j].startswith("+++ ") for j in range(index + 1, lookahead_end)):
                return "\n".join(lines[index:]).strip("\n")
        return None

    stripped = text.strip()
    if not (stripped.startswith("```") and stripped.endswith("```")):
        for match in re.finditer(r"```[^\n]*\n(.*?)\n```", text, flags=re.DOTALL):
            inner = match.group(1).strip("\n")
            extracted = extract_unified_diff(inner)
            if extracted is not None:
                return extracted
        return text

    first_newline = stripped.find("\n")
    if first_newline == -1:
        return text

    inner = stripped[first_newline + 1 : -3]
    extracted = extract_unified_diff(inner)
    return extracted if extracted is not None else inner.strip("\n")


def resolve_output_file(output_file: Path | None) -> Path | None:
    if output_file is None:
        return None

    try:
        output_file = output_file.expanduser()
    except RuntimeError:
        pass

    if output_file.is_absolute():
        return output_file

    base_dir = Path(tempfile.gettempdir()) / "codex_gemini_bridge"
    return base_dir / output_file


def emit_result(result: dict, output_file: Path | None) -> None:
    if output_file is not None and "output_file" not in result:
        try:
            result["output_file"] = output_file.absolute().as_posix()
        except Exception:
            result["output_file"] = str(output_file)

    result_json = json.dumps(result, indent=2, ensure_ascii=False)

    if output_file is not None:
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(result_json, encoding="utf-8")
        except Exception as error:
            result["output_file_error"] = f"Failed to write --output-file: {error}"
            result_json = json.dumps(result, indent=2, ensure_ascii=False)

    print(result_json)


def main():
    parser = argparse.ArgumentParser(description="Gemini Bridge")
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--PROMPT", help="Instruction for the task to send to gemini.")
    prompt_group.add_argument("--PROMPT_FILE", type=Path, help="Read prompt text from this file (UTF-8).")
    parser.add_argument("--cd", required=True, type=Path, help="Set the workspace root for gemini before executing the task.")
    parser.add_argument("--sandbox", action="store_true", default=False, help="Run in sandbox mode. Defaults to `False`.")
    parser.add_argument("--approval-mode", default=None, choices=["default", "auto_edit", "yolo"], help="Set the approval mode for the gemini session.")
    parser.add_argument("--SESSION_ID", default="", help="Resume the specified session of the gemini. Defaults to empty string, start a new session.")
    parser.add_argument("--return-all-messages", action="store_true", help="Return all messages (e.g. reasoning, tool calls, etc.) from the gemini session. Set to `False` by default, only the agent's final reply message is returned.")
    parser.add_argument("--model", default="", help="The model to use for the gemini session. This parameter is strictly prohibited unless explicitly specified by the user.")
    parser.add_argument("--output-file", default=None, type=Path, help="Write the resulting JSON to this file path (useful for background execution). Relative paths are written under the OS temp directory.")
    parser.add_argument("--gemini-cwd", default=None, type=Path, help="Run gemini from this working directory. Defaults to --cd.")
    parser.add_argument("--include-directories", action="append", default=[], help="Additional directories to include in the gemini workspace (repeatable).")
    parser.add_argument("--strip-code-fences", action=argparse.BooleanOptionalAction, default=True, help="Strip a single outer Markdown code fence from the assistant message.")

    args = parser.parse_args()
    output_file = resolve_output_file(args.output_file)

    cd: Path = args.cd
    if not cd.exists():
        result = {
            "success": False,
            "error": f"The workspace root directory `{cd.absolute().as_posix()}` does not exist. Please check the path and try again."
        }
        emit_result(result, output_file)
        return

    PROMPT = args.PROMPT
    if args.PROMPT_FILE is not None:
        try:
            PROMPT = args.PROMPT_FILE.read_text(encoding="utf-8")
        except Exception as error:
            emit_result({"success": False, "error": f"Failed to read --PROMPT_FILE: {error}"}, output_file)
            return

    if os.name == "nt":
        PROMPT = windows_escape(PROMPT)

    cmd = ["gemini", "-o", "stream-json"]

    if args.sandbox:
        cmd.extend(["--sandbox"])

    if args.approval_mode:
        cmd.extend(["--approval-mode", args.approval_mode])

    if args.model:
        cmd.extend(["--model", args.model])

    if args.SESSION_ID:
        cmd.extend(["--resume", args.SESSION_ID])

    gemini_cwd = args.gemini_cwd or cd

    include_directories = list(args.include_directories)
    if args.gemini_cwd is not None:
        include_directories.insert(0, cd.absolute().as_posix())

    for include_dir in include_directories:
        cmd.extend(["--include-directories", include_dir])

    cmd.append(PROMPT)

    all_messages = []
    agent_messages = ""
    success = True
    err_message = ""
    thread_id = None
    non_json_output = []

    try:
        for line in run_shell_command(cmd, cwd=gemini_cwd.absolute().as_posix()):
            stripped = line.strip()
            if not stripped.startswith("{"):
                non_json_output.append(stripped)
                continue

            try:
                line_dict = json.loads(stripped)
                all_messages.append(line_dict)
                item_type = line_dict.get("type", "")
                item_role = line_dict.get("role", "")
                if item_type == "message" and item_role == "assistant":
                    agent_messages = agent_messages + line_dict.get("content", "")
                if line_dict.get("session_id") is not None:
                    thread_id = line_dict.get("session_id")

            except json.JSONDecodeError:
                non_json_output.append(stripped)
                continue

            except Exception as error:
                err_message += "\n\n[unexpected error] " + f"Unexpected error: {error}. Line: {line!r}"
                break
    except FileNotFoundError as error:
        success = False
        err_message = f"Failed to execute gemini: {error}"
    except OSError as error:
        success = False
        err_message = f"Failed to execute gemini: {error}"

    if thread_id is None:
        success = False
        err_message = "Failed to get `SESSION_ID` from the gemini session. \n\n" + err_message

    if success and len(agent_messages) == 0:
        success = False
        err_message = (
            "Failed to retrieve `agent_messages` data from the Gemini session. This might be due to Gemini performing a tool call. You can continue using the `SESSION_ID` to proceed with the conversation. \n\n "
            + err_message
        )

    if args.strip_code_fences and agent_messages:
        agent_messages = strip_outer_code_fence(agent_messages)

    if non_json_output and not success:
        err_message = err_message + "\n\n[non-json output]\n" + "\n".join(non_json_output)

    if success:
        result = {
            "success": True,
            "SESSION_ID": thread_id,
            "agent_messages": agent_messages,
        }
    else:
        result = {"success": False, "error": err_message}
        if thread_id is not None:
            result["SESSION_ID"] = thread_id
        if agent_messages:
            result["agent_messages"] = agent_messages

    if args.return_all_messages:
        result["all_messages"] = all_messages
        if non_json_output:
            result["non_json_output"] = non_json_output

    emit_result(result, output_file)


if __name__ == "__main__":
    main()
