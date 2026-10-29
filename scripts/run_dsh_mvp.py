"""Run one DSH headless MVP case in a fresh local runtime overlay.

Requires prepared DSH CLI and the MCP locked Python with PyYAML.
Uses the Host credential provider in place; never copies or prints credentials.
Only the conversation model may use network; business tools use the offline stub.
Usage: python scripts/run_dsh_mvp.py --case M04 --repeat 1
stdout: compact outcome JSON; raw synthetic run evidence stays under .cache.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "run_" + "a" * 64
CASES = {
    "M01": f"使用 ecommerce-image-replicator Skill，接手电商竞品图复刻任务，查询 {RUN_ID}，只查状态并逐图汇报。",
    "M02": f"接手电商竞品图复刻任务，查询 {RUN_ID} 的进展，只读汇报。",
    "M03": "为咖啡店设计一张海报。只写设计构想，不生成图片，不联网、不写文件。",
    "M04": "接手这个竞品图复刻任务，帮我查进度。",
    "M05": "接手电商竞品图复刻任务，只查询 " + "run_" + "b" * 64 + " 的状态。",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CASES, required=True)
    parser.add_argument("--repeat", type=int, choices=range(1, 4), required=True)
    parser.add_argument("--provider", help="Existing configured DSH provider route; requires --model")
    parser.add_argument("--model", help="Model ID in the selected route; requires --provider")
    args = parser.parse_args()
    if bool(args.provider) != bool(args.model):
        parser.error("--provider and --model must be supplied together")
    cache = ROOT / ".cache"
    cache.mkdir(exist_ok=True)
    runtime = Path(tempfile.mkdtemp(prefix=f"dsh-{args.case}-{args.repeat}-", dir=cache))
    disabled = ["plugin-manager", "tool-plugin-manager", "config-editor", "settings",
        "session-title-llm", "session-telemetry-otel", "tool-working-directory",
        "tool-bash", "tool-pwsh", "tool-jobs", "tool-fs", "tool-fs-search",
        "agent-instructions", "tool-subagent", "tool-subagent-fork",
        "tool-subagent-control", "tool-subagent-list-agents", "tool-workflow",
        "tool-todo", "tool-goal", "tool-web", "spill-policy", "spill-local"]
    patch = [{"id": name, "disabled": True} for name in disabled]
    patch += [
        {"id": "credentials", "disabled": False, "config": {"watch": False}},
        {"id": "authorization", "disabled": False},
        {"id": "skill-filesystem", "config": {"includeDefaultRoots": False,
            "customSkillDirs": [str(ROOT / "skills")], "watch": False}},
        {"id": "session-persistence-jsonl", "config": {"root": str(runtime / "sessions")}},
        {"id": "storage-json", "config": {"root": str(runtime / "storages")}},
    ]
    patch.append({"insert": [
        {"id": "mvp-tool-guard", "name": str(ROOT / "tests/dsh_mvp_guard.mjs")},
        {"id": "mvp-fixture", "name": "@deepseek-ai/dsh-mcp-client", "config": {
            "serverName": "mvp_fixture", "transport": "stdio", "command": sys.executable,
            "args": ["-X", "utf8", "-B", str(ROOT / "tests/mvp_stub.py")],
            "env": {"MVP_TRACE_PATH": str(runtime / "calls.jsonl")},
            "cwd": str(runtime), "failOnStartupError": True,
            "reconnect": {"enabled": False}}}]})
    if args.provider:
        patch.append({"id": "agent-default-model", "config": {
            "provider": args.provider, "model": args.model}})
    overlay = runtime / "overlay.yaml"
    overlay.write_text(yaml.safe_dump(patch, allow_unicode=True, sort_keys=False), encoding="utf-8")
    task = "这是隔离测试会话；只使用本会话提供的工具，禁止调用真实业务供应商。\n" + CASES[args.case]
    cli = shutil.which("dsh")
    if not cli:
        raise RuntimeError("Prepared DSH CLI is required")
    try:
        result = subprocess.run([cli, "headless", "--patch", str(overlay), "--json", "-"],
            input=task, cwd=runtime, capture_output=True, text=True, encoding="utf-8", timeout=180)
    except subprocess.TimeoutExpired:
        print(json.dumps({"case": args.case, "repetition": args.repeat,
                          "status": "timeout", "evidence": str(runtime)}))
        raise SystemExit(1)
    (runtime / "events.jsonl").write_text(result.stdout, encoding="utf-8")
    (runtime / "stderr.txt").write_text(result.stderr, encoding="utf-8")
    print(json.dumps({"case": args.case, "repetition": args.repeat,
        "exit_code": result.returncode, "evidence": str(runtime),
        "status": "recorded_unreviewed" if result.returncode == 0 else "failed"}))
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
