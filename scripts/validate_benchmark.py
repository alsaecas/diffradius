from __future__ import annotations

import tempfile
from pathlib import Path

from diffradius.benchmark import all_cases, materialize, run_oracle, run_visible_tests


def main() -> int:
    failures = []
    with tempfile.TemporaryDirectory(prefix="diffradius-validation-") as tmp:
        root = Path(tmp)
        for spec in all_cases():
            case = materialize(spec.id, root)
            visible = run_visible_tests(case)
            oracle = run_oracle(case)
            broken = bool(case.expected)
            visible_ok = visible.returncode == 0
            oracle_ok = oracle.returncode == 0
            expected_oracle_ok = not broken
            ok = visible_ok and oracle_ok == expected_oracle_ok
            status = "PASS" if ok else "FAIL"
            oracle_label = "PASS" if oracle_ok else "FAIL"
            print(f"{status} {case.id}: visible=PASS oracle={oracle_label}")
            if not ok:
                failures.append((case.id, visible.stdout + visible.stderr, oracle.stdout + oracle.stderr))
    if failures:
        for case_id, visible, oracle in failures:
            print(f"\n--- {case_id} visible ---\n{visible}\n--- oracle ---\n{oracle}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
