from __future__ import annotations

import tempfile
from pathlib import Path

from diffradius.benchmark import all_cases, benchmark_fingerprint, materialize, run_oracle, run_visible_tests


def main() -> int:
    failures = []
    with tempfile.TemporaryDirectory(prefix="diffradius-validation-") as tmp:
        root = Path(tmp)
        for spec in all_cases():
            before = materialize(spec.id, root, "before")
            after = materialize(spec.id, root, "after")
            before_visible = run_visible_tests(before)
            after_visible = run_visible_tests(after)
            before_oracle = run_oracle(before)
            after_oracle = run_oracle(after)
            broken = bool(after.expected)

            # A benchmark regression must be attributable to the change: the held-out oracle
            # passes on the old implementation, then fails on the changed one. Safe controls
            # pass on both sides. Visible tests must pass on both sides.
            ok = (
                before_visible.returncode == 0
                and after_visible.returncode == 0
                and before_oracle.returncode == 0
                and (after_oracle.returncode != 0 if broken else after_oracle.returncode == 0)
            )
            status = "PASS" if ok else "FAIL"
            before_visible_label = "FAIL" if before_visible.returncode else "PASS"
            after_visible_label = "FAIL" if after_visible.returncode else "PASS"
            before_oracle_label = "FAIL" if before_oracle.returncode else "PASS"
            after_oracle_label = "FAIL" if after_oracle.returncode else "PASS"
            print(
                f"{status} {after.id}: "
                f"visible(before/after)={before_visible_label}/{after_visible_label} "
                f"oracle(before/after)={before_oracle_label}/{after_oracle_label}"
            )
            if not ok:
                failures.append(
                    (
                        after.id,
                        before_visible.stderr,
                        after_visible.stderr,
                        before_oracle.stderr,
                        after_oracle.stderr,
                    )
                )
    if failures:
        for case_id, bv, av, bo, ao in failures:
            print(
                f"\n--- {case_id} before-visible ---\n{bv}"
                f"\n--- after-visible ---\n{av}"
                f"\n--- before-oracle ---\n{bo}"
                f"\n--- after-oracle ---\n{ao}"
            )
        return 1
    print(f"Benchmark fingerprint: {benchmark_fingerprint()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
