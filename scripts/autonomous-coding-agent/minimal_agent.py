"""Minimal autonomous coding agent loop with command allowlist and JSONL audit logging."""

import datetime, json, pathlib, subprocess
from openai import OpenAI

client = OpenAI()
MODEL, MAX_STEPS = "gpt-4o", 12
WORKSPACE = pathlib.Path(".").resolve()

def _safe_path(path: str) -> pathlib.Path:
    target = (WORKSPACE / path).resolve()
    if not target.is_relative_to(WORKSPACE):
        raise ValueError(f"Blocked path outside workspace: {path}")
    return target

def read_file(path: str) -> str:
    target = _safe_path(path)
    return target.read_text(encoding="utf-8") if target.exists() else f"ERROR: {path} not found"

def edit_code(path: str, content: str) -> str:
    target = _safe_path(path)
    if "test_" in target.name or target.name == "conftest.py":
        return "ERROR: Guardrail blocked modifying test files directly."
    target.write_text(content, encoding="utf-8")
    return f"Updated {path} ({len(content)} chars)"

def run_tests(test_path: str = "tests") -> str:
    res = subprocess.run(
        ["python", "-m", "pytest", test_path, "-v", "--tb=short"],
        capture_output=True, text=True, timeout=60, cwd=WORKSPACE
    )
    return f"exit_code={res.returncode}\n{(res.stdout + res.stderr)[:3000]}"

TOOLS = {"read_file": read_file, "edit_code": edit_code, "run_tests": run_tests}
SCHEMAS = [
    {"type": "function", "function": {"name": "read_file", "description": "Read a workspace file.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "edit_code", "description": "Write updated code to a source file.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "run_tests", "description": "Run pytest on a test path.",
        "parameters": {"type": "object", "properties": {"test_path": {"type": "string"}}}}},
]

def log_step(task_id: str, step: int, tool: str, args: dict, obs: str) -> None:
    """Append one JSONL audit record per tool invocation.

    Defined here, ahead of run_agent(), because run_agent() calls it on every
    tool call. supervisor_agent.py imports this same function from this module
    to log its own review decisions to the same per-task log file.
    """
    log_path = WORKSPACE / "agent_logs" / f"{task_id}.jsonl"
    log_path.parent.mkdir(exist_ok=True)
    entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "step": step,
        "tool": tool,
        "arg_keys": list(args.keys()),  # log parameter keys without leaking sensitive values
        "obs_preview": obs[:500],
    }
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")

def run_agent(goal: str, task_id: str = "task-001") -> dict:
    messages = [
        {"role": "system", "content": "You are a coding agent. Read files, run tests, edit source code, and verify tests pass before responding with DONE."},
        {"role": "user", "content": goal},
    ]
    for step in range(1, MAX_STEPS + 1):
        msg = client.chat.completions.create(model=MODEL, messages=messages, tools=SCHEMAS).choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            return {"completed": "DONE" in (msg.content or ""), "steps": step, "summary": msg.content or ""}
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments or "{}")
            obs = TOOLS[tc.function.name](**args)
            log_step(task_id, step, tc.function.name, args, obs)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": obs})
    return {"completed": False, "steps": MAX_STEPS, "summary": "Step limit reached."}