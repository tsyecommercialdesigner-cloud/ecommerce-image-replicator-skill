"""Development-only stdio probe. Requires the MCP checkout's locked environment.

Usage: python scripts/probe_mcp.py --source <MCP checkout>
Writes no files outside this repository's .cache; never calls execute or providers.
stdout: one JSON report; failure: nonzero exit, diagnostic on stderr.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
import sys
import tempfile


def serve(source, root):
    sys.path.insert(0, str(source / "src"))

    def audit(event, args):
        if event in {"socket.connect", "socket.getaddrinfo", "socket.sendto"}:
            raise RuntimeError("Probe prohibits provider/network access")
        if event == "open" and isinstance(args[0], (str, bytes)):
            if Path(os.fsdecode(args[0])).name == ".env":
                raise RuntimeError("Probe prohibits credential files")

    from image_replicator.config import Settings
    from image_replicator.server import create_server
    import image_replicator.config as config
    import image_replicator.server as server

    def denied(*args, **kwargs):
        raise RuntimeError("Credential access prohibited")

    config.read_keys = denied
    server.read_keys = denied
    async def run():
        # Windows creates a loopback socketpair when constructing its event loop.
        # Install the network guard after that internal initialization, before MCP.
        sys.addaudithook(audit)
        await create_server(Settings(project_root=root, workspace=root),
                            task_workspaces=True, state_dir=root).run_stdio_async()

    asyncio.run(run())


async def probe(source, root):
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client
    from PIL import Image

    (root / "references/detail").mkdir(parents=True)
    (root / "products").mkdir()
    (root / "brief").mkdir()
    Image.new("RGB", (790, 857), "white").save(root / "references/detail/01.png")
    Image.new("RGB", (128, 128), "white").save(root / "products/product.png")
    (root / "brief/task.md").write_text("Synthetic protocol fixture; no product claims.", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if not any(
        word in k.upper() for word in ("KEY", "TOKEN", "SECRET", "PASSWORD"))}
    params = StdioServerParameters(command=sys.executable, args=[str(Path(__file__).resolve()),
        "--source", str(source), "--serve", str(root)], env=env, cwd=str(root))
    trace = []
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as client:
            await client.discover()
            tools = await client.list_tools()
            names = {t.name for t in tools.tools}
            assert len(names) == 12 and "recover_postprocess" in names
            resources = await client.list_resources()
            prompts = await client.list_prompts()
            assert len(resources.resources) == len(prompts.prompts) == 1
            resource = await client.read_resource("replicator://input-contract")
            contract = json.loads(resource.contents[0].text)
            assert contract["execution_limit_policy"] == "opt-in-v1"
            assert contract["postprocess_recovery_policy"] == "downloaded-local-v1"
            assert (await client.get_prompt("prepare_inputs")).messages

            async def call(name, arguments):
                result = await client.call_tool(name, arguments)
                trace.append({"tool": name, "isError": result.is_error})
                assert not result.is_error, name
                return result.structured_content

            inputs = await call("inspect_inputs", {"workspace": str(root)})
            assert inputs["images"]
            prepared = await call("prepare_run", {"workspace": str(root)})
            identity = {"run_id": prepared["run_id"]}
            state = await call("get_run", identity)
            assert state["run_id"] == identity["run_id"]
            preflight = await call("preflight_run", identity)
            assert preflight["provider_requests"] == 0
            assert preflight["jobs"][0]["status"] == "analysis_required"
            design = await call("get_design", {**identity, "image_id": state["jobs"][0]["image_id"]})
            assert design["status"] == "analysis_required"
            return {"status": "passed", "server_version": client.server_info.version,
                "tools": sorted(names), "resources": 1, "prompts": 1,
                "trace": trace, "provider_requests": 0,
                "scope": "independent stdio, synthetic fixture; not Host/agent behavior"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--serve", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    if args.serve:
        serve(source, args.serve.resolve(strict=True))
        return
    cache = Path(__file__).resolve().parents[1] / ".cache"
    cache.mkdir(exist_ok=True)
    evidence = cache / "mvp-protocol.json"
    evidence.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="mvp-protocol-", dir=cache) as temporary:
        report = asyncio.run(asyncio.wait_for(probe(source, Path(temporary)), timeout=45))
    evidence.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
