"""Arac/Tool sistemi - /py, /sys, web, dosya."""

import io, os, subprocess, sys, json
from contextlib import redirect_stdout, redirect_stderr


class ToolResult:
    def __init__(self, output="", error="", exit_code=0):
        self.output = output
        self.error = error
        self.exit_code = exit_code


def cmd_py(code, timeout=30):
    try:
        f_out, f_err = io.StringIO(), io.StringIO()
        with redirect_stdout(f_out), redirect_stderr(f_err):
            exec(code)
        return ToolResult(
            output=f_out.getvalue().strip(), error=f_err.getvalue().strip()
        )
    except Exception as e:
        return ToolResult(error=str(e), exit_code=1)


def cmd_sys(command, timeout=30):
    try:
        r = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return ToolResult(
            output=r.stdout.strip(), error=r.stderr.strip(), exit_code=r.returncode
        )
    except subprocess.TimeoutExpired:
        return ToolResult(error="Zaman asimi", exit_code=124)
    except Exception as e:
        return ToolResult(error=str(e), exit_code=1)


def cmd_read(path):
    if not os.path.exists(path):
        return ToolResult(error=f"Dosya bulunamadi: {path}", exit_code=1)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return ToolResult(output=f"{path} ({len(content)} bytes)\n{content[:10000]}")
    except Exception as e:
        return ToolResult(error=str(e), exit_code=1)


def cmd_write(path, content):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return ToolResult(output=f"Yazildi: {path} ({len(content)} bytes)")
    except Exception as e:
        return ToolResult(error=str(e), exit_code=1)


def cmd_ls(path="."):
    try:
        files = os.listdir(path)
        result = "\n".join(sorted(files))
        return ToolResult(output=f"{len(files)} dosya:\n{result}")
    except Exception as e:
        return ToolResult(error=str(e), exit_code=1)


TOOL_REGISTRY = {
    "py": cmd_py,
    "sys": cmd_sys,
    "read": cmd_read,
    "write": cmd_write,
    "ls": cmd_ls,
}
