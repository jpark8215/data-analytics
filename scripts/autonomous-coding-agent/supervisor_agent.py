"""Supervisor agent that reviews worker output and decides to ACCEPT, RETRY, or ESCALATE."""

import json, subprocess
from openai import OpenAI
from minimal_agent import MODEL, WORKSPACE, log_step, run_agent, run_tests

client = OpenAI()

def get_git_diff() -> str:
    res = subprocess.run(["git", "diff"], capture_output=True, text=True, cwd=WORKSPACE)
    return (res.stdout or "No uncommitted diff.")[:4000]

def supervisor_review(goal: str, worker_result: dict, test_output: str, diff_output: str) -> dict:
    prompt = (
        "You are a supervising engineering agent reviewing a worker agent's patch.\n"
        f"Goal: {goal}\n"
        f"Worker summary: {worker_result['summary']}\n"
        f"Test output:\n{test_output}\n\n"
        f"Git diff:\n{diff_output}\n\n"
        "Respond strictly as JSON with keys 'decision' (ACCEPT, RETRY, or ESCALATE) and 'reason'.\n"
        "Use RETRY if tests still fail or the fix looks incomplete.\n"
        "Use ESCALATE if tests were altered, the diff touches unrelated files, or human judgment is needed."
    )
    resp = client.chat.completions.create(
        model=MODEL, response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(resp.choices[0].message.content)

def run_supervised(goal: str, max_retries: int = 2, task_id: str = "supervised-001") -> bool:
    current_goal = goal
    for attempt in range(1, max_retries + 2):
        worker_result = run_agent(current_goal, task_id=f"{task_id}-a{attempt}")
        test_output = run_tests()
        review = supervisor_review(goal, worker_result, test_output, get_git_diff())
        log_step(task_id, attempt, "supervisor_review", {"decision": review.get("decision")}, json.dumps(review))

        decision, reason = review.get("decision", "ESCALATE").upper(), review.get("reason", "")
        if decision == "ACCEPT" and "exit_code=0" in test_output:
            return True
        if decision == "ESCALATE":
            print(f"Human review required: {reason}")
            return False
        current_goal = f"{goal}\n\nSupervisor feedback from attempt {attempt}: {reason}"
    return False