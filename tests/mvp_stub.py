"""Offline DSH test server. Exposes only get_run; never imports the provider.

Run with the MCP checkout's locked Python environment. Trace file is fixed under
this repository's .cache. Only synthetic IDs are accepted. No user data is read.
"""
import asyncio
import json
from pathlib import Path
import sys
import os
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

ROOT = Path(__file__).resolve().parents[1]
TRACE = Path(os.environ.get("MVP_TRACE_PATH", ROOT / ".cache/dsh-mvp-trace.jsonl")).resolve()
if not TRACE.is_relative_to((ROOT / ".cache").resolve()):
    raise ValueError("Fixture trace must remain under this repository's .cache")
SERVER = MCPServer("replicator-mvp-offline", version="0.1.0-fixture")
IDENTITY = "run_" + "a" * 64


@SERVER.tool()
def get_run(run_id: str) -> dict:
    """Return a synthetic task snapshot. Test transport, not a production service."""
    TRACE.parent.mkdir(exist_ok=True)
    with TRACE.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"tool": "get_run", "arguments": {"run_id": run_id},
                                 "fixture": True}) + "\n")
    if run_id != IDENTITY:
        raise ToolError("Unknown synthetic task identity")
    return {"run_id": IDENTITY, "status": "partial", "fixture": True,
        "workspace": "synthetic-fixture", "jobs": [
            {"image_id": "synthetic/reference-01", "status": "downloaded",
             "generation_status": "generated", "review_status": "review_required"},
            {"image_id": "synthetic/reference-02", "index": 1, "status": "unknown",
             "generation_status": "blocked", "phase": "generate"},
            {"image_id": "synthetic/reference-03", "status": "not_submitted",
             "generation_status": "blocked", "phase": "analysis",
             "analysis_kind": "visual", "error_code": "analysis_retry_exhausted"}]}


async def main():
    def deny_network(event, args):
        if event in {"socket.connect", "socket.getaddrinfo", "socket.sendto"}:
            raise RuntimeError("Offline fixture prohibits network")
    sys.addaudithook(deny_network)
    await SERVER.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
