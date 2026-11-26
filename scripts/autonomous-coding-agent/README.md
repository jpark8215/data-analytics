# Autonomous Coding Agent Examples

Runnable companion code for the blog post:
"From Chatbot to Digital Teammate: How Autonomous Coding Agents Plan, Build, and Supervise Each Other, and How to Keep Them Under Control"

## Files

- `minimal_agent.py`: A minimal coding agent loop (~55 lines) with `read_file`, `run_tests`, and `edit_code` tools, a step limit, and structured JSONL audit logging.
- `supervisor_agent.py`: A supervisor agent that inspects the worker's test results and git diff, then returns `ACCEPT`, `RETRY`, or `ESCALATE`.

## Setup

```bash
pip install openai pytest
export OPENAI_API_KEY="your-api-key"
```

You can also point `OPENAI_BASE_URL` at any OpenAI-compatible local inference server (such as NVIDIA NIM or Ollama).

## Usage

Run the single worker loop against a test goal:

```bash
python minimal_agent.py
```

Run the supervised multi-agent workflow:

```bash
python supervisor_agent.py
```

Every run writes a structured step-by-step audit trace under `agent_logs/`.
