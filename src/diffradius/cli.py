from __future__ import annotations

import argparse
import json
from pathlib import Path

from .benchmark import all_cases
from .evaluate import RUNNERS, compare_results, evaluate
from .render import render_comparison, render_review
from .repository import RepositoryView, git_diff
from .workflow import run_final
from .trajectory_render import render_trajectory_file


def _review(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    diff = Path(args.diff_file).read_text(encoding="utf-8") if args.diff_file else git_diff(repo, args.base, args.head)
    ticket = Path(args.ticket_file).read_text(encoding="utf-8") if args.ticket_file else args.ticket
    view = RepositoryView(repo, diff, ticket or "No ticket supplied", base_ref=args.base)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    result = run_final(view, out_dir / "trajectories")
    payload = result.model_dump(mode="json")
    (out_dir / "review.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    markdown = render_review(result.report, result.usage)
    (out_dir / "review.md").write_text(markdown, encoding="utf-8")
    print(markdown)
    return 0


def _eval(args: argparse.Namespace) -> int:
    out = Path(args.output)
    case_ids = [case.strip() for case in args.cases.split(",") if case.strip()] if args.cases else None
    if args.mode in {"all", "both"}:
        modes = list(RUNNERS) if args.mode == "all" else ["baseline", "final"]
        results = {mode: evaluate(mode, out, case_ids) for mode in modes}
        comparison = compare_results(results)
        (out / "comparison.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")
        markdown = render_comparison(comparison)
        (out / "comparison.md").write_text(markdown, encoding="utf-8")
        print(markdown)
    else:
        payload = evaluate(args.mode, out, case_ids)
        print(json.dumps({"quality": payload["aggregate"], "usage": payload["usage"]}, indent=2))
    return 0


def _cases(_: argparse.Namespace) -> int:
    for case in all_cases():
        suffix = " [HARD]" if case.hard else ""
        print(f"{case.id}: {case.title}{suffix}")
    return 0


def _trajectory(args: argparse.Namespace) -> int:
    source = Path(args.input)
    destination = Path(args.output) if args.output else source.with_suffix(".md")
    markdown = render_trajectory_file(source, destination)
    if args.print:
        print(markdown)
    else:
        print(destination)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="diffradius")
    sub = parser.add_subparsers(dest="command", required=True)

    review = sub.add_parser("review", help="Review a real local repository change")
    review.add_argument("--repo", default=".")
    review.add_argument("--base", default="main")
    review.add_argument("--head", default="HEAD")
    review.add_argument("--diff-file")
    review.add_argument("--ticket", default="")
    review.add_argument("--ticket-file")
    review.add_argument("--output", default="results/review")
    review.set_defaults(func=_review)

    ev = sub.add_parser("evaluate", help="Run the fixed synthetic benchmark")
    ev.add_argument(
        "--mode",
        choices=[*RUNNERS.keys(), "both", "all"],
        default="all",
        help="Use 'all' for the experiment/ablation matrix; 'both' compares only baseline and final.",
    )
    ev.add_argument("--cases", help="Comma-separated case IDs")
    ev.add_argument("--output", default="results/benchmark")
    ev.set_defaults(func=_eval)

    cases = sub.add_parser("cases", help="List benchmark cases")
    cases.set_defaults(func=_cases)

    trajectory = sub.add_parser("trajectory", help="Render a JSON agent trajectory as judge-friendly Markdown")
    trajectory.add_argument("--input", required=True)
    trajectory.add_argument("--output")
    trajectory.add_argument("--print", action="store_true", dest="print")
    trajectory.set_defaults(func=_trajectory)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
