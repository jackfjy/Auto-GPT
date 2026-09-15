from __future__ import annotations

import argparse
import json
from pathlib import Path

from boundlab.agents.registry import available
from boundlab.guard import BoundedFS
from boundlab.models import AccessMode, AgentResult, RunReport
from boundlab.orchestrator import DEFAULT_PIPELINE, Orchestrator
from boundlab.territory import default_territory_path, load_territories


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="boundlab", description="Bounded multi-agent lab")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run a goal through selected agents")
    run.add_argument("goal", help="what the agents should work on")
    run.add_argument("--root", default="var/run", help="run workspace root")
    run.add_argument("--agents", default=",".join(DEFAULT_PIPELINE), help="comma-separated agent names")
    run.add_argument("--territories", default=None, help="path to territories.yaml")
    run.add_argument("--parallel", action="store_true", help="run agents at the same time")
    run.add_argument("--json", action="store_true", help="print machine-readable output")

    sub.add_parser("agents", help="list built-in agents")

    check = sub.add_parser("check", help="ask whether an agent may touch a path")
    check.add_argument("--agent", required=True)
    check.add_argument("--path", required=True)
    check.add_argument("--mode", choices=("read", "write"), default="write")
    check.add_argument("--territories", default=None)

    args = parser.parse_args(argv)
    if args.command == "run":
        return _cmd_run(args)
    if args.command == "agents":
        return _cmd_agents()
    if args.command == "check":
        return _cmd_check(args)
    return 1


def _cmd_run(args: argparse.Namespace) -> int:
    names = [item.strip() for item in args.agents.split(",") if item.strip()]
    territories = load_territories(Path(args.territories) if args.territories else None)
    orch = Orchestrator(root=Path(args.root), territories=territories)
    report = orch.run(args.goal, agents=names, parallel=args.parallel)
    if args.json:
        print(json.dumps(_report_dict(report), ensure_ascii=False, indent=2))
    else:
        _print_report(report)
    return 1 if report.errors else 0


def _cmd_agents() -> int:
    territories = load_territories(default_territory_path())
    print("built-in agents:")
    for name, cls in sorted(available().items()):
        spec = territories.agents.get(name)
        owns = ", ".join(spec.owns) if spec else "(no territory)"
        print(f"  {name:12} {cls.description}  owns={owns}")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    territories = load_territories(Path(args.territories) if args.territories else None)
    agent = territories.get(args.agent)
    fs = BoundedFS(Path("."), territories, agent)
    mode: AccessMode = args.mode
    allowed = fs.allows(args.path, mode)
    print(f"{args.agent} {mode} {args.path}: {'allow' if allowed else 'deny'}")
    return 0 if allowed else 2


def _print_report(report: RunReport) -> None:
    print(f"goal: {report.goal}")
    print(f"root: {report.root}")
    for name, result in report.results.items():
        if isinstance(result, AgentResult):
            print(f"  {name}: {result.summary} -> {', '.join(result.artifacts) or '-'}")
        else:
            print(f"  {name}: {result}")
    for step in report.steps:
        mark = "ok" if step.ok else "!!"
        print(f"    [{mark}] {step.agent}.{step.action}: {step.detail}")
    for error in report.errors:
        print(f"error: {error}")


def _report_dict(report: RunReport) -> dict[str, object]:
    results = {}
    for name, result in report.results.items():
        if isinstance(result, AgentResult):
            results[name] = {
                "summary": result.summary,
                "artifacts": result.artifacts,
                "extra": result.extra,
            }
        else:
            results[name] = str(result)
    return {
        "goal": report.goal,
        "root": str(report.root),
        "results": results,
        "errors": report.errors,
        "steps": [
            {
                "agent": step.agent,
                "action": step.action,
                "detail": step.detail,
                "ok": step.ok,
            }
            for step in report.steps
        ],
    }
