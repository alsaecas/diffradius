from __future__ import annotations

import argparse
import json
from pathlib import Path

from .benchmark import all_cases
from .evaluate import compare_results, evaluate
from .repository import RepositoryView, git_diff
from .workflow import run_final


def _review(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    if args.diff_file:
        diff = Path(args.diff_file).read_text(encoding="utf-8")
    else:
        diff = git_diff(repo, args.base, args.head)
    ticket = Path(args.ticket_file).read_text(encoding="utf-8") if args.ticket_file else args.ticket
    view = RepositoryView(repo, diff, ticket or "No ticket supplied")
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    result = run_final(view, out_dir / "trajectories")
    payload = result.model_dump(mode="json")
    (out_dir / "review.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


def _eval(args: argparse.Namespace) -> int:
    out = Path(args.output)
    case_ids = args.cases.split(",") if args.cases else None
    if args.mode == "both":
        baseline = evaluate("baseline", out, case_ids)
        final = evaluate("final", out, case_ids)
        comparison = compare_results(baseline, final)
        (out / "comparison.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")
        print(json.dumps(comparison, indent=2))
    else:
        payload = evaluate(args.mode, out, case_ids)
        print(json.dumps(payload["aggregate"], indent=2))
    return 0


def _cases(_: argparse.Namespace) -> int:
    for case in all_cases():
        suffix = " [HARD]" if case.hard else ""
        print(f"{case.id}: {case.title}{suffix}")
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
    ev.add_argument("--mode", choices=["baseline", "final", "both"], default="both")
    ev.add_argument("--cases", help="Comma-separated case IDs")
    ev.add_argument("--output", default="results/benchmark")
    ev.set_defaults(func=_eval)

    cases = sub.add_parser("cases", help="List benchmark cases")
    cases.set_defaults(func=_cases)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
