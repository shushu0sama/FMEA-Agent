"""CLI entry point: `python -m fmea_agent demo examples/simple_pump.json`.

Orchestrates fixture loading, repository construction, workflow execution and
output emission. All FMEA semantics stay in the domain and workflow layers.
"""

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from fmea_agent.adapters.inmemory import NoOpRiskStrategy
from fmea_agent.agents.workflow import build_workflow_graph
from fmea_agent.agents.workflow_state import WorkflowState
from fmea_agent.cli.loading import load_failure_library, load_system_fixture

_DEFAULT_LIBRARY_NAME = "demo_failure_library.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fmea_agent", description="FMEA Agent - MVP-0 runnable vertical slice"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser(
        "demo", help="run the demo FMEA workflow on a fixture and print structured JSON"
    )
    demo.add_argument("fixture", type=Path, help="path to a system fixture JSON")
    demo.add_argument(
        "--failure-library",
        type=Path,
        default=None,
        help="path to a failure library JSON "
        "(default: demo_failure_library.json next to the fixture)",
    )
    demo.add_argument(
        "--output",
        type=Path,
        default=None,
        help="write output JSON to this file instead of stdout",
    )
    return parser


def _run_demo(fixture: Path, library: Path | None, output: Path | None) -> int:
    system_repo, request = load_system_fixture(fixture)
    library_path = library if library is not None else fixture.parent / _DEFAULT_LIBRARY_NAME
    knowledge_repo = load_failure_library(library_path)

    graph = build_workflow_graph(system_repo, knowledge_repo, NoOpRiskStrategy())
    result: Any = graph.invoke(WorkflowState(request=request))
    final = result if isinstance(result, WorkflowState) else WorkflowState.model_validate(result)

    if final.errors or final.output is None:
        for message in final.errors:
            print(f"error: {message}", file=sys.stderr)
        return 1

    text = json.dumps(final.output, indent=2)
    if output is not None:
        output.write_text(text + "\n", encoding="utf-8")
        print(f"output written to {output}", file=sys.stderr)
    else:
        print(text)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            return _run_demo(args.fixture, args.failure_library, args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2
